// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
// Copyright (C) 2025 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import isEmpty from "lodash/isEmpty";
import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  mapFormFields,
  DynamicSubFormField,
  generateDynamicFieldProps,
  generateFieldProps,
  ErrorMessage,
} from "@js/invenio_administration";
import ReactJson from "@microlink/react-json-view";
import {
  Accordion,
  Icon,
  Modal,
  Button,
  Divider,
  Message,
  Header,
} from "semantic-ui-react";
import { Form, Formik } from "formik";
import { Form as SemanticForm } from "semantic-ui-react";
import { i18next } from "@translations/invenio_jobs/i18next";
import { Trans } from "react-i18next";
import { Input, Dropdown, TextArea } from "react-invenio-forms";

export class RunActionForm extends Component {
  state = { activeIndex: -1 };

  handleClick = (e, titleProps) => {
    const { index } = titleProps;
    const { activeIndex } = this.state;
    const newIndex = activeIndex === index ? -1 : index;

    this.setState({ activeIndex: newIndex });
  };

  render() {
    const {
      actionSchema,
      actionCancelCallback,
      actionConfig,
      loading,
      formData,
      error,
      resource,
      onSubmit,
    } = this.props;
    const jsonData = JSON.parse(resource.default_args);
    const { activeIndex } = this.state;
    return (
      <Formik initialValues={formData} onSubmit={onSubmit}>
        {(props) => {
          const actionsErrors = props?.errors;
          return (
            <>
              <Modal.Content>
                <SemanticForm
                  as={Form}
                  id="action-form"
                  onSubmit={props.handleSubmit}
                >
                  <Input
                    fieldSchema={_get(actionSchema, "title")}
                    {...generateFieldProps(
                      "title",
                      _get(actionSchema, "title"),
                      undefined,
                      true,
                      actionSchema["title"],
                      props,
                      actionSchema,
                      formData,
                      mapFormFields
                    )}
                  />
                  <Dropdown
                    fieldSchema={_get(actionSchema, "queue")}
                    {...generateFieldProps(
                      "queue",
                      _get(actionSchema, "queue"),
                      undefined,
                      true,
                      actionSchema["queue"],
                      props,
                      actionSchema,
                      formData,
                      mapFormFields
                    )}
                    value={resource.default_queue}
                  />
                  <DynamicSubFormField
                    {...generateDynamicFieldProps(
                      "args",
                      _get(actionSchema, "args"),
                      undefined,
                      true,
                      actionSchema["args"],
                      props,
                      actionSchema,
                      formData,
                      mapFormFields
                    )}
                    fieldSchema={_get(actionSchema, "args")}
                  />
                  <Accordion fluid styled>
                    <Accordion.Title
                      active={activeIndex === 0}
                      index={0}
                      onClick={this.handleClick}
                    >
                      <Icon name="dropdown" />
                      {i18next.t("Advanced configuration")}
                    </Accordion.Title>
                    <Accordion.Content active={activeIndex === 0}>
                      <Header size="tiny">
                        {i18next.t("Reference configuration of this job:")}
                      </Header>
                      <ReactJson src={jsonData} name={null} />
                    </Accordion.Content>
                    <Accordion.Content active={activeIndex === 0}>
                      <Divider />
                      <Message info>
                        <Trans>
                          <b>Custom args:</b> when provided, the input below
                          will override any arguments specified above.
                        </Trans>
                      </Message>
                      <TextArea
                        {...generateFieldProps(
                          "custom_args",
                          _get(actionSchema, "custom_args"),
                          undefined,
                          true,
                          actionSchema["custom_args"],
                          props,
                          actionSchema,
                          formData,
                          mapFormFields
                        )}
                        fieldSchema={_get(actionSchema, "custom_args")}
                      />
                    </Accordion.Content>
                  </Accordion>
                  {!isEmpty(error) && (
                    <ErrorMessage
                      {...error}
                      content={
                        actionsErrors && Object.keys(actionsErrors).length > 0
                          ? Object.values(actionsErrors)[0]
                          : error.content
                      }
                      removeNotification={this.resetErrorState}
                    />
                  )}
                </SemanticForm>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  type="submit"
                  primary
                  form="action-form"
                  loading={loading}
                >
                  {i18next.t(actionConfig.modal_text) ||
                    i18next.t(actionConfig.text)}
                </Button>
                <Button
                  onClick={actionCancelCallback}
                  floated="left"
                  icon="cancel"
                  labelPosition="left"
                  content={i18next.t("Cancel")}
                />
              </Modal.Actions>
            </>
          );
        }}
      </Formik>
    );
  }
}

RunActionForm.propTypes = {
  resource: PropTypes.object.isRequired,
  actionSchema: PropTypes.object.isRequired,
  actionKey: PropTypes.string.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
  actionCancelCallback: PropTypes.func.isRequired,
  formFields: PropTypes.object,
  actionConfig: PropTypes.object.isRequired,
  actionPayload: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  formData: PropTypes.object,
  error: PropTypes.shape({
    content: PropTypes.string,
  }),
};

RunActionForm.defaultProps = {
  formFields: {},
  actionPayload: {},
  loading: false,
  formData: {},
  error: null,
};
