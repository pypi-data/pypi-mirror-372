"""Load default YAML settings file, then look for user defined settings and create a ChainMap."""
from collections.abc import MutableMapping
from collections import defaultdict
from argparse import ArgumentParser
from pathlib import Path

import functools
import inspect
import yaml
import os


class ConfigurationError(Exception):
    pass


try:
    from yamlinclude import YamlIncludeConstructor
except ImportError:
    YamlIncludeConstructor = None

from argus_cli.helpers import log as log_module


# FIXME: Legacy. This instance should be removed, but is depended by api_generator.
ARGUS_CLI_CONFIG_LOCATION = Path(
    os.environ.get("ARGUS_CLI_SETTINGS", os.path.expanduser("~/.argus_cli.yaml"))
)
ARGUS_CLI_SETTINGS_INCLUDES = Path(
    os.environ.get("ARGUS_CLI_SETTINGS_INCLUDES", "~/.argus_cli.d")
).expanduser()

MISSING_INCLUDES_ERROR = "could not determine a constructor for the tag '!include'"
NO_INCLUDES_MSG = "the configuration uses includes but they are not enabled - install pyyaml-include to enable includes"

if YamlIncludeConstructor:
    # setup yaml includes if available
    YamlIncludeConstructor.add_to_loader_class(
        loader_class=yaml.SafeLoader, base_dir=ARGUS_CLI_SETTINGS_INCLUDES
    )


def _merge(source: dict, destination: dict) -> dict:
    """Deep merges two dictionaries and replaces values from destination with the ones from source."""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            _merge(value, node)
        else:
            destination[key] = value

    return destination


def _get_environment() -> str:
    # TODO: This should really be handled in a better way, but might need some refactoring
    provider = ArgumentParser(add_help=False)
    provider.add_argument("--environment")
    arguments = vars(provider.parse_known_args()[0])

    return arguments.get("environment")


def _get_debug_mode(config: dict) -> dict:
    """Sets up debug mode if there is a --debug argument on the commandline"""
    provider = ArgumentParser(add_help=False)
    provider.add_argument("--debug", action="store_true")
    arguments = vars(provider.parse_known_args()[0])

    if arguments.get("debug"):
        config["global"] = {"debug": True}

        for logger in config["logging"]["handlers"].values():
            logger["level"] = "DEBUG"

        log_module.log.info("Debug mode activated!")

    return config


def nested_defaultdict():
    return defaultdict(nested_defaultdict)


class Config(MutableMapping):
    """Loads and stores data from configuration.

    Configuration is either loaded from the system environment variables or
    the provided configuration file.

    Environments
    ------------

    The configuration files can also have a custom "environments" inside them,
    for specific use-cases. For example when a user wants to run a command in a
    development environment.

    These custom environments will be found under the top level key
    `environments`. Under this key the first key will be the name of the
    custom environment, and bellow this again will be the normal keys.

    In the following example, we have a development environment with a
    custom URL.

    .. code-block:: yaml
        api:
            url: https://example.com/

        environments:
            development:
                api:
                    url: https://test.example.com/
    """

    #: Stores the configuration variables
    _dict = nested_defaultdict()

    env_key = None
    config_key = None

    def __init__(
        self,
        env_prefix: str = None,
        config_file: Path = None,
        base_config: dict = None,
        environment: str = None,
    ):
        """Creates a new config

        :param env_prefix: Will be prepended to all env checks (e.g. "<PREFIX>_KEY")
        :param config_file: The file where the config can be found
        :param base_config: Config base to base off
        :param environment: Environment tag in the settings to load on get
        """
        if not base_config:
            base_config = {}

        if config_file:
            with open(str(config_file.absolute())) as f:
                try:
                    file_config = yaml.safe_load(f) or {}
                except yaml.constructor.ConstructorError as e:
                    if MISSING_INCLUDES_ERROR in e.problem:
                        raise ConfigurationError(NO_INCLUDES_MSG)
                    raise

        else:
            file_config = {}

        self.env_prefix = (
            env_prefix or ""
        )  # With no prefix, it can be left blank as we're doing string formatting.

        self._dict = _merge(file_config, base_config)
        if environment:
            try:
                self._dict = _merge(
                    # If a key is empty, it will be None. That would make _merge raise an exception.
                    self._dict["environments"][environment] or {},
                    self._dict,
                )
            except KeyError as e:
                # Give the key error a bit more descriptive text
                raise KeyError(
                    "Could not find custom environments '{env}'. Is the environment"
                    " present under 'environments' in your config file?".format(
                        env=environment
                    )
                )

    def __call__(
        self, func: callable = None, *, env_key: str = None, config_key: str = None
    ):
        """Decorator to create a partial function with arguments from config or env filled in.

        Can be called with or without parameters.

        Example:
            >>> @config
            Or:
            >>> @config(env_key="something", config_key="funny")

        :param func: Function to decorate
        :param env_key: Environment key for this function
        :param config_key: Config key for this function
        """
        if not func:
            return functools.partial(self, config_key=config_key, env_key=env_key)

        # TODO: Find a cleaner way to do this
        self.config_key = config_key
        self.env_key = env_key

        arguments = {
            name: self[name]
            for name in inspect.signature(func).parameters.keys()
            if name in self
        }

        self.env_key = None
        self.config_key = None

        return functools.partial(func, **arguments)

    def __getitem__(self, key):
        """Gets an item from either the dict or the env."""
        env_key = key
        if self.env_prefix:
            env_key = self.env_prefix + "_" + key
        if self.env_key:
            env_key = self.env_key + "_" + key

        try:
            # Try to get from the environment
            return os.environ[env_key.upper()]
        except KeyError:
            if self.config_key:
                return self._dict[self.config_key][key]
            return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)


def generate_config(environment: str = None):
    try:
        base_config = yaml.safe_load(
            open(Path(__file__).resolve().parent / "resources" / "config.yaml")
        )
    except yaml.constructor.ConstructorError as e:
        if MISSING_INCLUDES_ERROR in e.problem:
            raise ConfigurationError(NO_INCLUDES_MSG)
        raise
    return Config(
        env_prefix="ARGUS",
        config_file=ARGUS_CLI_CONFIG_LOCATION
        if ARGUS_CLI_CONFIG_LOCATION.exists()
        else None,
        environment=environment,
        base_config=base_config,
    )


settings = generate_config(_get_environment())
_get_debug_mode(settings)
log_module.setup_logger(settings["logging"])
