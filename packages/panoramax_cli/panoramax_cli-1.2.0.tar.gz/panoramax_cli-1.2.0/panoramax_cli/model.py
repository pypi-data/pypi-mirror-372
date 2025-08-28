from dataclasses import dataclass, field, fields
from typing import Optional, Dict, List, Any
import os
import hashlib
from copy import deepcopy
from enum import Enum
from pathlib import Path
from geopic_tag_reader.reader import GeoPicTags, PartialGeoPicTags
from geopic_tag_reader.sequence import (
    Picture as TRPicture,
    SortMethod,
    MergeParams,
    SplitParams,
)
from panoramax_cli.http import Client
from panoramax_cli.exception import CliException
from panoramax_cli.metadata import MetadataHandler

UPLOADSET_LOCAL_FILE = "_panoramax.txt"


@dataclass
class Panoramax:
    """Panoramax API instance"""

    url: str
    token: Optional[str] = None


@dataclass
class Collection:
    id: Optional[str] = None


@dataclass
class Picture:
    path: Optional[str] = None
    metadata: Optional[GeoPicTags] = None
    overridden_metadata: Optional[PartialGeoPicTags] = None

    def has_mandatory_metadata(self):
        """To be valid a picture should have a coordinate and a timestamp"""
        if self.metadata is not None:
            return True
        mandatory_fields = ["lon", "lat", "ts"]
        for m in mandatory_fields:
            if getattr(self.overridden_metadata, m) is None:
                return False
        return True

    def update_overriden_metadata(self, new_metadata: PartialGeoPicTags):
        """Update overriden metadata with new value only if there is no existing value"""
        if self.overridden_metadata is None:
            self.overridden_metadata = new_metadata
            return
        for f in fields(self.overridden_metadata):
            old_value = getattr(self.overridden_metadata, f.name)
            if old_value is None:
                setattr(
                    self.overridden_metadata,
                    f.name,
                    getattr(new_metadata, f.name),
                )

    def toTRPicture(self):
        """Transforms into Tag Reader Picture"""

        if self.path is None:
            raise Exception("No file path defined")

        if self.metadata is not None:
            meta = deepcopy(self.metadata)
            if self.overridden_metadata is not None:
                for field in fields(self.overridden_metadata):
                    override_value = getattr(self.overridden_metadata, field.name)
                    if override_value is not None:
                        setattr(meta, field.name, override_value)
        elif self.overridden_metadata is not None:
            meta = GeoPicTags(
                lat=self.overridden_metadata.lat,
                lon=self.overridden_metadata.lon,
                ts=self.overridden_metadata.ts,
                heading=self.overridden_metadata.heading,
                type=self.overridden_metadata.type,
                model=self.overridden_metadata.model,
                crop=self.overridden_metadata.crop,
                focal_length=self.overridden_metadata.focal_length,
                make=self.overridden_metadata.make,
                yaw=self.overridden_metadata.yaw,
                pitch=self.overridden_metadata.pitch,
                roll=self.overridden_metadata.roll,
                altitude=self.overridden_metadata.altitude,
                exif=self.overridden_metadata.exif,
            )
        else:
            raise Exception("No metadata available")

        return TRPicture(self.path, meta)


class FileName(str, Enum):
    original_name = "original-name"
    id_name = "id"


class UploadFileStatus(str, Enum):
    synchronized = "synchronized"
    rejected = "rejected"
    not_sent = "not_sent"
    ignored = "ignored"


@dataclass
class UploadFile:
    """Single file of an upload set"""

    path: Path
    content_md5: Optional[str] = None
    externalMetadata: Optional[PartialGeoPicTags] = None
    picture_id: Optional[str] = None
    rejected: Optional[str] = None
    status: UploadFileStatus = UploadFileStatus.not_sent

    def compute_hash(self) -> None:
        if self.content_md5 is None:
            if self.path is None:
                raise CliException("No file available to compute hash")
            with open(self.path, "rb") as f:
                self.content_md5 = hashlib.md5(f.read()).hexdigest()


