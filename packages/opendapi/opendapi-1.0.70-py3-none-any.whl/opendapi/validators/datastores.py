"""Teams validator module"""

import functools
from collections import Counter, defaultdict
from typing import Dict, List, NamedTuple, Tuple, Union

from opendapi.defs import DATASTORES_SUFFIX, OPENDAPI_SPEC_URL, OpenDAPIEntity
from opendapi.validators.base import BaseValidator, ValidationError
from opendapi.validators.defs import FileSet, MergeKeyCompositeIDParams
from opendapi.weakref import weak_lru_cache


class DatastoreFilepathIndex(NamedTuple):
    """Datastore filepath, urn, and index."""

    filepath: str
    datastore_index: int
    host_index: int


class DatastoresValidator(BaseValidator):
    """
    Validator class for datastores files
    """

    SUFFIX = DATASTORES_SUFFIX
    SPEC_VERSION = "0-0-1"
    ENTITY = OpenDAPIEntity.DATASTORES

    # Paths & keys to use for uniqueness check within a list of dicts when merging
    MERGE_UNIQUE_LOOKUP_KEYS: List[
        Tuple[
            List[Union[str, int, MergeKeyCompositeIDParams.IgnoreListIndexType]],
            MergeKeyCompositeIDParams,
        ]
    ] = [(["datastores"], MergeKeyCompositeIDParams(required=[["urn"]]))]

    MUST_GENERATE_EVEN_IF_ENTITY_TYPE_EXISTS = False

    @functools.cached_property
    def original_file_state(self) -> Dict[str, Dict]:
        """Collect the original file state"""
        og_file_state = super().original_file_state
        deduped_file_state = {}
        for filepath, content in og_file_state.items():
            deduped_datastores = []
            seen_urns = set()
            for datastore in content.get("datastores", []):
                urn = datastore.get("urn")
                # will fail during schema validation
                if not urn:  # pragma: no cover
                    continue
                # dupe - we skip it
                if (
                    urn in seen_urns
                    and datastore.get("type") == "google_cloud_postgresql"
                ):  # pragma: no cover
                    continue
                seen_urns.add(urn)
                deduped_datastores.append(datastore)
            content["datastores"] = deduped_datastores
            deduped_file_state[filepath] = content
        return deduped_file_state

    @weak_lru_cache()
    def _get_file_state_datastore_urn_counts(self, fileset: FileSet) -> Counter:
        """Collect all the datastores urns"""
        return Counter(
            (
                dt.get("urn")
                for content in self.get_file_state(fileset).values()
                for dt in content.get("datastores", [])
            )
        )

    def _validate_datastore_urns_globally_unique(
        self, file: str, content: dict, fileset: FileSet
    ):
        """Validate if the datastore urns are globally unique"""
        datastore_urn_counts = self._get_file_state_datastore_urn_counts(fileset)
        non_unique_datastore_urns = {
            datastore["urn"]
            for datastore in content.get("datastores", [])
            if datastore_urn_counts[datastore["urn"]] > 1
        }
        if non_unique_datastore_urns:
            raise ValidationError(
                f"Non-globally-unique datastore urns in file '{file}': {non_unique_datastore_urns}"
            )

    @weak_lru_cache()
    def _get_non_globally_unique_datastore_host_locations_errors(
        self, fileset: FileSet
    ) -> Dict[str, str]:
        """Validate that the hosts are unique"""
        datastore_location_to_datastore_info: Dict[
            str, List[DatastoreFilepathIndex]
        ] = defaultdict(list)
        for filepath, content in self.get_file_state(fileset).items():
            for datastore_index, datastore in enumerate(content.get("datastores", [])):
                for host_index, host_info in enumerate(
                    datastore.get("host", {}).values()
                ):
                    datastore_location_to_datastore_info[host_info["location"]].append(
                        DatastoreFilepathIndex(
                            filepath=filepath,
                            datastore_index=datastore_index,
                            host_index=host_index,
                        )
                    )
        error_str_by_filepath = {}
        for (
            location,
            datastore_info_list,
        ) in datastore_location_to_datastore_info.items():
            if len(datastore_info_list) > 1:
                error_str = f"The remote datastore - {location} - is repeated across multiple datastores: "
                for datastore_info in datastore_info_list:
                    error_str += (
                        f"\n- {datastore_info.filepath} - "
                        f"datastore_index: {datastore_info.datastore_index} - "
                        f"host_index: {datastore_info.host_index}"
                    )
                for datastore_info in datastore_info_list:
                    error_str_by_filepath[datastore_info.filepath] = error_str
        return error_str_by_filepath

    def _validate_datastore_host_locations_globally_unique(
        self, file: str, fileset: FileSet
    ):
        """Validate that the hosts are present"""

        error_str_by_filepath = (
            self._get_non_globally_unique_datastore_host_locations_errors(fileset)
        )
        if error_str := error_str_by_filepath.get(file):
            raise ValidationError(error_str)

    def validate_content(self, file: str, content: Dict, fileset: FileSet):
        """Validate the content of the files"""
        super().validate_content(file, content, fileset)
        self._validate_datastore_urns_globally_unique(file, content, fileset)
        self._validate_datastore_host_locations_globally_unique(file, fileset)

    def _get_base_generated_files(self) -> Dict[str, Dict]:
        """Set Autoupdate templates in {file_path: content} format"""
        return {
            f"{self.base_destination_dir}/{self.config.org_name_snakecase}.datastores.yaml": {
                "schema": OPENDAPI_SPEC_URL.format(
                    version=self.SPEC_VERSION, entity="datastores"
                ),
                "datastores": [],
            }
        }
