"""GDSFactory+ Pydantic models."""

from __future__ import annotations

from typing import Literal, TypeAlias

import pydantic as pyd

__all__ = [
    "Message",
    "LogLevel",
    "ReloadFactoriesMessage",
    "ReloadLayoutMessage",
    "ReloadSchematicMessage",
    "RestartServerMessage",
    "LogMessage",
]

LogLevel: TypeAlias = Literal["debug", "info", "warning", "error"]


class ReloadSchematicMessage(pyd.BaseModel):
    """A message to vscode to trigger a schematic reload."""

    what: Literal["reloadSchematic"] = "reloadSchematic"
    path: str


class ReloadFactoriesMessage(pyd.BaseModel):
    """A message to vscode to trigger a pics tree reload."""

    what: Literal["reloadFactories"] = "reloadFactories"


class RestartServerMessage(pyd.BaseModel):
    """A message to vscode to trigger a server restart."""

    what: Literal["restartServer"] = "restartServer"


class ReloadLayoutMessage(pyd.BaseModel):
    """A message to vscode to trigger a gds viewer reload."""

    what: Literal["reloadLayout"] = "reloadLayout"
    cell: str


class LogMessage(pyd.BaseModel):
    """A message to vscode to log a message."""

    what: Literal["log"] = "log"
    level: LogLevel
    message: str


Message: TypeAlias = (
    ReloadFactoriesMessage
    | ReloadLayoutMessage
    | RestartServerMessage
    | ReloadSchematicMessage
    | LogMessage
)
