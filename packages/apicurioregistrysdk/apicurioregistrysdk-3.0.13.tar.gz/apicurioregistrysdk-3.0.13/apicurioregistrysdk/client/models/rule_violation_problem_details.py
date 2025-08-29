from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .problem_details import ProblemDetails
    from .rule_violation_cause import RuleViolationCause

@dataclass
class RuleViolationProblemDetails(APIError, AdditionalDataHolder, Parsable):
    """
    All error responses, whether `4xx` or `5xx` will include one of these as the responsebody.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # List of rule violation causes.
    causes: Optional[list[RuleViolationCause]] = None
    # A human-readable explanation specific to this occurrence of the problem.
    detail: Optional[str] = None
    # A URI reference that identifies the specific occurrence of the problem.
    instance: Optional[str] = None
    # The name of the error (typically a server exception class name).
    name: Optional[str] = None
    # The HTTP status code.
    status: Optional[int] = None
    # A short, human-readable summary of the problem type.
    title: Optional[str] = None
    # A URI reference [RFC3986] that identifies the problem type.
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RuleViolationProblemDetails:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RuleViolationProblemDetails
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RuleViolationProblemDetails()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .problem_details import ProblemDetails
        from .rule_violation_cause import RuleViolationCause

        from .problem_details import ProblemDetails
        from .rule_violation_cause import RuleViolationCause

        fields: dict[str, Callable[[Any], None]] = {
            "causes": lambda n : setattr(self, 'causes', n.get_collection_of_object_values(RuleViolationCause)),
            "detail": lambda n : setattr(self, 'detail', n.get_str_value()),
            "instance": lambda n : setattr(self, 'instance', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_int_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_collection_of_object_values("causes", self.causes)
        writer.write_str_value("detail", self.detail)
        writer.write_str_value("instance", self.instance)
        writer.write_str_value("name", self.name)
        writer.write_int_value("status", self.status)
        writer.write_str_value("title", self.title)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def primary_message(self) -> Optional[str]:
        """
        The primary error message.
        """
        return super().message

