from argus_cli.plugin import run, import_external_plugins

from argus_plugins import argus_cli_module
from argus_plugins.api_provider import import_submodules

# Import commands so that they get registered
from argus_plugins import *


def main():
    import_submodules("argus_api.api")
    import_external_plugins("argus_cli.plugins")
    run(argus_cli_module)


if __name__ == "__main__":
    main()
