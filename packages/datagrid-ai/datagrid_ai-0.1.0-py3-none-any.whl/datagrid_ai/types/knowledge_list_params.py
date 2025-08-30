# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["KnowledgeListParams"]


class KnowledgeListParams(TypedDict, total=False):
    after: str
    """A cursor to use in pagination.

    `after` is an object ID that defines your place in the list. For example, if you
    make a list request and receive 100 objects, ending with `obj_foo`, your
    subsequent call can include `after=obj_foo` to fetch the next page of the list.
    """

    before: str
    """A cursor to use in pagination.

    `before` is an object ID that defines your place in the list. For example, if
    you make a list request and receive 100 objects, starting with `obj_bar`, your
    subsequent call can include `before=obj_bar` to fetch the previous page of the
    list.
    """

    limit: int
    """The limit on the number of objects to return, ranging between 1 and 100."""
