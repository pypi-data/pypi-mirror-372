from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .artifact_meta_data import ArtifactMetaData
    from .version_meta_data import VersionMetaData

@dataclass
class CreateArtifactResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The artifact property
    artifact: Optional[ArtifactMetaData] = None
    # The version property
    version: Optional[VersionMetaData] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreateArtifactResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreateArtifactResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreateArtifactResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .artifact_meta_data import ArtifactMetaData
        from .version_meta_data import VersionMetaData

        from .artifact_meta_data import ArtifactMetaData
        from .version_meta_data import VersionMetaData

        fields: dict[str, Callable[[Any], None]] = {
            "artifact": lambda n : setattr(self, 'artifact', n.get_object_value(ArtifactMetaData)),
            "version": lambda n : setattr(self, 'version', n.get_object_value(VersionMetaData)),
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
        writer.write_object_value("artifact", self.artifact)
        writer.write_object_value("version", self.version)
        writer.write_additional_data_value(self.additional_data)
    

