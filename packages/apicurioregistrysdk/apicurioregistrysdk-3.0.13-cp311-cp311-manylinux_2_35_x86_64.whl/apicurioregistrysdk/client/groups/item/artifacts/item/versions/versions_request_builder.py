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
    from ......models.create_version import CreateVersion
    from ......models.problem_details import ProblemDetails
    from ......models.rule_violation_problem_details import RuleViolationProblemDetails
    from ......models.sort_order import SortOrder
    from ......models.version_meta_data import VersionMetaData
    from ......models.version_search_results import VersionSearchResults
    from ......models.version_sort_by import VersionSortBy
    from .item.with_version_expression_item_request_builder import WithVersionExpressionItemRequestBuilder

class VersionsRequestBuilder(BaseRequestBuilder):
    """
    Manage all the versions of an artifact in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new VersionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/groups/{groupId}/artifacts/{artifactId}/versions{?dryRun*,limit*,offset*,order*,orderby*}", path_parameters)
    
    def by_version_expression(self,version_expression: str) -> WithVersionExpressionItemRequestBuilder:
        """
        Manage a single version of a single artifact in the registry.
        param version_expression: An expression resolvable to a specific version ID within the given group and artifact. The following rules apply: - If the expression is in the form "branch={branchId}", and artifact branch {branchId} exists: The expression is resolved to a version that the branch points to. - Otherwise: The expression is resolved to a version with the same ID, which must follow the "[a-zA-Z0-9._//-+]{1,256}" pattern.
        Returns: WithVersionExpressionItemRequestBuilder
        """
        if version_expression is None:
            raise TypeError("version_expression cannot be null.")
        from .item.with_version_expression_item_request_builder import WithVersionExpressionItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["versionExpression"] = version_expression
        return WithVersionExpressionItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderGetQueryParameters]] = None) -> Optional[VersionSearchResults]:
        """
        Returns a list of all versions of the artifact.  The result set is paged.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VersionSearchResults]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.problem_details import ProblemDetails
        from ......models.rule_violation_problem_details import RuleViolationProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "404": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.version_search_results import VersionSearchResults

        return await self.request_adapter.send_async(request_info, VersionSearchResults, error_mapping)
    
    async def post(self,body: CreateVersion, request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderPostQueryParameters]] = None) -> Optional[VersionMetaData]:
        """
        Creates a new version of the artifact by uploading new content.  The configured rules forthe artifact are applied, and if they all pass, the new content is added as the most recent version of the artifact.  If any of the rules fail, an error is returned.The body of the request can be the raw content of the new artifact version, or the raw content and a set of references pointing to other artifacts, and the typeof that content should match the artifact's type (for example if the artifact type is `AVRO`then the content of the request should be an Apache Avro document).This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* An invalid version number was provided (HTTP error `400`)* No artifact with this `artifactId` exists (HTTP error `404`)* The new content violates one of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VersionMetaData]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ......models.problem_details import ProblemDetails
        from ......models.rule_violation_problem_details import RuleViolationProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "404": ProblemDetails,
            "409": RuleViolationProblemDetails,
            "422": ProblemDetails,
            "500": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.version_meta_data import VersionMetaData

        return await self.request_adapter.send_async(request_info, VersionMetaData, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a list of all versions of the artifact.  The result set is paged.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: CreateVersion, request_configuration: Optional[RequestConfiguration[VersionsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates a new version of the artifact by uploading new content.  The configured rules forthe artifact are applied, and if they all pass, the new content is added as the most recent version of the artifact.  If any of the rules fail, an error is returned.The body of the request can be the raw content of the new artifact version, or the raw content and a set of references pointing to other artifacts, and the typeof that content should match the artifact's type (for example if the artifact type is `AVRO`then the content of the request should be an Apache Avro document).This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* An invalid version number was provided (HTTP error `400`)* No artifact with this `artifactId` exists (HTTP error `404`)* The new content violates one of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)
        param body: The request body
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
    
    def with_url(self,raw_url: str) -> VersionsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: VersionsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return VersionsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class VersionsRequestBuilderGetQueryParameters():
        """
        Returns a list of all versions of the artifact.  The result set is paged.This operation can fail for the following reasons:* No artifact with this `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        """
        # The number of versions to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of versions to skip before starting to collect the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[SortOrder] = None

        # The field to sort by.  Can be one of:* `name`* `version`* `createdOn`
        orderby: Optional[VersionSortBy] = None

    
    @dataclass
    class VersionsRequestBuilderGetRequestConfiguration(RequestConfiguration[VersionsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class VersionsRequestBuilderPostQueryParameters():
        """
        Creates a new version of the artifact by uploading new content.  The configured rules forthe artifact are applied, and if they all pass, the new content is added as the most recent version of the artifact.  If any of the rules fail, an error is returned.The body of the request can be the raw content of the new artifact version, or the raw content and a set of references pointing to other artifacts, and the typeof that content should match the artifact's type (for example if the artifact type is `AVRO`then the content of the request should be an Apache Avro document).This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* An invalid version number was provided (HTTP error `400`)* No artifact with this `artifactId` exists (HTTP error `404`)* The new content violates one of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)
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
    class VersionsRequestBuilderPostRequestConfiguration(RequestConfiguration[VersionsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

