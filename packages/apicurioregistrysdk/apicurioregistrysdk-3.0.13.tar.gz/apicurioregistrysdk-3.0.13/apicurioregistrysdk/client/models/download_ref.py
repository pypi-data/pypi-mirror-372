from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class DownloadRef(AdditionalDataHolder, Parsable):
    """
    Models a download "link".  Useful for browser use-cases.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The downloadId property
    download_id: Optional[str] = None
    # The href property
    href: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DownloadRef:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DownloadRef
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DownloadRef()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "downloadId": lambda n : setattr(self, 'download_id', n.get_str_value()),
            "href": lambda n : setattr(self, 'href', n.get_str_value()),
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
        writer.write_str_value("downloadId", self.download_id)
        writer.write_str_value("href", self.href)
        writer.write_additional_data_value(self.additional_data)
    

