# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration view module."""

from flask import current_app
from invenio_administration.views.base import (
    AdminResourceCreateView,
    AdminResourceEditView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _

from invenio_jobs.config import JOBS_QUEUES
from invenio_jobs.models import Task
from invenio_jobs.services.schema import RunSchema
from invenio_jobs.services.ui_schema import ScheduleUISchema


class JobsAdminMixin:
    """Common admin properties."""

    api_endpoint = "/jobs"
    resource_config = "jobs_resource"
    pid_path = "id"

    display_search = False
    display_delete = False
    display_create = True
    display_edit = True

    search_config_name = "JOBS_SEARCH"
    search_sort_config_name = "JOBS_SORT_OPTIONS"
    search_facets_config_name = "JOBS_FACETS"

    actions = {
        "schedule": {
            "text": _("Schedule"),
            "payload_schema": ScheduleUISchema,
            "order": 1,
            "icon": "calendar",
        },
        "runs": {
            "text": _("Configure and run"),
            "modal_text": _("Run now"),
            "payload_schema": RunSchema,
            "order": 2,
            "icon": "play",
        },
    }


class JobsListView(JobsAdminMixin, AdminResourceListView):
    """Configuration for Jobs list view."""

    name = "jobs"
    search_request_headers = {"Accept": "application/vnd.inveniordm.v1+json"}
    title = "Jobs"
    menu_label = "Jobs"
    category = "System"
    icon = "settings"
    template = "invenio_jobs/system/jobs/jobs-search.html"
    create_view_name = "jobs-create"

    item_field_list = {
        "job": {"text": _("Jobs"), "order": 1, "width": 3},
        "active": {"text": _("Status"), "order": 2, "width": 2},
        "last_run_start_time": {"text": _("Last run"), "order": 3, "width": 3},
        "user": {"text": _("Started by"), "order": 4, "width": 3},
        "next_run": {"text": _("Next run"), "order": 5, "width": 3},
    }


class JobsDetailsView(JobsAdminMixin, AdminResourceListView):
    """Configuration for Jobs detail view which shows runs."""

    url = "/jobs/<pid_value>"
    search_request_headers = {"Accept": "application/json"}
    request_headers = {"Accept": "application/json"}
    name = "job-details"
    resource_config = "runs_resource"
    title = "Job Details"
    disabled = lambda _: True

    template = "invenio_jobs/system/jobs/jobs-details.html"

    list_view_name = "jobs"
    pid_value = "<pid_value>"

    item_field_list = {
        "run": {"text": _("Run (ISO UTC)"), "order": 1, "width": 2},
        "duration": {"text": _("Duration"), "order": 2, "width": 2},
        "message": {"text": _("Message"), "order": 3, "width": 10},
        "user": {"text": _("Started by"), "order": 4, "width": 2},
        "action": {"text": _("Action"), "order": 5, "width": 2},
    }

    def get_api_endpoint(self, pid_value=None):
        """overwrite get_api_endpoint to accept pid_value."""
        return f"/api/jobs/{pid_value}/runs"

    def get_details_api_endpoint(self):
        """Compute api endpoint link for job details view."""
        api_url_prefix = current_app.config["SITE_API_URL"]
        slash_tpl = "/" if not self.api_endpoint.startswith("/") else ""

        if not self.api_endpoint.startswith(api_url_prefix):
            return f"{api_url_prefix}{slash_tpl}{self.api_endpoint}"

        return f"{slash_tpl}{self.api_endpoint}"

    def get_context(self, **kwargs):
        """Compute admin view context."""
        ctx = super().get_context(**kwargs)
        ctx["request_headers"] = self.request_headers
        ctx["ui_config"] = self.item_field_list
        ctx["name"] = self.name
        ctx["api_endpoint"] = self.get_details_api_endpoint()
        return ctx


class JobsFormMixin:
    """Mixin class for form fields."""

    @property
    def form_fields(self):
        """Initializing form fields."""
        jobs_queues = [
            {"title_l10n": str(queue["title"]), "id": queue["name"]}
            for queue in JOBS_QUEUES.values()
        ]
        tasks = [{"title_l10n": t.title, "id": name} for name, t in Task.all().items()]
        return {
            "title": {
                "order": 1,
                "text": _("Title"),
                "description": _("A title of the job."),
            },
            "description": {
                "order": 2,
                "text": _("Description"),
                "description": _("A short description about the job."),
            },
            "default_queue": {
                "order": 3,
                "text": _("Queue"),
                "description": _("A queue for the job run."),
                "placeholder": "Select the queue",
                "options": jobs_queues,
            },
            "task": {
                "order": 4,
                "text": _("Task"),
                "description": _("A task for the job run."),
                "placeholder": "Select the task",
                "options": tasks,
            },
            "active": {
                "order": 5,
                "text": _("Active"),
            },
            "created": {"order": 7},
            "updated": {"order": 8},
        }


class JobsEditView(JobsAdminMixin, JobsFormMixin, AdminResourceEditView):
    """Configuration for job edit view."""

    name = "jobs-edit"
    url = "/jobs/<pid_value>/edit"
    title = "Job Edit"
    list_view_name = "jobs"


class JobsCreateView(JobsAdminMixin, JobsFormMixin, AdminResourceCreateView):
    """Configuration for Jobs create view."""

    name = "jobs-create"
    url = "/jobs/create"
    api_endpoint = "/jobs"
    title = "Create Job"
    list_view_name = "jobs"
