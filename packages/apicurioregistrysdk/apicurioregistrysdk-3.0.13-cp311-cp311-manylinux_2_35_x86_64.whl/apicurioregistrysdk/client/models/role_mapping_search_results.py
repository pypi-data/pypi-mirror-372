from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .role_mapping import RoleMapping

@dataclass
class RoleMappingSearchResults(AdditionalDataHolder, Parsable):
    """
    Describes the response received when searching for artifacts.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The total number of role mappings that matched the query that produced the result set (may be more than the number of role mappings in the result set).
    count: Optional[int] = None
    # The role mappings returned in the result set.
    role_mappings: Optional[list[RoleMapping]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RoleMappingSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RoleMappingSearchResults
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RoleMappingSearchResults()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .role_mapping import RoleMapping

        from .role_mapping import RoleMapping

        fields: dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "roleMappings": lambda n : setattr(self, 'role_mappings', n.get_collection_of_object_values(RoleMapping)),
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
        writer.write_int_value("count", self.count)
        writer.write_collection_of_object_values("roleMappings", self.role_mappings)
        writer.write_additional_data_value(self.additional_data)
    

