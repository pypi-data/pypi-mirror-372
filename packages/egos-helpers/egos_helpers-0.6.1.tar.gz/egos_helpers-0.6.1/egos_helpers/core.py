#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Helper functions """

import logging
import os
from typing import Any, Dict, Optional
from .constants import NAME

log = logging.getLogger(NAME)

def gather_environ(keys: Dict[str,Dict[str,Any]]) -> Dict[str,Any]:
    """
    Return a dict of environment variables correlating to the keys dict.
    The environment variables have to be set in **ALL_UPPER_CASE**.

    Supported settings for each key:
    * `type`: one of `string`, `int`, `list`, `boolean`, `enum` or `filter`
    * `default`: if omitted, it will be set to `None`
    * `hidden`: no `log.info` will be generated if unset or a default value
                is used
    * `deprecated`: boolean flag to issue a `log.warning` if set
    * `replaced_by`: string referencing the name of another key, that should
                     take the value of this key if `deprecated` is `True`
    * `redact`: boolean flag to have the value of this key replaced with a
                redacted string in the `log.info` message

    Every environment variable found will be echoed on `log.info()` (except those
    with `redact: True`).

    `boolean` keys will use :py:func:`strtobool` to convert a string to boolean.

    The env separator for the type `list` is `<space>` and the key/value separator
    for the type `filter` (which is stored as a dictionary) is the first `=` sign.
    So a `filter` with the value `a=b=c=d` will be stored as `{'a': 'b=c=d'}`.

    The keys must be in the following format:

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
                'default': {},
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

    Based on the found environment variables, this will return a `Dict[str, Any]`.

        return {
            'key_one': 'one',
            'key_two': False,
            'key_three': {
                'foo': 'bar'
            },
            'key_four': 'super_secret_string',
            'key_five': 33,
            'key_six': 'WARNING'
        }

    :param keys: The environ keys to use
    :type keys: Dict[str,Dict[str,Any]]
    :returns: A dict of the found environ values
    :rtype: Dict[str,Any]
    """

    environs = {}

    # Check the environment variables
    for key, key_attributes in keys.items():
        if os.environ.get(key.upper()):
            environs.update({key: os.environ[key.upper()]})

            try:
                key_attributes['type']
            except KeyError:
                key_attributes['type'] = 'string'

            if key_attributes['type'] == 'list':
                environs[key] = environs[key].split(' ')

            if key_attributes['type'] == 'filter':
                filters = environs[key].split('=', 1)
                try:
                    environs[key] = {filters[0]: filters[1]}
                except IndexError:
                    log.warning(f"`{environs[key]}` not understood for {key.upper()}. Ignoring.")
                    del environs[key]
                    continue

            if key_attributes['type'] == 'int':
                try:
                    environs[key] = int(environs[key])
                except ValueError:
                    log.warning(f"`{environs[key]}` not understood for {key.upper()}. Ignoring.")
                    del environs[key]
                    continue

            if key_attributes['type'] == 'boolean':
                try:
                    environs[key] = bool(strtobool(environs[key]))
                except ValueError:
                    log.warning(f"`{environs[key]}` not understood for {key.upper()}. Ignoring.")
                    del environs[key]
                    continue

            if key_attributes['type'] == 'enum':
                if not environs[key] in key_attributes['values']:
                    log.warning(f"`{environs[key]}` not understood for {key.upper()}. Ignoring.")
                    del environs[key]
                    continue

            log.info(
                redact(
                    message=f'{key.upper()} is set to `{environs[key]}`.',
                    param=environs[key],
                    replace=key_attributes.get('redact', False)
                )
            )

    environs = _handle_deprecations(environs=environs, keys=keys)
    environs = _fill_missing_environs(environs=environs, keys=keys)
    return environs

