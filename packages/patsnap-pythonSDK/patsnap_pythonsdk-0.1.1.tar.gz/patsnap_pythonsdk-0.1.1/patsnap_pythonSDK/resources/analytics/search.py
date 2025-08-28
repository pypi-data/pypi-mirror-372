from __future__ import annotations

from typing import Optional, List

from ...http import HttpClient
from ...models.analytics.search import (
    AnalyticsQuerySearchCountRequest,
    SearchPatentCountResponse,
    AnalyticsQuerySearchRequest,
    SortField,
    AnalyticsQueryFilterRequest,
    PatentDataFieldResponse,
)
from ...models.search.patents import SearchPatentV2Response


class AnalyticsSearchResource:
    """Resource handler for analytics search operations."""
    
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client
    
    def query_count(
        self,
        *,
        query_text: str,
        collapse_order: Optional[str] = None,
        collapse_by: Optional[str] = None,
        collapse_order_authority: Optional[List[str]] = None,
        stemming: Optional[int] = None,
        collapse_type: Optional[str] = None,
    ) -> SearchPatentCountResponse:
        """
        Get total search patent count for analytics queries.
        
        Searches PatSnap's global patent database using standard text queries
        to get the total search patent count of different queries.
        
        Args:
            query_text: Analytics query, maximum length 1,500 characters
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST), 
                          valid only if collapse_by is APD or PBD
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order_authority: Order of patent collapse according to authorities 
                                    priority list, valid only if collapse_by is AUTHORITY
            stemming: Whether to turn on stemming function (1: on, 0: off). Default is 0
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            
        Returns:
            SearchPatentCountResponse: Response containing total search result count
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = AnalyticsSearchResource(http_client)
            >>> response = resource.query_count(
            ...     query_text="TACD: virtual reality",
            ...     collapse_by="PBD",
            ...     stemming=0
            ... )
            >>> print(f"Total results: {response.total_search_result_count}")
        """
        # Create and validate request
        request = AnalyticsQuerySearchCountRequest(
            query_text=query_text,
            collapse_order=collapse_order,
            collapse_by=collapse_by,
            collapse_order_authority=collapse_order_authority,
            stemming=stemming,
            collapse_type=collapse_type,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/query-search-count/v2", json=json_data)
        
        # Parse and return response
        return SearchPatentCountResponse(**response["data"])
    
    def query_search(
        self,
        *,
        query_text: str,
        offset: Optional[int] = None,
        sort: Optional[List[dict]] = None,
        collapse_order: Optional[str] = None,
        collapse_by: Optional[str] = None,
        collapse_order_authority: Optional[List[str]] = None,
        limit: Optional[int] = None,
        stemming: Optional[int] = None,
        collapse_type: Optional[str] = None,
    ) -> SearchPatentV2Response:
        """
        Search PatSnap's global patent database using analytics queries.
        
        Searches PatSnap's global patent database using standard text queries
        and returns actual patent data including patent numbers, titles, assignees, etc.
        
        Args:
            query_text: Analytics query, maximum length 1,500 characters
            offset: Offset value; limit + offset <= 20000 (max for Semantic Search is 1000)
            sort: Field order specifications as list of dicts with 'field' and 'order' keys
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST), 
                          valid only if collapse_by is APD or PBD
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order_authority: Order of patent collapse according to authorities 
                                    priority list, valid only if collapse_by is AUTHORITY
            limit: Limit of returned response; must be <= 1,000
            stemming: Whether to turn on stemming function (1: on, 0: off). Default is 0
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            
        Returns:
            SearchPatentV2Response: Response containing patent search results
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = AnalyticsSearchResource(http_client)
            >>> response = resource.query_search(
            ...     query_text="TACD: virtual reality",
            ...     limit=20,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(response.results)} patents")
        """
        # Convert sort dicts to SortField objects if provided
        sort_fields = None
        if sort:
            sort_fields = [SortField(**s) for s in sort]
        
        # Create and validate request
        request = AnalyticsQuerySearchRequest(
            query_text=query_text,
            offset=offset,
            sort=sort_fields,
            collapse_order=collapse_order,
            collapse_by=collapse_by,
            collapse_order_authority=collapse_order_authority,
            limit=limit,
            stemming=stemming,
            collapse_type=collapse_type,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Convert SortField objects back to dicts for JSON serialization
        if json_data.get("sort"):
            json_data["sort"] = [{"field": s.field, "order": s.order} for s in json_data["sort"]]
        
        # Make HTTP request
        response = self._http.post("/search/patent/query-search-patent/v2", json=json_data)
        
        # Parse and return response - handle both wrapped and direct response formats
        if "data" in response:
            # Response has data wrapper
            return SearchPatentV2Response(data=response["data"])
        else:
            # Response is direct data (no wrapper)
            return SearchPatentV2Response(data=response)
    
    def query_filter(
        self,
        *,
        query: str,
        field: str,
        offset: int,
        limit: Optional[int] = None,
        collapse_order: Optional[str] = None,
        collapse_by: Optional[str] = None,
        collapse_order_authority: Optional[List[str]] = None,
        stemming: Optional[int] = None,
        lang: Optional[str] = None,
        collapse_type: Optional[str] = None,
    ) -> List[PatentDataFieldResponse]:
        """
        Get aggregated statistical results of specified field dimensions.
        
        Receives aggregated statistical results of specified field dimensions
        according to the search results of the query. Supports Top200 statistical
        results at most, with single call returning Top100 at most.
        
        Args:
            query: Analytics query, maximum length 800 characters. Cannot contain 
                  complex wildcards like $W $PRE $WS $SEN $PARA $FREQ
            field: Filter field dimension code (up to 5 fields, comma-separated).
                  E.g., AUTHORITY, ASSIGNEE, PUBLICATION_YEAR, IPC, etc.
            offset: Offset value; 0 <= offset+limit <= 200
            limit: Number of statistical results to return (1-100, default: 50)
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order_authority: Order of patent collapse according to authorities priority
            stemming: Whether to turn on stemming function (1: on, 0: off)
            lang: Select language: cn, en, or jp (default: cn)
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            
        Returns:
            List[PatentDataFieldResponse]: List of field statistics responses
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = AnalyticsSearchResource(http_client)
            >>> results = resource.query_filter(
            ...     query="TTL:汽车",
            ...     field="ASSIGNEE",
            ...     offset=0,
            ...     limit=50
            ... )
            >>> for result in results:
            ...     for assignee in result.assignee:
            ...         print(f"{assignee.name}: {assignee.count}")
        """
        # Create and validate request
        request = AnalyticsQueryFilterRequest(
            query=query,
            field=field,
            offset=offset,
            limit=limit,
            collapse_order=collapse_order,
            collapse_by=collapse_by,
            collapse_order_authority=collapse_order_authority,
            stemming=stemming,
            lang=lang,
            collapse_type=collapse_type,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/query/v2", json=json_data)
        
        # Parse and return response - the API returns a list of objects
        results = []
        for item in response["data"]:
            results.append(PatentDataFieldResponse(**item))
        
        return results


__all__ = ["AnalyticsSearchResource"]
