from pathlib import Path

import yaml
from tqdm import tqdm

from argus_api.api.events.v1.aggregated import find_aggregated_events
from argus_cli.plugin import register_command
from argus_cli.helpers.log import log
from argus_cli.helpers.pagination import offset_paginated
from argus_cli.utils.arguments import organize_parameters
from argus_cli.utils.formatting import get_data_formatter
from argus_cli.utils.time import timestamp_to_date, date_or_relative
from argus_plugins import argus_cli_module

from argus_plugins.cases.utils import get_customer_id
from argus_plugins.events import utils
from argus_plugins.events.search_model import SearchOptions
from argus_plugins.enrichments import EVENTS_ENRICHMENTS, enrich_data

#: hard limit on maximum results the backend can return
SEARCH_RESULTS_MAX = 100000

argument_api_name_map = {
    "customer": "customerID",
    "flag": "includeFlags",
    "alarm": "alarmID",
    "ip": "ip",
    "source_ip": "sourceIP",
    "destination_ip": "destinationIP",
    "signature": "signature",
    "properties": "properties",
    "attack_category_id": "attackCategoryID",
}


def rename_variables(parameters: dict) -> tuple:
    """Renames input parameters to a more programmable format

    :param parameters: Parameters to convert
    :return: Include and exclude parameters in dicts
    """
    include = {
        argument_api_name_map[key.replace("include_", "")]: value
        for key, value in parameters.items()
        if key.startswith("include_") and value
    }
    exclude = {
        argument_api_name_map[key.replace("exclude_", "")]: value
        for key, value in parameters.items()
        if key.startswith("exclude_") and value
    }

    if "includeFlags" in exclude.keys():
        # Hack because include/exclude flag differs from all other parameters
        include["excludeFlags"] = exclude.pop("includeFlags")

    return include, exclude


def format_event(event: dict) -> dict:
    """Replaces some keys from the event to human readable format

    The following keys are modified:
        r"*timestamp*": Timestamp to ISO8601 date-time format.

    :param event: Event to modify
    :returns: Modified event
    """
    for time_key in filter(lambda key: "timestamp" in key.lower(), event.keys()):
        event[time_key] = timestamp_to_date(event[time_key] / 1000)

    return event


