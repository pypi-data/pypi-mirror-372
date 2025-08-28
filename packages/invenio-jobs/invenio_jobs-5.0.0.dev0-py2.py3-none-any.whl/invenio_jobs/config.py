# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration."""

from invenio_i18n import lazy_gettext as _

from .services.permissions import (
    JobLogsPermissionPolicy,
    JobPermissionPolicy,
    RunPermissionPolicy,
    TasksPermissionPolicy,
)

JOBS_TASKS_PERMISSION_POLICY = TasksPermissionPolicy
"""Permission policy for tasks."""

JOBS_PERMISSION_POLICY = JobPermissionPolicy
"""Permission policy for jobs."""

JOBS_RUNS_PERMISSION_POLICY = RunPermissionPolicy
"""Permission policy for job runs."""

APP_LOGS_PERMISSION_POLICY = JobLogsPermissionPolicy
"""Permission policy for job logs."""

JOBS_FACETS = {}
"""Facets/aggregations for Jobs results."""

JOBS_QUEUES = {
    "celery": {
        "name": "celery",
        "title": _("Default"),
        "description": _("Default queue"),
    },
    "low": {
        "name": "low",
        "title": _("Low"),
        "description": _("Low priority queue"),
    },
}
"""List of available Celery queues.

This doesn't create any of the queues, but just controls to which Celery queue a job
is pushed to. You still need to configure Celery workers to listen to these queues.
"""

JOBS_DEFAULT_QUEUE = None
"""Default Celery queue."""

JOBS_SORT_OPTIONS = {
    "jobs": dict(
        title=_("Jobs"),
        fields=["jobs"],
    ),
    "last_run_start_time": dict(
        title=_("Last run"),
        fields=["last_run_start_time"],
    ),
    "user": dict(
        title=_("Started by"),
        fields=["user"],
    ),
    "next_run": dict(
        title=_("Next run"),
        fields=["next_run"],
    ),
}
"""Definitions of available Jobs sort options. """

JOBS_SEARCH = {
    "facets": [],
    "sort": ["jobs", "last_run_start_time", "user", "next_run"],
}
"""Jobs search configuration."""

JOBS_LOGGING_LEVEL = "DEBUG"
"""Logging level for jobs."""

JOBS_LOGGING = True
"""Enable logging for jobs."""

JOBS_LOGGING_INDEX = "job-logs"
""""Index name for job logs."""

JOBS_LOGGING_RETENTION_DAYS = 90
"""Retention period for job logs in days."""
