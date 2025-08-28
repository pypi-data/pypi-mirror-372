// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Modal, Icon } from "semantic-ui-react";
import { ActionModal, ActionForm } from "@js/invenio_administration";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_jobs/i18next";
import ScheduleJobModal from "./ScheduleJobModal";

export class JobActions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    };
  }

  onModalTriggerClick = (e, { payloadSchema, dataName, dataActionKey }) => {
    const { modalOpen } = this.state;
    const { resource, actions: actionsConfig } = this.props;
    if (dataActionKey === "schedule") {
      this.setState({
        modalOpen: true,
        modalHeader: i18next.t("Schedule Job"),
        modalBody: (
          <ScheduleJobModal
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            modalOpen={modalOpen}
            data={resource}
            payloadSchema={payloadSchema}
            apiUrl={`/api/jobs/${resource.id}`}
          />
        ),
      });
    } else {
      this.setState({
        modalOpen: true,
        modalHeader: dataName,
        modalBody: (
          <ActionForm
            actionKey={dataActionKey}
            actionSchema={payloadSchema}
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
            actionPayload={resource}
            actionConfig={actionsConfig[dataActionKey]}
          />
        ),
      });
    }
  };

  closeModal = () => {
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
  };

  handleSuccess = () => {
    const { resource } = this.props;
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
    setTimeout(() => {
      window.location = resource.links.self_admin_html;
    }, 1500);
  };

  render() {
    const { actions, Element, resource } = this.props;
    const { modalOpen, modalHeader, modalBody } = this.state;

    return (
      <>
        {Object.entries(actions).map(([actionKey, actionConfig]) => {
          const icon = actionConfig.icon;
          const labelPos = icon ? "left" : null;
          return (
            <Element
              key={actionKey}
              onClick={this.onModalTriggerClick}
              payloadSchema={actionConfig.payload_schema}
              dataName={actionConfig.text}
              dataActionKey={actionKey}
              basic
              icon={!_isEmpty(icon)}
              labelPosition={labelPos}
            >
              {!_isEmpty(icon) && <Icon name={icon} />}
              {actionConfig.text}...
            </Element>
          );
        })}
        <ActionModal modalOpen={modalOpen} resource={resource}>
          {modalHeader && <Modal.Header>{modalHeader}</Modal.Header>}
          {!_isEmpty(modalBody) && modalBody}
        </ActionModal>
      </>
    );
  }
}

JobActions.propTypes = {
  resource: PropTypes.object.isRequired,
  actions: PropTypes.shape({
    text: PropTypes.string.isRequired,
    payload_schema: PropTypes.object.isRequired,
    order: PropTypes.number.isRequired,
  }),
  Element: PropTypes.node,
};

JobActions.defaultProps = {
  Element: Button,
  actions: undefined,
};