@register_command(extending="events", module=argus_cli_module)
def search(
    start: date_or_relative,
    end: date_or_relative,
    format: get_data_formatter = "csv",
    include_customer: get_customer_id = None,
    exclude_customer: get_customer_id = None,
    include_flag: utils.FLAGS = None,
    exclude_flag: utils.FLAGS = None,
    include_alarm: int = None,
    exclude_alarm: int = None,
    include_ip: str = None,
    exclude_ip: str = None,
    include_source_ip: str = None,
    exclude_source_ip: str = None,
    include_destination_ip: str = None,
    exclude_destination_ip: str = None,
    include_signature: str = None,
    exclude_signature: str = None,
    include_properties: dict = None,
    exclude_properties: dict = None,
    include_attack_category_id: int = None,
    exclude_attack_category_id: int = None,
    exact_match_properties: bool = True,
    min_severity: utils.SEVERITIES = "high",
    min_count: int = None,
    source_ip_min_bits: int = None,
    destination_ip_min_bits: int = None,
    enrich: EVENTS_ENRICHMENTS = None,
    limit: int = 500,
    paginate: bool = True,
    progress: bool = False,
    print_events: bool = True,
):
    """Searches for events in argus.

    Include and exclude parameters are mimics the aggregated event search endpoint,
    and can be found in the api documentation.

    Example use:
        argus-cli events search "2 days ago" "now"
            --format json
            --include-properties '{"argus.timestamp": 9001, "uhost": "host.example.com"}'

    :param start: Start time of the search in ISO8016 format (Example: 2018-01-01)
    :param end: End time of the search in ISO8016 format (Example: 2018-01-01)
    :param format: Follows the normal str.format() syntax.
    :param list include_customer: Customer(s) to include
    :param list exclude_customer: Customer(s) to exclude
    :param list include_flag: Flag(s) to include
    :param list exclude_flag: Flag(s) to exclude
    :param list include_alarm: Alarm ID(s) to include
    :param list exclude_alarm: Alarm ID(s) to exclude
    :param list include_ip: IP(s) to include
    :param list exclude_ip: IP(s) to exclude
    :param list include_source_ip: Source IP(s) to include
    :param list exclude_source_ip: Source IP(s) to exclude
    :param list include_destination_ip: Destination IP(s) to include
    :param list exclude_destination_ip: Destination IP(s) to exclude
    :param list include_signature: Signature(s) to include
    :param list exclude_signature: Signature(s) to exclude
    :param include_properties: Properties to include
    :param exclude_properties: Properties to exclude
    :param list include_attack_category_id: attack category ID(s) to include
    :param list exclude_attack_category_id: attack category ID(s) to exclude
    :param exact_match_properties: Exact match of properties specified at the top level
    :param min_severity: Minimum severity of events
    :param min_count: Minimum aggregated count of events
    :param source_ip_min_bits: Do not include source CIDR\-networks with wider mask than this
    :param destination_ip_min_bits: Do not include destination CIDR\-networks with wider mask than this
    :param list enrich: optional enrichments to perform on the events
    :param limit: number of items to fetch per request ("page size") - default 500
    :param paginate: if set, disable pagination (only the number of results set by --limit will be fetched)
    :param progress: if set, display a progress bar
    :param print_events: set by default. if unset, events will not be printed out.

    :alias format: format-string
    """
    log.info("Organizing parameters...")
    include, exclude = rename_variables(locals())
    parameters = organize_parameters(include, exclude)
    if limit > 1000:
        log.warning(
            "limit is higher that 1000, which can negatively impact the service. Consider setting a lower limit."
        )

    log.info("Getting events from Argus...")
    events = []
    pages = offset_paginated(find_aggregated_events)(
        limit=limit,
        startTimestamp=start,
        endTimestamp=end,
        minSeverity=min_severity,
        minCount=min_count,
        sourceIPMinBits=source_ip_min_bits,
        destinationIPMinBits=destination_ip_min_bits,
        exactMatchProperties=exact_match_properties,
        **parameters,
    )
    if not paginate:
        pages = [pages._first_page]
    progress_bar = None
    for page in pages:
        if page["count"] > SEARCH_RESULTS_MAX:
            log.error(
                f"this search would return more than {SEARCH_RESULTS_MAX} items "
                f"({page['count']}), which is not supported. "
                f"Please narrow your search."
            )
            exit(1)
        if not progress_bar:
            # initialize the progress bar only once we have a count to avoid displaying
            # an empty bar while waiting for the first batch
            progress_bar = tqdm(
                disable=not progress,
                dynamic_ncols=True,
                total=page["count"],
                initial=page["size"],
            )
        else:
            # refresh the total, since data is dynamic
            progress_bar.total = page["count"]
            progress_bar.refresh()
            # update progress manually
            progress_bar.update(page["size"])
        events.extend(page["data"])
    if progress_bar:
        # can be uninitialized if the result set is empty
        progress_bar.close()

    if not events:
        log.info("There are no events in the search.")
        if not print_events:
            return format([])

    if enrich is not None:
        log.debug(f"Enriching events with {' '.join(enrich)}")
        enrich_data(events, enrich)

    log.info("Formatting output to human-readable format...")
    for event in events:
        event = format_event(event)

    formatted = format(events)

    if print_events:
        log.info("Printing output...")
        print(formatted)
    else:
        log.info(f"found {len(events)} events")
        return formatted


@register_command(extending="events", module=argus_cli_module)
def search_yaml(
    config: Path,
    start: date_or_relative,
    end: date_or_relative,
    format: get_data_formatter = "csv",
    limit: int = 500,
    paginate: bool = True,
    progress: bool = False,
):
    """Run a search described in configuration file.

    Example configuration:

      customer:
        include:
          - "mnemonic"
      ip:
        exclude:
          - "127.0.0.1"
        min_severity: "high"
        properties:
          include:
            "example.property": "value"


    :param config: path to the search configuration file.
    :param start: start time of the search in ISO8016 format (Example: 2018-01-01)
    :param end: end time of the search in ISO8016 format (Example: 2018-01-01)
    :param format: follows the normal str.format() syntax.
    :param limit: number of items to fetch per request ("page size") - default 500
    :param paginate: if set, disable pagination (only the number of results set by --limit will be fetched)
    :param progress: if set, display a progress bar
    """
    settings_raw = yaml.safe_load(config.expanduser().read_text())
    settings = SearchOptions(**settings_raw)
    args = settings.to_search_args()
    search(
        start=start,
        end=end,
        format=format,
        limit=limit,
        paginate=paginate,
        progress=progress,
        **args,
    )
