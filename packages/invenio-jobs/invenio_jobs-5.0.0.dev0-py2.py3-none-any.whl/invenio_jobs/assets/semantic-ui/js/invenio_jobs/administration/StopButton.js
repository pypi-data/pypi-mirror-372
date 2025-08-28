// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_jobs/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { http } from "react-invenio-forms";
import { Button, Icon } from "semantic-ui-react";
import { withCancel } from "react-invenio-forms";

export const StopButton = ({ stopURL, setStatus, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    const cancellableAction = await withCancel(
      http.post(stopURL).catch((error) => {
        if (error.response) {
          onError(error.response.data);
        } else {
          onError(error);
        }
      })
    );
    const response = await cancellableAction.promise;
    setStatus(response.data.status);
    setLoading(false);
  };

  return (
    <Button
      fluid
      className="error outline"
      size="medium"
      onClick={handleClick}
      loading={loading}
      icon
      labelPosition="left"
    >
      <Icon name="stop" />
      {i18next.t("Stop")}
    </Button>
  );
};

StopButton.propTypes = {
  stopURL: PropTypes.string.isRequired,
  setStatus: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired,
};
