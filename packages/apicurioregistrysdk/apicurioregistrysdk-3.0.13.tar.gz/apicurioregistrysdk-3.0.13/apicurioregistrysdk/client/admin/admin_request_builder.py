from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .config.config_request_builder import ConfigRequestBuilder
    from .export.export_request_builder import ExportRequestBuilder
    from .import_.import_request_builder import ImportRequestBuilder
    from .role_mappings.role_mappings_request_builder import RoleMappingsRequestBuilder
    from .rules.rules_request_builder import RulesRequestBuilder
    from .snapshots.snapshots_request_builder import SnapshotsRequestBuilder

class AdminRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /admin
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new AdminRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/admin", path_parameters)
    
    @property
    def config(self) -> ConfigRequestBuilder:
        """
        The config property
        """
        from .config.config_request_builder import ConfigRequestBuilder

        return ConfigRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def export(self) -> ExportRequestBuilder:
        """
        Provides a way to export registry data.
        """
        from .export.export_request_builder import ExportRequestBuilder

        return ExportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def import_(self) -> ImportRequestBuilder:
        """
        Provides a way to import data into the registry.
        """
        from .import_.import_request_builder import ImportRequestBuilder

        return ImportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def role_mappings(self) -> RoleMappingsRequestBuilder:
        """
        Collection to manage role mappings for authenticated principals
        """
        from .role_mappings.role_mappings_request_builder import RoleMappingsRequestBuilder

        return RoleMappingsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def rules(self) -> RulesRequestBuilder:
        """
        Manage the global rules that apply to all artifacts if not otherwise configured.
        """
        from .rules.rules_request_builder import RulesRequestBuilder

        return RulesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def snapshots(self) -> SnapshotsRequestBuilder:
        """
        Triggers a snapshot of the Registry storage. Only supported in KafkaSQL storage
        """
        from .snapshots.snapshots_request_builder import SnapshotsRequestBuilder

        return SnapshotsRequestBuilder(self.request_adapter, self.path_parameters)
    

