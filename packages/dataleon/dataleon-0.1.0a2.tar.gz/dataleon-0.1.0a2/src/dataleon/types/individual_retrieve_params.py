# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["IndividualRetrieveParams"]


class IndividualRetrieveParams(TypedDict, total=False):
    document: bool
    """Include document information"""

    scope: str
    """Scope filter (id or scope)"""
