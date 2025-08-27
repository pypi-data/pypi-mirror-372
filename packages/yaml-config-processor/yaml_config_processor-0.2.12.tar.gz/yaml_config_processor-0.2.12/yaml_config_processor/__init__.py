"""
YAML Config Processor

A package for processing configuration templates from YAML strings with JSON user configurations.
"""

from yaml_config_processor.processor import ConfigProcessor, TEMPLATE_META_SCHEMA

try:
    from yaml_config_processor._version import version as __version__
except ImportError:
    # This will happen if the _version.py file is not present at the stage of the package creation on the side of
    # the CI/CD Github Actions.

    # One and only version value setup is here and only here. CHANGELOG.md is optional.
    __version__ = "0.2.11"

__all__ = ['ConfigProcessor', 'TEMPLATE_META_SCHEMA'] # That means that only these names will be imported when using `from yaml_config_processor import *`
