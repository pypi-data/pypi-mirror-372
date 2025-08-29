from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Comment(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The commentId property
    comment_id: Optional[str] = None
    # The createdOn property
    created_on: Optional[datetime.datetime] = None
    # The owner property
    owner: Optional[str] = None
    # The value property
    value: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Comment:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Comment
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Comment()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "commentId": lambda n : setattr(self, 'comment_id', n.get_str_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "value": lambda n : setattr(self, 'value', n.get_str_value()),
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
        writer.write_str_value("commentId", self.comment_id)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_str_value("owner", self.owner)
        writer.write_str_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

