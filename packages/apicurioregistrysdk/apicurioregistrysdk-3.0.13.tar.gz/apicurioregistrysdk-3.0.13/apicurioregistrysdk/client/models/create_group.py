from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .labels import Labels

@dataclass
class CreateGroup(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The description property
    description: Optional[str] = None
    # An ID of a single artifact group.
    group_id: Optional[str] = None
    # User-defined name-value pairs. Name and value must be strings.
    labels: Optional[Labels] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreateGroup:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreateGroup
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreateGroup()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .labels import Labels

        from .labels import Labels

        fields: dict[str, Callable[[Any], None]] = {
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "groupId": lambda n : setattr(self, 'group_id', n.get_str_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_object_value(Labels)),
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
        writer.write_str_value("description", self.description)
        writer.write_str_value("groupId", self.group_id)
        writer.write_object_value("labels", self.labels)
        writer.write_additional_data_value(self.additional_data)
    

