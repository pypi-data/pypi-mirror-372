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
    from ..models.create_group import CreateGroup
    from ..models.group_meta_data import GroupMetaData
    from ..models.group_search_results import GroupSearchResults
    from ..models.group_sort_by import GroupSortBy
    from ..models.problem_details import ProblemDetails
    from ..models.sort_order import SortOrder
    from .item.with_group_item_request_builder import WithGroupItemRequestBuilder

class GroupsRequestBuilder(BaseRequestBuilder):
    """
    Collection of the groups in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new GroupsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/groups{?limit*,offset*,order*,orderby*}", path_parameters)
    
    def by_group_id(self,group_id: str) -> WithGroupItemRequestBuilder:
        """
        Collection to manage a single group in the registry.
        param group_id: The artifact group ID.  Must be a string provided by the client, representing the name of the grouping of artifacts. Must follow the ".{1,512}" pattern.
        Returns: WithGroupItemRequestBuilder
        """
        if group_id is None:
            raise TypeError("group_id cannot be null.")
        from .item.with_group_item_request_builder import WithGroupItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["groupId"] = group_id
        return WithGroupItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[GroupsRequestBuilderGetQueryParameters]] = None) -> Optional[GroupSearchResults]:
        """
        Returns a list of all groups.  This list is paged.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GroupSearchResults]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ..models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models.group_search_results import GroupSearchResults

        return await self.request_adapter.send_async(request_info, GroupSearchResults, error_mapping)
    
    async def post(self,body: CreateGroup, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[GroupMetaData]:
        """
        Creates a new group.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)* The group already exist (HTTP error `409`)
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GroupMetaData]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ..models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "409": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models.group_meta_data import GroupMetaData

        return await self.request_adapter.send_async(request_info, GroupMetaData, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[GroupsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a list of all groups.  This list is paged.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: CreateGroup, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Creates a new group.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)* The group already exist (HTTP error `409`)
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
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
        Returns a list of all groups.  This list is paged.
        """
        # The number of groups to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of groups to skip before starting the result set.  Defaults to 0.
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
    
    @dataclass
    class GroupsRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

