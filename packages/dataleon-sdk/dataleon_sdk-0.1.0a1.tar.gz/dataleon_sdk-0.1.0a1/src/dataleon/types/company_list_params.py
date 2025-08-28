# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["CompanyListParams"]


class CompanyListParams(TypedDict, total=False):
    end_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """Filter companies created before this date (format YYYY-MM-DD)"""

    limit: int
    """Number of results to return (between 1 and 100)"""

    offset: int
    """Number of results to skip (must be ≥ 0)"""

    source_id: str
    """Filter by source ID"""

    start_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """Filter companies created after this date (format YYYY-MM-DD)"""

    state: Literal["VOID", "WAITING", "STARTED", "RUNNING", "PROCESSED", "FAILED", "ABORTED", "EXPIRED", "DELETED"]
    """Filter by company state (must be one of the allowed values)"""

    status: Literal["rejected", "need_review", "approved"]
    """Filter by individual status (must be one of the allowed values)"""

    workspace_id: str
    """Filter by workspace ID"""
