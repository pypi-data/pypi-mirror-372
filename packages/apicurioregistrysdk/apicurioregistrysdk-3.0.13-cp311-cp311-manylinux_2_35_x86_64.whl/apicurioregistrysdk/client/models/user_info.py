from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class UserInfo(AdditionalDataHolder, Parsable):
    """
    Information about a single user.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The admin property
    admin: Optional[bool] = None
    # The developer property
    developer: Optional[bool] = None
    # The displayName property
    display_name: Optional[str] = None
    # The username property
    username: Optional[str] = None
    # The viewer property
    viewer: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UserInfo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UserInfo
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UserInfo()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "admin": lambda n : setattr(self, 'admin', n.get_bool_value()),
            "developer": lambda n : setattr(self, 'developer', n.get_bool_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "username": lambda n : setattr(self, 'username', n.get_str_value()),
            "viewer": lambda n : setattr(self, 'viewer', n.get_bool_value()),
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
        writer.write_bool_value("admin", self.admin)
        writer.write_bool_value("developer", self.developer)
        writer.write_str_value("displayName", self.display_name)
        writer.write_str_value("username", self.username)
        writer.write_bool_value("viewer", self.viewer)
        writer.write_additional_data_value(self.additional_data)
    

