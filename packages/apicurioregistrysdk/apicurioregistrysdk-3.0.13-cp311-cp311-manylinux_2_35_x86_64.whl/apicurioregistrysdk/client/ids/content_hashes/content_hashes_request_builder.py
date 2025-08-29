from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_content_hash_item_request_builder import WithContentHashItemRequestBuilder

class ContentHashesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /ids/contentHashes
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ContentHashesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/ids/contentHashes", path_parameters)
    
    def by_content_hash(self,content_hash: str) -> WithContentHashItemRequestBuilder:
        """
        Access artifact content utilizing the SHA-256 hash of the content.
        param content_hash: SHA-256 content hash for a single artifact content.
        Returns: WithContentHashItemRequestBuilder
        """
        if content_hash is None:
            raise TypeError("content_hash cannot be null.")
        from .item.with_content_hash_item_request_builder import WithContentHashItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["contentHash"] = content_hash
        return WithContentHashItemRequestBuilder(self.request_adapter, url_tpl_params)
    

