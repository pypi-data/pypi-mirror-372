from argus_cli.plugin import create_module, import_external_plugins
from argus_plugins.api_provider import argus_api
from argus_cli import __version__, argus_api_version, internal_plugins_version

cli_versions = f"argus-toolbelt: {__version__}, argus-api: {argus_api_version}, argus-cli-internal-plugins: {internal_plugins_version}"

__all__ = [
    "assets",
    "cases",
    "customer_networks",
    "datastore",
    "events",
    "reports",
]

# Initialize the toolbelt with the framework.
argus_cli_module = create_module(providers=[argus_api])
argus_cli_module.argument_parser.add_argument(
    "--version", action="version", version=cli_versions
)
