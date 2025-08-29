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
    from ........models.artifact_reference import ArtifactReference
    from ........models.problem_details import ProblemDetails
    from ........models.reference_type import ReferenceType

class ReferencesRequestBuilder(BaseRequestBuilder):
    """
    Manage the references for a single version of an artifact in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ReferencesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/groups/{groupId}/artifacts/{artifactId}/versions/{versionExpression}/references{?refType*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ReferencesRequestBuilderGetQueryParameters]] = None) -> Optional[list[ArtifactReference]]:
        """
        Retrieves all references for a single version of an artifact.  Both the `artifactId` and theunique `version` number must be provided.  Using the `refType` query parameter, it is possibleto retrieve an array of either the inbound or outbound references.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[ArtifactReference]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ........models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "404": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ........models.artifact_reference import ArtifactReference

        return await self.request_adapter.send_collection_async(request_info, ArtifactReference, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ReferencesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieves all references for a single version of an artifact.  Both the `artifactId` and theunique `version` number must be provided.  Using the `refType` query parameter, it is possibleto retrieve an array of either the inbound or outbound references.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ReferencesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ReferencesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ReferencesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ReferencesRequestBuilderGetQueryParameters():
        """
        Retrieves all references for a single version of an artifact.  Both the `artifactId` and theunique `version` number must be provided.  Using the `refType` query parameter, it is possibleto retrieve an array of either the inbound or outbound references.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "ref_type":
                return "refType"
            return original_name
        
        # Determines the type of reference to return, either INBOUND or OUTBOUND.  Defaults to OUTBOUND.
        ref_type: Optional[ReferenceType] = None

    
    @dataclass
    class ReferencesRequestBuilderGetRequestConfiguration(RequestConfiguration[ReferencesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

