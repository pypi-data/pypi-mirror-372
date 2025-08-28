// This file is part of InvenioRDM
// Copyright (C) 2024 CERN
// Copyright (C) 2025 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  Label,
  Container,
  Divider,
  Grid,
  Header,
  Icon,
  List,
  Message,
  Segment,
} from "semantic-ui-react";
import { http, withCancel } from "react-invenio-forms";
import { DateTime } from "luxon";
import { i18next } from "@translations/invenio_jobs/i18next";

export class RunsLogs extends Component {
  constructor(props) {
    super(props);

    const { logs, run, sort } = props;

    this.state = {
      error: null,
      logs: logs.map((log) => ({
        ...log,
        formatted_timestamp: DateTime.fromISO(log.timestamp).toFormat(
          "yyyy-MM-dd HH:mm"
        ),
      })),
      run,
      sort,
      runDuration: this.getDurationInMinutes(run.started_at, run.finished_at),
      formatted_started_at: this.formatDatetime(run.started_at),
    };
  }

  componentDidMount() {
    this.logsInterval = setInterval(async () => {
      const { run, sort } = this.state;
      if (run.status === "RUNNING") {
        await this.fetchLogs(run.id, sort);
        await this.checkRunStatus(run.id, run.job_id);
      }
    }, 2000);
  }

  componentWillUnmount() {
    clearInterval(this.logsInterval);
    this.logsFetchCancel?.cancel();
    this.statusFetchCancel?.cancel();
  }

  getDurationInMinutes(startedAt, finishedAt) {
    if (!startedAt) return 0;
    const start = DateTime.fromISO(startedAt);
    const end = finishedAt ? DateTime.fromISO(finishedAt) : DateTime.now();
    return Math.floor(end.diff(start, "minutes").minutes);
  }

  formatDatetime(ts) {
    return ts ? DateTime.fromISO(ts).toFormat("yyyy-MM-dd HH:mm") : null;
  }

  fetchLogs = async (runId, sort) => {
    try {
      const searchAfterParams = (sort || [])
        .map((value) => `search_after=${value}`)
        .join("&");

      // own cancel token for this request
      const cancellableFetch = withCancel(
        http.get(`/api/logs/jobs?q=${runId}&${searchAfterParams}`)
      );
      this.logsFetchCancel = cancellableFetch;

      const res = await cancellableFetch.promise;
      if (res.status !== 200)
        throw new Error(`Failed to fetch logs: ${res.statusText}`);

      const incoming = res.data.hits.hits.map((log) => ({
        ...log,
        formatted_timestamp: DateTime.fromISO(log.timestamp).toFormat(
          "yyyy-MM-dd HH:mm"
        ),
      }));
      const newSort = res.data.hits.sort;

      /* dedup by timestamp|level|msg combo */
      this.setState((prev) => {
        const seen = new Set(
          prev.logs.map((l) => `${l.timestamp}|${l.level}|${l.message ?? ""}`)
        );
        const unique = incoming.filter(
          (l) => !seen.has(`${l.timestamp}|${l.level}|${l.message ?? ""}`)
        );
        return {
          logs: [...prev.logs, ...unique],
          error: null,
          sort: newSort || prev.sort,
        };
      });
    } catch (err) {
      console.error("Error fetching logs:", err);
      this.setState({ error: err.message });
    }
  };

  checkRunStatus = async (runId, jobId) => {
    try {
      // own cancel token for this request
      const cancellable = withCancel(
        http.get(`/api/jobs/${jobId}/runs/${runId}`)
      );
      this.statusFetchCancel = cancellable;

      const res = await cancellable.promise;
      if (res.status !== 200)
        throw new Error(`Failed to fetch run status: ${res.statusText}`);

      const run = res.data;

      this.setState({
        run,
        runDuration: this.getDurationInMinutes(run.started_at, run.finished_at),
        formatted_started_at: this.formatDatetime(run.started_at),
      });

      if (["SUCCESS", "FAILED", "PARTIAL_SUCCESS"].includes(run.status)) {
        clearInterval(this.logsInterval);
      }
    } catch (err) {
      console.error("Error checking run status:", err);
      this.setState({ error: err.message });
    }
  };

  render() {
    const {
      error,
      logs,
      run,
      runDuration,
      formatted_started_at: formattedStartedAt,
    } = this.state;
    const levelClass = {
      DEBUG: "",
      INFO: "primary",
      WARNING: "warning",
      ERROR: "negative",
      CRITICAL: "negative",
    };

    const statusIcon = {
      SUCCESS: { name: "check circle", color: "green" },
      FAILED: { name: "times circle", color: "red" },
      RUNNING: { name: "spinner", color: "blue" },
      PARTIAL_SUCCESS: { name: "exclamation circle", color: "orange" },
    };

    const iconProps = statusIcon[run.status] || {
      name: "clock outline",
      color: "grey",
    };

    return (
      <Container>
        {logs.length === 0 && (
          <Message info>
            <Message.Header className="mb-5">
              {i18next.t("No logs to display")}
            </Message.Header>
            {i18next.t("Possible reasons include:")}
            <Message.List>
              <Message.Item>
                {i18next.t("The job has not produced any logs yet.")}
              </Message.Item>
              <Message.Item>
                {i18next.t("Logs were deleted due to the retention policy.")}
              </Message.Item>
            </Message.List>
          </Message>
        )}
        {logs.length > 0 && (
          <>
            <Header as="h2" className="mt-20">
              {run.title}
            </Header>
            <Divider />
            {error && (
              <Message negative>
                <Message.Header>
                  {i18next.t("Error Fetching Logs")}
                </Message.Header>
                <p>{error}</p>
              </Message>
            )}
            <Grid celled>
              <Grid.Row>
                <Grid.Column width={3}>
                  <Header as="h4" color="grey">
                    {i18next.t("Job run")}
                  </Header>
                  <List>
                    <List.Item>
                      <Icon name={iconProps.name} color={iconProps.color} />
                      <List.Content>
                        {formattedStartedAt ? (
                          <>
                            <p>
                              <strong>{formattedStartedAt}</strong>
                            </p>
                            <p className="description">
                              {runDuration} {i18next.t("mins")}
                            </p>
                          </>
                        ) : (
                          <p className="description">
                            {i18next.t("Not yet started")}
                          </p>
                        )}
                        {run.message && (
                          <Label basic color={iconProps.color}>
                            {run.message}
                          </Label>
                        )}
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>
                <Grid.Column className="log-table" width={13}>
                  <Segment>
                    {logs.map((log) => (
                      <div
                        key={`${log.timestamp}-${log.level}-${log.message}`}
                        className={`log-line ${log.level.toLowerCase()}`}
                      >
                        <span className="log-timestamp">
                          [{log.formatted_timestamp}]
                        </span>{" "}
                        <span className={levelClass[log.level] || ""}>
                          {log.level}
                        </span>{" "}
                        <span className="log-message">{log.message}</span>
                      </div>
                    ))}
                  </Segment>
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </>
        )}
      </Container>
    );
  }
}

RunsLogs.propTypes = {
  run: PropTypes.object.isRequired,
  logs: PropTypes.array.isRequired,
  sort: PropTypes.array.isRequired,
};
