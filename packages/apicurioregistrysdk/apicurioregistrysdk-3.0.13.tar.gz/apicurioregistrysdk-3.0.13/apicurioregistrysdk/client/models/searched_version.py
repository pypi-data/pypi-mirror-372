from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .labels import Labels
    from .version_state import VersionState

@dataclass
class SearchedVersion(AdditionalDataHolder, Parsable):
    """
    Models a single artifact from the result set returned when searching for artifacts.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ID of a single artifact.
    artifact_id: Optional[str] = None
    # The artifactType property
    artifact_type: Optional[str] = None
    # The contentId property
    content_id: Optional[int] = None
    # The createdOn property
    created_on: Optional[datetime.datetime] = None
    # The description property
    description: Optional[str] = None
    # The globalId property
    global_id: Optional[int] = None
    # An ID of a single artifact group.
    group_id: Optional[str] = None
    # User-defined name-value pairs. Name and value must be strings.
    labels: Optional[Labels] = None
    # The modifiedBy property
    modified_by: Optional[str] = None
    # The modifiedOn property
    modified_on: Optional[datetime.datetime] = None
    # The name property
    name: Optional[str] = None
    # The owner property
    owner: Optional[str] = None
    # Describes the state of an artifact or artifact version.  The following statesare possible:* ENABLED* DISABLED* DEPRECATED
    state: Optional[VersionState] = None
    # A single version of an artifact.  Can be provided by the client when creating a new version,or it can be server-generated.  The value can be any string unique to the artifact, but it isrecommended to use a simple integer or a semver value.
    version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SearchedVersion:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SearchedVersion
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SearchedVersion()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .labels import Labels
        from .version_state import VersionState

        from .labels import Labels
        from .version_state import VersionState

        fields: dict[str, Callable[[Any], None]] = {
            "artifactId": lambda n : setattr(self, 'artifact_id', n.get_str_value()),
            "artifactType": lambda n : setattr(self, 'artifact_type', n.get_str_value()),
            "contentId": lambda n : setattr(self, 'content_id', n.get_int_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "globalId": lambda n : setattr(self, 'global_id', n.get_int_value()),
            "groupId": lambda n : setattr(self, 'group_id', n.get_str_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_object_value(Labels)),
            "modifiedBy": lambda n : setattr(self, 'modified_by', n.get_str_value()),
            "modifiedOn": lambda n : setattr(self, 'modified_on', n.get_datetime_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "state": lambda n : setattr(self, 'state', n.get_enum_value(VersionState)),
            "version": lambda n : setattr(self, 'version', n.get_str_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_str_value("artifactId", self.artifact_id)
        writer.write_str_value("artifactType", self.artifact_type)
        writer.write_int_value("contentId", self.content_id)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_str_value("description", self.description)
        writer.write_int_value("globalId", self.global_id)
        writer.write_str_value("groupId", self.group_id)
        writer.write_object_value("labels", self.labels)
        writer.write_str_value("modifiedBy", self.modified_by)
        writer.write_datetime_value("modifiedOn", self.modified_on)
        writer.write_str_value("name", self.name)
        writer.write_str_value("owner", self.owner)
        writer.write_enum_value("state", self.state)
        writer.write_str_value("version", self.version)
        writer.write_additional_data_value(self.additional_data)
    

