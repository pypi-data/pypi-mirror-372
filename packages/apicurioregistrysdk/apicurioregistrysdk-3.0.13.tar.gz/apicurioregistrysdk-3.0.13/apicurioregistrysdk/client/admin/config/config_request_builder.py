from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .artifact_types.artifact_types_request_builder import ArtifactTypesRequestBuilder
    from .properties.properties_request_builder import PropertiesRequestBuilder

class ConfigRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /admin/config
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ConfigRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/admin/config", path_parameters)
    
    @property
    def artifact_types(self) -> ArtifactTypesRequestBuilder:
        """
        The list of artifact types supported by this instance of Registry.
        """
        from .artifact_types.artifact_types_request_builder import ArtifactTypesRequestBuilder

        return ArtifactTypesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def properties(self) -> PropertiesRequestBuilder:
        """
        Manage configuration properties.
        """
        from .properties.properties_request_builder import PropertiesRequestBuilder

        return PropertiesRequestBuilder(self.request_adapter, self.path_parameters)
    

