# egos-helpers

A python library for helper functions. Used in the [egos-tech](https://gitlab.com/egos-tech) projects.

## Functions

* `gather_environ`: Return a dict of environment variables correlating to the keys dict.
* `short_msg`: Truncates the message to `chars` characters and adds two dots at the end.
* `strtobool`: Converts a string to a boolean
* `redact`: Replaces in `message` the `param` string with `replace_value`

See [egos_helpers/core.py](https://gitlab.com/egos-tech/egos-helpers/-/blob/main/egos_helpers/core.py) for the full description of each function.

## Usage example

Install `egos-helpers`:

```sh
python3 -m venv .venv
source .venv/bin/activate
# if you don't have a requirements.txt file
pip install -U egos-helpers
# if you do have a requirements.txt file
pip install -U -r requirements.txt
```

In your python project:

```py
from egos_helpers import gather_environ

class MyClass:

    keys = {
        'key_one': {
            'default': ['one', 2],
            'type': "list",
        },
        'key_two':{
            'hidden': True,
            'default': False,
            'type': "boolean",
        },
        'key_three': {
            'default': [],
            'type': "filter",
        },
        'key_four': {
            'default': None,
            'redact': True,
            'type': 'string',
        },
        'key_five': {
            'default': 12,
            'type': 'int',
        },
        'key_six': {
            'default': 'INFO',
            'type': 'enum',
            'values': [
                'DEBUG',
                'INFO',
                'WARNING',
                'ERROR'
            ],
        },
        'key_seven': {
            'default': '12',
            'deprecated': True,
            'replaced_by': 'key_five',
            'type': 'int',
        }
    }

    def __init__(self):
        envkeys = gather_environ(keys=MyClass.keys)
        print(envkeys)
```
