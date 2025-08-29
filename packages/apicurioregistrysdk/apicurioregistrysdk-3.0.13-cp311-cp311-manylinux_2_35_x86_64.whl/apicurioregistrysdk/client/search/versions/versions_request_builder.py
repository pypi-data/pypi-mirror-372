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
    from ...models.problem_details import ProblemDetails
    from ...models.sort_order import SortOrder
    from ...models.version_search_results import VersionSearchResults
    from ...models.version_sort_by import VersionSortBy
    from ...models.version_state import VersionState

class VersionsRequestBuilder(BaseRequestBuilder):
    """
    Search for versions in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new VersionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/search/versions{?artifactId*,artifactType*,canonical*,contentId*,description*,globalId*,groupId*,labels*,limit*,name*,offset*,order*,orderby*,state*,version*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderGetQueryParameters]] = None) -> Optional[VersionSearchResults]:
        """
        Returns a paginated list of all versions that match the provided filter criteria.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VersionSearchResults]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.version_search_results import VersionSearchResults

        return await self.request_adapter.send_async(request_info, VersionSearchResults, error_mapping)
    
    async def post(self,body: bytes, content_type: str, request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderPostQueryParameters]] = None) -> Optional[VersionSearchResults]:
        """
        Returns a paginated list of all versions that match the posted content.This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* A server error occurred (HTTP error `500`)
        param body: Binary request body
        param content_type: The request body content type.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VersionSearchResults]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        if content_type is None:
            raise TypeError("content_type cannot be null.")
        request_info = self.to_post_request_information(
            body, content_type, request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.version_search_results import VersionSearchResults

        return await self.request_adapter.send_async(request_info, VersionSearchResults, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paginated list of all versions that match the provided filter criteria.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: bytes, content_type: str, request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paginated list of all versions that match the posted content.This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* A server error occurred (HTTP error `500`)
        param body: Binary request body
        param content_type: The request body content type.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        if content_type is None:
            raise TypeError("content_type cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_stream_content(body, content_type)
        return request_info
    
    def with_url(self,raw_url: str) -> VersionsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: VersionsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return VersionsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class VersionsRequestBuilderGetQueryParameters():
        """
        Returns a paginated list of all versions that match the provided filter criteria.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "artifact_id":
                return "artifactId"
            if original_name == "artifact_type":
                return "artifactType"
            if original_name == "content_id":
                return "contentId"
            if original_name == "global_id":
                return "globalId"
            if original_name == "group_id":
                return "groupId"
            if original_name == "description":
                return "description"
            if original_name == "labels":
                return "labels"
            if original_name == "limit":
                return "limit"
            if original_name == "name":
                return "name"
            if original_name == "offset":
                return "offset"
            if original_name == "order":
                return "order"
            if original_name == "orderby":
                return "orderby"
            if original_name == "state":
                return "state"
            if original_name == "version":
                return "version"
            return original_name
        
        # Filter by artifactId.
        artifact_id: Optional[str] = None

        # Filter by artifact type (`AVRO`, `JSON`, etc).
        artifact_type: Optional[str] = None

        # Filter by contentId.
        content_id: Optional[int] = None

        # Filter by description.
        description: Optional[str] = None

        # Filter by globalId.
        global_id: Optional[int] = None

        # Filter by artifact group.
        group_id: Optional[str] = None

        # Filter by one or more name/value label.  Separate each name/value pair using a colon.  Forexample `labels=foo:bar` will return only artifacts with a label named `foo`and value `bar`.
        labels: Optional[list[str]] = None

        # The number of versions to return.  Defaults to 20.
        limit: Optional[int] = None

        # Filter by name.
        name: Optional[str] = None

        # The number of versions to skip before starting to collect the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[SortOrder] = None

        # The field to sort by.  Can be one of:* `name`* `createdOn`
        orderby: Optional[VersionSortBy] = None

        # Filter by version state.
        state: Optional[VersionState] = None

        # Filter by version number.
        version: Optional[str] = None

    
    @dataclass
    class VersionsRequestBuilderGetRequestConfiguration(RequestConfiguration[VersionsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class VersionsRequestBuilderPostQueryParameters():
        """
        Returns a paginated list of all versions that match the posted content.This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* A server error occurred (HTTP error `500`)
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "artifact_id":
                return "artifactId"
            if original_name == "artifact_type":
                return "artifactType"
            if original_name == "group_id":
                return "groupId"
            if original_name == "canonical":
                return "canonical"
            if original_name == "limit":
                return "limit"
            if original_name == "offset":
                return "offset"
            if original_name == "order":
                return "order"
            if original_name == "orderby":
                return "orderby"
            return original_name
        
        # Filter by artifact Id.
        artifact_id: Optional[str] = None

        # Indicates the type of artifact represented by the content being used for the search.  This is only needed when using the `canonical` query parameter, so that the server knows how to canonicalize the content prior to searching for matching versions.
        artifact_type: Optional[str] = None

        # Parameter that can be set to `true` to indicate that the server should "canonicalize" the content when searching for matching artifacts.  Canonicalization is unique to each artifact type, but typically involves removing any extra whitespace and formatting the content in a consistent manner.  Must be used along with the `artifactType` query parameter.
        canonical: Optional[bool] = None

        # Filter by group Id.
        group_id: Optional[str] = None

        # The number of versions to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of versions to skip before starting to collect the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[SortOrder] = None

        # The field to sort by.  Can be one of:* `name`* `createdOn`
        orderby: Optional[VersionSortBy] = None

    
    @dataclass
    class VersionsRequestBuilderPostRequestConfiguration(RequestConfiguration[VersionsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

