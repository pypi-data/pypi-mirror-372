// This file is part of InvenioRequests
// Copyright (C) 2022-2024 CERN.
// Copyright (C) 2024 Northwestern University.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import React from "react";
import ReactDOM from "react-dom";
import { overrideStore } from "react-overridable";
import { InvenioRequestsApp } from "./InvenioRequestsApp";
import { defaultContribComponents } from "./contrib";
import {
  AcceptStatus,
  CancelStatus,
  DeclineStatus,
  DeleteStatus,
  ExpireStatus,
  SubmitStatus,
} from "./request";
import {
  TimelineAcceptEvent,
  TimelineCancelEvent,
  TimelineCommentDeletionEvent,
  TimelineDeclineEvent,
  TimelineExpireEvent,
  TimelineUnknownEvent,
  TimelineReviewersUpdatedEvent,
} from "./timelineEvents";

const requestDetailsDiv = document.getElementById("request-detail");
const request = JSON.parse(requestDetailsDiv.dataset.record);
const defaultQueryParams = JSON.parse(requestDetailsDiv.dataset.defaultQueryConfig);
const userAvatar = JSON.parse(requestDetailsDiv.dataset.userAvatar);
const permissions = JSON.parse(requestDetailsDiv.dataset.permissions);
const config = JSON.parse(requestDetailsDiv.dataset.config);

const defaultComponents = {
  ...defaultContribComponents,
  "TimelineEvent.layout.unknown": TimelineUnknownEvent,
  "TimelineEvent.layout.declined": TimelineDeclineEvent,
  "TimelineEvent.layout.accepted": TimelineAcceptEvent,
  "TimelineEvent.layout.expired": TimelineExpireEvent,
  "TimelineEvent.layout.cancelled": TimelineCancelEvent,
  "TimelineEvent.layout.reviewers_updated": TimelineReviewersUpdatedEvent,
  "TimelineEvent.layout.comment_deleted": TimelineCommentDeletionEvent,
  "RequestStatus.layout.submitted": SubmitStatus,
  "RequestStatus.layout.deleted": DeleteStatus,
  "RequestStatus.layout.accepted": AcceptStatus,
  "RequestStatus.layout.declined": DeclineStatus,
  "RequestStatus.layout.cancelled": CancelStatus,
  "RequestStatus.layout.expired": ExpireStatus,
  "RequestActionModal.title.cancel": () => i18next.t("Cancel request"),
  "RequestActionModal.title.accept": () => i18next.t("Accept request"),
  "RequestActionModal.title.decline": () => i18next.t("Decline request"),
};

const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <InvenioRequestsApp
    request={request}
    defaultQueryParams={defaultQueryParams}
    overriddenCmps={{ ...defaultComponents, ...overriddenComponents }}
    userAvatar={userAvatar}
    permissions={permissions}
    config={config}
  />,
  requestDetailsDiv
);
