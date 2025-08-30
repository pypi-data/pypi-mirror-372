"""Defs for Validators"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Dict, List, Optional, Tuple, Union

from opendapi.defs import OpenDAPIEntity
from opendapi.utils import build_location_without_repo_from_fullpath


class ValidationError(Exception):
    """Exception raised for validation errors"""


class MultiValidationError(ValidationError):
    """Exception raised for multiple validation errors"""

    def __init__(self, errors: List[str], prefix_message: str = None):
        self.errors = errors
        self.prefix_message = prefix_message

    def __str__(self):
        return (
            f"\n\n{self.prefix_message}\n\n"
            + f"Found {len(self.errors)} errors:\n\n"
            + "\n\n".join(self.errors)
        )


class FileSet(Enum):
    """Enum for the file set"""

    ORIGINAL = "original"
    GENERATED = "generated"
    MERGED = "merged"


class IntegrationType(Enum):
    """Enum for the integration type"""

    STATIC = "static"
    RUNTIME = "runtime"
    DBT = "dbt"


@dataclass
class CollectedFile:  # pylint: disable=too-many-instance-attributes
    """class for the collect result"""

    original: Optional[Dict]
    generated: Optional[Dict]
    merged: Dict
    filepath: str
    commit_sha: Optional[str]
    entity: OpenDAPIEntity
    root_dir: str
    additional_metadata_from_generated: Optional[Dict] = None
    generate_skipped: bool = False

    @property
    def server_filepath(self) -> str:
        """Return the server filepath"""
        return build_location_without_repo_from_fullpath(self.root_dir, self.filepath)

    @property
    def for_server(self) -> Dict:
        """Return the object as a dict"""
        return {
            "original": self.original,
            "generated": self.generated,
            "merged": self.merged,
            "filepath": self.server_filepath,
            "commit_sha": self.commit_sha,
            "entity": self.entity.value,
            "additional_metadata_from_generated": self.additional_metadata_from_generated,
            "generate_skipped": self.generate_skipped,
        }

    @property
    def as_json(self) -> Dict:
        """Return the object as a dict"""
        return {
            "original": self.original,
            "generated": self.generated,
            "merged": self.merged,
            "filepath": self.filepath,
            "commit_sha": self.commit_sha,
            "entity": self.entity.value,
            "root_dir": self.root_dir,
            "additional_metadata_from_generated": self.additional_metadata_from_generated,
            "generate_skipped": self.generate_skipped,
        }

    @classmethod
    def from_dict(cls, dict_: Dict) -> CollectedFile:
        """Create a CollectedFile from a json object"""
        return cls(
            original=dict_["original"],
            generated=dict_["generated"],
            merged=dict_["merged"],
            filepath=dict_["filepath"],
            commit_sha=dict_["commit_sha"],
            entity=OpenDAPIEntity(dict_["entity"]),
            root_dir=dict_["root_dir"],
            additional_metadata_from_generated=dict_.get(
                "additional_metadata_from_generated"
            ),
            generate_skipped=dict_.get("generate_skipped", False),
        )

    def reconcile(  # pylint: disable=too-many-branches
        self,
        other: Optional[CollectedFile],
    ) -> CollectedFile:
        """
        Reconcile two CollectedFiles, choosing actually generated values.
        This is useful for multi-runtime setups, where some runtimes may
        run and be skipped, or run the same generation multiple times.
        """
        if not other:
            return self

        if self.filepath != other.filepath:
            raise ValueError("Cannot reconcile files with different filepaths")

        if self.entity is not other.entity:
            raise ValueError("Cannot reconcile files with different entities")

        if self.commit_sha != other.commit_sha:
            raise ValueError("Cannot reconcile files with different commit SHAs")

        if self.original != other.original:
            raise ValueError("Cannot reconcile files with different original contents")

        # choose the appropriate generated
        if self.generate_skipped == other.generate_skipped:
            if (
                self.generated != other.generated
                or self.additional_metadata_from_generated
                != other.additional_metadata_from_generated
            ):
                raise ValueError(
                    "Cannot reconcile files with different generated contents or metadatas"
                )
            generate_skipped = self.generate_skipped
            generated = self.generated
            additional_metadata_from_generated = self.additional_metadata_from_generated
        elif self.generate_skipped:
            generate_skipped = other.generate_skipped
            generated = other.generated
            additional_metadata_from_generated = (
                other.additional_metadata_from_generated
            )
        else:
            generate_skipped = self.generate_skipped
            generated = self.generated
            additional_metadata_from_generated = self.additional_metadata_from_generated

        # do the same for merged
        if self.generate_skipped == other.generate_skipped:
            if self.merged != other.merged:
                raise ValueError(
                    "Cannot reconcile files with different merged contents"
                )
            merged = self.merged
        elif self.generate_skipped:
            merged = other.merged
        else:
            merged = self.merged

        return CollectedFile(
            original=self.original,
            generated=generated,
            merged=merged,
            filepath=self.filepath,
            commit_sha=self.commit_sha,
            entity=self.entity,
            additional_metadata_from_generated=additional_metadata_from_generated,
            generate_skipped=generate_skipped,
            root_dir=self.root_dir,
        )


@dataclass
class MergeKeyCompositeIDParams:
    """
    Class to store required and not required portions of a UUID
    """

    class NoIDFoundError(Exception):  # pylint: disable=too-few-public-methods
        """
        Exception raised when no ID can be found
        """

    class IgnoreListIndexType:  # pylint: disable=too-few-public-methods
        """
        Helper class if you want to match path keys that occur at any index
        """

        def __eq__(self, other):
            return isinstance(other, int)

    IGNORE_LIST_INDEX: ClassVar[IgnoreListIndexType] = IgnoreListIndexType()

    class NotSetType:  # pylint: disable=too-few-public-methods
        """represents not set"""

    NOT_SET: ClassVar[NotSetType] = NotSetType()

    # paths to values in the dict
    # for which we must have explicit terminal values
    required: List[List[str]]

    # paths to values in the dict
    # for which we need not reach the terminal value
    optional: List[List[str]] = field(default_factory=list)

    def __post_init__(self):
        """
        additional validation
        """
        # ensure that a returned UUID is not the empty tuple or the item itself
        if not self.required or any(
            not path_to_key_el for path_to_key_el in self.required
        ):
            raise ValueError(
                "Not having required portions for a UUID leads to nonsensical merging"
            )

    def get_id_if_matched(self, itm: dict) -> Optional[
        Tuple[
            Tuple[
                Tuple[str, ...],
                Union[
                    str, int, float, bool, None, MergeKeyCompositeIDParams.NotSetType
                ],
            ],
            ...,
        ]
    ]:
        """
        Returns an ID if we can create one from the given key, meaning that
        all required ID portions are fetched.
        """

        # we will build up the ID
        id_ = []

        # iterate through all paths to ID elements, which may be nested
        # the assumption is that each intermediate portion until we reach the terminal
        # element will be a dict, and the last element is a primitive
        # if we cannot reach the terminal element for a required ID portion,
        # we return None, since that means that an ID cannot be constructed
        for path_to_key_element in self.required:
            cur = itm
            for path_el in path_to_key_element:
                if path_el not in cur:
                    return None
                cur = cur[path_el]
            # we make sure to add the path_to_key_element to the ID, so that we can
            # disambiguate between different keys that have the same terminal value
            id_.append((tuple(path_to_key_element), cur))

        # do similar thing to above, but in this case not reaching a terminal element is OK.
        # to disambiguate between None being a terminal value VS it not being present, in the event
        # we do not reach a terminal element we add NOT_SET to the ID
        for path_to_key_element in self.optional:
            cur = itm
            for path_el in path_to_key_element:
                if path_el not in cur:
                    cur = self.NOT_SET
                    break
                cur = cur[path_el]
            id_.append((tuple(path_to_key_element), cur))

        # make hashable
        return tuple(id_)

    @staticmethod
    def safe_get_key_and_id(
        itm: Dict, merge_keys: List[MergeKeyCompositeIDParams]
    ) -> Optional[
        Tuple[
            MergeKeyCompositeIDParams,
            Tuple[
                Tuple[str, ...],
                Tuple[
                    Union[
                        str,
                        int,
                        float,
                        bool,
                        None,
                        MergeKeyCompositeIDParams.NotSetType,
                    ],
                    ...,
                ],
            ],
        ],
    ]:
        """
        Given a list of merge keys, return the first key and id for that we can create
        from itm, returning None if no match
        """
        return next(
            ((key, id_) for key in merge_keys if (id_ := key.get_id_if_matched(itm))),
            None,
        )

    @classmethod
    def get_key_and_id(
        cls, itm: Dict, merge_keys: List[MergeKeyCompositeIDParams]
    ) -> Tuple[
        MergeKeyCompositeIDParams,
        Tuple[
            Tuple[str, ...],
            Tuple[
                Union[
                    str,
                    int,
                    float,
                    bool,
                    None,
                    MergeKeyCompositeIDParams.NotSetType,
                ],
                ...,
            ],
        ],
    ]:
        """
        Given a list of merge keys, return the first key and id for that we can create
        from itm, raising MergeKeyCompositeIDParams.NoIDFoundError if no match
        """
        key_and_id = cls.safe_get_key_and_id(itm, merge_keys)
        if not key_and_id:
            raise cls.NoIDFoundError(
                f"No ID found in {itm} for any of the keys {merge_keys}"
            )
        return key_and_id
