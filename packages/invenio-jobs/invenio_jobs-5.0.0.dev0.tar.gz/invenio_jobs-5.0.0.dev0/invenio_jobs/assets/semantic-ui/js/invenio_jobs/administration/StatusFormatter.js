// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { BoolFormatter } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_jobs/i18next";
import React from "react";
import PropTypes from "prop-types";

export const StatusFormatter = ({ status }) => {
  return (
    <span>
      <BoolFormatter
        tooltip={i18next.t("Queued")}
        icon="wait"
        color="grey"
        value={status === "QUEUED"}
      />
      <BoolFormatter
        tooltip={i18next.t("Running")}
        icon="spinner"
        color="grey"
        value={status === "RUNNING"}
      />
      <BoolFormatter
        tooltip={i18next.t("Success")}
        icon="check"
        color="green"
        value={status === "SUCCESS"}
      />
      <BoolFormatter
        tooltip={i18next.t("Failed")}
        icon="cancel"
        color="red"
        value={status === "FAILED"}
      />
      <BoolFormatter
        tooltip={i18next.t("Warning")}
        icon="warning"
        color="yellow"
        value={status === "WARNING"}
      />
      <BoolFormatter
        tooltip={i18next.t("Cancelling")}
        icon="arrow down"
        color="yellow"
        value={status === "CANCELLING"}
      />
      <BoolFormatter
        tooltip={i18next.t("Cancelled")}
        icon="ban"
        color="red"
        value={status === "CANCELLED"}
      />
      <BoolFormatter
        tooltip={i18next.t("Partial Success")}
        icon="exclamation circle"
        color="orange"
        value={status === "PARTIAL_SUCCESS"}
      />
    </span>
  );
};

StatusFormatter.propTypes = {
  status: PropTypes.string.isRequired,
};
