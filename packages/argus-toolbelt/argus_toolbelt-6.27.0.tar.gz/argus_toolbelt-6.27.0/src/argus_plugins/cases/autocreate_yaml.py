import sys
from argparse import ArgumentTypeError
from datetime import datetime
from enum import Enum
from io import StringIO
from pathlib import Path

import dateparser
import yaml
from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_cli.utils.formatting import get_data_formatter
from argus_cli.utils.time import time_parser
from argus_plugins import argus_cli_module
from argus_plugins.cases.autocreate_case import CLOSED_CASE_UPDATE_METHODS, autocreate
from argus_plugins.cases.utils import CASE_TYPES, PRIORITIES, STATUSES
from argus_plugins.events.search import search
from argus_plugins.events.search_model import SearchOptions
from pydantic import BaseModel, ValidationError, validator
from pydantic.typing import Dict, List, Literal, Optional, Union

# convert lists of values to enums for validation
StatusEnum = Enum("StatusEnum", {v: v for v in STATUSES})
PrioritiesEnum = Enum("PrioritiesEnum", {v: v for v in PRIORITIES})
CaseTypesEnum = Enum("CaseTypesEnum", {v: v for v in CASE_TYPES})
ClosedCaseUpdateMethodEnum = Enum(
    "ClosedCaseUpdateMethod",
    {v: v for v in CLOSED_CASE_UPDATE_METHODS},
)


def _relative_time(value: str, base: Optional[datetime] = None) -> datetime:
    """parses a string as a relative datetime.

    if ``base`` is set, input will be parsed as relative to ``base``, otherwise
    it will be parsed as relative to the current datetime.

     :param value: time string to parse. "ago" will be appended to this value if not
       already present. Example: "1 hour" will be parsed as "1 hour ago".
    :param base: if set, point in time to which the value is relative.
    """
    altered_value = value.replace("ago", "").strip() + " ago"
    parse_settings = {"RELATIVE_BASE": base} if base else None
    parsed = dateparser.parse(altered_value, settings=parse_settings)
    if parsed is None:
        raise ValueError(
            f'could not parse time string "{value}" (parsed as: "{altered_value}")'
        )
    return parsed


class TitleFormat(str, Enum):
    fmtstr = ("fmtstr",)
    jinja = "jinja"


class LocalizedCaseTitle(BaseModel):
    en: str
    no: str

    def to_args(self):
        return {"case_title": None, "case_title_no": self.no, "case_title_en": self.en}


class AutocreateCaseOptions(BaseModel):
    group_by: List[str] = []
    title: Optional[Union[str, LocalizedCaseTitle]] = None
    title_format: TitleFormat = TitleFormat.fmtstr
    status: StatusEnum = StatusEnum.pendingCustomer
    priority: PrioritiesEnum = PrioritiesEnum.medium
    type: StatusEnum = CaseTypesEnum.securityIncident
    service: str = "ids"
    category: Optional[str] = None
    close_after_create: bool = False
    use_fields: bool = False

    tags: Optional[Dict[str, str]] = None
    fields: Optional[Dict[str, str]] = None

    class Config:
        use_enum_values = True

    def to_args(self) -> dict:
        """convert the model instance to a dict of arguments ready to be passed
        to the ``autocreate`` function."""
        title_opts = {"case_title": None, "case_title_no": None, "case_title_en": None}
        if isinstance(self.title, str):
            title_opts["case_title"] = self.title
        elif isinstance(self.title, LocalizedCaseTitle):
            title_opts = self.title.to_args()

        return {
            **title_opts,
            "case_status": self.status,
            "case_priority": self.priority,
            "case_type": self.type,
            "case_title_format": self.title_format,
            "case_service": self.service,
            "case_category": self.category,
            "tags": self.tags,
            "fields": self.fields,
            "close_after_create": self.close_after_create,
            "group_by": self.group_by,
            "use_fields": self.use_fields,
        }


class AutocreateNotificationOptions(BaseModel):
    skip_notifications: bool = False
    watcher: Optional[str] = None
    watcher_from_field: Optional[str] = None
    watcher_verbose: Optional[bool] = False

    def to_args(self):
        """convert the model instance to a dict of arguments ready to be passed
        to the ``autocreate`` function."""
        return {
            "case_watcher": self.watcher,
            "case_watcher_from_field": self.watcher_from_field,
            "skip_notifications": self.skip_notifications,
            "case_watcher_verbose": self.watcher_verbose,
        }


