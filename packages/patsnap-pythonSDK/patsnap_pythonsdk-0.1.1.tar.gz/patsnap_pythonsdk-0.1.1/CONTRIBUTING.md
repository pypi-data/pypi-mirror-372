# Contributing to Patsnap Python SDK

Welcome to the Patsnap Python SDK! This guide will help you understand our namespace-based architecture and contribute new endpoints systematically.

## 🏗️ Architecture Overview

Our SDK uses a **namespace-based architecture** that transforms cryptic endpoint codes into intuitive, discoverable API methods:

```python
# ❌ Old way (cryptic codes)
[P069] Patsnap Standard Patent Number Search
[AI64-1] Create AI Weekly Differentiation Analysis

# ✅ New way (intuitive namespaces)
patsnap.patents.search.by_number()
patsnap.ai.agent.create_weekly_analysis()
```

## 📁 Project Structure

```
patsnap-pythonSDK/
├── namespaces/           # API namespace implementations
│   ├── ai/              # AI operations
│   ├── patents/         # Patent operations  
│   ├── analytics/       # Analytics & reports
│   ├── drugs/           # Drug & life sciences
│   ├── literature/      # Literature search
│   ├── chemical/        # Chemical & bio data
│   └── monitoring/      # Monitoring & exports
├── models/              # Pydantic data models
│   ├── ai/
│   ├── patents/
│   └── ...
├── resources/           # HTTP resource handlers
│   ├── ai/
│   ├── patents/
│   └── ...
├── examples/            # Usage examples
├── tests/               # Test suites
└── docs/
    └── implementation/  # Design documents
```

## 🎯 Namespace Design Principles

### 1. **Domain → Category → Action**
```python
patsnap.{domain}.{category}.{action}()

# Examples:
patsnap.patents.search.by_number()      # Domain: patents, Category: search, Action: by_number
patsnap.ai.agent.create_analysis()      # Domain: ai, Category: agent, Action: create_analysis
patsnap.drugs.data.basic_info()         # Domain: drugs, Category: data, Action: basic_info
```

### 2. **Consistent Categories**
- **search** - Search operations
- **data** - Data retrieval  
- **analysis** - Analysis operations
- **legal** - Legal information
- **clinical** - Clinical data (drugs domain)
- **projects** - Project management (monitoring domain)

### 3. **Intuitive Method Names**
- Use descriptive names: `by_number()` not `pn()`
- Avoid cryptic codes: `create_weekly_analysis()` not `ai64_1()`
- Be consistent: `basic_info()` across all domains

## 🔧 Implementation Workflow

When adding new endpoints, follow this systematic approach:

### Step 1: Identify the Namespace
Determine which domain and category the endpoint belongs to:

```python
# Example: [P070] Keyword Assistant
# Domain: patents (P prefix)
# Category: search (keyword assistance is search-related)
# Method: patsnap.patents.search.keyword_assistant()
```

### Step 2: Create the Models
Create Pydantic models for request and response:

```python
# models/patents/search.py
class KeywordAssistantRequest(BaseModel):
    query: str
    limit: Optional[int] = Field(default=10, le=100)
    
class KeywordAssistantResponse(BaseModel):
    keywords: List[str]
    suggestions: List[str]
    confidence_scores: Dict[str, float]
```

### Step 3: Implement the Resource
Create the HTTP resource handler:

```python
# resources/patents/search.py
class PatentsSearchResource:
    def keyword_assistant(self, **kwargs) -> KeywordAssistantResponse:
        request = KeywordAssistantRequest(**kwargs)
        response = self._http.post("/v2/patents/keyword-assistant", 
                                 json=request.model_dump())
        return KeywordAssistantResponse(**response["data"])
```

### Step 4: Add to Namespace
Add the method to the appropriate namespace:

```python
# namespaces/patents/search.py
class PatentsSearchNamespace:
    def keyword_assistant(self, **kwargs):
        """Get keyword suggestions for patent search."""
        return self._resource.keyword_assistant(**kwargs)
```

### Step 5: Create Tests
Write comprehensive tests:

```python
# tests/test_patents_search.py
def test_keyword_assistant_success():
    # Test successful keyword assistance
    
def test_keyword_assistant_validation_error():
    # Test input validation
    
def test_keyword_assistant_api_error():
    # Test API error handling
```

### Step 6: Add Examples
Create usage examples:

```python
# examples/patents/keyword_assistant.py
import patsnap_pythonSDK as patsnap

patsnap.configure(client_id="...", client_secret="...")

# Get keyword suggestions
suggestions = patsnap.patents.search.keyword_assistant(
    query="artificial intelligence",
    limit=20
)

print(f"Keywords: {suggestions.keywords}")
print(f"Suggestions: {suggestions.suggestions}")
```

## 📋 Implementation Checklist

For each new endpoint, ensure you create:

- [ ] **Models** - Request/Response Pydantic models
- [ ] **Resource** - HTTP resource handler with proper error handling
- [ ] **Namespace** - Clean API method in appropriate namespace
- [ ] **Tests** - Unit tests covering success, validation, and error cases
- [ ] **Examples** - Usage example showing how to use the endpoint
- [ ] **Documentation** - Docstrings with parameter descriptions

