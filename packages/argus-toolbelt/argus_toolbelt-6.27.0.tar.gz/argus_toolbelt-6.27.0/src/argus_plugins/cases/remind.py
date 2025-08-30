import smtplib
import sys
import time
import json
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from urllib.parse import quote

from argus_cli.plugin import run
from argus_cli.plugin import register_command
from argus_cli.utils.time import date_or_relative
from argus_cli.helpers.log import log
from argus_api.api.cases.v2.case import advanced_case_search
from argus_plugins import argus_cli_module

from argus_plugins.cases import utils
from argus_plugins.cases.utils import get_customer_id

UNASSIGNED = "unassigned"
SKIPABLES = ["tech", "assigned", "unassigned"]

DEFAULT_STATUS = utils.STATUSES[:-1]  # Exclude closed status


def parse_data(cases: list, skip_notify_tech: bool) -> dict:
    """Parses cases and associates them with a user

    :param cases: Cases to parse
    :param skip_notify_tech: If true, sort all assigned cases under "unassigned"
    :returns: All cases sorted after the user to send to (or "unassigned" to send to notify list)
    """
    parsed_cases = {UNASSIGNED: []}

    for case in cases:
        if case["assignedTech"] and not skip_notify_tech:
            tech = case["assignedTech"]["userName"]
            log.info("%s: Adding case #%s" % (tech, case["id"]))
            if tech not in parsed_cases:
                parsed_cases[tech] = []
            parsed_cases[tech].append(case)
        else:
            log.info("%s: Adding case #%s" % (UNASSIGNED, case["id"]))
            parsed_cases[UNASSIGNED].append(case)

    return parsed_cases


