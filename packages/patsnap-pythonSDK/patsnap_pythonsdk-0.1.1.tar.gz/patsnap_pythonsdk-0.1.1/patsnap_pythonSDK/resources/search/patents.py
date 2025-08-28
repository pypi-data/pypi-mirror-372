from __future__ import annotations

from typing import Optional, List, Dict, Union, BinaryIO
import os
from pathlib import Path

from ...http import HttpClient
from ...models.search.patents import (
    PatentSearchPnRequest, 
    SearchPatentV2Response,
    CompanySearchRequest,
    CurrentAssigneeSearchRequest,
    DefensePatentSearchRequest,
    SimilarPatentSearchRequest,
    SearchComputeV2Response,
    SemanticSearchRequest,
    FileUrlResponse,
    ImageSearchSingleRequest,
    ImageSearchResponse,
    ImageSearchMultipleRequest,
)


class PatentsSearchResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def search_pn(
        self,
        *,
        pn: Optional[str] = None,
        apno: Optional[str] = None,
        authority: Optional[List[str]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SearchPatentV2Response:
        """Search patents by patent number or application number.
        
        Args:
            pn: Patent number to search for
            apno: Application number to search for
            authority: List of patent authorities to search in (e.g., ['US', 'CN'])
            offset: Number of results to skip for pagination (default: 0)
            limit: Maximum number of results to return (default: 10, max: 1000)
            
        Returns:
            SearchPatentV2Response: Search results containing patent data
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> results = resource.search_pn(
            ...     pn="US11205304B2",
            ...     authority=["US"],
            ...     limit=20
            ... )
            >>> print(f"Found {results.total_search_result_count} patents")
        """
        request = PatentSearchPnRequest(
            pn=pn,
            apno=apno,
            authority=authority,
            offset=offset,
            limit=limit,
        )
        
        # Convert the request to dict and filter out None values
        params = {k: v for k, v in request.model_dump().items() if v is not None}
        
        response = self._http.post("/search/patent/pn-search-patent/v2", json=params)
        # Handle both wrapped and direct response formats
        if "data" in response:
            return SearchPatentV2Response(data=response["data"])
        else:
            return SearchPatentV2Response(data=response)
    
    def company_search(
        self,
        *,
        application: str,
        collapse_type: Optional[str] = None,
        collapse_by: Optional[str] = None,
        collapse_order: Optional[str] = None,
        collapse_order_authority: Optional[List[str]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SearchPatentV2Response:
        """
        Search patents by original applicant/assignee names.
        
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
            
        Returns:
            SearchPatentV2Response: Patent search results with metadata
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> results = resource.company_search(
            ...     application="Apple, Inc.",
            ...     limit=50,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        # Create and validate request
        request = CompanySearchRequest(
            application=application,
            collapse_type=collapse_type,
            collapse_by=collapse_by,
            collapse_order=collapse_order,
            collapse_order_authority=collapse_order_authority,
            sort=sort,
            offset=offset,
            limit=limit,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/company-search-patent/v2", json=json_data)
        
        # Parse and return response - handle both wrapped and direct response formats
        if "data" in response:
            return SearchPatentV2Response(data=response["data"])
        else:
            return SearchPatentV2Response(data=response)
    
    def current_assignee_search(
        self,
        *,
        assignee: str,
        collapse_type: Optional[str] = None,
        collapse_by: Optional[str] = None,
        collapse_order: Optional[str] = None,
        collapse_order_authority: Optional[List[str]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SearchPatentV2Response:
        """
        Search patents by current assignee names.
        
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
            
        Returns:
            SearchPatentV2Response: Patent search results with metadata
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> results = resource.current_assignee_search(
            ...     assignee="Apple, Inc.",
            ...     limit=50,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        # Create and validate request
        request = CurrentAssigneeSearchRequest(
            assignee=assignee,
            collapse_type=collapse_type,
            collapse_by=collapse_by,
            collapse_order=collapse_order,
            collapse_order_authority=collapse_order_authority,
            sort=sort,
            offset=offset,
            limit=limit,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/current-search-patent/v2", json=json_data)
        
        # Parse and return response - handle both wrapped and direct response formats
        if "data" in response:
            return SearchPatentV2Response(data=response["data"])
        else:
            return SearchPatentV2Response(data=response)
    
    def defense_patent_search(
        self,
        *,
        application: str,
        collapse_type: Optional[str] = None,
        collapse_by: Optional[str] = None,
        collapse_order: Optional[str] = None,
        collapse_order_authority: Optional[List[str]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SearchPatentV2Response:
        """
        Search defense/military patents by applicant names.
        
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
            
        Returns:
            SearchPatentV2Response: Patent search results with metadata
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> results = resource.defense_patent_search(
            ...     application="Lockheed Martin Corporation",
            ...     limit=50,
            ...     sort=[{"field": "SCORE", "order": "DESC"}]
            ... )
            >>> print(f"Found {len(results.results)} defense patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} ({patent.pn})")
        """
        # Create and validate request
        request = DefensePatentSearchRequest(
            application=application,
            collapse_type=collapse_type,
            collapse_by=collapse_by,
            collapse_order=collapse_order,
            collapse_order_authority=collapse_order_authority,
            sort=sort,
            offset=offset,
            limit=limit,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/company-search-defense-patent/v2", json=json_data)
        
        # Handle empty response (no results found)
        if not response or response == {}:
            # Return empty response structure
            empty_data = {
                "results": [],
                "result_count": 0,
                "total_search_result_count": 0
            }
            return SearchPatentV2Response(data=empty_data)
        
        # Parse and return response - handle both wrapped and direct response formats
        if "data" in response:
            return SearchPatentV2Response(data=response["data"])
        else:
            return SearchPatentV2Response(data=response)
    
    def similar_patent_search(
        self,
        *,
        patent_id: Optional[str] = None,
        patent_number: Optional[str] = None,
        country: Optional[List[str]] = None,
        pbd_from: Optional[str] = None,
        pbd_to: Optional[str] = None,
        apd_from: Optional[str] = None,
        apd_to: Optional[str] = None,
        relevancy: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SearchComputeV2Response:
        """
        Search for patents similar to a given patent by ID or number.
        
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
            
        Returns:
            SearchComputeV2Response: Similar patent search results with relevancy scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> results = resource.similar_patent_search(
            ...     patent_id="b053642f-3108-4ea9-b629-420b0ab959e3",
            ...     limit=50,
            ...     relevancy="70%"
            ... )
            >>> print(f"Found {len(results.results)} similar patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} (Relevancy: {patent.relevancy})")
        """
        # Validate that at least one of patent_id or patent_number is provided
        if not patent_id and not patent_number:
            raise ValueError("Either patent_id or patent_number must be provided")
        
        # Create and validate request
        request = SimilarPatentSearchRequest(
            patent_id=patent_id,
            patent_number=patent_number,
            country=country,
            pbd_from=pbd_from,
            pbd_to=pbd_to,
            apd_from=apd_from,
            apd_to=apd_to,
            relevancy=relevancy,
            offset=offset,
            limit=limit,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/similar-search-patent/v2", json=json_data)
        
        # Parse and return response
        # Handle both wrapped and direct response formats
        if "data" in response:
            return SearchComputeV2Response(data=response["data"])
        else:
            return SearchComputeV2Response(data=response)
    
    def semantic_search(
        self,
        *,
        text: str,
        country: Optional[List[str]] = None,
        pbd_from: Optional[str] = None,
        pbd_to: Optional[str] = None,
        apd_from: Optional[str] = None,
        apd_to: Optional[str] = None,
        relevancy: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SearchComputeV2Response:
        """
        Search for patents using semantic analysis of technical text.
        
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
            
        Returns:
            SearchComputeV2Response: Semantic search results with relevancy scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> text = '''The invention discloses an automobile front-view based 
            ...            wireless video transmission system and method...'''
            >>> results = resource.semantic_search(
            ...     text=text,
            ...     limit=50,
            ...     relevancy="60%"
            ... )
            >>> print(f"Found {len(results.results)} semantically similar patents")
            >>> for patent in results.results[:3]:
            ...     print(f"- {patent.title} (Relevancy: {patent.relevancy})")
        """
        # Create and validate request
        request = SemanticSearchRequest(
            text=text,
            country=country,
            pbd_from=pbd_from,
            pbd_to=pbd_to,
            apd_from=apd_from,
            apd_to=apd_to,
            relevancy=relevancy,
            offset=offset,
            limit=limit,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/semantic-search-patent/v2", json=json_data)
        
        # Parse and return response
        # Handle both wrapped and direct response formats
        if "data" in response:
            return SearchComputeV2Response(data=response["data"])
        else:
            return SearchComputeV2Response(data=response)
    
    def upload_image(
        self,
        image: Union[str, Path, BinaryIO],
    ) -> FileUrlResponse:
        """
        Upload an image and get a public URL for image search operations.
        
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
                  
        Returns:
            FileUrlResponse: Contains the public URL and expiration time
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the image file is invalid
            FileNotFoundError: If the image file path doesn't exist
            ValueError: If the image format or size is not supported
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> # Upload from file path
            >>> result = resource.upload_image("path/to/image.jpg")
            >>> print(f"Image URL: {result.url}")
            >>> print(f"Expires in: {result.expire} seconds")
            >>> 
            >>> # Upload from file object
            >>> with open("image.png", "rb") as f:
            ...     result = resource.upload_image(f)
        """
        # Validate and prepare file for upload
        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Check file extension
            if image_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                raise ValueError(f"Unsupported image format: {image_path.suffix}. Only JPG and PNG are supported.")
            
            # Check file size (4MB limit)
            file_size = image_path.stat().st_size
            if file_size > 4 * 1024 * 1024:  # 4MB in bytes
                raise ValueError(f"Image file too large: {file_size / (1024*1024):.1f}MB. Maximum size is 4MB.")
            
            # Open file for upload
            with open(image_path, 'rb') as f:
                file_data = f.read()
                filename = image_path.name
        else:
            # Handle file-like object
            if hasattr(image, 'read'):
                file_data = image.read()
                filename = getattr(image, 'name', 'image.jpg')
            else:
                raise ValueError("Image must be a file path (str/Path) or file-like object")
            
            # Reset file pointer if possible
            if hasattr(image, 'seek'):
                try:
                    image.seek(0)
                except (OSError, IOError):
                    pass  # Some file objects don't support seeking
        
        # Prepare multipart form data
        files = {
            'image': (filename, file_data, 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png')
        }
        
        # Make HTTP request with file upload
        # Note: This assumes the HttpClient has a method to handle multipart uploads
        # If not available, this will need to be implemented in the HttpClient
        response = self._http.post("/image-search/image-upload", files=files)
        
        # Parse and return response
        return FileUrlResponse(**response["data"])
    
    def image_search(
        self,
        *,
        url: str,
        patent_type: str,
        model: int,
        apply_start_time: Optional[str] = None,
        apply_end_time: Optional[str] = None,
        public_start_time: Optional[str] = None,
        public_end_time: Optional[str] = None,
        assignees: Optional[str] = None,
        country: Optional[List[str]] = None,
        field: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        lang: Optional[str] = None,
        is_https: Optional[int] = None,
        include_machine_translation: Optional[bool] = None,
        legal_status: Optional[str] = None,
        simple_legal_status: Optional[str] = None,
        main_field: Optional[str] = None,
        loc: Optional[str] = None,
        stemming: Optional[int] = None,
        pre_filter: Optional[int] = None,
    ) -> ImageSearchResponse:
        """
        Search for patents using image similarity analysis.
        
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
            
        Returns:
            ImageSearchResponse: Similar patent search results with similarity scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> # Search for design patents similar to an image
            >>> results = resource.image_search(
            ...     url="https://example.com/patent_image.jpg",
            ...     patent_type="D",
            ...     model=1,  # Smart Recommendation for designs
            ...     limit=50
            ... )
            >>> print(f"Found {len(results.patent_messages)} similar patents")
            >>> for patent in results.patent_messages[:3]:
            ...     print(f"- {patent.title} (Score: {patent.score})")
        """
        # Create and validate request
        request = ImageSearchSingleRequest(
            url=url,
            patent_type=patent_type,
            model=model,
            apply_start_time=apply_start_time,
            apply_end_time=apply_end_time,
            public_start_time=public_start_time,
            public_end_time=public_end_time,
            assignees=assignees,
            country=country,
            field=field,
            order=order,
            limit=limit,
            offset=offset,
            lang=lang,
            is_https=is_https,
            include_machine_translation=include_machine_translation,
            legal_status=legal_status,
            simple_legal_status=simple_legal_status,
            main_field=main_field,
            loc=loc,
            stemming=stemming,
            pre_filter=pre_filter,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/image-single", json=json_data)
        
        # Parse and return response
        return ImageSearchResponse(**response["data"])
    
    def multi_image_search(
        self,
        *,
        urls: List[str],
        patent_type: str,
        model: int,
        apply_start_time: Optional[str] = None,
        apply_end_time: Optional[str] = None,
        public_start_time: Optional[str] = None,
        public_end_time: Optional[str] = None,
        assignees: Optional[str] = None,
        country: Optional[List[str]] = None,
        field: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        lang: Optional[str] = None,
        legal_status: Optional[str] = None,
        simple_legal_status: Optional[str] = None,
        main_field: Optional[str] = None,
        loc: Optional[str] = None,
        stemming: Optional[int] = None,
    ) -> ImageSearchResponse:
        """
        Search for patents using multiple image similarity analysis.
        
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
            
        Returns:
            ImageSearchResponse: Similar patent search results with similarity scores
            
        Raises:
            ApiError: If the API request fails or returns an error
            ValidationError: If the request parameters are invalid
            ValueError: If urls list is empty or contains more than 4 URLs
            
        Example:
            >>> resource = PatentsSearchResource(http_client)
            >>> # Search using multiple design images
            >>> results = resource.multi_image_search(
            ...     urls=[
            ...         "https://example.com/design1.jpg",
            ...         "https://example.com/design2.jpg",
            ...         "https://example.com/design3.jpg"
            ...     ],
            ...     patent_type="D",
            ...     model=1,  # Smart Recommendation uses first image for LOC
            ...     limit=50
            ... )
            >>> print(f"Found {len(results.patent_messages)} similar patents")
            >>> for patent in results.patent_messages[:3]:
            ...     print(f"- {patent.title} (Score: {patent.score})")
        """
        # Validate URLs list
        if not urls:
            raise ValueError("At least one image URL is required")
        if len(urls) > 4:
            raise ValueError("Maximum 4 image URLs are allowed")
        
        # Create and validate request
        request = ImageSearchMultipleRequest(
            urls=urls,
            patent_type=patent_type,
            model=model,
            apply_start_time=apply_start_time,
            apply_end_time=apply_end_time,
            public_start_time=public_start_time,
            public_end_time=public_end_time,
            assignees=assignees,
            country=country,
            field=field,
            order=order,
            limit=limit,
            offset=offset,
            lang=lang,
            legal_status=legal_status,
            simple_legal_status=simple_legal_status,
            main_field=main_field,
            loc=loc,
            stemming=stemming,
        )
        
        # Convert request to dict and filter out None values
        json_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        # Make HTTP request
        response = self._http.post("/search/patent/image-multiple", json=json_data)
        
        # Parse and return response
        return ImageSearchResponse(**response["data"])
