from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PatentSearchPnRequest(BaseModel):
    pn: Optional[str] = Field(default=None, description="Patent number")
    apno: Optional[str] = Field(default=None, description="Application number")
    authority: Optional[List[str]] = Field(default=None, description="Authorities list, e.g. ['US','CN']")
    offset: Optional[int] = Field(default=None, ge=0, description="Offset, default 0")
    limit: Optional[int] = Field(default=None, ge=1, le=1000, description="Limit, default 10, max 1000")


class PatentBaseV2Response(BaseModel):
    pn: str = Field(description="Patent number")
    apdt: int = Field(description="Application date (YYYYMMDD format)")
    apno: str = Field(description="Application number")
    pbdt: int = Field(description="Publication date (YYYYMMDD format)")
    title: str = Field(description="Patent title")
    inventor: str = Field(description="Inventor name(s)")
    patent_id: str = Field(description="Unique patent identifier")
    current_assignee: str = Field(description="Current patent assignee")
    original_assignee: str = Field(description="Original patent assignee")


class SearchPatentV2ResponseData(BaseModel):
    """Data section of SearchPatentV2Response"""
    results: List[PatentBaseV2Response] = Field(description="List of patent search results")
    result_count: int = Field(description="Number of results in this response")
    total_search_result_count: int = Field(description="Total number of available results")

class SearchPatentV2Response(BaseModel):
    """Complete response wrapper for patent search V2"""
    data: SearchPatentV2ResponseData = Field(description="Response data containing results")


class CompanySearchRequest(BaseModel):
    """Request model for original applicant/assignee search.
    
    Searches for patents by standardized original assignee (applicant) names.
    Supports up to 100 companies with OR logic.
    
    Example:
        >>> request = CompanySearchRequest(
        ...     application="Apple, Inc.",
        ...     limit=50,
        ...     sort=[{"field": "SCORE", "order": "DESC"}]
        ... )
    """
    
    application: str = Field(
        description="Standardized Original Assignee (Applicant) name. Up to 100 companies can be searched; multiple companies separated by ' OR ', e.g. 'Apple OR Huawei'"
    )
    collapse_type: Optional[str] = Field(
        default=None,
        description="Collapse type: ALL (no collapse), APNO (by application number), DOCDB (simple family), INPADOC (inpadoc family), EXTEND (patsnap family)"
    )
    collapse_by: Optional[str] = Field(
        default=None,
        description="Sort field for patent collapse: APD (application date), PBD (publication date), AUTHORITY, SCORE"
    )
    collapse_order: Optional[str] = Field(
        default=None,
        description="Patent collapse ordering rule (OLDEST or LATEST), valid only if collapse_by is APD or PBD"
    )
    collapse_order_authority: Optional[List[str]] = Field(
        default=None,
        description="Order of patent collapse according to authorities priority list, valid only if collapse_by is AUTHORITY"
    )
    sort: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Field order. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE. Orders: desc, asc"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Limit of returned response; must be <= 1,000"
    )


class CurrentAssigneeSearchRequest(BaseModel):
    """Request model for current assignee search.
    
    Searches for patents by standardized current assignee names.
    Supports up to 100 companies with OR logic.
    
    Example:
        >>> request = CurrentAssigneeSearchRequest(
        ...     assignee="Apple, Inc.",
        ...     limit=50,
        ...     sort=[{"field": "SCORE", "order": "DESC"}]
        ... )
    """
    
    assignee: str = Field(
        description="Standardized Current Assignee name. Up to 100 companies can be searched; multiple companies separated by ' OR ', e.g. 'Apple OR Huawei'"
    )
    collapse_type: Optional[str] = Field(
        default=None,
        description="Collapse type: ALL (no collapse), APNO (by application number), DOCDB (simple family), INPADOC (inpadoc family), EXTEND (patsnap family)"
    )
    collapse_by: Optional[str] = Field(
        default=None,
        description="Sort field for patent collapse: APD (application date), PBD (publication date), AUTHORITY, SCORE"
    )
    collapse_order: Optional[str] = Field(
        default=None,
        description="Patent collapse ordering rule (OLDEST or LATEST), valid only if collapse_by is APD or PBD"
    )
    collapse_order_authority: Optional[List[str]] = Field(
        default=None,
        description="Order of patent collapse according to authorities priority list, valid only if collapse_by is AUTHORITY"
    )
    sort: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Field order. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE. Orders: desc, asc"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Limit of returned response; must be <= 1,000"
    )


