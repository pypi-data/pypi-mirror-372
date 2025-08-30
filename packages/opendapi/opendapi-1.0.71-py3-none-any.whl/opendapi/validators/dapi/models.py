"""Common models for use by dapi validators"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from opendapi.models import OverrideConfig


@dataclass
class ProjectInfo:
    """Data class for project related information"""

    # Organization name in snakecase
    org_name_snakecase: str

    # The main project config
    override: OverrideConfig

    # Root directory of the application in the checked out local repo/storage
    root_path: str

    # Full path of the application in the checked out local storage
    full_path: str
    artifact_full_path: Optional[str] = None

    def construct_dapi_location(self, table_name: str) -> str:
        """Construct the location of the DAPI file within a project"""
        return f"{self.full_path}/dapis/{table_name}.dapi.yaml"

    def filter_dapis(self, dapis: Dict[str, Dict]) -> Dict[str, Dict]:
        """Get the owned DAPIs"""
        return {
            filepath: dapi
            for filepath, dapi in dapis.items()
            if filepath.startswith(self.full_path)
        }


@dataclass
class PackageScopedProjectInfo(ProjectInfo):
    """Project info for package scoped DAPI validators"""

    file_contents: Optional[Dict] = field(default_factory=dict)
