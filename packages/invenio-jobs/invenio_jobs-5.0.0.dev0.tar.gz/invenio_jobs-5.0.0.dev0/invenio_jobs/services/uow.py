# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Unit of work."""
from invenio_records_resources.services.uow import Operation

from invenio_jobs.logging.jobs import job_context


class JobContextOp(Operation):
    """Unit of work operation to set the job context."""

    def __init__(self, ctx):
        """Constructor."""
        self._ctx = ctx
        self.token = None

    def on_register(self, uow):
        """Register the operation."""
        self.token = job_context.set(self._ctx)

    def on_post_commit(self, uow):
        """Post commit operation."""
        job_context.reset(self.token)
