from argus_cli.plugin import register_command
from argus_cli.helpers import formatting

from argus_api.api.customers.v2.customer import get_customer
from argus_api.api.customernetworks.v1.network import get_customer_networks
from argus_api.api.sensors.v1.location import list_locations as _list_locations
from argus_plugins import argus_cli_module


@register_command(extending="customer-networks", module=argus_cli_module)
def list(customer: str) -> None:
    """
    This function handles the subcommand "show", and only fetches and displays a list of existing networks

    :param customer: Customer shortname or ID
    """

    # Find customer by name
    customer = get_customer(idOrShortName=customer)

    if not customer:
        raise LookupError(
            "No customer has been selected. Customer is required to edit customer networks."
        )

    # Otherwise select the only customer
    networks = get_customer_networks(customerID=[customer["data"]["id"]], limit=0)

    def format_column(value: dict, key: str):
        if key == "flags" and value:
            return ",".join(value)
        elif key == "networkAddress":
            return "%s/%s" % (value["address"], value["maskBits"])
        elif key == "location":
            return value["name"]
        else:
            return value or "-"

    print(
        formatting.table(
            data=networks["data"],
            keys=["networkAddress", "description", "zone", "location", "flags"],
            format=format_column,
            title="Networks for %s" % customer["data"]["name"],
        )
    )


@register_command(extending="customer-networks", module=argus_cli_module)
def list_locations(customer: str) -> None:
    """
    This function handles the subcommand "show", and only fetches and displays a list of existing networks

    :param customer: Customer whose locations to search (shortname or ID).
    """

    # Find customer by name
    customer = get_customer(idOrShortName=customer)["data"]

    locations = _list_locations(customerID=customer["id"], limit=0)["data"]

    def format_column(value: dict, key: str):
        if key == "flags" and value:
            return ",".join(value)
        elif key == "networkAddress":
            return "%s/%s" % (value["address"], value["maskBits"])
        elif key == "location":
            return value["name"]
        else:
            return value or "-"

    print(
        formatting.table(
            data=locations,
            keys=["id", "shortName", "zone", "name", "flags"],
            format=format_column,
            title="Locations",
        )
    )
