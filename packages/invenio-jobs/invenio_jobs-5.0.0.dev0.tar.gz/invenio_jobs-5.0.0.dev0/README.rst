..
    Copyright (C) 2024 CERN.

    Invenio-Jobs is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

==============
 Invenio-Jobs
==============

.. image:: https://github.com/inveniosoftware/invenio-jobs/workflows/CI/badge.svg
        :target: https://github.com/inveniosoftware/invenio-jobs/actions?query=workflow%3ACI

.. image:: https://img.shields.io/github/tag/inveniosoftware/invenio-jobs.svg
        :target: https://github.com/inveniosoftware/invenio-jobs/releases

.. image:: https://img.shields.io/pypi/dm/invenio-jobs.svg
        :target: https://pypi.python.org/pypi/invenio-jobs

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-jobs.svg
        :target: https://github.com/inveniosoftware/invenio-jobs/blob/master/LICENSE

InvenioRDM module for jobs management

Usage
=====

This module adds a custom scheduler to schedule jobs that exist in the local database.

To use this scheduler, the following command can be ran locally:

.. code-block:: console

    $ celery -A invenio_app.celery beat -l ERROR --scheduler invenio_jobs.services.scheduler:RunScheduler -s /var/run/celery-schedule --pidfile /var/run/celerybeat.pid


More Help
---------

Further documentation is available on
https://invenio-jobs.readthedocs.io/
