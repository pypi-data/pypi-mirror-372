from typing import Optional, List, NamedTuple, Set
from datetime import datetime

from argus_api.api.cases.v2.case import (
    advanced_case_search,
    list_case_history,
    list_transaction_notifications,
)
from argus_api.api.cases.v2.servicesubscription import list_subscriptions

from argus_cli.utils.formatting import get_data_formatter, FORMATS
from argus_cli.helpers.log import log
from argus_cli.helpers.pagination import offset_paginated
from argus_cli.plugin import register_command
from argus_plugins import argus_cli_module
from argus_plugins.cases.utils import get_customer_id

MNEMONIC_CUSTOMER_ID = 1

#: services a customer must be subscribed to in order to be included in the check
FILTER_SERVICES = ["ids", "logstorage", "irt"]
#: services to which a case must belong to be included in the check
MONITORED_SERVICES = ["ids", "logstorage", "irt", "administrative"]


class SubscribedCustomer(NamedTuple):
    id: int
    name: str
    shortName: str


def get_service_customers() -> Set[SubscribedCustomer]:
    """returns the set of customers subscribed to services that are relevant for the
    notification check.
    """
    customers = set()
    for service in FILTER_SERVICES:
        for page in offset_paginated(list_subscriptions)(service=service):
            customers.update(
                SubscribedCustomer(
                    id=sub["customer"]["id"],
                    name=sub["customer"]["name"],
                    shortName=sub["customer"]["shortName"],
                )
                for sub in page["data"]
            )
    return customers


def customer_is_notified(case_id: int, transaction_id: str) -> bool:
    """Checks if the any of the contacts are NOT a mnemonic email."""
    notifications = list_transaction_notifications(
        case_id,
        transaction_id,
    )["data"]

    return any(
        notification["contact"].split("@")[-1] != "mnemonic.no"
        for notification in notifications
    )


def _is_internal(transaction_or_change: dict) -> bool:
    obj = transaction_or_change.get("object", {})
    if not isinstance(obj, dict):
        return False
    return "INTERNAL" in obj.get("flags", [])


def _is_status_change(transaction: dict) -> bool:
    """a transaction is a status change if only status and/or priority are listed in
    the changes.

    If an internal comment has been added in the transactions it is still only a status
    change from the perspective of the user, who can't see it.
    """
    changes = filter(lambda change: not _is_internal(change), transaction["changes"])
    return all(c["field"] in ("status", "priority", "assignedTechID") for c in changes)


def _is_from_mnemonic(case: dict, transaction: dict) -> bool:
    """Check whether a transaction originates from Mnemonic"""
    if transaction["operation"] == "createCase":
        return "SUBMITTED_BY_TECH" in case["flags"]
    else:
        return transaction["user"]["customer"].get("id", -1) == MNEMONIC_CUSTOMER_ID


def non_notified_transactions(
    case: dict, start: int, end: int, ignored_users=Optional[List[str]]
):
    """Returns all transactions where the customer wasn't notified and it wasn't an internal comment."""

    transactions = list_case_history(
        case["id"],
        operation=["createCase", "addCaseComment", "updateCase", "publishCase"],
        startTimestamp=start,
        endTimestamp=end,
    )["data"]

    for transaction in transactions:

        is_internal = _is_internal(transaction)
        skipped_notification = "SKIP_NOTIFICATION" in transaction.get("flags", [])
        is_status_change = _is_status_change(transaction)
        user_is_ignored = transaction["user"]["userName"] in ignored_users
        from_mnemonic = _is_from_mnemonic(case, transaction)

        if any(
            (
                is_internal,
                is_status_change,
                skipped_notification,
                not from_mnemonic,
                user_is_ignored,
            )
        ):
            # In the case that the comment is internal or is marked as a comment
            # that should be skipped: Ignore the given transaction.
            continue
        elif not customer_is_notified(case["id"], transaction["id"]):
            log.info(
                f"case {case['id']} ({case['customer']['shortName']}) : non notified transaction found : {transaction['id']}"
            )
            yield transaction


@register_command(extending="cases", module=argus_cli_module)
def notification_check(
    start: datetime,
    end: datetime,
    exclude_customer: get_customer_id = [],
    ignore_user: str = [],
    format: FORMATS = "csv",
):
    """Outputs all cases where the customer didn't get a notification

    :param start: The start of the search
    :param end:  The end of the search
    :param list exclude_customer: Customer (shortname) to exclude from the search. Mnemonic is automatically excluded
    :param list ignore_user: Users (shortNames) whose transactions will never be inspected for notifications
    :param format: How the output will be formatted.
    """
    log.warning(
        "This one-off script is going to be moved after ARGUS-11915 is completed!"
    )

    startTimestamp = int(start.timestamp() * 1000)
    endTimestamp = int(end.timestamp() * 1000)

    log.info("Fetching cases...")

    cases = advanced_case_search(
        startTimestamp=startTimestamp,
        endTimestamp=endTimestamp,
        includeDescription=False,
        excludeFlags=["INTERNAL"],
        service=MONITORED_SERVICES,
        customer=[customer.id for customer in get_service_customers()],
        subCriteria=[
            {
                "exclude": True,
                "customerID": [customer for customer in (exclude_customer + [1])],
            }
        ],
        limit=0,
    )["data"]

    log.info("Fetched {} cases".format(len(cases)))

    non_notified = []
    total = len(cases)
    count = 0
    for case in cases:
        count += 1
        log.info(f"Checking case #{case['id']} ({count}/{total})")
        if case["accessMode"] in ("readRestricted", "explicit"):
            log.debug(
                f"skipping case #{case['id']} due to access mode: {case['accessMode']}"
            )
            continue

        for transaction in non_notified_transactions(
            case,
            startTimestamp,
            endTimestamp,
            ignored_users=ignore_user,
        ):
            non_notified.append(
                {
                    "Case ID": "[{id}|https://argusweb.mnemonic.no/spa/case/view/{id}]".format(
                        id=case["id"]
                    ),
                    "Customer": case["customer"]["shortName"],
                    "Transaction Time": datetime.fromtimestamp(
                        transaction["timestamp"] / 1000
                    ).isoformat(sep=" "),
                    "User": transaction["user"]["userName"],
                    "Operation": transaction["operation"],
                    "Sub-Changes": [
                        change["field"] for change in transaction.get("changes", [])
                    ],
                }
            )

    print(get_data_formatter(format)(non_notified))
