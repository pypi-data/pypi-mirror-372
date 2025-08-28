# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for logging."""

import warnings


class TaskExecutionPartialError(Exception):
    """Exception raised when the task is executed with errors."""

    def __init__(
        self, message="The task was executed with errors.", errored_entries_count=0
    ):
        """Constructor for the TaskExecutionPartialError class."""
        self.message = message
        self.errored_entries_count = errored_entries_count
        super().__init__(message)


class TaskExecutionError(Exception):
    """[DEPRECATED] Exception raised when the task is executed with errors."""

    def __init__(self, message="The task was executed with errors."):
        """Constructor for the TaskExecutionError class."""
        warnings.warn(
            "TaskExecutionError is deprecated and will be removed in a future version. "
            "Use TaskExecutionPartialError instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.message = message
        super().__init__(message)