class DefensePatentSearchRequest(BaseModel):
    """Request model for defense patent search.
    
    Searches for defense/military patents by applicant names.
    Supports up to 100 companies with OR logic.
    
    Example:
        >>> request = DefensePatentSearchRequest(
        ...     application="Lockheed Martin Corporation",
        ...     limit=50,
        ...     sort=[{"field": "SCORE", "order": "DESC"}]
        ... )
    """
    
    application: str = Field(
        description="Applicant name for defense patents. Up to 100 companies can be searched; multiple companies separated by ' OR ', e.g. 'Lockheed Martin Corporation OR Boeing Company'"
    )
    collapse_type: Optional[str] = Field(
        default=None,
        description="Collapse type: ALL (no collapse), APNO (by application number), DOCDB (simple family), INPADOC (inpadoc family), EXTEND (patsnap family)"
    )
    collapse_by: Optional[str] = Field(
        default=None,
        description="Sort field for patent collapse: APD (application date), PBD (publication date), AUTHORITY, SCORE"
    )
    collapse_order: Optional[str] = Field(
        default=None,
        description="Patent collapse ordering rule (OLDEST or LATEST), valid only if collapse_by is APD or PBD"
    )
    collapse_order_authority: Optional[List[str]] = Field(
        default=None,
        description="Order of patent collapse according to authorities priority list, valid only if collapse_by is AUTHORITY"
    )
    sort: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Field order. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE. Orders: desc, asc"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Limit of returned response; must be <= 1,000"
    )


class SimilarPatentSearchRequest(BaseModel):
    """Request model for similar patent search.
    
    Searches for patents similar to a given patent by ID or number.
    Patent ID is preferred when both are provided. Maximum 1000 results.
    
    Example:
        >>> request = SimilarPatentSearchRequest(
        ...     patent_id="b053642f-3108-4ea9-b629-420b0ab959e3",
        ...     limit=50,
        ...     relevancy="70%"
        ... )
    """
    
    patent_id: Optional[str] = Field(
        default=None,
        description="Patent ID (preferred when both patent_id and patent_number are provided)"
    )
    patent_number: Optional[str] = Field(
        default=None,
        description="Patent number (used if patent_id is not provided)"
    )
    country: Optional[List[str]] = Field(
        default=None,
        description="Authority and kind code (e.g., ['CNA', 'CNB']). Authority codes from https://analytics.patsnap.com/status"
    )
    pbd_from: Optional[str] = Field(
        default=None,
        description="Start year of publication date (format: YYYYMMDD)"
    )
    pbd_to: Optional[str] = Field(
        default=None,
        description="End year of publication date (format: YYYYMMDD)"
    )
    apd_from: Optional[str] = Field(
        default=None,
        description="Start year of application date (format: YYYYMMDD)"
    )
    apd_to: Optional[str] = Field(
        default=None,
        description="End year of application date (format: YYYYMMDD)"
    )
    relevancy: Optional[str] = Field(
        default=None,
        description="Minimum relevancy threshold (e.g., '50%', '70%')"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Limit of returned response; must be <= 1,000"
    )


class SemanticResult(BaseModel):
    """Individual semantic search result with relevancy score."""
    
    pn: str = Field(description="Patent number")
    apdt: int = Field(description="Application date")
    apno: str = Field(description="Application number")
    pbdt: int = Field(description="Publication date")
    title: str = Field(description="Patent title")
    inventor: str = Field(description="Inventor names")
    patent_id: str = Field(description="Patent ID")
    relevancy: str = Field(description="Relevancy percentage between result patent and input content")
    current_assignee: str = Field(description="Current assignee")
    original_assignee: str = Field(description="Original assignee (applicant)")


class SearchComputeV2ResponseData(BaseModel):
    """Data section of SearchComputeV2Response"""
    results: List[SemanticResult] = Field(description="List of similar patent results")
    result_count: int = Field(description="Number of results in this response")
    total_search_result_count: int = Field(description="Total number of available results")

