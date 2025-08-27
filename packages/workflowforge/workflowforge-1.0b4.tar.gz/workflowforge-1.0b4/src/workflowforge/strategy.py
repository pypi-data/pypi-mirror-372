"""Definición de estrategias y matrices para jobs."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Matrix(BaseModel):
    """Representa una matriz de build."""

    model_config = {"extra": "allow"}

    include: list[dict[str, Any]] | None = Field(
        None, description="Configuraciones adicionales"
    )
    exclude: list[dict[str, Any]] | None = Field(
        None, description="Configuraciones a excluir"
    )

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Serializa la matriz incluyendo variables dinámicas."""
        result = super().model_dump(**kwargs)
        return {k: v for k, v in result.items() if v is not None}


class Strategy(BaseModel):
    """Representa una estrategia de ejecución para jobs."""

    matrix: Matrix | None = Field(None, description="Matriz de configuraciones")
    fail_fast: bool | None = Field(None, description="Fallar rápido si hay error")
    max_parallel: int | None = Field(None, description="Máximo de jobs paralelos")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Serializa la estrategia."""
        result = {}

        if self.matrix:
            result["matrix"] = self.matrix.model_dump(**kwargs)
        if self.fail_fast is not None:
            result["fail-fast"] = self.fail_fast
        if self.max_parallel is not None:
            result["max-parallel"] = self.max_parallel

        return result


# Factory functions para crear estrategias fácilmente
def matrix(**variables) -> Matrix:
    """Crea una Matrix de manera conveniente."""
    return Matrix(**variables)


def strategy(
    matrix: Matrix | None = None,
    fail_fast: bool | None = None,
    max_parallel: int | None = None,
) -> Strategy:
    """Crea una Strategy de manera conveniente."""
    return Strategy(matrix=matrix, fail_fast=fail_fast, max_parallel=max_parallel)
