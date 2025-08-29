from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .labels import Labels
    from .user_interface_config_auth_type import UserInterfaceConfigAuth_type

@dataclass
class UserInterfaceConfigAuth(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The obacEnabled property
    obac_enabled: Optional[bool] = None
    # User-defined name-value pairs. Name and value must be strings.
    options: Optional[Labels] = None
    # The rbacEnabled property
    rbac_enabled: Optional[bool] = None
    # The type property
    type: Optional[UserInterfaceConfigAuth_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UserInterfaceConfigAuth:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UserInterfaceConfigAuth
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UserInterfaceConfigAuth()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .labels import Labels
        from .user_interface_config_auth_type import UserInterfaceConfigAuth_type

        from .labels import Labels
        from .user_interface_config_auth_type import UserInterfaceConfigAuth_type

        fields: dict[str, Callable[[Any], None]] = {
            "obacEnabled": lambda n : setattr(self, 'obac_enabled', n.get_bool_value()),
            "options": lambda n : setattr(self, 'options', n.get_object_value(Labels)),
            "rbacEnabled": lambda n : setattr(self, 'rbac_enabled', n.get_bool_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(UserInterfaceConfigAuth_type)),
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
        writer.write_bool_value("obacEnabled", self.obac_enabled)
        writer.write_object_value("options", self.options)
        writer.write_bool_value("rbacEnabled", self.rbac_enabled)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

