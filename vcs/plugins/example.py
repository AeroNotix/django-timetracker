'''This is an example plugin module.

The plugin directory should contain as many python source files as you
wish so that they will be available for choice in the VCS section of
the timetracker.

They allow you to easily add or remove report processors from the
application with minimal impact to the rest of the codebase.

However, they require that you adhere to a strict interface.

Each plugin MUST contain:

* ACCOUNTS

A list of account names for which this report processor is available
to.

* CALLBACK

The name of the function which provides this plugin's functionality.

* PLUGIN_NAME

The pretty-printed name of this plugin, this will be displayed to the
user so ensure that it is understandable what this report is and does.
'''

ACCOUNTS = ["PW", "QR", "TT"]
CALLBACK = "main"
PLUGIN_NAME = "An example plugin module!"

def main(f):
    save_to_disk(f)
