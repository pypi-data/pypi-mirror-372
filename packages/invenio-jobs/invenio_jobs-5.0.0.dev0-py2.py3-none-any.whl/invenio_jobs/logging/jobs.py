# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio jobs logging module.

This extension provides logging configuration specifically for job execution logs.
"""

from __future__ import absolute_import, print_function

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from functools import wraps

from flask import current_app
from invenio_logging.ext import InvenioLoggingBase
from invenio_search import current_search_client
from invenio_search.utils import prefix_index

from invenio_jobs.services import JobLogEntrySchema

from .. import config

# Define a global context variable to enrich logs
EMPTY_JOB_CTX = object()
job_context = ContextVar("job_context", default=EMPTY_JOB_CTX)


class ContextAwareOSHandler(logging.Handler):
    """Custom logging handler that enriches logs with global context and indexes them in OS."""

    def emit(self, record):
        """Emit log record after enriching it with global context."""
        if job_context.get() is not EMPTY_JOB_CTX:
            enriched_log = self.enrich_log(record)
            self.index_in_os(enriched_log)

    def enrich_log(self, record):
        """Enrich log record with contextvars' global context."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "context": job_context.get(),
        }
        serialized_data = JobLogEntrySchema().load(log_data)
        return serialized_data

    def index_in_os(self, log_data):
        """Send log data to OpenSearch."""
        full_index_name = prefix_index(current_app.config["JOBS_LOGGING_INDEX"])
        current_search_client.index(index=full_index_name, body=log_data)


@contextmanager
def set_job_context(data):
    """Context manager for safely setting and cleaning up contextvars."""
    token = job_context.set(data)
    try:
        yield job_context  # Yield the contextvar for modification
    finally:
        job_context.reset(token)  # Ensures cleanup


def with_job_context(base_context):
    """Decorator to set job context for a function."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with set_job_context(base_context) as context:
                return func(*args, **kwargs)

        return wrapper

    return decorator


class InvenioLoggingJobs(InvenioLoggingBase):
    """Logging extension for jobs."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        if not app.config["JOBS_LOGGING"]:
            return
        self.install_handler(app)

        app.extensions["invenio-logging-jobs"] = self

    def init_config(self, app):
        """Initialize config."""
        for k in dir(config):
            if k.startswith("JOBS_LOGGING"):
                app.config.setdefault(k, getattr(config, k))

    def install_handler(self, app):
        """Install logging handler for jobs."""
        # Set logging level
        if app.config["JOBS_LOGGING_LEVEL"] is not None:
            for h in app.logger.handlers:
                h.setLevel(app.config["JOBS_LOGGING_LEVEL"])

        # Add OpenSearch logging handler if not already added
        if not any(isinstance(h, ContextAwareOSHandler) for h in app.logger.handlers):
            os_handler = ContextAwareOSHandler()
            os_handler.setLevel(app.config["JOBS_LOGGING_LEVEL"])
            app.logger.addHandler(os_handler)

    def before_request(self):
        """Set job context to empty dictionary."""
        if job_context.get() is not EMPTY_JOB_CTX:
            # Already set — possibly an error, but overwrite
            job_context.set(EMPTY_JOB_CTX)

    def teardown_request(self):
        """Clean up job context after request."""
        if job_context.get() is not EMPTY_JOB_CTX:
            job_context.set(EMPTY_JOB_CTX)
