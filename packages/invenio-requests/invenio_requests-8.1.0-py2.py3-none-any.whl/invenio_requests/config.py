# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generic and customizable requests."""

from invenio_i18n import lazy_gettext as _
from invenio_users_resources.entity_resolvers import GroupResolver, UserResolver

from invenio_requests.services.requests import facets

from .customizations import CommentEventType, LogEventType, ReviewersUpdatedType
from .services.permissions import PermissionPolicy

REQUESTS_PERMISSION_POLICY = PermissionPolicy
"""Override the default requests/comments permission policy."""

REQUESTS_REGISTERED_TYPES = []
"""Configuration for registered Request Types."""

REQUESTS_REGISTERED_EVENT_TYPES = [
    LogEventType(),
    CommentEventType(),
    ReviewersUpdatedType(),
]
"""Configuration for registered Request Event Types."""

REQUESTS_ENTITY_RESOLVERS = [UserResolver(), GroupResolver()]
"""Registered resolvers for resolving/creating references in request metadata."""

REQUESTS_ROUTES = {
    "details": "/requests/<pid_value>",
}
"""Invenio requests ui endpoints."""

REQUESTS_SEARCH = {
    "facets": ["type", "status"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Requests search default configuration."""

REQUESTS_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # search defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
}
"""Definitions of available request sort options."""

REQUESTS_FACETS = {
    "type": {
        "facet": facets.type,
        "ui": {
            "field": "type",
        },
    },
    "status": {
        "facet": facets.status,
        "ui": {
            "field": "status",
        },
    },
}
"""Invenio requests facets."""

REQUESTS_TIMELINE_PAGE_SIZE = 15
"""Amount of items per page on the request details timeline"""


REQUESTS_MODERATION_ROLE = "administration-moderation"
"""ID of the Role used for moderation."""


#
# User moderation administration
#
REQUESTS_USER_MODERATION_SEARCH = {
    "facets": ["status", "is_open"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Community requests search configuration (i.e list of community requests)"""

REQUESTS_USER_MODERATION_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # ES defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
}
"""Definitions of available record sort options."""

REQUESTS_USER_MODERATION_FACETS = {
    "status": {
        "facet": facets.status,
        "ui": {
            "field": "status",
        },
    },
    "is_open": {"facet": facets.is_open, "ui": {"field": "is_open"}},
}
"""Available facets defined for this module."""

REQUESTS_REVIEWERS_ENABLED = False
"""Enable reviewers for requests."""

REQUESTS_REVIEWERS_MAX_NUMBER = 15
"""Maximum number of reviewers allowed for a request."""
