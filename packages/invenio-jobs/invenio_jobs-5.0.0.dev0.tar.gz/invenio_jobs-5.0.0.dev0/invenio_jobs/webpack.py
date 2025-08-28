# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for jobs."""

from invenio_assets.webpack import WebpackThemeBundle

administration = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-jobs-search": "./js/invenio_jobs/administration/index.js",
                "invenio-jobs-details": "./js/invenio_jobs/administration/JobDetailsView.js",
                "invenio-runs-logs-details": "./js/invenio_jobs/administration/RunsLogsView.js",
            },
            dependencies={
                "react-invenio-forms": "^4.0.0",
                "react-searchkit": "^3.0.0",
                "@microlink/react-json-view": "^1.21.3",
            },
            aliases={
                "@less/invenio_jobs": "less/invenio_jobs",
                "@js/invenio_jobs": "js/invenio_jobs",
                "@translations/invenio_jobs": "translations/invenio_jobs",
            },
        ),
    },
)
