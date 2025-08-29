from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .info.info_request_builder import InfoRequestBuilder
    from .ui_config.ui_config_request_builder import UiConfigRequestBuilder

class SystemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /system
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new SystemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/system", path_parameters)
    
    @property
    def info(self) -> InfoRequestBuilder:
        """
        Retrieve system information
        """
        from .info.info_request_builder import InfoRequestBuilder

        return InfoRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def ui_config(self) -> UiConfigRequestBuilder:
        """
        This endpoint is used by the user interface to retrieve UI specific configurationin a JSON payload.  This allows the UI and the backend to be configured in the same place (the backend process/pod).  When the UI loads, it will make an API callto this endpoint to determine what UI features and options are configured.
        """
        from .ui_config.ui_config_request_builder import UiConfigRequestBuilder

        return UiConfigRequestBuilder(self.request_adapter, self.path_parameters)
    

