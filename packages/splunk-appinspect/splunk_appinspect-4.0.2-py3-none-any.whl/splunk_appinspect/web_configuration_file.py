# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk web.conf abstraction module"""
from . import configuration_file


class WebConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [web.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Webconf) file."""

    def __init__(self) -> None:
        configuration_file.ConfigurationFile.__init__(self)