def create_emails(
    subject: str,
    message: str,
    parsed_cases: dict,
    notify: list,
    base_url: str,
    search_criteria=None,
    dry: bool = False,
    from_address: str = "argus-noreply@mnemonic.no",
) -> dict:
    """Crates emails from the parsed_cases dict

    :param subject: The subject of the email
    :param message: The boilerplate part of the email
    :param parsed_cases: The parsed cases to create emails from
    :param notify: Who to notify for unassigned cases
    :param search_criteria: dict of search criterias used to link to a relevant
      search. Used only if there are more than one case.
    :param from_address: The sender address to use
    :return: A mail for each user
    """
    mails = {}

    for user, cases in parsed_cases.items():
        if len(cases) == 0:
            # Don't bother generating a mail without any cases
            continue

        body = ""

        # generate UI search link for multiple cases
        if search_criteria is not None and len(cases) > 1:
            search_url = f"https://{base_url}/spa/case/filter?filterSearch={quote(json.dumps(search_criteria))}"
            body += f'<p><a href="{search_url}">all mentioned cases</a></p>'

        body += f"<p>{message}</p>\n<br>\n"
        for case in cases:
            body += (
                '<p><a href="https://{base_url}/spa/case/view/{case_id}">#{case_id}</a> '
                "- {status} - {subject} - Last Update: {time}</p>\n".format(
                    base_url=base_url,
                    case_id=case["id"],
                    status=case["status"],
                    subject=case["subject"],
                    time=datetime.fromtimestamp(
                        case["lastUpdatedTimestamp"] / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        mails[user] = MIMEText(body, "html")
        mails[user]["Subject"] = subject
        mails[user]["From"] = from_address
        mails[user]["To"] = (
            ";".join(notify) if user == UNASSIGNED else "%s@mnemonic.no" % user
        )

        if dry:
            print(f'To: {mails[user]["To"]}')
            print(f'From: {mails[user]["From"]}')
            print(f'Subject: {mails[user]["Subject"]}')
            print(body)
            print("------------------------------")

    return mails


@register_command(extending="cases", module=argus_cli_module)
def remind(
    subject: str,
    message: str,
    notify: list = None,
    case_type: utils.CASE_TYPES = None,
    service: str = None,
    status: utils.STATUSES = DEFAULT_STATUS,
    customer: str = None,
    exclude_customer: get_customer_id = None,
    priority: utils.PRIORITIES = None,
    skip: SKIPABLES = [],
    skip_assigned: bool = False,
    skip_unassigned: bool = False,
    skip_notify_tech: bool = False,
    skip_not_due: bool = False,
    start: date_or_relative = None,
    end: date_or_relative = None,
    days: int = 14,
    dry: bool = False,
    from_address: str = "argus-noreply@mnemonic.no",
    smtp_host: str = "smtp.mnemonic.no",
    base_url: str = "argusweb.mnemonic.no",
):
    """A command for reminding people when they have pending cases that haven't been updated for a while.

    :param subject: The subject of the email
    :param message: The body of the email
    :param notify: Email(s) to notify for unassigned cases
    :param list case_type: The log type of the case
    :param list service: The service type of the case
    :param list status: The status of the case
    :param list customer: Customers to use (shortname)
    :param list exclude_customer: Customers to exclude
    :param list priority: Priorities to have on the case
    :param list skip: Certain things to not notify about -- DEPRECATED
    :param skip_assigned: Exclude cases which have a tech assignee
    :param skip_not_due: Exclude cases which have not reached the tech due date
    :param skip_unassigned: Exclude cases which are not assigned to any tech
    :param skip_notify_tech: Skip sending notifications to assigned tech, instead only send to notify list (unassigned cases will always be sent to notify list)
    :param start: Only consider cases created after this date
    :param days: Only consider cases updated within the last X days
    :param dry: Runs the program without sending the actual email
    :param from_address: The from-address to send mail from
    :param smtp_host: The SMTP host to send mail from
    :param base_url: The base URL for formatting the email link

    :alias smtp_host: smtp
    """

    if "unassigned" in skip:
        skip_unassigned = True

    if "assigned" in skip:
        skip_assigned = True

    if "tech" in skip:
        skip_notify_tech = True

    log.info("Getting cases to notify about")

    search_criteria = {
        "limit": 0,
        "type": case_type,
        "service": service,
        "status": status,
        "priority": priority,
        "customer": customer,
        "startTimestamp": str(start) if start is not None else None,
        "timeFieldStrategy": ["createdTimestamp"],
        "subCriteria": [],
    }

    if days:
        search_criteria["subCriteria"].append(
            {
                "required": True,
                "timeFieldStrategy": ["lastUpdatedTimestamp"],
                "endTimestamp": ("-%dd" % days),
            }
        )

    if skip_not_due:
        search_criteria["subCriteria"].append(
            {
                "exclude": True,
                "timeFieldStrategy": ["techDueTimestamp"],
                "startTimestamp": "now",
            }
        )

    if skip_assigned:
        search_criteria["subCriteria"].append(
            {
                "required": True,
                "techAssigned": False,
            }
        )

    if skip_unassigned:
        search_criteria["subCriteria"].append(
            {
                "required": True,
                "techAssigned": True,
            }
        )

    if exclude_customer:
        search_criteria["subCriteria"].append(
            {"exclude": True, "customerID": exclude_customer or None}
        )

    result = advanced_case_search(**search_criteria)

    cases = result["data"]
    parsed_cases = parse_data(cases, skip_notify_tech)

    if parsed_cases[UNASSIGNED] and not notify:
        print("No --notify recipient specified")
        sys.exit(1)

    log.info("Creating emails")
    mails = create_emails(
        subject,
        message,
        parsed_cases,
        notify or [],
        base_url,
        dry=dry,
        search_criteria=search_criteria,
        from_address=from_address,
    )

    if len(mails) == 0:
        log.info("No emails to send")
    elif dry:
        log.info("Not sending any emails (DRY RUN)")
    else:
        log.info("Sending email")
        for recipient, mail in mails.items():
            smtp = smtplib.SMTP(smtp_host)
            smtp.send_message(mail)
            smtp.quit()


if __name__ == "__main__":
    run(remind)