class AutocreateWorkflowsOptions(BaseModel):
    request_soc_analysis: Optional[bool] = False
    request: Optional[str] = None
    request_on_update: Optional[str] = None
    acknowledge: Optional[str] = None
    acknowledge_on_update: Optional[str] = None
    comment: Optional[str] = None

    def to_args(self):
        """convert the model instance to a dict of arguments ready to be passed
        to the ``autocreate`` function."""
        return {
            "request_soc_analysis": self.request_soc_analysis,
            "request_workflow": self.request,
            "request_workflow_on_update": self.request_on_update,
            "acknowledge_workflow": self.acknowledge,
            "acknowledge_workflow_on_update": self.acknowledge_on_update,
            "workflow_comment": self.comment,
        }


class AutocreateUpdateOptions(BaseModel):
    closed_case: Optional[ClosedCaseUpdateMethodEnum] = None
    silent: bool = False
    status_on_update: Optional[StatusEnum] = None

    def to_args(self):
        """convert the model instance to a dict of arguments ready to be passed
        to the ``autocreate`` function."""
        return {
            "closed_case_update": self.closed_case,
            "status_on_update": self.status_on_update,
            "silent_update": self.silent,
        }


class AutocreateOptions(BaseModel):
    """Configuration model for the ``autocreate-yaml`` command.

    Allows representing arguments to both ``events search`` and ``cases autocreate``
    commands.
    """

    autocreate_yaml_version: Literal[1] = 1
    search: SearchOptions

    key: str
    template_folder: Optional[Path] = None

    base_time: str = "now"
    time_frame: str
    timeout: Optional[str] = None

    sort_by: List[str] = []

    case: AutocreateCaseOptions = AutocreateCaseOptions()
    notifications: AutocreateNotificationOptions = AutocreateNotificationOptions()
    workflows: AutocreateWorkflowsOptions = AutocreateWorkflowsOptions()
    updates: AutocreateUpdateOptions = AutocreateUpdateOptions()

    initial_internal_comment: bool = False
    internal_case: bool = False
    send_to_qa: bool = False
    explicit_access: List[str] = []

    attach_events: Optional[Literal["json", "csv"]] = None

    test_data: bool = False
    default_prod_excluded_flags: List[str] = ["NOTIFIED", "INITIAL_TUNING"]

    class Config:
        use_enum_values = True

    def search_time_args(self) -> dict:
        """converts time values to a dict of arguments ready to be passed to the
        events ``search`` function.
        """
        return {
            "start": int(self.start_dt.timestamp() * 1000),
            "end": int(self.end_dt.timestamp() * 1000),
        }

    @property
    def end_dt(self):
        return _relative_time(self.base_time)

    @property
    def start_dt(self):
        return _relative_time(self.time_frame, base=self.end_dt)

    @property
    def timeout_dt(self):
        if not self.timeout:
            return datetime.now()
        return _relative_time(self.timeout, base=self.end_dt)

    def to_search_args(self):
        """converts relevant settings to the full set of arguments expected by
        the events ``search`` function.
        """
        return {
            **self.search.to_search_args(),
            **self.search_time_args(),
            "format": get_data_formatter("json"),
            "print_events": False,
        }

    def to_autocreate_args(self):
        """converts relevant settings to the full set of arguments expected by
        the events ``autocreate`` function.
        """
        args = self.dict(
            exclude={
                "search",
                "case",
                "notifications",
                "workflows",
                "updates",
                "base_time",
                "time_frame",
                "default_prod_excluded_flags",
                "timeout",
                "autocreate_yaml_version",
            }
        )
        args.update(
            {
                **self.notifications.to_args(),
                **self.case.to_args(),
                **self.notifications.to_args(),
                **self.workflows.to_args(),
                **self.updates.to_args(),
                "timeout": self.timeout_dt,
            }
        )
        return args

    @validator("base_time", always=True)
    def validate_datetime(cls, v):
        try:
            time_parser(v)
        except ArgumentTypeError:
            raise ValueError(f'could not parse time string "{v}"')
        return v

    @validator("time_frame", "timeout", always=True)
    def validate_relative_dt(cls, v):
        if v is None:
            return v
        _relative_time(v)
        return v


