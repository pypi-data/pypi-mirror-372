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
    from ...models.group_search_results import GroupSearchResults
    from ...models.group_sort_by import GroupSortBy
    from ...models.problem_details import ProblemDetails
    from ...models.sort_order import SortOrder

class GroupsRequestBuilder(BaseRequestBuilder):
    """
    Search for groups in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new GroupsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/search/groups{?description*,groupId*,labels*,limit*,offset*,order*,orderby*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[GroupsRequestBuilderGetQueryParameters]] = None) -> Optional[GroupSearchResults]:
        """
        Returns a paginated list of all groups that match the provided filter criteria.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GroupSearchResults]
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
        from ...models.group_search_results import GroupSearchResults

        return await self.request_adapter.send_async(request_info, GroupSearchResults, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[GroupsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paginated list of all groups that match the provided filter criteria.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> GroupsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: GroupsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return GroupsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class GroupsRequestBuilderGetQueryParameters():
        """
        Returns a paginated list of all groups that match the provided filter criteria.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "group_id":
                return "groupId"
            if original_name == "description":
                return "description"
            if original_name == "labels":
                return "labels"
            if original_name == "limit":
                return "limit"
            if original_name == "offset":
                return "offset"
            if original_name == "order":
                return "order"
            if original_name == "orderby":
                return "orderby"
            return original_name
        
        # Filter by description.
        description: Optional[str] = None

        # Filter by group name.
        group_id: Optional[str] = None

        # Filter by one or more name/value label.  Separate each name/value pair using a colon.  Forexample `labels=foo:bar` will return only artifacts with a label named `foo`and value `bar`.
        labels: Optional[list[str]] = None

        # The number of artifacts to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of artifacts to skip before starting to collect the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[SortOrder] = None

        # The field to sort by.  Can be one of:* `name`* `createdOn`
        orderby: Optional[GroupSortBy] = None

    
    @dataclass
    class GroupsRequestBuilderGetRequestConfiguration(RequestConfiguration[GroupsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

