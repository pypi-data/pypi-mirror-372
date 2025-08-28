from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalyticsQuerySearchCountRequest(BaseModel):
    """Request model for analytics query search count.
    
    This endpoint searches PatSnap's global patent database using standard text queries
    to get the total search patent count of different queries.
    
    Example:
        >>> request = AnalyticsQuerySearchCountRequest(
        ...     query_text="TACD: virtual reality",
        ...     collapse_by="PBD",
        ...     stemming=0
        ... )
    """
    
    query_text: str = Field(
        description="Analytics query, maximum length 1,500 characters",
        max_length=1500
    )
    collapse_order: Optional[str] = Field(
        default=None,
        description="Patent collapse ordering rule (OLDEST or LATEST), valid only if collapse_by is APD or PBD"
    )
    collapse_by: Optional[str] = Field(
        default=None,
        description="Sort field for patent collapse: APD (application date), PBD (publication date), AUTHORITY, or SCORE"
    )
    collapse_order_authority: Optional[List[str]] = Field(
        default=None,
        description="Order of patent collapse according to authorities priority list, valid only if collapse_by is AUTHORITY"
    )
    stemming: Optional[int] = Field(
        default=0,
        description="Whether to turn on stemming function: 1 (on) or 0 (off). Default is 0"
    )
    collapse_type: Optional[str] = Field(
        default=None,
        description="Collapse type: ALL (no collapse), APNO (by application number), DOCDB (simple family), INPADOC (inpadoc family), EXTEND (patsnap family)"
    )


class SearchPatentCountResponse(BaseModel):
    """Response model for analytics query search count.
    
    Example:
        >>> response = SearchPatentCountResponse(
        ...     total_search_result_count=1000
        ... )
    """
    
    total_search_result_count: int = Field(
        description="Total search result count"
    )
    
    @property
    def patent_count(self) -> int:
        """Alias for total_search_result_count for backward compatibility"""
        return self.total_search_result_count


class SortField(BaseModel):
    """Sort field specification for analytics query search."""
    
    field: str = Field(
        description="Field to sort by: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE"
    )
    order: str = Field(
        description="Sort order: DESC or ASC"
    )


class AnalyticsQuerySearchRequest(BaseModel):
    """Request model for analytics query search.
    
    This endpoint searches PatSnap's global patent database using standard text queries
    and returns actual patent data including patent numbers, titles, assignees, etc.
    
    Example:
        >>> request = AnalyticsQuerySearchRequest(
        ...     query_text="TACD: virtual reality",
        ...     limit=20,
        ...     sort=[{"field": "SCORE", "order": "DESC"}]
        ... )
    """
    
    query_text: str = Field(
        description="Analytics query, maximum length 1,500 characters",
        max_length=1500
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset value; limit + offset <= 20000 (max for Semantic Search is 1000)"
    )
    sort: Optional[List[SortField]] = Field(
        default=None,
        description="Field order specifications. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE"
    )
    collapse_order: Optional[str] = Field(
        default=None,
        description="Patent collapse ordering rule (OLDEST or LATEST), valid only if collapse_by is APD or PBD"
    )
    collapse_by: Optional[str] = Field(
        default=None,
        description="Sort field for patent collapse: APD (application date), PBD (publication date), AUTHORITY, or SCORE"
    )
    collapse_order_authority: Optional[List[str]] = Field(
        default=None,
        description="Order of patent collapse according to authorities priority list, valid only if collapse_by is AUTHORITY"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Limit of returned response; must be <= 1,000"
    )
    stemming: Optional[int] = Field(
        default=0,
        description="Whether to turn on stemming function: 1 (on) or 0 (off). Default is 0"
    )
    collapse_type: Optional[str] = Field(
        default=None,
        description="Collapse type: ALL (no collapse), APNO (by application number), DOCDB (simple family), INPADOC (inpadoc family), EXTEND (patsnap family)"
    )


class AnalyticsQueryFilterRequest(BaseModel):
    """Request model for analytics query search and filter.
    
    This endpoint receives aggregated statistical results of specified field dimensions
    according to the search results of the query.
    
    Example:
        >>> request = AnalyticsQueryFilterRequest(
        ...     query="TTL:汽车",
        ...     field="ASSIGNEE",
        ...     limit=50,
        ...     offset=0
        ... )
    """
    
    query: str = Field(
        description="Analytics query, maximum length 800 characters. Cannot contain complex wildcards like $W $PRE $WS $SEN $PARA $FREQ",
        max_length=800
    )
    field: str = Field(
        description="Filter field dimension code (up to 5 fields, comma-separated). E.g., AUTHORITY, ASSIGNEE, PUBLICATION_YEAR, IPC, etc."
    )
    offset: int = Field(
        ge=0,
        description="Offset value; 0 <= offset+limit <= 200"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of statistical results to return (1-100, default: 50)"
    )
    collapse_order: Optional[str] = Field(
        default=None,
        description="Patent collapse ordering rule (OLDEST or LATEST), valid when collapse_type=APNO and collapse_by=APD/PBD"
    )
    collapse_by: Optional[str] = Field(
        default=None,
        description="Sort field for patent collapse: APD (application date), PBD (publication date), AUTHORITY, or SCORE"
    )
    collapse_order_authority: Optional[List[str]] = Field(
        default=None,
        description="Order of patent collapse according to authorities priority list, valid only if collapse_by is AUTHORITY"
    )
    stemming: Optional[int] = Field(
        default=0,
        description="Whether to turn on stemming function: 1 (on) or 0 (off). Default is 0"
    )
    lang: Optional[str] = Field(
        default="cn",
        description="Select language: cn, en, or jp. Default is cn"
    )
    collapse_type: Optional[str] = Field(
        default=None,
        description="Collapse type: ALL (no collapse), APNO (by application number), DOCDB (simple family), INPADOC (inpadoc family), EXTEND (patsnap family)"
    )


class SearchPatentFieldResponse(BaseModel):
    """Individual field statistic response item."""
    
    name: str = Field(description="Field value name")
    count: int = Field(description="Count for this field value")


class PatentDataFieldResponse(BaseModel):
    """Response model for analytics query search and filter.
    
    The response structure is dynamic based on the requested field.
    Common field names include: assignee, authority, publication_year, etc.
    
    Example:
        >>> response = PatentDataFieldResponse(
        ...     assignee=[
        ...         {"name": "APPLE INC.", "count": 2509},
        ...         {"name": "GOOGLE LLC", "count": 1834}
        ...     ]
        ... )
    """
    
    # Dynamic fields based on the requested field parameter
    # We'll use a flexible approach to handle different field types
    def __init__(self, **data):
        # Handle dynamic field names by storing all data
        super().__init__()
        for key, value in data.items():
            if isinstance(value, list):
                # Convert list of dicts to SearchPatentFieldResponse objects
                setattr(self, key, [SearchPatentFieldResponse(**item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)
    
    class Config:
        extra = "allow"  # Allow additional fields


__all__ = [
    "AnalyticsQuerySearchCountRequest",
    "SearchPatentCountResponse",
    "SortField",
    "AnalyticsQuerySearchRequest",
    "AnalyticsQueryFilterRequest",
    "SearchPatentFieldResponse",
    "PatentDataFieldResponse",
]
