from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .artifacts.artifacts_request_builder import ArtifactsRequestBuilder
    from .groups.groups_request_builder import GroupsRequestBuilder
    from .versions.versions_request_builder import VersionsRequestBuilder

class SearchRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /search
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new SearchRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/search", path_parameters)
    
    @property
    def artifacts(self) -> ArtifactsRequestBuilder:
        """
        Search for artifacts in the registry.
        """
        from .artifacts.artifacts_request_builder import ArtifactsRequestBuilder

        return ArtifactsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def groups(self) -> GroupsRequestBuilder:
        """
        Search for groups in the registry.
        """
        from .groups.groups_request_builder import GroupsRequestBuilder

        return GroupsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def versions(self) -> VersionsRequestBuilder:
        """
        Search for versions in the registry.
        """
        from .versions.versions_request_builder import VersionsRequestBuilder

        return VersionsRequestBuilder(self.request_adapter, self.path_parameters)
    

