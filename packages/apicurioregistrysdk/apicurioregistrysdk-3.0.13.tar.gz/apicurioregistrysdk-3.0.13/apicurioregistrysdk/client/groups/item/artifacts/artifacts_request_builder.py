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
    from ....models.artifact_search_results import ArtifactSearchResults
    from ....models.artifact_sort_by import ArtifactSortBy
    from ....models.create_artifact import CreateArtifact
    from ....models.create_artifact_response import CreateArtifactResponse
    from ....models.if_artifact_exists import IfArtifactExists
    from ....models.problem_details import ProblemDetails
    from ....models.rule_violation_problem_details import RuleViolationProblemDetails
    from ....models.sort_order import SortOrder
    from .item.with_artifact_item_request_builder import WithArtifactItemRequestBuilder

class ArtifactsRequestBuilder(BaseRequestBuilder):
    """
    Manage the collection of artifacts within a single group in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ArtifactsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/groups/{groupId}/artifacts{?canonical*,dryRun*,ifExists*,limit*,offset*,order*,orderby*}", path_parameters)
    
    def by_artifact_id(self,artifact_id: str) -> WithArtifactItemRequestBuilder:
        """
        Manage a single artifact.
        param artifact_id: The artifact ID.  Can be a string (client-provided) or UUID (server-generated), representing the unique artifact identifier. Must follow the ".{1,512}" pattern.
        Returns: WithArtifactItemRequestBuilder
        """
        if artifact_id is None:
            raise TypeError("artifact_id cannot be null.")
        from .item.with_artifact_item_request_builder import WithArtifactItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["artifactId"] = artifact_id
        return WithArtifactItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Deletes all of the artifacts that exist in a given group.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails
        from ....models.rule_violation_problem_details import RuleViolationProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ArtifactsRequestBuilderGetQueryParameters]] = None) -> Optional[ArtifactSearchResults]:
        """
        Returns a list of all artifacts in the group.  This list is paged.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ArtifactSearchResults]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails
        from ....models.rule_violation_problem_details import RuleViolationProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.artifact_search_results import ArtifactSearchResults

        return await self.request_adapter.send_async(request_info, ArtifactSearchResults, error_mapping)
    
    async def post(self,body: CreateArtifact, request_configuration: Optional[RequestConfiguration[ArtifactsRequestBuilderPostQueryParameters]] = None) -> Optional[CreateArtifactResponse]:
        """
        Creates a new artifact.  The body of the request should be a `CreateArtifact` object, which includes the metadata of the new artifact and, optionally, the metadata and content of the first version.If the artifact type is not provided, the registry attempts to figure out what kind of artifact is being added from thefollowing supported list:* Avro (`AVRO`)* Protobuf (`PROTOBUF`)* JSON Schema (`JSON`)* Kafka Connect (`KCONNECT`)* OpenAPI (`OPENAPI`)* AsyncAPI (`ASYNCAPI`)* GraphQL (`GRAPHQL`)* Web Services Description Language (`WSDL`)* XML Schema (`XSD`)An artifact will be created using the unique artifact ID that can optionally be provided in the request body.  If not provided in the request, the server willgenerate a unique ID for the artifact.  It is typically recommended that callersprovide the ID, because it is typically a meaningful identifier, and as suchfor most use cases should be supplied by the caller.If an artifact with the provided artifact ID already exists, the default behavioris for the server to reject the content with a 409 error.  However, the caller cansupply the `ifExists` query parameter to alter this default behavior. The `ifExists`query parameter can have one of the following values:* `FAIL` (*default*) - server rejects the content with a 409 error* `CREATE_VERSION` - server creates a new version of the existing artifact and returns it* `FIND_OR_CREATE_VERSION` - server returns an existing **version** that matches the provided content if such a version exists, otherwise a new version is createdThis operation may fail for one of the following reasons:* An invalid `ArtifactType` was indicated (HTTP error `400`)* No `ArtifactType` was indicated and the server could not determine one from the content (HTTP error `400`)* Provided content (request body) was empty (HTTP error `400`)* An invalid version number was used for the optional included first version (HTTP error `400`)* An artifact with the provided ID already exists (HTTP error `409`)* The content violates one of the configured global rules (HTTP error `409`)* A server error occurred (HTTP error `500`)Note that if the `dryRun` query parameter is set to `true`, then this operationwill not actually make any changes.  Instead it will succeed or fail based on whether it **would have worked**.  Use this option to, for example, check if anartifact is valid or if a new version passes configured compatibility checks.
        param body: Data sent when creating a new artifact.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[CreateArtifactResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ....models.problem_details import ProblemDetails
        from ....models.rule_violation_problem_details import RuleViolationProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "409": RuleViolationProblemDetails,
            "422": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.create_artifact_response import CreateArtifactResponse

        return await self.request_adapter.send_async(request_info, CreateArtifactResponse, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Deletes all of the artifacts that exist in a given group.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ArtifactsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a list of all artifacts in the group.  This list is paged.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: CreateArtifact, request_configuration: Optional[RequestConfiguration[ArtifactsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates a new artifact.  The body of the request should be a `CreateArtifact` object, which includes the metadata of the new artifact and, optionally, the metadata and content of the first version.If the artifact type is not provided, the registry attempts to figure out what kind of artifact is being added from thefollowing supported list:* Avro (`AVRO`)* Protobuf (`PROTOBUF`)* JSON Schema (`JSON`)* Kafka Connect (`KCONNECT`)* OpenAPI (`OPENAPI`)* AsyncAPI (`ASYNCAPI`)* GraphQL (`GRAPHQL`)* Web Services Description Language (`WSDL`)* XML Schema (`XSD`)An artifact will be created using the unique artifact ID that can optionally be provided in the request body.  If not provided in the request, the server willgenerate a unique ID for the artifact.  It is typically recommended that callersprovide the ID, because it is typically a meaningful identifier, and as suchfor most use cases should be supplied by the caller.If an artifact with the provided artifact ID already exists, the default behavioris for the server to reject the content with a 409 error.  However, the caller cansupply the `ifExists` query parameter to alter this default behavior. The `ifExists`query parameter can have one of the following values:* `FAIL` (*default*) - server rejects the content with a 409 error* `CREATE_VERSION` - server creates a new version of the existing artifact and returns it* `FIND_OR_CREATE_VERSION` - server returns an existing **version** that matches the provided content if such a version exists, otherwise a new version is createdThis operation may fail for one of the following reasons:* An invalid `ArtifactType` was indicated (HTTP error `400`)* No `ArtifactType` was indicated and the server could not determine one from the content (HTTP error `400`)* Provided content (request body) was empty (HTTP error `400`)* An invalid version number was used for the optional included first version (HTTP error `400`)* An artifact with the provided ID already exists (HTTP error `409`)* The content violates one of the configured global rules (HTTP error `409`)* A server error occurred (HTTP error `500`)Note that if the `dryRun` query parameter is set to `true`, then this operationwill not actually make any changes.  Instead it will succeed or fail based on whether it **would have worked**.  Use this option to, for example, check if anartifact is valid or if a new version passes configured compatibility checks.
        param body: Data sent when creating a new artifact.
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
    
    def with_url(self,raw_url: str) -> ArtifactsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ArtifactsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ArtifactsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ArtifactsRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ArtifactsRequestBuilderGetQueryParameters():
        """
        Returns a list of all artifacts in the group.  This list is paged.
        """
        # The number of artifacts to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of artifacts to skip before starting the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[SortOrder] = None

        # The field to sort by.  Can be one of:* `name`* `createdOn`
        orderby: Optional[ArtifactSortBy] = None

    
    @dataclass
    class ArtifactsRequestBuilderGetRequestConfiguration(RequestConfiguration[ArtifactsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ArtifactsRequestBuilderPostQueryParameters():
        """
        Creates a new artifact.  The body of the request should be a `CreateArtifact` object, which includes the metadata of the new artifact and, optionally, the metadata and content of the first version.If the artifact type is not provided, the registry attempts to figure out what kind of artifact is being added from thefollowing supported list:* Avro (`AVRO`)* Protobuf (`PROTOBUF`)* JSON Schema (`JSON`)* Kafka Connect (`KCONNECT`)* OpenAPI (`OPENAPI`)* AsyncAPI (`ASYNCAPI`)* GraphQL (`GRAPHQL`)* Web Services Description Language (`WSDL`)* XML Schema (`XSD`)An artifact will be created using the unique artifact ID that can optionally be provided in the request body.  If not provided in the request, the server willgenerate a unique ID for the artifact.  It is typically recommended that callersprovide the ID, because it is typically a meaningful identifier, and as suchfor most use cases should be supplied by the caller.If an artifact with the provided artifact ID already exists, the default behavioris for the server to reject the content with a 409 error.  However, the caller cansupply the `ifExists` query parameter to alter this default behavior. The `ifExists`query parameter can have one of the following values:* `FAIL` (*default*) - server rejects the content with a 409 error* `CREATE_VERSION` - server creates a new version of the existing artifact and returns it* `FIND_OR_CREATE_VERSION` - server returns an existing **version** that matches the provided content if such a version exists, otherwise a new version is createdThis operation may fail for one of the following reasons:* An invalid `ArtifactType` was indicated (HTTP error `400`)* No `ArtifactType` was indicated and the server could not determine one from the content (HTTP error `400`)* Provided content (request body) was empty (HTTP error `400`)* An invalid version number was used for the optional included first version (HTTP error `400`)* An artifact with the provided ID already exists (HTTP error `409`)* The content violates one of the configured global rules (HTTP error `409`)* A server error occurred (HTTP error `500`)Note that if the `dryRun` query parameter is set to `true`, then this operationwill not actually make any changes.  Instead it will succeed or fail based on whether it **would have worked**.  Use this option to, for example, check if anartifact is valid or if a new version passes configured compatibility checks.
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
            if original_name == "if_exists":
                return "ifExists"
            if original_name == "canonical":
                return "canonical"
            return original_name
        
        # Used only when the `ifExists` query parameter is set to `RETURN_OR_UPDATE`, this parameter can be set to `true` to indicate that the server should "canonicalize" the content when searching for a matching version.  The canonicalization algorithm is unique to each artifact type, but typically involves removing extra whitespace and formatting the content in a consistent manner.
        canonical: Optional[bool] = None

        # When set to `true`, the operation will not result in any changes. Instead, itwill return a result based on whether the operation **would have succeeded**.
        dry_run: Optional[bool] = None

        # Set this option to instruct the server on what to do if the artifact already exists.
        if_exists: Optional[IfArtifactExists] = None

    
    @dataclass
    class ArtifactsRequestBuilderPostRequestConfiguration(RequestConfiguration[ArtifactsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

