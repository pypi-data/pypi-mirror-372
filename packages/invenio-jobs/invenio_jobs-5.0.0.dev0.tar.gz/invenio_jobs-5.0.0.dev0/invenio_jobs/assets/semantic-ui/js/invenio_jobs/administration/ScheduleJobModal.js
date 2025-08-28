// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Modal, Dropdown, Input, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_jobs/i18next";
import { Formik, Form, Field } from "formik";
import { http, withCancel, ErrorMessage } from "react-invenio-forms";
import { NotificationContext } from "@js/invenio_administration";

export class ScheduleJobModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      error: undefined,
    };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  static contextType = NotificationContext;

  handleSubmit = async (values) => {
    const { addNotification } = this.context;
    this.setState({ loading: true });
    const { apiUrl, data, actionSuccessCallback, payloadSchema } = this.props;
    const { selectedOption } = values;

    // Filter out the values based on the schema for the selected option
    const selectedOptionSchema = payloadSchema[selectedOption];
    const filteredValues = Object.keys(values).reduce((acc, key) => {
      if (
        key !== "selectedOption" && // Exclude the selectedOption itself
        Object.prototype.hasOwnProperty.call(
          selectedOptionSchema?.properties,
          key
        ) // Include only fields present in the schema
      ) {
        acc[key] = values[key];
      }
      return acc;
    }, {});

    const payload = {
      ...data,
      schedule: {
        type: selectedOption,
        ...filteredValues,
      },
    };

    this.cancellableAction = withCancel(http.put(apiUrl, payload));
    try {
      await this.cancellableAction.promise;
      this.setState({ loading: false });
      addNotification({
        title: i18next.t("Success"),
        content: i18next.t("Job {{title}} has been scheduled.", {
          id: data.title,
        }),
        type: "success",
      });
      actionSuccessCallback();
    } catch (error) {
      const errorMessage = error?.response?.data?.message || error?.message;
      this.setState({
        error: errorMessage,
        loading: false,
      });
    }
  };

  render() {
    const { data, payloadSchema, actionCancelCallback } = this.props;
    const { error, loading } = this.state;

    const options = payloadSchema
      ? Object.keys(payloadSchema).map((type) => ({
          key: type,
          text: type.charAt(0).toUpperCase() + type.slice(1),
          value: type,
        }))
      : [];

    const initialValues = {
      selectedOption: data?.schedule?.type || "",
      ...data.schedule,
    };

    return (
      <Formik initialValues={initialValues} onSubmit={this.handleSubmit}>
        {({ values, setFieldValue, handleSubmit }) => (
          <Form>
            {error && (
              <Modal.Content>
                <ErrorMessage
                  header={i18next.t("Unable to set schedule.")}
                  content={i18next.t(error)}
                  icon="exclamation"
                  className="text-align-left"
                  negative
                />
              </Modal.Content>
            )}
            <Modal.Content>
              <Dropdown
                placeholder="Select a schedule type"
                fluid
                selection
                options={options}
                className="mb-10"
                onChange={(e, { value }) =>
                  setFieldValue("selectedOption", value)
                }
                value={values.selectedOption}
              />
              {values.selectedOption &&
                payloadSchema[values.selectedOption] && (
                  <>
                    {Object.keys(
                      payloadSchema[values.selectedOption].properties
                    )
                      .sort(
                        (a, b) =>
                          payloadSchema[values.selectedOption].properties[a]
                            .metadata.order -
                          payloadSchema[values.selectedOption].properties[b]
                            .metadata.order
                      )
                      .map((property) => (
                        <Field
                          key={property}
                          name={property}
                          render={({ field }) => (
                            <Input
                              {...field}
                              label={
                                payloadSchema[values.selectedOption].properties[
                                  property
                                ].metadata?.title
                              }
                              className="m-5"
                              type={
                                payloadSchema[values.selectedOption].properties[
                                  property
                                ].type === "string"
                                  ? "text"
                                  : "number"
                              }
                            />
                          )}
                        />
                      ))}
                  </>
                )}
            </Modal.Content>
            <Modal.Actions>
              <Button
                icon="cancel"
                onClick={actionCancelCallback}
                content={i18next.t("Cancel")}
                loading={loading}
                floated="left"
                size="medium"
              />
              <Button positive type="submit" onClick={handleSubmit}>
                <Icon name="check" />
                {i18next.t("Save")}
              </Button>
            </Modal.Actions>
          </Form>
        )}
      </Formik>
    );
  }
}

ScheduleJobModal.propTypes = {
  modalOpen: PropTypes.bool.isRequired,
  data: PropTypes.object.isRequired,
  payloadSchema: PropTypes.object.isRequired,
  apiUrl: PropTypes.string.isRequired,
  actionCancelCallback: PropTypes.func.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
};

export default ScheduleJobModal;
