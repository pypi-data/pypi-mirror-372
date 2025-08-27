"""Definición de Steps para jobs de GitHub Actions."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class Step(BaseModel, ABC):
    """Clase base abstracta para steps."""

    name: str | None = Field(None, description="Nombre del step")
    id: str | None = Field(None, description="ID único del step")
    if_condition: str | None = Field(
        None, alias="if", description="Condición para ejecutar el step"
    )
    continue_on_error: bool | None = Field(None, description="Continuar si hay error")
    timeout_minutes: int | None = Field(None, description="Timeout en minutos")
    env: dict[str, str] | None = Field(
        None, description="Variables de entorno del step"
    )

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convierte el step a diccionario para YAML."""
        pass


class ActionStep(Step):
    """Step que ejecuta una action."""

    uses: str = Field(..., description="Action a usar")
    with_params: dict[str, Any] | None = Field(
        None, description="Parámetros de la action"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convierte el ActionStep a diccionario."""
        result = {"uses": self.uses}

        if self.name:
            result["name"] = self.name
        if self.id:
            result["id"] = self.id
        if self.if_condition:
            result["if"] = self.if_condition
        if self.continue_on_error is not None:
            result["continue-on-error"] = self.continue_on_error
        if self.timeout_minutes:
            result["timeout-minutes"] = self.timeout_minutes
        if self.env:
            result["env"] = self.env
        if self.with_params:
            result["with"] = self.with_params

        return result


class RunStep(Step):
    """Step que ejecuta comandos shell."""

    run: str = Field(..., description="Comando a ejecutar")
    shell: str | None = Field(None, description="Shell a usar")
    working_directory: str | None = Field(
        None, alias="working-directory", description="Directorio de trabajo"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convierte el RunStep a diccionario."""
        result = {"run": self.run}

        if self.name:
            result["name"] = self.name
        if self.id:
            result["id"] = self.id
        if self.if_condition:
            result["if"] = self.if_condition
        if self.continue_on_error is not None:
            result["continue-on-error"] = self.continue_on_error
        if self.timeout_minutes:
            result["timeout-minutes"] = self.timeout_minutes
        if self.env:
            result["env"] = self.env
        if self.shell:
            result["shell"] = self.shell
        if self.working_directory:
            result["working-directory"] = self.working_directory

        return result


# Factory functions para crear steps fácilmente
def action(
    uses: str,
    name: str | None = None,
    with_: dict[str, Any] | None = None,
    **kwargs,
) -> ActionStep:
    """Crea un ActionStep de manera conveniente."""
    with_params = with_ if with_ is not None else (kwargs if kwargs else None)
    return ActionStep(uses=uses, name=name, with_params=with_params)


def run(command: str, name: str | None = None, shell: str | None = None) -> RunStep:
    """Crea un RunStep de manera conveniente."""
    return RunStep(run=command, name=name, shell=shell)  # nosec B604
