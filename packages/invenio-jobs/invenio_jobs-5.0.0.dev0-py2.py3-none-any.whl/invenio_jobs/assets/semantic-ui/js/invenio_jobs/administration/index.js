// This file is part of Invenio
// Copyright (C) 2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { initDefaultSearchComponents } from "@js/invenio_administration";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { NotificationController } from "@js/invenio_administration";
import { RunActionForm } from "./RunActionForm";
import { SearchResultItemLayout } from "./JobSearchResultItemLayout";
import { JobSearchLayout } from "./JobSearchLayout";
import { JobActions } from "./JobActions";

const domContainer = document.getElementById("invenio-search-config");

const defaultComponents = initDefaultSearchComponents(domContainer);

const overriddenComponents = {
  ...defaultComponents,
  "InvenioAdministration.SearchResultItem.layout": SearchResultItemLayout,
  "InvenioAdministration.ResourceActions": JobActions,
  "SearchApp.layout": JobSearchLayout,
  "InvenioAdministration.ActionForm.runs.layout": RunActionForm,
};

createSearchAppInit(
  overriddenComponents,
  true,
  "invenio-search-config",
  false,
  NotificationController
);
