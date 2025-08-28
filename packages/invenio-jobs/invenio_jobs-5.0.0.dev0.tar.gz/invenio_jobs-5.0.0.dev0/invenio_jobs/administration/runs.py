# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration Runs view module."""

from dateutil import parser
from flask import abort, g
from invenio_administration.views.base import AdminResourceListView
from invenio_i18n import lazy_gettext as _

from invenio_jobs.administration.jobs import JobsAdminMixin
from invenio_jobs.proxies import current_jobs_logs_service, current_runs_service
from invenio_jobs.services.errors import RunTooManyResults


class RunsDetailsView(JobsAdminMixin, AdminResourceListView):
    """Configuration for System Runs details view."""

    url = "/runs/<pid_value>"
    search_request_headers = {"Accept": "application/json"}
    request_headers = {"Accept": "application/json"}
    name = "run-details"
    resource_config = "runs_resource"
    title = "Run Details"
    disabled = lambda _: True

    template = "invenio_jobs/system/runs/runs-details.html"

    list_view_name = "jobs"
    pid_value = "<pid_value>"

    def get_context(self, **kwargs):
        """Compute admin view context."""
        pid_value = kwargs.get("pid_value", "")
        logs, sort = self._get_logs(pid_value)
        if not logs:
            logs = []
            job_id = ""
            run_dict = {}
        else:
            job_id = logs[0]["context"]["job_id"]
            run_dict = self._get_run_dict(job_id, pid_value)

        ctx = super().get_context(**kwargs)
        ctx["logs"] = logs
        ctx["run"] = run_dict
        ctx["sort"] = sort
        return ctx

    def _get_logs(self, pid_value):
        """Retrieve and format logs."""
        params = dict(q=f'"{pid_value}"')
        try:
            logs_result = current_jobs_logs_service.search(g.identity, params)
        except RunTooManyResults as e:
            # If too many results, return empty list
            # This should be improved https://github.com/inveniosoftware/invenio-jobs/issues/74
            abort(413, description=e.description)
        result_dict = logs_result.to_dict()
        logs = result_dict["hits"]["hits"]
        sort = result_dict["hits"].get("sort")

        return logs, sort

    def _get_run_dict(self, job_id, pid_value):
        """Retrieve and format run dictionary."""
        run_dict = current_runs_service.read(g.identity, job_id, pid_value).to_dict()
        return run_dict

    def _format_datetime(self, timestamp):
        """Format ISO datetime to a user-friendly string."""
        dt = parser.isoparse(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
