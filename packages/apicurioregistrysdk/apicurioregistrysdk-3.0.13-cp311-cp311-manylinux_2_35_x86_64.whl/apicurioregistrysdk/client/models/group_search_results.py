from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .searched_group import SearchedGroup

@dataclass
class GroupSearchResults(AdditionalDataHolder, Parsable):
    """
    Describes the response received when searching for groups.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The total number of groups that matched the query that produced the result set (may be more than the number of groups in the result set).
    count: Optional[int] = None
    # The groups returned in the result set.
    groups: Optional[list[SearchedGroup]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GroupSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GroupSearchResults
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GroupSearchResults()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .searched_group import SearchedGroup

        from .searched_group import SearchedGroup

        fields: dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "groups": lambda n : setattr(self, 'groups', n.get_collection_of_object_values(SearchedGroup)),
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
        writer.write_collection_of_object_values("groups", self.groups)
        writer.write_additional_data_value(self.additional_data)
    

