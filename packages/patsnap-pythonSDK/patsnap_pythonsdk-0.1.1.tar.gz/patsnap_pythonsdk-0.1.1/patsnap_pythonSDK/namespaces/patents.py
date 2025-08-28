from __future__ import annotations

from ..http import HttpClient
from ..resources.search import PatentsSearchResource


class PatentsNamespace:
    """Patents namespace for patent-related operations."""
    
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client
        # Initialize search resources under patents
        self._search = PatentsSearchNamespace(http_client)
    
    @property
    def search(self) -> PatentsSearchNamespace:
        """Access patent search operations."""
        return self._search


class PatentsSearchNamespace:
    """Patent search operations."""
    
    def __init__(self, http_client: HttpClient) -> None:
        self._patents = PatentsSearchResource(http_client)
    
    def by_number(self, **kwargs):
        """Search patents by patent number or application number.
        
        Args:
            pn: Patent number to search for
            apno: Application number to search for  
            authority: List of patent authorities (e.g., ['US', 'CN'])
            limit: Maximum number of results (default: 10, max: 1000)
            offset: Number of results to skip (default: 0)
            **kwargs: Additional parameters
            
        Returns:
            SearchPatentV2Response: Search results with patent data
            
        Raises:
            ApiError: If the API request fails
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> results = patsnap.patents.search.by_number(
            ...     pn="US11205304B2",
            ...     authority=["US"],
            ...     limit=20
            ... )
            >>> print(f"Found {results.total_search_result_count} patents")
        """
        return self._patents.search_pn(**kwargs)
    
    def by_original_assignee(self, **kwargs):
        """Search patents by original applicant/assignee names.
        
        Receives original assignee (applicant) patent data including patent count,
        patent number, patent ID, etc. Supports up to 100 companies with OR logic.
        
        Args:
            application: Standardized Original Assignee (Applicant) name. Up to 100 companies
                        can be searched; multiple companies separated by ' OR ', e.g. 'Apple OR Huawei'
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_order_authority: Order of patent collapse according to authorities priority
            sort: Field order. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE
            offset: Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)
            limit: Limit of returned response; must be <= 1,000
            **kwargs: Additional parameters
            
        Returns:
            SearchPatentV2Response: Patent search results with metadata
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> results = patsnap.patents.search.by_original_assignee(
            ...     application="Apple, Inc.",
            ...     limit=50,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} patents from Apple")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        return self._patents.company_search(**kwargs)
    
    def by_current_assignee(self, **kwargs):
        """Search patents by current assignee names.
        
        Receives current assignee patent data including patent count,
        patent number, patent ID, etc. Supports up to 100 companies with OR logic.
        
        Args:
            assignee: Standardized Current Assignee name. Up to 100 companies
                     can be searched; multiple companies separated by ' OR ', e.g. 'Apple OR Huawei'
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_order_authority: Order of patent collapse according to authorities priority
            sort: Field order. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE
            offset: Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)
            limit: Limit of returned response; must be <= 1,000
            **kwargs: Additional parameters
            
        Returns:
            SearchPatentV2Response: Patent search results with metadata
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> results = patsnap.patents.search.by_current_assignee(
            ...     assignee="Apple, Inc.",
            ...     limit=50,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} patents currently owned by Apple")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        return self._patents.current_assignee_search(**kwargs)
    
    def by_defense_applicant(self, **kwargs):
        """Search defense/military patents by applicant names.
        
        Receives applicant defense patent data including patent count,
        patent number, patent ID, etc. Supports up to 100 companies with OR logic.
        
        Args:
            application: Applicant name for defense patents. Up to 100 companies
                        can be searched; multiple companies separated by ' OR ', 
                        e.g. 'Lockheed Martin Corporation OR Boeing Company'
            collapse_type: Collapse type (ALL, APNO, DOCDB, INPADOC, EXTEND)
            collapse_by: Sort field for patent collapse (APD, PBD, AUTHORITY, SCORE)
            collapse_order: Patent collapse ordering rule (OLDEST or LATEST)
            collapse_order_authority: Order of patent collapse according to authorities priority
            sort: Field order. Fields: PBDT_YEARMONTHDAY, APD_YEARMONTHDAY, ISD, SCORE
            offset: Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)
            limit: Limit of returned response; must be <= 1,000
            **kwargs: Additional parameters
            
        Returns:
            SearchPatentV2Response: Patent search results with metadata
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> results = patsnap.patents.search.by_defense_applicant(
            ...     application="Lockheed Martin Corporation",
            ...     limit=50,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} defense patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        return self._patents.defense_patent_search(**kwargs)
    
    def by_similarity(self, **kwargs):
        """Search for patents similar to a given patent by ID or number.
        
        Receives similar patent list by patent ID or patent number search.
        Patent ID is preferred when both are provided. Maximum 1000 results.
        Sorted by default from high to low similarity score.
        
        Note: This API is suitable for similar patent searches of invention patents
        and utility model patents. For design patents, use P060/P061 APIs.
        
        Args:
            patent_id: Patent ID (preferred when both patent_id and patent_number are provided)
            patent_number: Patent number (used if patent_id is not provided)
            country: Authority and kind code (e.g., ['CNA', 'CNB'])
            pbd_from: Start year of publication date (format: YYYYMMDD)
            pbd_to: End year of publication date (format: YYYYMMDD)
            apd_from: Start year of application date (format: YYYYMMDD)
            apd_to: End year of application date (format: YYYYMMDD)
            relevancy: Minimum relevancy threshold (e.g., '50%', '70%')
            offset: Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)
            limit: Limit of returned response; must be <= 1,000
            **kwargs: Additional parameters
            
        Returns:
            SearchComputeV2Response: Similar patent search results with relevancy scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            ValueError: If neither patent_id nor patent_number is provided
            
        Example:
            >>> results = patsnap.patents.search.by_similarity(
            ...     patent_id="b053642f-3108-4ea9-b629-420b0ab959e3",
            ...     limit=50,
            ...     relevancy="70%"
            ... )
            >>> print(f"Found {len(results.results)} similar patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} (Relevancy: {patent.relevancy})")
        """
        return self._patents.similar_patent_search(**kwargs)
    
    def by_semantic_text(self, **kwargs):
        """Search for patents using semantic analysis of technical text.
        
        Receives patent list by semantic search using technical descriptions,
        abstracts, or other patent text. Maximum 1000 results. Sorted by
        default from high to low similarity. Recommended to use >200 words
        for best results.
        
        Args:
            text: Semantic query text (technical description, abstract, etc.).
                 Recommend >200 words for best results
            country: Authority and kind code (e.g., ['CNA', 'CNB'])
            pbd_from: Start year of publication date (format: YYYYMMDD)
            pbd_to: End year of publication date (format: YYYYMMDD)
            apd_from: Start year of application date (format: YYYYMMDD)
            apd_to: End year of application date (format: YYYYMMDD)
            relevancy: Minimum relevancy threshold (e.g., '50%', '70%')
            offset: Offset value; limit + offset <= 20000 (max 1000 for Semantic Search)
            limit: Limit of returned response; must be <= 1,000
            **kwargs: Additional parameters
            
        Returns:
            SearchComputeV2Response: Semantic search results with relevancy scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            ValueError: If text parameter is missing
            
        Example:
            >>> text = '''The invention discloses an automobile front-view based 
            ...            wireless video transmission system and method. The system
            ...            comprises a front-view camera, wireless video transmitting
            ...            module, wireless video receiving module, display screen...'''
            >>> results = patsnap.patents.search.by_semantic_text(
            ...     text=text,
            ...     limit=50,
            ...     relevancy="60%"
            ... )
            >>> print(f"Found {len(results.results)} semantically similar patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} (Relevancy: {patent.relevancy})")
        """
        return self._patents.semantic_search(**kwargs)
    
    def upload_image(self, **kwargs):
        """Upload an image and get a public URL for image search operations.
        
        Uploads an image file and returns a publicly accessible URL that can be used
        for subsequent image search operations. The URL is valid for 9 hours and will
        be automatically deleted after expiration.
        
        Supported formats: JPG, PNG
        File size limit: 4MB (4096KB)
        URL validity: 9 hours (32400 seconds)
        
        Args:
            image: Image file to upload. Can be:
                  - File path (str or Path object)
                  - File-like object (BinaryIO)
            **kwargs: Additional parameters
                  
        Returns:
            FileUrlResponse: Contains the public URL and expiration time
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the image file is invalid
            FileNotFoundError: If the image file path doesn't exist
            ValueError: If the image format or size is not supported
            
        Example:
            >>> # Upload from file path
            >>> result = patsnap.patents.search.upload_image(image="path/to/image.jpg")
            >>> print(f"Image URL: {result.url}")
            >>> print(f"Expires in: {result.expire} seconds (9 hours)")
            >>> 
            >>> # Upload from file object
            >>> with open("patent_diagram.png", "rb") as f:
            ...     result = patsnap.patents.search.upload_image(image=f)
            ...     print(f"Uploaded: {result.url}")
        """
        return self._patents.upload_image(**kwargs)
    
    def by_image(self, **kwargs):
        """Search for patents using image similarity analysis.
        
        Finds design patents or utility patents that are visually similar to the
        provided image. Supports different search models optimized for design
        patents vs utility models. Returns up to 100 similar patents per call.
        
        Args:
            url: Image URL for similarity search (from upload_image or external)
            patent_type: Patent type - 'D' for Design patents, 'U' for Utility models
            model: Search model:
                  Design patents: 1=Smart Recommendation (recommended), 2=Image Search
                  Utility models: 3=Search by shape only, 4=Search by shape & color (recommended)
            apply_start_time: Patent application date from (format: YYYYMMDD)
            apply_end_time: Patent application date to (format: YYYYMMDD)
            public_start_time: Patent publication date from (format: YYYYMMDD)
            public_end_time: Patent publication date to (format: YYYYMMDD)
            assignees: All assignees filter
            country: Patent authority codes (e.g., ['US', 'EU', 'CN'])
            field: Field sort - SCORE, APD, PBD, ISD (default: SCORE)
            order: Order - desc, asc (default: desc)
            limit: Number of patents to return (1-100, default: 10)
            offset: Offset for pagination (0-1000, default: 0)
            lang: Language preference - original, cn, en (default: original)
            is_https: Return https images - 1=https, 0=http (default: 0)
            include_machine_translation: Include machine translations
            legal_status: Patent legal status (comma-separated)
            simple_legal_status: Simple legal status - 0=Inactive, 1=Active, 2=Pending
            main_field: Main field search (title, abstract, claims, etc.)
            loc: LOC classification for Industrial Designs
            stemming: Stemming function - 1=on, 0=off (default: 0)
            pre_filter: Pre-filter function - 1=on, 0=off (default: 1)
            **kwargs: Additional parameters
            
        Returns:
            ImageSearchResponse: Similar patent search results with similarity scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> # Upload image first
            >>> upload_result = patsnap.patents.search.upload_image(image="design.jpg")
            >>> 
            >>> # Search for similar design patents
            >>> results = patsnap.patents.search.by_image(
            ...     url=upload_result.url,
            ...     patent_type="D",
            ...     model=1,  # Smart Recommendation for designs
            ...     limit=50,
            ...     country=["US", "EU", "CN"]
            ... )
            >>> print(f"Found {len(results.patent_messages)} similar patents")
            >>> for patent in results.patent_messages[:3]:
            ...     print(f"- {patent.title} (Score: {patent.score})")
        """
        return self._patents.image_search(**kwargs)
    
    def by_multiple_images(self, **kwargs):
        """Search for patents using multiple image similarity analysis.
        
        Finds design patents or utility patents that are visually similar to the
        provided images (up to 4 images). The Smart Recommendation model uses the
        first image for LOC prediction and reorders results, so image order matters.
        
        Args:
            urls: List of image URLs (1-4 images) for similarity search
            patent_type: Patent type - 'D' for Design patents, 'U' for Utility models
            model: Search model:
                  Design patents: 1=Smart Recommendation (recommended), 2=Image Search
                  Utility models: 3=Search by shape only, 4=Search by shape & color (recommended)
            apply_start_time: Patent application date from (format: YYYYMMDD)
            apply_end_time: Patent application date to (format: YYYYMMDD)
            public_start_time: Patent publication date from (format: YYYYMMDD)
            public_end_time: Patent publication date to (format: YYYYMMDD)
            assignees: All assignees filter
            country: Patent authority codes (e.g., ['US', 'EU', 'CN'])
            field: Field sort - SCORE, APD, PBD, ISD (default: SCORE)
            order: Order - desc, asc (default: desc)
            limit: Number of patents to return (1-100, default: 10)
            offset: Offset for pagination (0-1000, default: 0)
            lang: Language preference - original, cn, en (default: original)
            legal_status: Patent legal status (comma-separated)
            simple_legal_status: Simple legal status - 0=Inactive, 1=Active, 2=Pending
            main_field: Main field search (title, abstract, claims, etc.)
            loc: LOC classification for Industrial Designs
            stemming: Stemming function - 1=on, 0=off (default: 0)
            **kwargs: Additional parameters
            
        Returns:
            ImageSearchResponse: Similar patent search results with similarity scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            ValueError: If urls list is empty or contains more than 4 URLs
            
        Example:
            >>> # Upload multiple images first
            >>> image1 = patsnap.patents.search.upload_image(image="design1.jpg")
            >>> image2 = patsnap.patents.search.upload_image(image="design2.jpg")
            >>> image3 = patsnap.patents.search.upload_image(image="design3.jpg")
            >>> 
            >>> # Search using multiple design images
            >>> results = patsnap.patents.search.by_multiple_images(
            ...     urls=[image1.url, image2.url, image3.url],
            ...     patent_type="D",
            ...     model=1,  # Smart Recommendation uses first image for LOC
            ...     limit=50,
            ...     country=["US", "EU", "CN"]
            ... )
            >>> print(f"Found {len(results.patent_messages)} similar patents")
            >>> for patent in results.patent_messages[:3]:
            ...     print(f"- {patent.title} (Score: {patent.score})")
            >>>
            >>> # Note: Image order matters with Smart Recommendation model
            >>> # The first image is used for LOC prediction and result reordering
        """
        return self._patents.multi_image_search(**kwargs)