class SearchComputeV2Response(BaseModel):
    """Complete response wrapper for similar patent search."""
    data: SearchComputeV2ResponseData = Field(description="Response data containing results")


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search using technical text.
    
    Searches for patents using semantic analysis of technical descriptions.
    Recommended to use >200 words for best results. Maximum 1000 results.
    
    Example:
        >>> request = SemanticSearchRequest(
        ...     text="The invention discloses an automobile front-view based wireless video transmission system...",
        ...     limit=50,
        ...     relevancy="60%"
        ... )
    """
    
    text: str = Field(
        description="Semantic query text (technical description, abstract, etc.). Recommend >200 words for best results"
    )
    country: Optional[List[str]] = Field(
        default=None,
        description="Authority and kind code (e.g., ['CNA', 'CNB']). Authority codes from https://analytics.patsnap.com/status"
    )
    pbd_from: Optional[str] = Field(
        default=None,
        description="Start year of publication date (format: YYYYMMDD)"
    )
    pbd_to: Optional[str] = Field(
        default=None,
        description="End year of publication date (format: YYYYMMDD)"
    )
    apd_from: Optional[str] = Field(
        default=None,
        description="Start year of application date (format: YYYYMMDD)"
    )
    apd_to: Optional[str] = Field(
        default=None,
        description="End year of application date (format: YYYYMMDD)"
    )
    relevancy: Optional[str] = Field(
        default=None,
        description="Minimum relevancy threshold (e.g., '50%', '70%')"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Limit of returned response; must be <= 1,000"
    )


class FileUrlResponse(BaseModel):
    """Response model for image upload with public URL."""
    
    url: str = Field(description="Public URL for the uploaded image")
    expire: int = Field(description="URL expiration time in seconds (typically 32400 = 9 hours)")


class ImageSearchSingleRequest(BaseModel):
    """Request model for single image patent search.
    
    Searches for design patents or utility patents using image similarity.
    Supports both design patents (D) and utility models (U) with different
    search models optimized for each type.
    
    Example:
        >>> request = ImageSearchSingleRequest(
        ...     url="https://example.com/patent_image.jpg",
        ...     patent_type="D",
        ...     model=1,
        ...     limit=50
        ... )
    """
    
    url: str = Field(description="Image URL for similarity search")
    patent_type: str = Field(description="Patent type: 'D' for Design patents, 'U' for Utility models")
    model: int = Field(description="Search model: Design(1=Smart Recommendation, 2=Image Search), Utility(3=Shape only, 4=Shape & color)")
    
    # Optional filtering parameters
    apply_start_time: Optional[str] = Field(default=None, description="Patent apply date from (format: YYYYMMDD)")
    apply_end_time: Optional[str] = Field(default=None, description="Patent apply date to (format: YYYYMMDD)")
    public_start_time: Optional[str] = Field(default=None, description="Patent publication date from (format: YYYYMMDD)")
    public_end_time: Optional[str] = Field(default=None, description="Patent publication date to (format: YYYYMMDD)")
    
    assignees: Optional[str] = Field(default=None, description="All assignees filter")
    country: Optional[List[str]] = Field(default=None, description="Patent authority codes (e.g., ['US', 'EU', 'CN'])")
    
    # Search parameters
    field: Optional[str] = Field(default="SCORE", description="Field sort: SCORE, APD, PBD, ISD (default: SCORE)")
    order: Optional[str] = Field(default="desc", description="Order: desc, asc (default: desc)")
    limit: Optional[int] = Field(default=10, ge=1, le=100, description="Number of patents to return (1-100, default: 10)")
    offset: Optional[int] = Field(default=0, ge=0, le=1000, description="Offset for pagination (0-1000, default: 0)")
    
    # Language and display options
    lang: Optional[str] = Field(default="original", description="Language preference: original, cn, en (default: original)")
    is_https: Optional[int] = Field(default=0, description="Return https images: 1=https, 0=http (default: 0)")
    include_machine_translation: Optional[bool] = Field(default=None, description="Include machine translations")
    
    # Legal status filters
    legal_status: Optional[str] = Field(default=None, description="Patent legal status (comma-separated)")
    simple_legal_status: Optional[str] = Field(default=None, description="Simple legal status: 0=Inactive, 1=Active, 2=Pending")
    
    # Advanced search options
    main_field: Optional[str] = Field(default=None, description="Main field search (title, abstract, claims, etc.)")
    loc: Optional[str] = Field(default=None, description="LOC classification for Industrial Designs")
    stemming: Optional[int] = Field(default=0, description="Stemming function: 1=on, 0=off (default: 0)")
    pre_filter: Optional[int] = Field(default=1, description="Pre-filter function: 1=on, 0=off (default: 1)")


class PatentMessage(BaseModel):
    """Individual patent result from image search."""
    
    url: str = Field(description="Similar image URL")
    apdt: int = Field(description="Application date")
    apno: str = Field(description="Application number")
    pbdt: int = Field(description="Publication date")
    title: str = Field(description="Patent title")
    inventor: str = Field(description="Inventor names")
    patent_id: str = Field(description="Patent ID")
    patent_pn: str = Field(description="Patent number")
    current_assignee: str = Field(description="Current assignee")
    original_assignee: str = Field(description="Original assignee (applicant)")
    score: Optional[float] = Field(default=None, description="Similarity score (when sorted by SCORE)")
    loc_match: Optional[int] = Field(default=None, description="LOC match indicator: 1=hit, 0=miss")


class ImageSearchResponse(BaseModel):
    """Response model for image-based patent search."""
    
    patent_messages: List[PatentMessage] = Field(description="List of similar patent results")
    total_search_result_count: int = Field(description="Total number of search results")


class ImageSearchMultipleRequest(BaseModel):
    """Request model for multiple image patent search.
    
    Searches for design patents or utility patents using up to 4 images simultaneously.
    The Smart Recommendation model (model=1) uses the first image for LOC prediction
    and reorders results, so image order affects search results.
    
    Example:
        >>> request = ImageSearchMultipleRequest(
        ...     urls=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        ...     patent_type="D",
        ...     model=1,
        ...     limit=50
        ... )
    """
    
    urls: List[str] = Field(min_items=1, max_items=4, description="List of image URLs (1-4 images)")
    patent_type: str = Field(description="Patent type: 'D' for Design patents, 'U' for Utility models")
    model: int = Field(description="Search model: Design(1=Smart Recommendation, 2=Image Search), Utility(3=Shape only, 4=Shape & color)")
    
    # Optional filtering parameters
    apply_start_time: Optional[str] = Field(default=None, description="Patent apply date from (format: YYYYMMDD)")
    apply_end_time: Optional[str] = Field(default=None, description="Patent apply date to (format: YYYYMMDD)")
    public_start_time: Optional[str] = Field(default=None, description="Patent publication date from (format: YYYYMMDD)")
    public_end_time: Optional[str] = Field(default=None, description="Patent publication date to (format: YYYYMMDD)")
    
    assignees: Optional[str] = Field(default=None, description="All assignees filter")
    country: Optional[List[str]] = Field(default=None, description="Patent authority codes (e.g., ['US', 'EU', 'CN'])")
    
    # Search parameters
    field: Optional[str] = Field(default="SCORE", description="Field sort: SCORE, APD, PBD, ISD (default: SCORE)")
    order: Optional[str] = Field(default="desc", description="Order: desc, asc (default: desc)")
    limit: Optional[int] = Field(default=10, ge=1, le=100, description="Number of patents to return (1-100, default: 10)")
    offset: Optional[int] = Field(default=0, ge=0, le=1000, description="Offset for pagination (0-1000, default: 0)")
    
    # Language and display options
    lang: Optional[str] = Field(default="original", description="Language preference: original, cn, en (default: original)")
    
    # Legal status filters
    legal_status: Optional[str] = Field(default=None, description="Patent legal status (comma-separated)")
    simple_legal_status: Optional[str] = Field(default=None, description="Simple legal status: 0=Inactive, 1=Active, 2=Pending")
    
    # Advanced search options
    main_field: Optional[str] = Field(default=None, description="Main field search (title, abstract, claims, etc.)")
    loc: Optional[str] = Field(default=None, description="LOC classification for Industrial Designs")
    stemming: Optional[int] = Field(default=0, description="Stemming function: 1=on, 0=off (default: 0)")


__all__ = [
    "PatentSearchPnRequest",
    "PatentBaseV2Response",
    "SearchPatentV2Response",
    "CompanySearchRequest",
    "CurrentAssigneeSearchRequest",
    "DefensePatentSearchRequest",
    "SimilarPatentSearchRequest",
    "SemanticResult",
    "SearchComputeV2Response",
    "SemanticSearchRequest",
    "FileUrlResponse",
    "ImageSearchSingleRequest",
    "PatentMessage",
    "ImageSearchResponse",
    "ImageSearchMultipleRequest",
]
