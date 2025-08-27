"""Clase principal para definir workflows de GitHub Actions."""

from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field

from .job import Job
from .triggers import Trigger


class Workflow(BaseModel):
    """Representa un workflow completo de GitHub Actions."""

    name: str = Field(..., description="Nombre del workflow")
    on: Trigger | list[Trigger] | dict[str, Any] = Field(
        ..., description="Eventos que disparan el workflow"
    )
    jobs: dict[str, Job] = Field(default_factory=dict, description="Jobs del workflow")
    env: dict[str, str] | None = Field(
        None, description="Variables de entorno globales"
    )
    defaults: dict[str, Any] | None = Field(
        None, description="Configuraciones por defecto"
    )
    concurrency: str | dict[str, Any] | None = Field(
        None, description="Control de concurrencia"
    )
    permissions: dict[str, str] | None = Field(
        None, description="Permisos del workflow"
    )

    def add_job(self, job_id: str, job: Job) -> "Workflow":
        """Añade un job al workflow."""
        self.jobs[job_id] = job
        return self

    def set_env(self, key: str, value: str) -> "Workflow":
        """Establece una variable de entorno global."""
        if self.env is None:
            self.env = {}
        self.env[key] = value
        return self

    def to_yaml(self) -> str:
        """Convierte el workflow a formato YAML."""
        workflow_dict = {
            "name": self.name,
            "on": self._serialize_triggers(),
            "jobs": {
                job_id: job.model_dump(exclude_none=True)
                for job_id, job in self.jobs.items()
            },
        }

        if self.env:
            workflow_dict["env"] = self.env
        if self.defaults:
            workflow_dict["defaults"] = self.defaults
        if self.concurrency:
            workflow_dict["concurrency"] = self.concurrency
        if self.permissions:
            workflow_dict["permissions"] = self.permissions

        yaml_content = yaml.dump(
            workflow_dict, default_flow_style=False, sort_keys=False
        )
        return f"# Do not modify - Generated with WorkflowForge\n{yaml_content}"

    def generate_readme(self, use_ai: bool = True, ai_model: str = "llama3.2") -> str:
        """Generate README documentation for this workflow.

        Args:
            use_ai: Whether to use AI generation (requires Ollama)
            ai_model: AI model to use for generation

        Returns:
            Generated README content
        """
        from .ai_documentation import generate_workflow_readme

        return generate_workflow_readme(self.to_yaml(), "github", use_ai)

    def generate_diagram(self, output_format: str = "png") -> str:
        """Generate visual diagram of this workflow.

        Args:
            output_format: Output format (png, svg, pdf, dot)

        Returns:
            Path to generated diagram file
        """
        from .visualization import visualizer

        viz = visualizer(output_format=output_format)
        return viz.generate_github_diagram(self)

    def save(
        self,
        filepath: str = None,
        generate_readme: bool = False,
        use_ai: bool = True,
        generate_diagram: bool = True,
    ) -> None:
        """Save workflow to YAML file.

        Args:
            filepath: Path to save the workflow YAML (default: workflow name + .yml)
            generate_readme: Whether to also generate a README file
            use_ai: Whether to use AI for README generation
            generate_diagram: Whether to generate visual diagram
        """
        if filepath is None:
            # Generate filename from workflow name
            safe_name = self.name.lower().replace(" ", "-").replace("_", "-")
            filepath = f"{safe_name}.yml"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

        if generate_readme:
            readme_path = filepath.replace(".yml", "_README.md").replace(
                ".yaml", "_README.md"
            )
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(self.generate_readme(use_ai=use_ai))

        if generate_diagram:
            diagram_path = self.generate_diagram()
            print(f"📊 Workflow diagram saved: {diagram_path}")

    def _serialize_triggers(self) -> str | list[str] | dict[str, Any]:
        """Serializa los triggers para el YAML."""
        if isinstance(self.on, list):
            # Combinar múltiples triggers en un solo diccionario
            result = {}
            for trigger in self.on:
                if hasattr(trigger, "to_dict"):
                    trigger_dict = trigger.to_dict()
                    if isinstance(trigger_dict, dict):
                        # Merge each trigger's dictionary
                        for key, value in trigger_dict.items():
                            if value is None or (isinstance(value, dict) and not value):
                                result[key] = None
                            else:
                                result[key] = value
                elif isinstance(trigger, str):
                    result[trigger] = None
            return result
        elif hasattr(self.on, "to_dict"):
            return self.on.to_dict()
        return self.on
