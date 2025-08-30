# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 KTH Royal Institute of Technology
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests resource config."""


import marshmallow as ma
from flask_resources import HTTPJSONException, create_error_handler
from invenio_records_resources.resources import (
    RecordResourceConfig,
    SearchRequestArgsSchema,
)
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from marshmallow import fields

from ...errors import CannotExecuteActionError, NoSuchActionError
from .fields import ReferenceString


#
# Request args
#
class RequestSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Add parameter to parse tags."""

    created_by = ReferenceString()
    topic = ReferenceString()
    receiver = ReferenceString()
    is_open = fields.Boolean()
    shared_with_me = fields.Boolean()


request_error_handlers = {
    CannotExecuteActionError: create_error_handler(
        lambda e: HTTPJSONException(
            code=400,
            description=str(e),
        )
    ),
    NoSuchActionError: create_error_handler(
        lambda e: HTTPJSONException(
            code=400,
            description=str(e),
        )
    ),
}


#
# Resource config
#
class RequestsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Requests resource configuration."""

    blueprint_name = "requests"
    url_prefix = "/requests"
    routes = {
        "list": "/",
        "user-prefix": "/user",
        "item": "/<id>",
        "action": "/<id>/actions/<action>",
    }

    request_view_args = {
        "id": ma.fields.UUID(),
        "action": ma.fields.Str(),
    }

    request_search_args = RequestSearchRequestArgsSchema

    error_handlers = FromConfig(
        "REQUESTS_ERROR_HANDLERS", default=request_error_handlers
    )

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }
