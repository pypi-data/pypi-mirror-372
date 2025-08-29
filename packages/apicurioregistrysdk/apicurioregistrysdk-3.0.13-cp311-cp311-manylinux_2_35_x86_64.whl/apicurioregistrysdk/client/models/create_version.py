from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .labels import Labels
    from .version_content import VersionContent

@dataclass
class CreateVersion(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The branches property
    branches: Optional[list[str]] = None
    # The content property
    content: Optional[VersionContent] = None
    # The description property
    description: Optional[str] = None
    # The isDraft property
    is_draft: Optional[bool] = None
    # User-defined name-value pairs. Name and value must be strings.
    labels: Optional[Labels] = None
    # The name property
    name: Optional[str] = None
    # A single version of an artifact.  Can be provided by the client when creating a new version,or it can be server-generated.  The value can be any string unique to the artifact, but it isrecommended to use a simple integer or a semver value.
    version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreateVersion:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreateVersion
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreateVersion()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .labels import Labels
        from .version_content import VersionContent

        from .labels import Labels
        from .version_content import VersionContent

        fields: dict[str, Callable[[Any], None]] = {
            "branches": lambda n : setattr(self, 'branches', n.get_collection_of_primitive_values(str)),
            "content": lambda n : setattr(self, 'content', n.get_object_value(VersionContent)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "isDraft": lambda n : setattr(self, 'is_draft', n.get_bool_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_object_value(Labels)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
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
        writer.write_collection_of_primitive_values("branches", self.branches)
        writer.write_object_value("content", self.content)
        writer.write_str_value("description", self.description)
        writer.write_bool_value("isDraft", self.is_draft)
        writer.write_object_value("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_str_value("version", self.version)
        writer.write_additional_data_value(self.additional_data)
    

