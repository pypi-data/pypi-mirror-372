# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio jobs logging tasks."""

from celery import shared_task
from flask import current_app
from invenio_search import current_search_client
from invenio_search.utils import prefix_index


@shared_task
def delete_logs():
    """Delete logs."""
    full_index_name = prefix_index(current_app.config["JOBS_LOGGING_INDEX"])
    current_search_client.delete_by_query(
        index=full_index_name,
        body={
            "query": {
                "range": {
                    "@timestamp": {
                        "lt": f"now-{current_app.config['JOBS_LOGGING_RETENTION_DAYS']}d/d"
                    }
                }
            }
        },
        conflicts="proceed",  # Avoid aborting on version conflicts
    )
