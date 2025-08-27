"""Definición de triggers para workflows de GitHub Actions."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Trigger(BaseModel, ABC):
    """Clase base abstracta para triggers."""

    @abstractmethod
    def to_dict(self) -> str | dict[str, Any]:
        """Convierte el trigger a formato para YAML."""
        pass


class PushTrigger(Trigger):
    """Trigger para eventos push."""

    branches: list[str] | None = Field(
        None, description="Ramas que disparan el trigger"
    )
    branches_ignore: list[str] | None = Field(None, description="Ramas a ignorar")
    tags: list[str] | None = Field(None, description="Tags que disparan el trigger")
    tags_ignore: list[str] | None = Field(None, description="Tags a ignorar")
    paths: list[str] | None = Field(None, description="Rutas que disparan el trigger")
    paths_ignore: list[str] | None = Field(None, description="Rutas a ignorar")

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        result = {}
        if self.branches:
            result["branches"] = self.branches
        if self.branches_ignore:
            result["branches-ignore"] = self.branches_ignore
        if self.tags:
            result["tags"] = self.tags
        if self.tags_ignore:
            result["tags-ignore"] = self.tags_ignore
        if self.paths:
            result["paths"] = self.paths
        if self.paths_ignore:
            result["paths-ignore"] = self.paths_ignore

        return {"push": result} if result else "push"


class PullRequestTrigger(Trigger):
    """Trigger para eventos pull request."""

    types: list[str] | None = Field(None, description="Tipos de eventos PR")
    branches: list[str] | None = Field(None, description="Ramas objetivo")
    branches_ignore: list[str] | None = Field(None, description="Ramas a ignorar")
    paths: list[str] | None = Field(None, description="Rutas que disparan el trigger")
    paths_ignore: list[str] | None = Field(None, description="Rutas a ignorar")

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        result = {}
        if self.types:
            result["types"] = self.types
        if self.branches:
            result["branches"] = self.branches
        if self.branches_ignore:
            result["branches-ignore"] = self.branches_ignore
        if self.paths:
            result["paths"] = self.paths
        if self.paths_ignore:
            result["paths-ignore"] = self.paths_ignore

        return {"pull_request": result} if result else "pull_request"


class ScheduleTrigger(Trigger):
    """Trigger para eventos programados (cron)."""

    cron: str = Field(..., description="Expresión cron")

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        return {"schedule": [{"cron": self.cron}]}


class WorkflowDispatchTrigger(Trigger):
    """Trigger para ejecución manual."""

    inputs: dict[str, dict[str, Any]] | None = Field(
        None, description="Inputs del workflow"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        result = {}
        if self.inputs:
            result["inputs"] = self.inputs
        return {"workflow_dispatch": result} if result else "workflow_dispatch"


class ReleaseTrigger(Trigger):
    """Trigger para eventos de release."""

    types: list[str] | None = Field(None, description="Tipos de eventos de release")

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        result = {}
        if self.types:
            result["types"] = self.types
        return {"release": result} if result else "release"


# Factory functions para crear triggers fácilmente
def on_push(
    branches: list[str] | None = None, paths: list[str] | None = None
) -> PushTrigger:
    """Crea un PushTrigger de manera conveniente."""
    return PushTrigger(branches=branches, paths=paths)


def on_pull_request(
    branches: list[str] | None = None, types: list[str] | None = None
) -> PullRequestTrigger:
    """Crea un PullRequestTrigger de manera conveniente."""
    return PullRequestTrigger(branches=branches, types=types)


def on_schedule(cron: str) -> ScheduleTrigger:
    """Crea un ScheduleTrigger de manera conveniente."""
    return ScheduleTrigger(cron=cron)


def on_workflow_dispatch(
    inputs: dict[str, dict[str, Any]] | None = None,
) -> WorkflowDispatchTrigger:
    """Crea un WorkflowDispatchTrigger de manera conveniente."""
    return WorkflowDispatchTrigger(inputs=inputs)


def on_release(types: list[str] | None = None) -> ReleaseTrigger:
    """Crea un ReleaseTrigger de manera conveniente."""
    return ReleaseTrigger(types=types)
