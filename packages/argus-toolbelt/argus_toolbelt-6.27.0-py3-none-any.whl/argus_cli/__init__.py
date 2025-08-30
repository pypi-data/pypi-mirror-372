try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

__version__ = version("argus-toolbelt")

argus_api_version = version("argus-api")
try:
    internal_plugins_version = version("argus-cli-internal-plugins")
except PackageNotFoundError:
    internal_plugins_version = "not installed"

from .plugin import register_command, register_provider, run
