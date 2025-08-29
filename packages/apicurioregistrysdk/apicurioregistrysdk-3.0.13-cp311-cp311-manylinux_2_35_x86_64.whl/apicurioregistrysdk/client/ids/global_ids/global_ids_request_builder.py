from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_global_item_request_builder import WithGlobalItemRequestBuilder

class GlobalIdsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /ids/globalIds
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new GlobalIdsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/ids/globalIds", path_parameters)
    
    def by_global_id(self,global_id: int) -> WithGlobalItemRequestBuilder:
        """
        Access artifact content utilizing an artifact version's globally unique identifier.
        param global_id: Global identifier for an artifact version.
        Returns: WithGlobalItemRequestBuilder
        """
        if global_id is None:
            raise TypeError("global_id cannot be null.")
        from .item.with_global_item_request_builder import WithGlobalItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["globalId"] = global_id
        return WithGlobalItemRequestBuilder(self.request_adapter, url_tpl_params)
    

