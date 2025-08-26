#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Global logging configuration """

import logging
from typing import Optional
from types import ModuleType, FunctionType
import pygelf
from .constants import NAME

def setup_logger(
    name: str,
    level: Optional[str] = 'INFO',
    gelf_host: Optional[str] = None,
    gelf_port: Optional[int] = None,
    configure_egos: Optional[bool] = True,
    **kwargs
) -> ModuleType:
    """
    sets up the logger

    This will also format the log based on :py:func:`get_formatter()`

    :param name: The main name of the logger to initialize
    :type name: str
    :param level: The logging level, defaults to 'INFO'
    :type level: Optional[str], optional
    :param gelf_host: The fqdn of the GELF host, defaults to None
    :type gelf_host: Optional[str], optional
    :param gelf_port: The port for the GELF host, defaults to None
    :type gelf_port: Optional[int], optional
    :param configure_egos: Set to `False` if you don't want the egos libraries to also log, defaults to True
    :type configure_egos: Optional[bool], optional
    :return: Returns a configured instance of :py:mod:`logging`
    :rtype: ModuleType
    """

    if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        level = 'INFO'

    logging.basicConfig(handlers=[logging.NullHandler()])
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(get_formatter(level))
    logger.addHandler(handler)

    if gelf_host and gelf_port:
        handler = pygelf.GelfUdpHandler(
            host=gelf_host,
            port=gelf_port,
            debug=True,
            include_extra_fields=True,
            **kwargs
        )
        logger.addHandler(handler)

    if configure_egos:
        # The logging settings for ix-notifiers
        ix_logger = logging.getLogger('ix-notifiers')
        ix_logger.setLevel(level)
        ix_handler = logging.StreamHandler()
        ix_handler.setFormatter(get_formatter(level))
        ix_logger.addHandler(ix_handler)

        # The logging settings for egos-helpers
        egos_logger = logging.getLogger(NAME)
        egos_logger.setLevel(level)
        egos_handler = logging.StreamHandler()
        egos_handler.setFormatter(get_formatter(level))
        egos_logger.addHandler(egos_handler)

    return logger

def get_formatter(level: Optional[str] = 'INFO') -> FunctionType:
    """
    Generates a formatter

    The generated formatter will include the module, line number and function
    name for the `DEBUG` level.

    :param level: The log level for which the formatter is created, defaults to 'INFO'
    :type level: Optional[str], optional
    :return: A configured instance of :py:meth:`logging.Formatter`
    :rtype: FunctionType
    """
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s [%(name)s'

    if level == 'DEBUG':
        fmt += ' %(module)s:%(lineno)d %(funcName)s'

    fmt += '] %(message)s'

    return logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
