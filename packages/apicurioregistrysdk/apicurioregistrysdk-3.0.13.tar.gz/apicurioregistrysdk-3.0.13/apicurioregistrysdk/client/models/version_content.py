from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .artifact_reference import ArtifactReference

@dataclass
class VersionContent(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Raw content of the artifact version or a valid (and accessible) URL where the content can be found.
    content: Optional[str] = None
    # The content-type, such as `application/json` or `text/xml`.
    content_type: Optional[str] = None
    # Collection of references to other artifacts.
    references: Optional[list[ArtifactReference]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VersionContent:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VersionContent
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VersionContent()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .artifact_reference import ArtifactReference

        from .artifact_reference import ArtifactReference

        fields: dict[str, Callable[[Any], None]] = {
            "content": lambda n : setattr(self, 'content', n.get_str_value()),
            "contentType": lambda n : setattr(self, 'content_type', n.get_str_value()),
            "references": lambda n : setattr(self, 'references', n.get_collection_of_object_values(ArtifactReference)),
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
        writer.write_str_value("content", self.content)
        writer.write_str_value("contentType", self.content_type)
        writer.write_collection_of_object_values("references", self.references)
        writer.write_additional_data_value(self.additional_data)
    

