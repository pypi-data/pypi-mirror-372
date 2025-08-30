# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    teamspace_id: Required[str]

    role: Required[Literal["admin", "member", "agents-only", "agent-specific"]]

    agent_ids: Optional[List[str]]
    """The agent IDs that the user has access to, if the role is agent-specific."""
