from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class UserInterfaceConfigFeatures(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The breadcrumbs property
    breadcrumbs: Optional[bool] = None
    # The deleteArtifact property
    delete_artifact: Optional[bool] = None
    # The deleteGroup property
    delete_group: Optional[bool] = None
    # The deleteVersion property
    delete_version: Optional[bool] = None
    # The draftMutability property
    draft_mutability: Optional[bool] = None
    # The readOnly property
    read_only: Optional[bool] = None
    # The roleManagement property
    role_management: Optional[bool] = None
    # The settings property
    settings: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UserInterfaceConfigFeatures:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UserInterfaceConfigFeatures
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UserInterfaceConfigFeatures()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "breadcrumbs": lambda n : setattr(self, 'breadcrumbs', n.get_bool_value()),
            "deleteArtifact": lambda n : setattr(self, 'delete_artifact', n.get_bool_value()),
            "deleteGroup": lambda n : setattr(self, 'delete_group', n.get_bool_value()),
            "deleteVersion": lambda n : setattr(self, 'delete_version', n.get_bool_value()),
            "draftMutability": lambda n : setattr(self, 'draft_mutability', n.get_bool_value()),
            "readOnly": lambda n : setattr(self, 'read_only', n.get_bool_value()),
            "roleManagement": lambda n : setattr(self, 'role_management', n.get_bool_value()),
            "settings": lambda n : setattr(self, 'settings', n.get_bool_value()),
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
        writer.write_bool_value("breadcrumbs", self.breadcrumbs)
        writer.write_bool_value("deleteArtifact", self.delete_artifact)
        writer.write_bool_value("deleteGroup", self.delete_group)
        writer.write_bool_value("deleteVersion", self.delete_version)
        writer.write_bool_value("draftMutability", self.draft_mutability)
        writer.write_bool_value("readOnly", self.read_only)
        writer.write_bool_value("roleManagement", self.role_management)
        writer.write_bool_value("settings", self.settings)
        writer.write_additional_data_value(self.additional_data)
    

