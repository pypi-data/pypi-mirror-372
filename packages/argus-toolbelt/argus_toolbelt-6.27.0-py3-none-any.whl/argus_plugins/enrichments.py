"""
Provides enrichments: functions that will add data to the input objects.

all enrichment data should be placed under a top-level field in order to avoid
name collisions with API fields.
"""
import enum
from typing import Union, Iterable
from functools import lru_cache

from argus_api.api.customernetworks.v1.network import search_customer_network
from argus_cli.helpers.log import log

# enrichment data will be stored in the following field of the enriched object's
# dictionary.
ENRICHMENTS_FIELD_NAME = "_enrichments_"


class Enrichments(enum.Enum):
    """Valid enrichment names"""

    EVENTS_CUSTOMER_NEWORKS_SOURCE = "customer-networks-source"
    EVENTS_CUSTOMER_NEWORKS_DESTINATION = "customer-networks-destination"

    @classmethod
    def has_value(cls, value):
        return value in (i.value for i in cls)


# enrichment applicable to event data
EVENTS_ENRICHMENTS = [
    Enrichments.EVENTS_CUSTOMER_NEWORKS_SOURCE.value,
    Enrichments.EVENTS_CUSTOMER_NEWORKS_DESTINATION.value,
]


class IPTypeField(enum.Enum):
    """Valid IP fields

    Event field from which to read - and enrichment field to write -
    IP address information from/to.
    """

    SOURCE = "source"
    DESTINATION = "destination"


def enrich_data(data: Iterable[dict], enrichments: Iterable[str]) -> None:
    """Performs the selected enrichment on the data

    :param data: input data as an iterable of API objects
    :param enrichments: names of enrichments to perform
    """
    for enrichment in (e for e in enrichments if not Enrichments.has_value(e)):
        log.warn(f'"{enrichment}" is not a valid enrichment name')

    if Enrichments.EVENTS_CUSTOMER_NEWORKS_SOURCE.value in enrichments:
        events_customer_networks(data, IPTypeField.SOURCE)
    if Enrichments.EVENTS_CUSTOMER_NEWORKS_DESTINATION.value in enrichments:
        events_customer_networks(data, IPTypeField.DESTINATION)


def events_customer_networks(events: Iterable[dict], field: IPTypeField) -> None:
    """Adds customer network information to events.

    Each event's IP address (source or destination, based on the value of the
    field parameter) is read from the event and searched for through the
    customer networks API.

    If the search has results, they are added to the enrichment field of the
    event as a list of API customer networks dictionaries. Otherwise, the
    field's value is set to None.

    The added fields are:
    event[ENRICHMENTS_FIELD_NAME]["customer-networks"][field]

    :param events: events to enrich
    :param field: the ip field from which the ip address will be read and
        destination field to which enrichment data will be writen.
    """

    enrich_field_name = "customer-networks"
    log.debug(f"runnning enrichment {enrich_field_name}-{field.value}")

    def enrich_event(event: dict) -> None:
        """Adds enrichment data to the event

        Calls the other nested functions to fetch enrichment data and adds it
        to an event.

        :param event: input event dict
        """
        ip = _get_ip(event)
        customer_id = _get_customer_id(event)
        enrich_field = event.setdefault(ENRICHMENTS_FIELD_NAME, {})
        enrich_subfield = enrich_field.setdefault(enrich_field_name, {})
        enrich_subfield.update({field.value: _lookup_networks(ip, customer_id)})

    def _get_ip(event: dict) -> Union[str, None]:
        """Get an event's source/destination IP address.

        :param event: input event dict
        :return: event's IP address or None
        """
        try:
            return event[field.value]["networkAddress"]["address"]
        except (KeyError, TypeError):
            return None

    def _get_customer_id(event: dict) -> Union[int, None]:
        """Get an event's customer ID.

        :param event: input event dict
        :return: event's IP customer ID or None
        """
        id_str = event.get("customerInfo", {}).get("id")
        return int(id_str) if id_str is not None else None

    def _get_net_mask(network: dict) -> Union[int, None]:
        """Extracts the mask from a Customer Network

        :param network: input custommer network's dict
        :return: network mask bits or None
        """
        return network.get("networkAddress", {}).get("maskBits")

    @lru_cache(maxsize=0)
    def _lookup_networks(ip: str, customerID: int) -> Union[dict, None]:
        """Returns customer networks for a given IP.

        :param ip: the IP to search for
        :param customerID: the customer's ID
        :return: list of customer networks dict or None if no results
        """
        if ip is None or customerID is None:
            return None
        networks = search_customer_network(customerID=customerID, addresses=[ip])
        networks_data = networks.get("data")
        if networks_data is not None:
            # sort from most specific to least specific
            networks_data.sort(key=_get_net_mask, reverse=True)
        return networks_data

    for event in events:
        enrich_event(event)
