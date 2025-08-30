# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request permissions."""

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    SystemProcess,
    SystemProcessWithoutSuperUser,
)

from .generators import Commenter, Creator, Receiver, Reviewers, Status, Topic


class PermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    # Ability in general to create requests (not which request you can create)
    can_create = [AuthenticatedUser(), SystemProcess()]
    # Just about ability to perform a search (not what requests you can access)
    can_search = [AuthenticatedUser(), SystemProcess()]

    can_search_user_requests = can_search

    # Read/update/delete action deals with requests in **multiple states**, and
    # thus must take the request status into account.
    can_read = [
        Status(["created"], [Creator()]),
        Status(
            [
                "submitted",
                "deleted",
                "cancelled",
                "expired",
                "accepted",
                "declined",
            ],
            [Creator(), Receiver(), Reviewers(), Topic()],
        ),
        SystemProcess(),
    ]

    can_update = [
        SystemProcess(),
        Status(["created"], [Creator()]),
        Status(["submitted"], [Creator(), Receiver()]),
    ]

    can_manage_access_options = [Disable()]

    can_action_delete = [
        Status(["created"], [Creator()]),
        Status(
            ["submitted", "deleted", "cancelled", "expired", "accepted", "declined"],
            [Disable()],
        ),
        SystemProcess(),
    ]

    # Submit, cancel, expire, accept and decline actions only deals
    # with requests in a **single state** and thus doesn't need to take the
    # request status into account.
    can_action_submit = [Creator(), SystemProcess()]
    can_action_cancel = [Creator(), SystemProcess()]
    # `SystemProcessWithoutSuperUser`: expire is an automatic action done only by
    # the system, therefore the `superuser-action` must be explicitly excluded
    # as it's added by default to any permission.
    can_action_expire = [SystemProcessWithoutSuperUser()]
    can_action_accept = [Receiver(), SystemProcess()]
    can_action_decline = [Receiver(), SystemProcess()]

    # Request events/comments
    # Events are in most cases protected by the associated request.
    can_update_comment = [
        Commenter(),
        SystemProcess(),
    ]
    can_delete_comment = [
        Commenter(),
        SystemProcess(),
    ]
    # If you can read the request you can create events for the request.
    can_create_comment = can_read

    # Needed by the search events permission because a permission_action must
    # be provided to create_search(), but the event search is already protected
    # by request's can_read, thus we use a dummy permission for the search.
    can_unused = [AnyUser()]
