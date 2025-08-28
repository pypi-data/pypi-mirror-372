from __future__ import annotations

from ..http import HttpClient
from ..resources.analytics import AnalyticsSearchResource


class AnalyticsNamespace:
    """Analytics namespace for analytics-related operations."""
    
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client
        # Initialize search resources under analytics
        self._search = AnalyticsSearchNamespace(http_client)
    
    @property
    def search(self) -> AnalyticsSearchNamespace:
        """Access analytics search operations."""
        return self._search


class AnalyticsSearchNamespace:
    """Analytics search operations."""
    
    def __init__(self, http_client: HttpClient) -> None:
        self._analytics_search = AnalyticsSearchResource(http_client)
    
    def query_count(self, **kwargs):
        """Get total search patent count for analytics queries.
        
        Searches PatSnap's global patent database using standard text queries
        to get the total search patent count of different queries.
        
        Args:
            query_text: Analytics query, maximum length 1,500 characters
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order_authority: Order of patent collapse according to authorities priority
            stemming: Whether to turn on stemming function (1: on, 0: off)
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            **kwargs: Additional parameters
            
        Returns:
            SearchPatentCountResponse: Response containing total search result count
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> count = patsnap.analytics.search.query_count(
            ...     query_text="TACD: virtual reality",
            ...     collapse_by="PBD",
            ...     stemming=0
            ... )
            >>> print(f"Total results: {count.total_search_result_count}")
        """
        return self._analytics_search.query_count(**kwargs)
    
    def query_search(self, **kwargs):
        """Search PatSnap's global patent database using analytics queries.
        
        Searches PatSnap's global patent database using standard text queries
        and returns actual patent data including patent numbers, titles, assignees, etc.
        
        Args:
            query_text: Analytics query, maximum length 1,500 characters
            offset: Offset value; limit + offset <= 20000 (max for Semantic Search is 1000)
            sort: Field order specifications as list of dicts with 'field' and 'order' keys
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order_authority: Order of patent collapse according to authorities priority
            limit: Limit of returned response; must be <= 1,000
            stemming: Whether to turn on stemming function (1: on, 0: off)
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            **kwargs: Additional parameters
            
        Returns:
            SearchPatentV2Response: Response containing patent search results
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> results = patsnap.analytics.search.query_search(
            ...     query_text="TACD: virtual reality",
            ...     limit=20,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        return self._analytics_search.query_search(**kwargs)
    
    def query_filter(self, **kwargs):
        """Get aggregated statistical results of specified field dimensions.
        
        Receives aggregated statistical results of specified field dimensions
        according to the search results of the query. Supports Top200 statistical
        results at most, with single call returning Top100 at most.
        
        Args:
            query: Analytics query, maximum length 800 characters
            field: Filter field dimension code (AUTHORITY, ASSIGNEE, PUBLICATION_YEAR, etc.)
            offset: Offset value; 0 <= offset+limit <= 200
            limit: Number of statistical results to return (1-100, default: 50)
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order_authority: Order of patent collapse according to authorities priority
            stemming: Whether to turn on stemming function (1: on, 0: off)
            lang: Select language: cn, en, or jp (default: cn)
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            **kwargs: Additional parameters
            
        Returns:
            List[PatentDataFieldResponse]: List of field statistics responses
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> results = patsnap.analytics.search.query_filter(
            ...     query="TTL:汽车",
            ...     field="ASSIGNEE",
            ...     offset=0,
            ...     limit=20
            ... )
            >>> for result in results:
            ...     for assignee in result.assignee:
            ...         print(f"{assignee.name}: {assignee.count:,}")
        """
        return self._analytics_search.query_filter(**kwargs)
