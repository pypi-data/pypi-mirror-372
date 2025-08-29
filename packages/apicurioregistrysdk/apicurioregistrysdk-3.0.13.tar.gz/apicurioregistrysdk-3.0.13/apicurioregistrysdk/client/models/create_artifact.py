from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .create_version import CreateVersion
    from .labels import Labels

@dataclass
class CreateArtifact(AdditionalDataHolder, Parsable):
    """
    Data sent when creating a new artifact.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ID of a single artifact.
    artifact_id: Optional[str] = None
    # The artifactType property
    artifact_type: Optional[str] = None
    # The description property
    description: Optional[str] = None
    # The firstVersion property
    first_version: Optional[CreateVersion] = None
    # User-defined name-value pairs. Name and value must be strings.
    labels: Optional[Labels] = None
    # The name property
    name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreateArtifact:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreateArtifact
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreateArtifact()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .create_version import CreateVersion
        from .labels import Labels

        from .create_version import CreateVersion
        from .labels import Labels

        fields: dict[str, Callable[[Any], None]] = {
            "artifactId": lambda n : setattr(self, 'artifact_id', n.get_str_value()),
            "artifactType": lambda n : setattr(self, 'artifact_type', n.get_str_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "firstVersion": lambda n : setattr(self, 'first_version', n.get_object_value(CreateVersion)),
            "labels": lambda n : setattr(self, 'labels', n.get_object_value(Labels)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
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
        writer.write_str_value("description", self.description)
        writer.write_object_value("firstVersion", self.first_version)
        writer.write_object_value("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_additional_data_value(self.additional_data)
    

