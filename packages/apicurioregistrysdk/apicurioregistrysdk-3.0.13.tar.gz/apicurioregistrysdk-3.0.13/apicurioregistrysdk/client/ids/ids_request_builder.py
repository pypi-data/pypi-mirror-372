from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .content_hashes.content_hashes_request_builder import ContentHashesRequestBuilder
    from .content_ids.content_ids_request_builder import ContentIdsRequestBuilder
    from .global_ids.global_ids_request_builder import GlobalIdsRequestBuilder

class IdsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /ids
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new IdsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/ids", path_parameters)
    
    @property
    def content_hashes(self) -> ContentHashesRequestBuilder:
        """
        The contentHashes property
        """
        from .content_hashes.content_hashes_request_builder import ContentHashesRequestBuilder

        return ContentHashesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def content_ids(self) -> ContentIdsRequestBuilder:
        """
        The contentIds property
        """
        from .content_ids.content_ids_request_builder import ContentIdsRequestBuilder

        return ContentIdsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def global_ids(self) -> GlobalIdsRequestBuilder:
        """
        The globalIds property
        """
        from .global_ids.global_ids_request_builder import GlobalIdsRequestBuilder

        return GlobalIdsRequestBuilder(self.request_adapter, self.path_parameters)
    