def debug_time_settings(
    settings: AutocreateOptions,
) -> None:
    """print out information about time configuration parsing.

    :param settings: autocreate configuration.
    """
    base_time_dt = settings.end_dt
    base_time_ts = int(base_time_dt.timestamp() * 1000)
    start_time_dt = settings.start_dt
    start_time_ts = int(start_time_dt.timestamp() * 1000)

    print("SEARCH INTERVAL:")
    print(
        f'base_time (end time): "{settings.base_time}" - parsed: "{base_time_dt}" ( timestamp: {base_time_ts} )'
    )
    print(f"start time: {start_time_dt} ( timestamp: {start_time_ts} )")
    print(
        f'start time calculated based on time_frame "{settings.time_frame}" parsed as "{settings.time_frame} ago" from base_time ({base_time_dt})'
    )
    print(
        f'search interval: from "{start_time_dt}" to "{base_time_dt} ({start_time_ts} to {base_time_ts})"'
    )
    print()
    print("TIMEOUT:")
    if settings.timeout is None:
        print(f'timeout: not set, using current datetime ("{settings.timeout_dt}")')
    else:
        timeout_dt = settings.timeout_dt
        timeout_ts = int(timeout_dt.timestamp() * 1000)
        print(
            f'timeout: "{settings.timeout}" parsed as "{settings.timeout} ago" from base_time ("{base_time_dt}") - parsed: "{timeout_dt}" ( timestamp: {timeout_ts} )'
        )


@register_command(extending="cases", module=argus_cli_module)
def autocreate_yaml(
    config: Path,
    template_folder: Path = None,
    dry: bool = False,
    base_time: str = None,
    time_frame: str = None,
    test_time_expr: bool = False,
    validate: bool = False,
    prod_excludes: bool = True,
):
    """A tool for automatically creating a case based on event - YAML edition

    Values from the configuration file will be passed to the "events search"
    and "cases autocreate" commands.

    Example configuration:
        key: "example"
        template_folder: "test_templates"
        time_frame: "1 day"
        timeout: "1 hour"
        search:
          customer:
            include:
              - "mnemonic"

    :param config: path to the autoreport configuration file.
    :param dry: if set, no data will be commited by autocreate.
    :param base_time: if set, overrides the base_time set in the configuration.
    :param time_frame: if set, overrides the time_frame set in the configuration.
    :param test_time_expr: if set, print information about time values parsing and exit.
    :param validate: if set, only check that the configuration is valid and exit.
    :param prod_excludes: if set to false with --no-prod-excludes, flags that are
      excluded by default during event search will not be excluded.
    """
    settings_raw = yaml.safe_load(config.expanduser().read_text())

    if validate:
        try:
            AutocreateOptions.validate(settings_raw)
        except ValidationError as e:
            print(str(e))
            sys.exit(1)
        print(f'"{config}" contains valid autocreate configuration data.')
        sys.exit(0)

    settings = AutocreateOptions(**settings_raw)
    if template_folder:
        settings.template_folder = template_folder
    elif not settings.template_folder:
        print(
            "no template_folder is set in the configuration file, --template-folder is required."
        )
        exit(1)

    if base_time:
        settings.base_time = base_time
    if time_frame:
        settings.time_frame = time_frame

    if test_time_expr:
        debug_time_settings(settings)
        sys.exit()

    search_args = settings.to_search_args()

    if prod_excludes:
        log.info(
            f"adding production excluded flags: {settings.default_prod_excluded_flags}"
        )
        search_args["exclude_flag"] = (
            search_args.get("exclude_flag") or []
        ) + settings.default_prod_excluded_flags

    log.info("running search")
    search_results = search(**search_args)
    search_output = StringIO()
    search_output.write(search_results)
    search_output.seek(0)

    autocreate_args = settings.to_autocreate_args()
    autocreate_args["data"] = search_output
    if dry:
        autocreate_args["dry"] = True

    log.info("running autocreate")
    autocreate(**autocreate_args)
