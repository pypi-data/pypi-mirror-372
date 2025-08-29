from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_content_item_request_builder import WithContentItemRequestBuilder

class ContentIdsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /ids/contentIds
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ContentIdsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/ids/contentIds", path_parameters)
    
    def by_content_id(self,content_id: int) -> WithContentItemRequestBuilder:
        """
        Access artifact content utilizing the unique content identifier for that content.
        param content_id: Global identifier for a single artifact content.
        Returns: WithContentItemRequestBuilder
        """
        if content_id is None:
            raise TypeError("content_id cannot be null.")
        from .item.with_content_item_request_builder import WithContentItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["contentId"] = content_id
        return WithContentItemRequestBuilder(self.request_adapter, url_tpl_params)
    

