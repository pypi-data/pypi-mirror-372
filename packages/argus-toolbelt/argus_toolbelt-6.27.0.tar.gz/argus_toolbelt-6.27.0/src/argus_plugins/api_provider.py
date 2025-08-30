import importlib
import pkgutil

from argus_cli import register_provider
from argus_cli.settings import settings
from argus_cli.helpers.log import log


# TODO: Debug isn't used, but rather look at settings._get_debug_mode.
#       This should be fixed.
# TODO: Environment isn't used, same thing as with --debug.
@register_provider()
def argus_api(apikey: str = None, debug: bool = False, environment: str = None) -> None:
    """Argus CLI provider"""
    if apikey:
        settings["api"]["api_key"] = apikey


def import_submodules(
    package: str, exclude_name: str = None, recursive: bool = True
) -> dict:
    """Import all submodules of a module, recursively.

    This is used to import all APIs when Argus is loaded,
    so that the commands become registered as plugins,
    but can also be used to recursively import any other
    package where you want every single file to load.

    :param package: Package name, e.g "argus_api.api"
    :param exclude_name: Any module containing this string will not be imported
    :param recursive: Recourse trough the package structure to import files?
    """
    module = importlib.import_module(package)

    results = {}

    for loader, name, is_pkg in pkgutil.iter_modules(
        module.__path__, prefix=package + "."
    ):
        if exclude_name and exclude_name in name:
            log.debug(f"{name} is in exclude_name, ignoring")
            continue

        results[name] = importlib.import_module(name)
        if recursive and is_pkg:
            results.update(import_submodules(name, exclude_name=exclude_name))
    return results
