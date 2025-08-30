from argus_cli.helpers import formatting


def diff_table(network_list: list, show_only_changes: bool = False) -> list:
    """Creates a dict with each network appearing twice, first
    with the existing data, in red, then with the changed data,
    in green, to show the diff before creating / updating / destroying

    :param bool show_only_changes: Only show the green row with changes (used for create action)
    :param list network_list: List of CustomerNetworks
    :returns: List with two rows for each network, one in green and one in red
    :returns: List[Dict[str, str]]
    """

    data = []
    for network in network_list:
        json = network.to_json()
        # Clean (before change) fields:
        if not show_only_changes:
            data.append(
                {
                    "IP": formatting.red("- " + json["networkAddress"]),
                    "Description": formatting.red(network["description"]),
                    "Zone": formatting.red(
                        network["zone"] if "zone" in network else ""
                    ),
                    "Location": formatting.red(
                        network["location"] if "location" in network else ""
                    ),
                    "Flags": formatting.red(", ".join(network["flags"])),
                }
            )

        json.update(network._dirty)
        # Changed fields:
        data.append(
            {
                "IP": formatting.green("+ " + json["networkAddress"]),
                "Description": formatting.green(json["description"]),
                "Zone": formatting.green(network["zone"] if "zone" in network else ""),
                "Location": formatting.green(
                    network["location"] if "location" in network else ""
                ),
                "Flags": formatting.green(", ".join(network.expected_flags())),
            }
        )
    return data


def diff_file_vs_argus(
    network_list: list,
    existing_networks: list,
) -> dict:
    """Compares a list of networks from a file to the networks on Argus for the customer,
    and returns a dict with keys: NOT_IN_FILE, CHANGED_IN_FILE, NOT_ON_SERVER, UNMODIFIED

    :param list network_list: Networks in file
    :param list existing_networks: Networks on Argus
    :param str api_key: API key to perform requests with
    :returns: Dict[str, list]
    """
    diff = {
        "NOT_IN_FILE": [],
        "CHANGED_IN_FILE": [],
        "NOT_ON_SERVER": [],
        "UNMODIFIED": [],
    }
    for network in existing_networks:
        # Check all existing networks
        if all((network not in network_on_file for network_on_file in network_list)):
            diff["NOT_IN_FILE"].append(network)
    for network in network_list:
        if any(
            (
                network_on_server.merge(network)
                for network_on_server in existing_networks
                if network in network_on_server and network != network_on_server
            )
        ):
            # Get the first network that is the same, but has
            # changed locally - that is, the network address and
            # subnet matches but flags, description, or
            # something else is different in the data received
            # from file
            merged = network.merge(
                next(
                    filter(
                        lambda network_on_server: (
                            network in network_on_server
                            and network != network_on_server
                        ),
                        existing_networks,
                    )
                )
            )
            diff["CHANGED_IN_FILE"].append(merged)
    for network in network_list:
        if all(
            (
                network not in network_on_server
                for network_on_server in existing_networks
            )
        ):
            diff["NOT_ON_SERVER"].append(network)
    for network in network_list:
        if any(
            (network == network_on_server for network_on_server in existing_networks)
        ):
            diff["UNMODIFIED"].append(network)
    return diff