def _fill_missing_environs(
    environs: Dict[str, Any],
    keys: Dict
) -> Dict[str, Any]:
    """
    Fills out the missing environment variables with the values stored in the keys

    :param environs: The already gathered environment variables
    :type environs: Dict[str,Any]
    :param keys: The environ keys to use
    :type keys: Dict[str, Dict[str,Any]]
    :returns:
        A dict of found environ values. For the unset environment variables,
        it returns the default set in the `keys`
    :rtype: Dict[str,Any]
    """
    for key, key_attributes in keys.items():
        if not key in environs and not key_attributes.get('deprecated', False) :
            display = key_attributes.get('default')

            if key_attributes['type'] == 'list':
                display = ' '.join(display)

            if key_attributes['type'] == 'filter':
                display = '='.join(display)

            if not key_attributes.get('hidden', False):
                log.info(
                    redact(
                        message=f'{key.upper()} is set to `{display}`.',
                        param=display,
                        replace=key_attributes.get('redact', False)
                    )
                )
            environs[key] = key_attributes.get('default')
    return environs

def _handle_deprecations(
    environs: Dict[str, Any],
    keys: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Handles deprecated environment variables

    :param environs: The already gathered environment variables
    :type environs: Dict[str,Any]
    :param keys: The environ keys to use
    :type keys: Dict[str, Dict[str,Any]]
    :returns: A dict environ values, after deprecation processing
    :rtype: Dict[str,Any]
    """
    for key, key_attributes in keys.items():
        if key in environs and key_attributes.get('deprecated', False) :
            message = f"{key.upper()} is deprecated and will be removed in a next version."
            if key_attributes.get('replaced_by'):
                message += f" Use {key_attributes['replaced_by'].upper()} instead."
                log.warning(message)
                if key_attributes['replaced_by'] in environs:
                    log.warning(
                        f"{key.upper()} and {key_attributes['replaced_by'].upper()} are both set."
                        f" Dropping {key.upper()}."
                    )
                    del environs[key]
                else:
                    environs[key_attributes['replaced_by']] = environs[key]
                    del environs[key]
            else:
                log.warning(message)

    return environs

def short_msg(msg: str, chars: int = 150) -> str:
    """
    Truncates the message to `chars` characters and adds two dots at the end.

    :param msg: The string to truncate
    :type msg: str
    :param chars: The max number of characters before adding `..` (default: 150)
    :type chars: int, optional
    :return: The truncated `msg`. It will return back the `msg` if the length is < `chars`
    :rtype: str
    """
    return (str(msg)[:chars] + '..') if len(str(msg)) > chars else str(msg)

def strtobool(value: str) -> bool:
    """
    Converts a string to a boolean

    :param value: The string to check if it represents true or false
    :type value: str
    :raises ValueError: When the string cannot be matched to a boolean
    :return: The corresponding boolean value
    :rtype: bool
    """
    str_to_bool_map = {
        'y': True,
        'yes': True,
        't': True,
        'true': True,
        'on': True,
        '1': True,
        'n': False,
        'no': False,
        'f': False,
        'false': False,
        'off': False,
        '0': False
    }

    try:
        return str_to_bool_map[str(value).lower()]
    except KeyError as exc:
        raise ValueError(f'"{value}" is not a valid bool value') from exc

def redact(
    message: str,
    param: str,
    replace: Optional[bool] = False,
    replace_value: str = 'xxxREDACTEDxxx'
) -> str:
    """
    Replaces in `message` the `param` string with `replace_value`

    :param message: The string to parse
    :type message: str
    :param param: The substring to be replaced
    :type param: str
    :param replace: A boolean informing if the `param` should be replaced or not, defaults to False
    :type replace: Optional[bool], optional
    :param replace_value: The value to replace `param` with, defaults to 'xxxREDACTEDxxx'
    :type replace_value: str, optional
    :return: The modified string
    :rtype: str
    """
    if replace and isinstance(param, str):
        return message.replace(param, replace_value)
    return message

def key_to_title(key: str) -> str:
    """
    converts a string key in form 'a_is_b' to a title in form 'A Is B'

    :param key: The source string `a_is_b`
    :type key: str
    :return: The convertet string `A Is B`
    :rtype: str
    """
    parsed = ""
    keys = key.split('_')
    for k in keys:
        parsed += f'{k.capitalize()} '
    return parsed[:-1]
