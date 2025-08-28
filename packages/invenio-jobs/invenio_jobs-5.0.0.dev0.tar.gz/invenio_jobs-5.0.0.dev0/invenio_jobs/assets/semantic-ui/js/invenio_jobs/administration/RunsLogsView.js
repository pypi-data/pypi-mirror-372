// This file is part of Invenio
// Copyright (C) 2024 CERN.
// Copyright (C) 2025 KTH Royal Institute of Technology.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";

import { RunsLogs } from "./RunsLogs";

const detailsConfig = document.getElementById("runs-logs-config");

if (detailsConfig) {
  const logs = JSON.parse(detailsConfig.dataset.logs);
  const run = JSON.parse(detailsConfig.dataset.run);
  const sort = JSON.parse(detailsConfig.dataset.sort);
  ReactDOM.render(
    <RunsLogs logs={logs} run={run} sort={sort} />,
    detailsConfig
  );
}
