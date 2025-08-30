Argus Plugins
================================================================================================
ArgusCLI provides an interface for your plugins, abstracting away tedious tasks such as 
parameter validation and command line argument parsers from the developer.

By default, Argus Toolbelt provides the Argus Plugins package as a default set of plugins,
but creating your own plugins is easy, and we hope this will encourage developers to
contribute with their own plugin to interface with the Argus API.


Creating a new plugin
-----------------------------------------------------------------------------------------
The `register_command` decorator will register a command against a plugin with a given name.
Both the plugin and the name of the command can be changed via it's parameters.
These parameters are `extending` and `alias`.

### Function metadata
Argus CLI will by default introspect functions when they've been registered with the framework
using the `@register_command()` decorator, which means that the function signature will be
used to create the command-line arguments, and the function docstring will be used to provide
command line documentation. 

Since Python 3.5, Python supports [function annotations](https://www.python.org/dev/peps/pep-3107/),
and Argus CLI uses these to infer the argument types from the function signature, and create
the right type of command-line arguments for your plugin.

Commandline help-text, and parameter descriptions, is extracted from the function docstring,
expected to follow the *reSTructuredText* style used by Sphinx autodoc

### Example #1: Registering a command

```python
@register_command()
def your_plugin_command(your_argument: str) -> str:
    """Short description becomes the plugin help text

    Longer description follows after a newline

    :param your_argument: This parameter description becomes the commandline argument help text
    """
    return your_argument
```

### Example #2: Registering a command with extra functionality

Pre-defined choices (enum fields) can be expressed as a *populated list*:
You can alias a keyword argument to something else using `:alias your_argument: something_else`

```python
@register_command()
def your_plugin_command(your_argument: ["option1", "option2"]):
    """This function has an argument that will be called something else on the command-line

    :param your_argument: This should be called something-else on the command-line
    :alias your_argument: something_else
    """
    pass
```

| **Note:** Plugins and their arguments are turned from snake_case into kebab-case on the commandline


Guides
-----------------------------------------------------------------------------------------

### Creating a simple plugin

Creating a plugin should be easy: Just create a new python file inside on of your plugin directories,
as defined by your `.argus_cli.yaml` settings file created during installation. By default, this file
will be found in your `$HOME` folder.


**Step 1**: Create the script

We want to call this plugin `basic-example`; so lets first create the file `basic_example.py`.
Argus CLI will now automatically load this file, and functions inside it that register commands
will be available on the commandline.


**Step 2**: Add a function

Create a simple function that says `Hello, Argus`. This will be the base for our plugin.

```python
def hello():
    print("Hello, Argus")
```

**Step 3**: Register the command to the commandline

Plugin registration is done with the `register_command` decorator from `argus_cli.plugins`.
This *decorator* will register your command against your plugin (which is the name of the file, converted
to kebab-case).

```python
from argus_cli.plugins import register_command

@register_command()
def hello():
    print("Hello, Argus")
```

**Step 4**: Adding help text to the plugin command

Now, let's add some *metadata* to our function. This metadata lets ArgusCLI give the user help text,
does type checking for arguments and create aliases. The framework is designed to force developers to
document their functions, so you'll need to use docstrings to add metadata.

The format for this is like a normal *reST* docstring. It contains the help-text and description that
will show up when the user runs the application with `-h` or `--help` and *reST* metadata parameters
(`:<metadata-field>:`).

Any of these parts can be omitted, but it is recommended to at least have a help-text.
```python
"""<help text>

<command description>

<metadata>
```

Let's update the command to provide some help-text:
```python
from argus_cli.plugins import register_command

@register_command()
def hello():
    """Print 'Hello, Argus'"""
    print("Hello, Argus")
```


Now let's modify our command to say hello to the user instead.
```python
from argus_cli.plugins import register_command

@register_command()
def hello(username):
    """Says hello to the user

    :param str username: Your name
    :alias username: name
    """
    print("Hello, %s" % username)
```

Now you can run your plugin by writing: `argus_cli basic-example hello --name Bob`.
Your terminal will now greet you, and you'll see `Hello, Bob`!


### Creating an API plugin
API plugins are super easy to write. The only thing you need to do to create a plugin
that use *ArgusAPI*, is to import the functions you need from `argus_api.api`

Lets create a plugin that shows the user how many alarms there are in Argus.
```python
from argus_api.api.alarms.v1.alarm import get_alarms
from argus_cli.plugins import register_command

@register_command(alias="number_of_alarms")
def num_alarms():
    """Displays the number of alarms in argus"""
    alarms = get_alarms()
    print("There are %d alarms" % alarms["count"])
```

You'll notice that this command introduces the `alias` parameter to `register_command`.
This parameter is handy for when you want to call your command something else than your function.
Now you can write `argus_cli basics number-of-alarms` to use the command.

The [Argus API documentation](https://docs.mnemonic.no/display/public/API/mnemonic+API+documentation) is a valuable resource
when writing commands that use the API, so make sure to have it handy. You can also inspect
the API functions source code to see more information on their parameters and how to use them

### Logging from a plugin
Any developer knows that troubleshooting is easier with a log that shows what the program is doing.
Because of this *ArgusCLI* has it's own logger with a plugin log level.

This log level is below `DEBUG`, so make sure that your log level is set to DEBUG.

This logger can be imported from `argus_cli.helpers.log`.

```python
from argus_cli.plugins import register_command
from argus_cli.helpers.log import log

@register_command()
def i_do_things():
    """Does things"""
    log.plugin("I am entering the plugin!")
    print("Goodbye cruel world")
    log.plugin("And now I'm leaving")
```

Your commandline will now show the logging and the print (or not, if you've set it to log it to a file).
```
[11:16:09.342][PLUGIN][basics.py:7]: I am entering the plugin!
Goodbye cruel world
[11:16:09.343][PLUGIN][basics.py:9]: And now I'm leaving
```
