/*
 * This file is part of Invenio.
 * Copyright (C) 2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { NotificationContext } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_jobs/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { DateTime } from "luxon";
import { UserListItemCompact } from "react-invenio-forms";
import { withState } from "react-searchkit";
import { Button, Table } from "semantic-ui-react";
import { StatusFormatter } from "./StatusFormatter";
import { StopButton } from "./StopButton";
import { diffTimestamps } from "./utils/diffTimestamps";

const MSG_MAX_LINES = 3;

class SearchResultItemComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      msgShowAll: false,
      status: props.result.status,
    };
  }

  toggleShowAll = () => {
    this.setState((prevState) => ({
      msgShowAll: !prevState.msgShowAll,
    }));
  };

  static contextType = NotificationContext;

  onError = (e) => {
    const { addNotification } = this.context;
    addNotification({
      title: i18next.t("Status ") + e.status,
      content: `${e.message}`,
      type: "error",
    });
    console.error(e);
  };

  render() {
    const { result } = this.props;
    const { msgShowAll, status } = this.state;
    const msgLines = result.message ? result.message.split("\n") : [];
    const msgHasMoreThanMaxLines = msgLines.length > MSG_MAX_LINES;
    const msgLinesShown =
      msgHasMoreThanMaxLines && msgShowAll
        ? msgLines
        : msgLines.slice(0, MSG_MAX_LINES);
    const createdFormatted = DateTime.fromISO(result.created).toFormat(
      "yyyy/LL/dd HH:mm:ss"
    );
    return (
      <Table.Row verticalAlign="top">
        <Table.Cell
          key={`run-name-${result.started_at}`}
          data-label={i18next.t("Run")}
          collapsing
          className="word-break-all"
        >
          <StatusFormatter status={status} />
          <a href={`/administration/runs/${result.id}`}>{createdFormatted}</a>
        </Table.Cell>
        <Table.Cell
          key={`run-last-run-${status}`}
          data-label={i18next.t("Duration")}
          collapsing
          className=""
        >
          {result.started_at === null
            ? `${i18next.t("Waiting")}...`
            : [
                result.finished_at === null
                  ? `${diffTimestamps(
                      new Date().toISOString(),
                      result.started_at,
                      i18next.language
                    )}...`
                  : diffTimestamps(
                      result.finished_at,
                      result.started_at,
                      i18next.language
                    ),
              ]}
        </Table.Cell>
        <Table.Cell
          key={`run-last-run-${result.message}`}
          data-label={i18next.t("Message")}
          className=""
        >
          {msgLinesShown.map((line) => {
            const lineIndex = msgLines.indexOf(line);
            return (
              <React.Fragment key={`msg-line-${lineIndex}-${line.length}`}>
                {line}
                <br />
              </React.Fragment>
            );
          })}
          {msgHasMoreThanMaxLines && (
            <React.Fragment>
              {!msgShowAll && <div>...</div>}
              <Button as="a" onClick={this.toggleShowAll} size="mini">
                {msgShowAll ? i18next.t("Show less") : i18next.t("Show all")}
              </Button>
            </React.Fragment>
          )}
        </Table.Cell>

        <Table.Cell
          key={`job-user-${result?.started_by?.id}`}
          data-label={i18next.t("Started by")}
          collapsing
          className="word-break-all"
        >
          {result.started_by ? (
            <UserListItemCompact
              user={result.started_by}
              id={result.started_by.id}
            />
          ) : (
            i18next.t("System")
          )}
        </Table.Cell>

        <Table.Cell collapsing>
          {status === "RUNNING" ? (
            <StopButton
              stopURL={result.links.stop}
              setStatus={(status) => {
                this.setState({ status: status });
              }}
              onError={this.onError}
            />
          ) : (
            ""
          )}
        </Table.Cell>
      </Table.Row>
    );
  }
}

SearchResultItemComponent.propTypes = {
  result: PropTypes.object.isRequired,
};

SearchResultItemComponent.defaultProps = {};

export const SearchResultItemLayout = withState(SearchResultItemComponent);
