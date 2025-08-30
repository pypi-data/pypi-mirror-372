"""Models for use in opendapi functions."""

# pylint: disable=too-few-public-methods

import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ConfigParam(Enum):
    """Enum for various configuration objects"""

    PROJECTS = "projects"
    PROJECT_PATH = "project_path"
    INCLUDE_ALL = "include_all"
    OVERRIDES = "overrides"
    PLAYBOOKS = "playbooks"
    MODEL_ALLOWLIST = "model_allowlist"
    ARTIFACT_PATH = "artifact_path"


class BaseConfig:
    """Base class for configuration objects"""

    @classmethod
    def from_dict(cls, data: dict):
        """Helper function to create a class using only necessary elements from the dict"""
        parameters = inspect.signature(cls).parameters
        filtered_data = {k: v for k, v in data.items() if k in parameters}
        return cls(**filtered_data)


@dataclass
class PlaybookConfig(BaseConfig):
    """Data class for a playbook item"""

    type: str
    datastore_urn: Optional[str] = None
    namespace: Optional[str] = None
    identifier_prefix: Optional[str] = None
    team_urn: Optional[str] = None
    model_allowlist: Optional[List[str]] = field(default_factory=list)


@dataclass
class OverrideConfig(BaseConfig):
    """Data class for an override config entry"""

    # Project path relative to the repo
    project_path: str

    # Some applications / integrations have a schema file that needs to be handled
    artifact_path: Optional[str] = None

    model_allowlist: Optional[List] = field(default_factory=list)
    playbooks: Optional[List[PlaybookConfig]] = field(default_factory=list)


@dataclass
class ProjectConfig(BaseConfig):
    """Data class for a project item"""

    include_all: Optional[bool] = True
    artifact_path: Optional[str] = None
    overrides: Optional[List[OverrideConfig]] = field(default_factory=list)
