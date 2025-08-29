from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ....models.handle_references_type import HandleReferencesType
    from ....models.problem_details import ProblemDetails
    from .references.references_request_builder import ReferencesRequestBuilder

class WithGlobalItemRequestBuilder(BaseRequestBuilder):
    """
    Access artifact content utilizing an artifact version's globally unique identifier.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithGlobalItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/ids/globalIds/{globalId}{?references*,returnArtifactType*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithGlobalItemRequestBuilderGetQueryParameters]] = None) -> Optional[bytes]:
        """
        Gets the content for an artifact version in the registry using its globally uniqueidentifier.This operation may fail for one of the following reasons:* No artifact version with this `globalId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: bytes
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "404": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "bytes", error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithGlobalItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Gets the content for an artifact version in the registry using its globally uniqueidentifier.This operation may fail for one of the following reasons:* No artifact version with this `globalId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "*/*, application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WithGlobalItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithGlobalItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithGlobalItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def references(self) -> ReferencesRequestBuilder:
        """
        The references property
        """
        from .references.references_request_builder import ReferencesRequestBuilder

        return ReferencesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithGlobalItemRequestBuilderGetQueryParameters():
        """
        Gets the content for an artifact version in the registry using its globally uniqueidentifier.This operation may fail for one of the following reasons:* No artifact version with this `globalId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "return_artifact_type":
                return "returnArtifactType"
            if original_name == "references":
                return "references"
            return original_name
        
        # Allows the user to specify how references in the content should be treated.
        references: Optional[HandleReferencesType] = None

        # When set to `true`, the HTTP response will include a header named `X-Registry-ArtifactType`that contains the type of the artifact being returned.
        return_artifact_type: Optional[bool] = None

    
    @dataclass
    class WithGlobalItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithGlobalItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

