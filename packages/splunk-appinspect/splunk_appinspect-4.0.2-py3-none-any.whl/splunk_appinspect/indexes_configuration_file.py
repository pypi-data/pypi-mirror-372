# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk indexes.conf abstraction module"""
from . import configuration_file


class IndexesConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [indexes.conf](https://docs.splunk.com/Documentation/Splunk/latest/admin/Indexesconf#indexes.conf.example) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
