# Copyright 2019 Splunk Inc. All rights reserved.
"""
Splunk AppInspect certification events listeners base class module
"""
from splunk_appinspect.python_analyzer.ast_info_query import Any


class Listener:
    """Splunk AppInspect certification events listeners base class."""

    def handle_event(self, event: str, *args: Any) -> None:
        """Entry point to call event handler."""
        event_name = "on_" + event
        if hasattr(self, event_name):
            getattr(self, event_name)(*args)
