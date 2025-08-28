# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service links."""

from invenio_records_resources.services.base import Link


class JobLink(Link):
    """Shortcut for writing Job links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({"id": str(record.id)})


class RunLink(Link):
    """Shortcut for writing Run links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update(
            {
                "id": str(record.id),
                "job_id": str(record.job_id),
            }
        )


def pagination_links(tpl):
    """Create pagination links (prev/selv/next) from the same template."""
    return {
        "prev": Link(
            tpl,
            when=lambda pagination, ctx: pagination.has_prev,
            vars=lambda pagination, vars: vars["args"].update(
                {"page": pagination.prev_page.page}
            ),
        ),
        "self": Link(tpl),
        "next": Link(
            tpl,
            when=lambda pagination, ctx: pagination.has_next,
            vars=lambda pagination, vars: vars["args"].update(
                {"page": pagination.next_page.page}
            ),
        ),
    }
