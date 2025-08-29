"""DAPI validator module"""

from __future__ import annotations

import copy
from abc import abstractmethod
from collections import Counter
from functools import cached_property
from typing import Dict, Generic, List, Tuple, Type, TypeVar, Union

from opendapi.config import construct_project_full_path, get_project_path_from_full_path
from opendapi.defs import DAPI_SUFFIX, OPENDAPI_SPEC_URL, OpenDAPIEntity, ORMIntegration
from opendapi.logging import logger
from opendapi.models import ConfigParam, OverrideConfig, PlaybookConfig, ProjectConfig
from opendapi.utils import find_files_with_suffix, sort_dapi_fields
from opendapi.validators.base import (
    BaseValidator,
    MultiValidationError,
    ValidationError,
)
from opendapi.validators.dapi.models import PackageScopedProjectInfo, ProjectInfo
from opendapi.validators.defs import FileSet, IntegrationType, MergeKeyCompositeIDParams

ProjectInfoType = TypeVar(  # pylint: disable=invalid-name
    "ProjectInfoType", bound=ProjectInfo
)


class BaseDapiValidator(BaseValidator):
    """
    Abstract base validator class for DAPI files
    """

    INTEGRATION_NAME: ORMIntegration = NotImplementedError
    SUFFIX = DAPI_SUFFIX
    SPEC_VERSION = "0-0-1"
    ENTITY = OpenDAPIEntity.DAPI

    MUST_GENERATE_EVEN_IF_ENTITY_TYPE_EXISTS = True

    # Paths & keys to use for uniqueness check within a list of dicts when merging
    MERGE_UNIQUE_LOOKUP_KEYS: List[
        Tuple[
            List[Union[str, int, MergeKeyCompositeIDParams.IgnoreListIndexType]],
            MergeKeyCompositeIDParams,
        ]
    ] = [
        (
            ["fields"],
            MergeKeyCompositeIDParams(required=[["name"], ["data_type"]]),
        ),
        (
            ["datastores", "sources"],
            MergeKeyCompositeIDParams(
                required=[["urn"]],
                optional=[["data", "namespace"], ["data", "identifier"]],
            ),
        ),
        (
            ["datastores", "sinks"],
            MergeKeyCompositeIDParams(
                required=[["urn"]],
                optional=[["data", "namespace"], ["data", "identifier"]],
            ),
        ),
        # this is less for merging and more for deduping, but merging would be fine
        # as well
        (
            [
                "fields",
                MergeKeyCompositeIDParams.IGNORE_LIST_INDEX,
                "data_subjects_and_categories",
            ],
            MergeKeyCompositeIDParams(required=[["subject_urn"], ["category_urn"]]),
        ),
    ]

    # Paths to disallow new entries when merging
    MERGE_DISALLOW_NEW_ENTRIES_PATH: List[List[str]] = [["fields"]]

    _REGISTRY: Dict[ORMIntegration, Type[BaseDapiValidator]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # another base class
        if cls.INTEGRATION_NAME is NotImplementedError:
            return

        if cls.INTEGRATION_NAME in cls._REGISTRY:  # pragma: nocover
            raise ValueError(f"Integration {cls.INTEGRATION_NAME} already registered")

        cls._REGISTRY[cls.INTEGRATION_NAME] = cls

    @staticmethod
    def get_validator(integration_name: ORMIntegration) -> Type[BaseDapiValidator]:
        """Get the validator for the integration"""
        return BaseDapiValidator._REGISTRY[integration_name]

    def _get_field_names(self, content: dict) -> List[str]:
        """Get the field names"""
        return [field["name"] for field in content["fields"]]

    def _retention_reference_is_a_valid_field(self, file: str, content: Dict):
        """Validate if the retention reference is a valid field"""
        retention_reference = content.get("retention_reference")
        if retention_reference and retention_reference not in self._get_field_names(
            content
        ):
            raise ValidationError(
                f"Retention reference '{retention_reference}' not a valid field in '{file}'"
            )

    def _validate_primary_key_is_a_valid_field(self, file: str, content: Dict):
        """Validate if the primary key is a valid field"""
        primary_key = content.get("primary_key") or []
        field_names = self._get_field_names(content)
        for key in primary_key:
            if key not in field_names:
                raise ValidationError(
                    f"Primary key element '{key}' not a valid field in '{file}'"
                )

    def _validate_field_names_unique(self, file: str, content: Dict):
        """Validate if the field names are unique"""
        field_names = self._get_field_names(content)
        duplicates = {name for name in field_names if field_names.count(name) > 1}
        if duplicates:
            raise ValidationError(
                f"Field names must be unique in '{file}'"
                f"Duplicate field names: {duplicates}"
            )

    def _validate_field_data_subjects_and_categories_unique(
        self, file: str, content: Dict
    ):
        """Validate if the field data subjects and categories are unique"""
        errors = []
        for field in content.get("fields", []):
            data_subjects_and_categories_counts = Counter(
                (subj_and_cat["subject_urn"], subj_and_cat["category_urn"])
                for subj_and_cat in field.get("data_subjects_and_categories", [])
            )
            non_unique_data_subjects_and_categories = {
                subj_and_cat
                for subj_and_cat, count in data_subjects_and_categories_counts.items()
                if count > 1
            }
            if non_unique_data_subjects_and_categories:
                errors.append(
                    (
                        f"In file '{file}', the following 'data_subjects_and_categories' pairs are "
                        f"repeated in field '{field['name']}': "
                        f"{non_unique_data_subjects_and_categories}"
                    )
                )
        if errors:
            raise MultiValidationError(
                errors, "Non-unique data subjects and categories pairs within fields"
            )

    def _is_personal_data_is_direct_identifier_matched(self, file: str, content: dict):
        """Validate that you cannot have a direct identifier without it also being personal data"""

        errors = []
        for field in content.get("fields", []):
            if field.get("is_direct_identifier") and not field.get("is_personal_data"):
                errors.append(
                    f"Field '{field['name']}' in file '{file}' is a direct identifier "
                    "but not marked as personal data"
                )

        if errors:
            raise MultiValidationError(
                errors,
                f"Mismatched personal data designations for mappings in '{file}'",
            )

    @cached_property
    def settings(self) -> ProjectConfig:
        """Get the settings from the config file for this integration"""
        settings = copy.deepcopy(
            self.config.get_integration_settings(self.INTEGRATION_NAME, self.runtime)
        )

        override_config = settings.get(ConfigParam.PROJECTS.value, {}).get(
            ConfigParam.OVERRIDES.value, []
        )

        overrides = []
        for override in override_config:
            playbooks = [
                PlaybookConfig.from_dict(playbook)
                for playbook in override.get(ConfigParam.PLAYBOOKS.value, [])
            ]
            override[ConfigParam.PLAYBOOKS.value] = playbooks
            overrides.append(OverrideConfig.from_dict(override))

        settings[ConfigParam.PROJECTS.value][ConfigParam.OVERRIDES.value] = overrides

        return ProjectConfig.from_dict(settings[ConfigParam.PROJECTS.value])

    def validate_content(self, file: str, content: Dict, fileset: FileSet):
        """Validate the content of the files"""
        super().validate_content(file, content, fileset)
        self._validate_primary_key_is_a_valid_field(file, content)
        self._validate_field_data_subjects_and_categories_unique(file, content)
        self._is_personal_data_is_direct_identifier_matched(file, content)
        self._validate_field_names_unique(file, content)
        self._retention_reference_is_a_valid_field(file, content)

    @property
    def base_destination_dir(self) -> str:
        return self.root_dir

    def filter_dapis(self, dapis: Dict[str, Dict]) -> Dict[str, Dict]:
        """Get the owned DAPIs"""
        return {
            file: content
            for file, content in dapis.items()
            # we want the BaseDapiValidator to be able to collect all Dapis
            # but all impls of BaseDapiValidator should only validate their own
            # integration
            # then, we want to match integrations directly, but if an integration is missing,
            # then we want to collect it with the fallback validator
            if (
                type(self) is BaseDapiValidator  # pylint: disable=unidiomatic-typecheck
                or (integration := content.get("context", {}).get("integration"))
                == self.INTEGRATION_NAME.value  # pylint: disable=no-member
                or not integration
                and self.INTEGRATION_NAME is ORMIntegration.NO_ORM_FALLBACK
            )
        }

    @cached_property
    def original_file_state(self) -> Dict[str, Dict]:
        """
        Get the contents of all files in the root directory,
        if they are part of the integration
        """
        dapis = self._get_file_contents_for_suffix(self.SUFFIX)
        og_file_state = self.filter_dapis(dapis)
        # Temporary fix for historical_ept_rates
        # KB Note: remove this once the bug is fixed
        for dapi in og_file_state.values():
            if dapi.get("urn", "").endswith("historical_ept_rates"):  # pragma: nocover
                seen_fields = set()
                deduped_fields = []
                for field in dapi["fields"]:
                    if field["name"] not in seen_fields:
                        deduped_fields.append(field)
                        seen_fields.add(field["name"])
                dapi["fields"] = deduped_fields

        # lets sort the fields for original just as we do
        # for generated making comparisons easier
        for dapi in og_file_state.values():
            dapi["fields"] = sort_dapi_fields(dapi["fields"])

        # NOTE: CLEANUP - lets remove is_pii, access from each field
        for dapi in og_file_state.values():
            for field in dapi["fields"]:
                field.pop("is_pii", None)
                field.pop("access", None)

        return og_file_state

    @cached_property
    def generated_file_state(self) -> Dict[str, Dict]:
        """Get the generated file state"""
        gen_files = super().generated_file_state
        # we will sort the fields for generated so that nested
        # fields are clustered in a coherent way
        for dapi in gen_files.values():
            dapi["fields"] = sort_dapi_fields(dapi["fields"])

        # NOTE: CLEANUP - lets remove is_pii, access from each field
        for dapi in gen_files.values():
            for field in dapi["fields"]:
                field.pop("is_pii", None)
                field.pop("access", None)

        return gen_files

    @staticmethod
    def add_non_playbook_datastore_fields(
        datastores: dict,
    ) -> dict:
        """Add non-playbook fields to the datastores"""
        for ds_type in ["sources", "sinks"]:
            for ds in datastores.get(ds_type, []):
                ds["business_purposes"] = []
                ds["retention_days"] = None
        return datastores

    @classmethod
    def add_default_non_generated_schema_portions(cls, dapi: dict) -> dict:
        """Add the default schema portion to the dapi"""
        dapi["fields"] = [
            {
                "description": None,
                "data_subjects_and_categories": [],
                "sensitivity_level": None,
                "is_personal_data": None,
                "is_direct_identifier": None,
                **field,
            }
            for field in dapi["fields"]
        ]
        return {
            "schema": OPENDAPI_SPEC_URL.format(version=cls.SPEC_VERSION, entity="dapi"),
            "type": "entity",
            "owner_team_urn": None,
            "datastores": DapiValidator.add_non_playbook_datastore_fields(
                {
                    "sources": [],
                    "sinks": [],
                }
            ),
            "description": None,
            "privacy_requirements": {
                "dsr_access_endpoint": None,
                "dsr_deletion_endpoint": None,
            },
            "context": {},
            **dapi,
        }

    def _get_base_generated_files(self) -> Dict[str, Dict]:
        """Set Autoupdate templates in {file_path: content} format"""
        return {
            f"{self.base_destination_dir}/sample_dataset.dapi.yaml": {
                "schema": OPENDAPI_SPEC_URL.format(
                    version=self.SPEC_VERSION, entity="dapi"
                ),
                "urn": "my_company.sample.dataset",
                "type": "entity",
                "description": "Sample dataset that shows how DAPI is created",
                "owner_team_urn": "my_company.sample.team",
                "datastores": {
                    "sources": [
                        {
                            "urn": "my_company.sample.datastore_1",
                            "data": {
                                "identifier": "sample_dataset",
                                "namespace": "sample_db.sample_schema",
                            },
                            "business_purposes": [],
                            "retention_days": None,
                        }
                    ],
                    "sinks": [
                        {
                            "urn": "my_company.sample.datastore_2",
                            "data": {
                                "identifier": "sample_dataset",
                                "namespace": "sample_db.sample_schema",
                            },
                            "business_purposes": [],
                            "retention_days": None,
                        }
                    ],
                },
                "fields": [
                    {
                        "name": "field1",
                        "data_type": "string",
                        "description": "Sample field 1 in the sample dataset",
                        "is_nullable": False,
                        "is_pii": False,
                        "access": "public",
                        "data_subjects_and_categories": [],
                        "sensitivity_level": None,
                        "is_personal_data": None,
                        "is_direct_identifier": None,
                    }
                ],
                "primary_key": ["field1"],
                "context": {
                    "integration": "custom_dapi",
                },
                "privacy_requirements": {
                    "dsr_access_endpoint": None,
                    "dsr_deletion_endpoint": None,
                },
            }
        }

    @classmethod
    def merge(cls, base: Dict, nxt: Dict) -> Dict:
        """Merge the base and next dictionaries"""
        # NOTE: this is a hack to allow for in flight PRs that have the diverged
        #       dapis to go through merging without considering data type
        if base.get("urn", "").rsplit(".", 1)[-1] in (
            "boms",
            "catalog_item_inventory_snapshots",
            "end_of_month_adjustments",
            "milestones",
            "onboarding_flows",
            "shopify_inventory_items",
            "shopify_product_images",
            "shopify_product_options",
            "shopify_product_variants",
            "shopify_products",
            "trackstar_inventory_snapshots",
            "weighted_average_costs",
        ):
            merge_unique_lookup_keys_override = copy.deepcopy(
                cls.MERGE_UNIQUE_LOOKUP_KEYS
            )
            for i, (path, _) in enumerate(merge_unique_lookup_keys_override):
                if path == ["fields"]:
                    merge_unique_lookup_keys_override[i] = (
                        path,
                        MergeKeyCompositeIDParams(required=[["name"]]),
                    )
        else:
            merge_unique_lookup_keys_override = None

        return cls._get_merger(merge_unique_lookup_keys_override).merge(
            copy.deepcopy(base), copy.deepcopy(nxt)
        )


class DapiValidator(BaseDapiValidator, Generic[ProjectInfoType]):
    """
    Abstract validator class for DAPI files
    """

    def selected_projects(self, validate: bool = True) -> List[ProjectInfoType]:
        """Get the selected projects"""
        projects = {}

        if self.settings.include_all:
            for project in self.get_all_projects():
                projects[project.full_path] = project

        for override in self.settings.overrides:
            project = self.get_project(override)
            projects[project.full_path] = project

        projects = list(projects.values())

        if validate:
            self.validate_projects(projects)

        return projects

    @abstractmethod
    def get_all_projects(self) -> List[ProjectInfoType]:
        """Generate a list of all projects that this validator should check"""

    @abstractmethod
    def get_project(self, override_config: OverrideConfig) -> ProjectInfoType:
        """Given a project override config, return an ProjectConfig object"""

    @abstractmethod
    def validate_projects(self, projects: List[ProjectInfoType]):
        """Validate the projects"""

    def filter_dapis(self, dapis: Dict[str, Dict]) -> Dict[str, Dict]:
        """Filter the dapis with projects as well"""
        integration_filtered_dapis = super().filter_dapis(dapis)
        projects = self.selected_projects()
        return {
            fp: dapi
            for project in projects
            for fp, dapi in project.filter_dapis(integration_filtered_dapis).items()
        }


class RuntimeDapiValidator(DapiValidator[ProjectInfoType], Generic[ProjectInfoType]):
    """
    Abstract validator class for Runtime-integration DAPI files
    """

    INTEGRATION_TYPE: IntegrationType = IntegrationType.RUNTIME

    def __init__(self, *, skip_generation, **kwargs):
        self._skip_generation = skip_generation
        super().__init__(**kwargs)

    @abstractmethod
    def _unskipped_validate_projects(self, projects: List[ProjectInfo]):
        """Validate the projects"""

    def _skipped_validate_projects(self, projects: List[ProjectInfo]):
        """Validate the projects"""
        # Possible that the project and artifacts may not exist if we are skipping generation

    def validate_projects(self, projects: List[ProjectInfo]):
        """Validate the projects"""
        # Possible that the project and artifacts may not exist if we are skipping generation
        if self._skip_generation:
            return self._skipped_validate_projects(projects)

        return self._unskipped_validate_projects(projects)

    @abstractmethod
    def _unskipped_get_base_generated_files(self) -> Dict[str, Dict]:
        """Build the base template for autoupdate"""

    def _skipped_get_base_generated_files(self) -> Dict[str, Dict]:
        """Build the base template for autoupdate"""
        return self.original_file_state

    def _get_base_generated_files(self) -> Dict[str, Dict]:
        """Build the base template for autoupdate"""
        if self._skip_generation:
            logger.info(
                (
                    "Skipping generation of DAPI files for runtime ORM integration, "
                    "falling back to current DAPI file state."
                ),
                extra={
                    "validator": type(self).__name__,
                },
            )
            return self._skipped_get_base_generated_files()

        return self._unskipped_get_base_generated_files()

    @property
    def _generate_skipped(self) -> bool:
        """Return True if generation is skipped"""
        return self._skip_generation


class PackageScopedDapiValidatorBase(BaseDapiValidator):
    """Base class for DAPI validators that are scoped to packages."""

    PACKAGE_JSON: str = "package.json"
    LOOKUP_FILE_SUFFIXES: List[str] = NotImplementedError

    def get_all_projects(self) -> List[PackageScopedProjectInfo]:
        """Get all package.json files in the project."""
        package_file = f"/{self.settings.artifact_path or self.PACKAGE_JSON}"
        files = find_files_with_suffix(self.root_dir, [package_file])
        packages = [filename.replace(package_file, "") for filename in files]

        if self.settings.include_all:
            projects = [
                PackageScopedProjectInfo(
                    org_name_snakecase=self.config.org_name_snakecase,
                    override=OverrideConfig(
                        project_path=get_project_path_from_full_path(
                            self.root_dir, package
                        )
                    ),
                    root_path=self.root_dir,
                    full_path=package,
                )
                for package in packages
            ]
        else:
            projects = []

        for override in self.settings.overrides:
            full_path = construct_project_full_path(
                self.root_dir, override.project_path
            )
            if full_path not in packages:
                continue

            project = PackageScopedProjectInfo(
                org_name_snakecase=self.config.org_name_snakecase,
                override=override,
                root_path=self.root_dir,
                full_path=construct_project_full_path(
                    self.root_dir, override.project_path
                ),
            )
            projects.append(project)

        # Update the file contents in the projects
        for project in projects:
            pkg_files = find_files_with_suffix(
                project.full_path, self.LOOKUP_FILE_SUFFIXES
            )
            for filename in pkg_files:
                with open(filename, encoding="utf-8") as f:
                    project.file_contents[filename] = f.read()

        return projects
