// This file is part of Invenio
// Copyright (C) 2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  NotificationController,
  initDefaultSearchComponents,
  AdminDetailsView,
} from "@js/invenio_administration";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { RunActionForm } from "./RunActionForm";
import _get from "lodash/get";
import React from "react";
import ReactDOM from "react-dom";
import { JobRunsHeader } from "./JobRunsHeader";
import { JobSearchLayout } from "./JobSearchLayout";
import { SearchResultItemLayout } from "./RunsSearchResultItemLayout";
import { OverridableContext, overrideStore } from "react-overridable";

const overriddenComponents = overrideStore.getAll();

const domContainer = document.getElementById("invenio-search-config");

const defaultComponents = initDefaultSearchComponents(domContainer);

const searchOverriddenComponents = {
  ...defaultComponents,
  "InvenioAdministration.SearchResultItem.layout": SearchResultItemLayout,
  "SearchApp.layout": JobSearchLayout,
};

createSearchAppInit(
  searchOverriddenComponents,
  true,
  "invenio-search-config",
  false,
  NotificationController
);

const pidValue = domContainer.dataset.pidValue;

const detailsConfig = document.getElementById("invenio-details-config");

const title = detailsConfig.dataset.title;
const fields = JSON.parse(detailsConfig.dataset.fields);
const resourceName = JSON.parse(detailsConfig.dataset.resourceName);
const displayEdit = JSON.parse(detailsConfig.dataset.displayEdit);
const displayDelete = JSON.parse(detailsConfig.dataset.displayDelete);
const apiEndpoint = _get(detailsConfig.dataset, "apiEndpoint");
const idKeyPath = JSON.parse(_get(detailsConfig.dataset, "pidPath", "pid"));
const listUIEndpoint = detailsConfig.dataset.listEndpoint;
const resourceSchema = JSON.parse(detailsConfig.dataset?.resourceSchema);
const requestHeaders = JSON.parse(detailsConfig.dataset?.requestHeaders);
const uiSchema = JSON.parse(detailsConfig.dataset?.uiConfig);
const name = detailsConfig.dataset?.name;

const cmps = {
  ...overriddenComponents,
  "InvenioAdministration.AdminDetailsView.job-details.layout": JobRunsHeader,
  "InvenioAdministration.ActionForm.runs.layout": RunActionForm,
};
detailsConfig &&
  ReactDOM.render(
    <OverridableContext.Provider value={cmps}>
      <AdminDetailsView
        title={title}
        apiEndpoint={apiEndpoint}
        columns={fields}
        pid={pidValue}
        displayEdit={displayEdit}
        displayDelete={displayDelete}
        idKeyPath={idKeyPath}
        resourceName={resourceName}
        listUIEndpoint={listUIEndpoint}
        resourceSchema={resourceSchema}
        requestHeaders={requestHeaders}
        uiSchema={uiSchema}
        name={name}
      />
    </OverridableContext.Provider>,
    detailsConfig
  );
