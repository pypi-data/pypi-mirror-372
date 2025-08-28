# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Registry of jobs."""


class JobsRegistry:
    """A simple class to register jobs."""

    def __init__(self):
        """Initialize the registry."""
        self._jobs = {}

    def register(self, job_instance, job_id=None):
        """Register a new job instance."""
        if job_id is None:
            job_id = job_instance.id
        if job_id in self._jobs:
            raise RuntimeError(f"Job with job id '{job_id}' is already registered.")
        self._jobs[job_id] = job_instance

    def get(self, job_id):
        """Get a job for a given job_id."""
        return self._jobs[job_id]

    def get_job_id(self, instance):
        """Get the service id for a specific instance."""
        for job_id, job_instance in self._jobs.items():
            if instance == job_instance:
                return job_id
        raise KeyError("Job not found in registry.")

    def get_all(self):
        """Return a list of available tasks."""
        return self._jobs

    @property
    def schemas(self):
        """Return all schemas registered for tasks."""
        schemas = {}
        for id_, registered_task in self._jobs.items():
            schema = registered_task.arguments_schema
            if schema:
                schemas[f"{schema.__name__}"] = schema
        return schemas
