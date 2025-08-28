# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxies."""

from flask import current_app
from werkzeug.local import LocalProxy

current_jobs = LocalProxy(lambda: current_app.extensions["invenio-jobs"])
"""Jobs extension."""

current_jobs_service = LocalProxy(lambda: current_jobs.service)
"""Jobs service."""

current_runs_service = LocalProxy(lambda: current_jobs.runs_service)
"""Runs service."""

current_tasks_service = LocalProxy(lambda: current_jobs.tasks_service)
"""Tasks service."""

current_jobs_logs_service = LocalProxy(lambda: current_jobs.jobs_log_service)
"""Job logs service."""