## 🎨 Code Standards

### Model Conventions
```python
# Use descriptive field names
class PatentSearchRequest(BaseModel):
    patent_number: Optional[str] = Field(None, description="Patent number to search")
    authority: Optional[List[str]] = Field(None, description="Patent authorities (e.g., ['US', 'CN'])")
    
# Include validation
class PaginatedRequest(BaseModel):
    limit: Optional[int] = Field(default=10, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
```

### Namespace Conventions
```python
class PatentsSearchNamespace:
    def by_number(self, **kwargs) -> SearchPatentV2Response:
        """Search patents by patent number.
        
        Args:
            patent_number: Patent number to search
            authority: List of authorities to search in
            limit: Maximum number of results (default: 10, max: 1000)
            offset: Number of results to skip (default: 0)
            
        Returns:
            SearchPatentV2Response: Search results with patents data
            
        Example:
            >>> results = patsnap.patents.search.by_number(
            ...     patent_number="US123456",
            ...     authority=["US"],
            ...     limit=20
            ... )
        """
        return self._resource.search_by_number(**kwargs)
```

### Error Handling
```python
# Resource layer handles HTTP errors
def search_by_number(self, **kwargs):
    try:
        request = PatentSearchRequest(**kwargs)
        response = self._http.post("/v2/patents/search", json=request.model_dump())
        return SearchPatentV2Response(**response["data"])
    except ValidationError as e:
        raise ValueError(f"Invalid request parameters: {e}")
    except HTTPError as e:
        raise ApiError(f"API request failed: {e}")
```

## 🚀 Getting Started

1. **Review the design documents** in `docs/implementation/`:
   - `NAMESPACE_DESIGN.md` - Complete API structure
   - `ENDPOINT_MAPPING.md` - Maps endpoint codes to API methods
   - `IMPLEMENTATION_PLAN.md` - Technical implementation details

2. **Choose an endpoint** from `docs/implementation/ENDPOINTS.md`

3. **Follow the implementation workflow** above

4. **Submit your contribution** with all required components

## 📚 Reference Documents

- **[Namespace Design](docs/implementation/NAMESPACE_DESIGN.md)** - Complete API structure with examples
- **[Endpoint Mapping](docs/implementation/ENDPOINT_MAPPING.md)** - Maps all 250+ endpoints to new API methods  
- **[Implementation Plan](docs/implementation/IMPLEMENTATION_PLAN.md)** - Technical implementation strategy
- **[Endpoints List](docs/implementation/ENDPOINTS.md)** - Complete list of all available endpoints

## 🎯 Domain Priorities

When implementing endpoints, follow this priority order:

1. **Patents** - Core patent search and data operations
2. **Analytics** - Patent analytics and trend analysis  
3. **AI** - AI-powered analysis and processing
4. **Drugs** - Drug and life sciences data
5. **Literature** - Literature search and analysis
6. **Chemical** - Chemical structure and sequence analysis
7. **Monitoring** - Project monitoring and data export

## 💡 Tips for Success

- **Start small** - Implement one endpoint at a time
- **Follow patterns** - Look at existing implementations for consistency
- **Test thoroughly** - Include edge cases and error scenarios
- **Document well** - Clear docstrings help users understand the API
- **Think user-first** - API should be intuitive and discoverable

## 🏗️ Response Model Guidelines (Updated)

### API Response Structure
Most Patsnap API endpoints return responses with a `data` wrapper:

```json
{
  "data": {
    "results": [...],
    "result_count": 10,
    "total_search_result_count": 1000
  }
}
```

### Model Implementation Pattern
Create separate data and wrapper models:

```python
class SearchResultsData(BaseModel):
    """Data section of search response"""
    results: List[PatentResult] = Field(description="Search results")
    result_count: int = Field(description="Number of results")
    total_search_result_count: int = Field(description="Total available results")

class SearchResponse(BaseModel):
    """Complete search response wrapper"""
    data: SearchResultsData = Field(description="Response data")
```

### Usage in Examples
Always access nested data correctly:

```python
# ✅ Correct - access through data wrapper
response = patsnap.patents.search.by_number(pn="US123456")
print(f"Found {response.data.total_search_result_count} patents")
for patent in response.data.results:
    print(patent.title)

# ❌ Incorrect - direct access will fail
print(f"Found {response.total_search_result_count} patents")  # AttributeError
```

### Special Cases
Some endpoints return lists directly (e.g., `query_filter`):
```python
# Returns List[PatentDataFieldResponse] directly
results = patsnap.analytics.search.query_filter(...)
for field_data in results:  # No .data wrapper needed
    print(field_data.assignee)
```

## 🤝 Getting Help

- Review existing implementations in `namespaces/patents/` and `namespaces/analytics/`
- Check the test files for examples of proper testing patterns
- Look at `examples/` for usage pattern examples
- **New**: Check recent fixes in response models for proper data wrapper handling


