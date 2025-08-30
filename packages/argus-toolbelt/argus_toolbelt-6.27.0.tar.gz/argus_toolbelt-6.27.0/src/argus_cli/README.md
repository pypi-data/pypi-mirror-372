Argus CLI Documentation
==========================================================================================
ArgusCLI is the part of the framework that end developers are going to interact with.
It provides an instance of the Argus API and a framework for registering plugins and
commands to the commandline tool.

Settings file
------------------------------------------------------------------------------------------
Settings can either be in the same directory as the script running *argus_cli* with the
name `settings.yaml`, or in a *user's home directory* with the name `.argus_cli.yaml`, or
specified via an environment variable called `ARGUS_CLI_SETTINGS`.

The application will first look for the environment variable, then the user specified settings,
then the system specified settings.

All available options for the *YAML*-file are listed in the example below:

```yaml
api:
    # Defining the API URL. Do not add a trailing slash
    api_url: "<Base URL for the API>"

    # When using API keys
    api_key: "<Your API key>"

    # When using username based auth
    username = <username>
    password = <password>
    mode = <auth mode (ldap, token, etc)>

cli:
    plugins:
        - <Plugin directory 1>
        - <Plugin directory 2>
        - <Plugin directory ...>

# For more logging settings, see the logging howto in the python docs
logging:
    version: 1
    disable_existing_loggers: false
    formatters:
        simple:
            format: "%(asctime)s %(levelname)s -- %(message)s"
        verbose:
            format: "%(asctime)s %(levelname)s -- %(name)s %(filename)s:%(lineno)s -- %(message)s"
    handlers:
        console:
            level: DEBUG
            class: logging.StreamHandler
            formatter: verbose
    loggers:
        argus_cli:
            level: DEBUG
            handlers: [console]
        argus_api:
            level: INFO
```
