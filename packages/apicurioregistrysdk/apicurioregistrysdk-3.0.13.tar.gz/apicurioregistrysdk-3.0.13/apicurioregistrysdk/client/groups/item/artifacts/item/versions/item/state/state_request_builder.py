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
    from ........models.problem_details import ProblemDetails
    from ........models.wrapped_version_state import WrappedVersionState

class StateRequestBuilder(BaseRequestBuilder):
    """
    Manage the state of an artifact version.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new StateRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/groups/{groupId}/artifacts/{artifactId}/versions/{versionExpression}/state{?dryRun*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[WrappedVersionState]:
        """
        Gets the current state of an artifact version.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[WrappedVersionState]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ........models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "404": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ........models.wrapped_version_state import WrappedVersionState

        return await self.request_adapter.send_async(request_info, WrappedVersionState, error_mapping)
    
    async def put(self,body: WrappedVersionState, request_configuration: Optional[RequestConfiguration[StateRequestBuilderPutQueryParameters]] = None) -> None:
        """
        Updates the state of an artifact version.NOTE: There are some restrictions on state transitions.  Notably a version cannot be transitioned to the `DRAFT` state from any other state.  The `DRAFT` state can only be entered (optionally) when creating a new artifact/version.A version in `DRAFT` state can only be transitioned to `ENABLED`.  When thishappens, any configured content rules will be applied.  This may result in afailure to change the state.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* An invalid new state was provided (HTTP error `400`)* The draft content violates one or more of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ........models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "404": ProblemDetails,
            "409": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Gets the current state of an artifact version.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: WrappedVersionState, request_configuration: Optional[RequestConfiguration[StateRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Updates the state of an artifact version.NOTE: There are some restrictions on state transitions.  Notably a version cannot be transitioned to the `DRAFT` state from any other state.  The `DRAFT` state can only be entered (optionally) when creating a new artifact/version.A version in `DRAFT` state can only be transitioned to `ENABLED`.  When thishappens, any configured content rules will be applied.  This may result in afailure to change the state.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* An invalid new state was provided (HTTP error `400`)* The draft content violates one or more of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> StateRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: StateRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return StateRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class StateRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class StateRequestBuilderPutQueryParameters():
        """
        Updates the state of an artifact version.NOTE: There are some restrictions on state transitions.  Notably a version cannot be transitioned to the `DRAFT` state from any other state.  The `DRAFT` state can only be entered (optionally) when creating a new artifact/version.A version in `DRAFT` state can only be transitioned to `ENABLED`.  When thishappens, any configured content rules will be applied.  This may result in afailure to change the state.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* No version with this `version` exists (HTTP error `404`)* An invalid new state was provided (HTTP error `400`)* The draft content violates one or more of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "dry_run":
                return "dryRun"
            return original_name
        
        # When set to `true`, the operation will not result in any changes. Instead, itwill return a result based on whether the operation **would have succeeded**.
        dry_run: Optional[bool] = None

    
    @dataclass
    class StateRequestBuilderPutRequestConfiguration(RequestConfiguration[StateRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

