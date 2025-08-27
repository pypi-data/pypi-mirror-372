# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FunctionDefinitionParam", "Parameters"]


class Parameters(TypedDict, total=False):
    pass


class FunctionDefinitionParam(TypedDict, total=False):
    name: Required[str]

    parameters: Required[Parameters]

    description: str

    strict: bool