@dataclass
class UploadParameters:
    sort_method: Optional[SortMethod] = None
    split_params: Optional[SplitParams] = field(default_factory=lambda: SplitParams())
    merge_params: Optional[MergeParams] = field(default_factory=lambda: MergeParams())
    already_blurred: Optional[bool] = None
    relative_heading: Optional[int] = None

    def update_with_instance_defaults(self, client: Client, panoramax: Panoramax):
        """Update the upload parameters with the instance's default values if none was provided (and if the merge/split functionnalities have not been disabled)"""
        conf = None
        updated_fields = []
        if self.merge_params is not None and (self.merge_params.maxDistance is None or self.merge_params.maxRotationAngle is None):
            conf = client.get_instance_configuration(panoramax)
            if self.merge_params.maxDistance is None:
                self.merge_params.maxDistance = conf.get("defaults", {}).get("duplicate_distance")
                updated_fields.append(f"duplicate distance = {self.merge_params.maxDistance}m")
            if self.merge_params.maxRotationAngle is None:
                self.merge_params.maxRotationAngle = conf.get("defaults", {}).get("duplicate_rotation")
                updated_fields.append(f"duplicate rotation = {self.merge_params.maxRotationAngle}°")
        if self.split_params is not None and (self.split_params.maxDistance is None or self.split_params.maxTime is None):
            conf = client.get_instance_configuration(panoramax)
            if self.split_params.maxDistance is None:
                self.split_params.maxDistance = conf.get("defaults", {}).get("split_distance")
                updated_fields.append(f"split distance = {self.split_params.maxDistance}m")
            if self.split_params.maxTime is None:
                self.split_params.maxTime = conf.get("defaults", {}).get("split_time")
                updated_fields.append(f"split time = {self.split_params.maxTime}s")

        if updated_fields:
            print(f"⚙️ Using the Panoramax instance's default values for parameters: {', '.join(updated_fields)}")


@dataclass
class AggregatedUploadSetStatus:
    """Aggregated status of an upload sets"""

    prepared: int
    preparing: Optional[int]
    broken: Optional[int]
    not_processed: Optional[int]

    def total(self):
        return self.prepared + (self.preparing or 0) + (self.broken or 0) + (self.not_processed or 0)


@dataclass
class UploadSet:
    """Container of files to upload"""

    id: Optional[str] = None
    path: Optional[Path] = None
    title: Optional[str] = None
    parameters: Optional[UploadParameters] = None
    metadata_handler: Optional[MetadataHandler] = None
    files: List[UploadFile] = field(default_factory=lambda: [])
    completed: bool = False
    dispatched: bool = False
    ready: bool = False
    status: Optional[AggregatedUploadSetStatus] = None
    associated_collections: Optional[List[Collection]] = None
    metadata: Dict[str, Any] = field(default_factory=lambda: {})

    def load_id(self) -> bool:
        """Try to load ID from local file if any"""

        if self.id is not None:
            return True

        if self.path is None:
            return False

        idFile = os.path.join(self.path, UPLOADSET_LOCAL_FILE)
        try:
            with open(idFile, "r") as f:
                self.id = f.read().strip().replace("upload_set_id=", "")
                if self.id == "":
                    self.id = None
        except FileNotFoundError:
            return False

        return self.id is not None

    def persist(self) -> Path:
        """Writes UploadSet ID into local file"""

        if self.id is None:
            raise CliException("Can't persist UploadSet without ID")

        if self.path is None:
            raise CliException("Can't persist UploadSet without path")

        idFile = os.path.join(self.path, UPLOADSET_LOCAL_FILE)
        with open(idFile, "w") as f:
            f.write("upload_set_id=" + self.id)

        return Path(idFile)

    def nb_prepared(self):
        return self.status.prepared if self.status else 0

    def nb_not_processed(self):
        return self.status.not_processed if self.status else 0

    def nb_preparing(self):
        return self.status.preparing if self.status else 0

    def nb_broken(self):
        return self.status.broken if self.status else 0

    def nb_not_sent(self):
        return sum([1 for f in self.files if f.status == UploadFileStatus.not_sent])

    def nb_not_ignored(self):
        return sum([1 for f in self.files if f.status != UploadFileStatus.ignored])
