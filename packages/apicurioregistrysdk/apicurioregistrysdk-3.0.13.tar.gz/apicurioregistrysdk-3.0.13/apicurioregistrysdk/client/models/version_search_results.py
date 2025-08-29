from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .searched_version import SearchedVersion

@dataclass
class VersionSearchResults(AdditionalDataHolder, Parsable):
    """
    Describes the response received when searching for artifacts.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The total number of versions that matched the query (may be more than the number of versionsreturned in the result set).
    count: Optional[int] = None
    # The collection of artifact versions returned in the result set.
    versions: Optional[list[SearchedVersion]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VersionSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VersionSearchResults
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VersionSearchResults()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .searched_version import SearchedVersion

        from .searched_version import SearchedVersion

        fields: dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "versions": lambda n : setattr(self, 'versions', n.get_collection_of_object_values(SearchedVersion)),
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
        writer.write_collection_of_object_values("versions", self.versions)
        writer.write_additional_data_value(self.additional_data)
    

