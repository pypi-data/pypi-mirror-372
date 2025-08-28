# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service permissions."""

from invenio_administration.generators import Administration
from invenio_records_permissions.generators import Disable, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy


class TasksPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for tasks."""

    can_search = [Administration(), SystemProcess()]
    can_read = [Administration(), SystemProcess()]


class JobPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for jobs."""

    can_search = [Administration(), SystemProcess()]
    can_create = [Administration(), SystemProcess()]
    can_read = [Administration(), SystemProcess()]
    can_update = [Administration(), SystemProcess()]
    can_delete = [Administration(), SystemProcess()]


class RunPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for runs.

    Later the runs may be done by librarians.
    """

    can_search = [Administration(), SystemProcess()]
    can_create = [Administration(), SystemProcess()]
    can_read = [Administration(), SystemProcess()]
    can_update = [Administration(), SystemProcess()]
    can_delete = [Administration(), SystemProcess()]
    can_stop = [Administration(), SystemProcess()]


class JobLogsPermissionPolicy(BasePermissionPolicy):
    """Access control configuration for job logs."""

    can_search = [Administration(), SystemProcess()]
    can_create = [Disable()]  # Logs are crated via python logging
    can_read = [Disable()]
    can_update = [Disable()]
    can_delete = [Disable()]
