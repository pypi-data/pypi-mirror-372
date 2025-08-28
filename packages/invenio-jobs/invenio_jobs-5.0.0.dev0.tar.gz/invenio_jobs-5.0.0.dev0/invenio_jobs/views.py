# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""InvenioRDM module for jobs management."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_jobs",
    __name__,
    template_folder="templates",
)


def create_jobs_bp(app):
    """Create jobs blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.jobs_resource.as_blueprint()


def create_tasks_bp(app):
    """Create tasks blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.tasks_resource.as_blueprint()


def create_runs_bp(app):
    """Create runs blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.runs_resource.as_blueprint()


def create_job_logs_bp(app):
    """Create job logs blueprint."""
    ext = app.extensions["invenio-jobs"]
    return ext.job_log_resource.as_blueprint()
