# Patents Examples

Examples for patent search and data retrieval operations.

## Available Examples

- **search_by_number.py** - Search patents by patent number or application number
- **original_assignee_search.py** - Search patents by original applicant/assignee names
- **current_assignee_search.py** - Search patents by current assignee/owner names
- **defense_patent_search.py** - Search defense/military patents by applicant names
- **similar_patent_search.py** - Similar patent search and analysis examples
- **semantic_search.py** - Semantic patent search using technical text and abstracts
- **image_upload.py** - Upload patent images for visual search operations
- **image_search.py** - Visual patent search using image similarity analysis
- **multi_image_search.py** - Multi-image patent search using up to 4 images for comprehensive analysis

## Planned Examples

- **legal_status.py** - Patent legal status and lifecycle information
- **citation_analysis.py** - Patent citation networks and relationships
- **classification.py** - Patent classification and technology categorization
- **valuation.py** - Patent valuation and market indicators

## Usage

Each example demonstrates different aspects of patent search:

### Patent Number Search
```python
# Search by specific patent numbers
results = patsnap.patents.search.by_number(
    pn="US11205304B2",
    authority=["US"],
    limit=20
)
```

### Original Assignee Search  
```python
# Search by original applicant names
results = patsnap.patents.search.by_original_assignee(
    application="Apple, Inc.",
    limit=50,
    sort=[{"field": "SCORE", "order": "DESC"}]
)
```

### Current Assignee Search
```python
# Search by current owner names
results = patsnap.patents.search.by_current_assignee(
    assignee="Apple, Inc.",
    limit=50,
    sort=[{"field": "SCORE", "order": "DESC"}]
)
```

### Defense Patent Search
```python
# Search defense/military patents by applicant names
results = patsnap.patents.search.by_defense_applicant(
    application="Lockheed Martin Corporation",
    limit=50,
    sort=[{"field": "SCORE", "order": "DESC"}]
)
```

### Similar Patent Search
```python
# Find patents similar to a given patent by ID or number
results = patsnap.patents.search.by_similarity(
    patent_id="b053642f-3108-4ea9-b629-420b0ab959e3",
    limit=50,
    relevancy="70%"
)
```

### Semantic Patent Search
```python
# Search patents using technical descriptions or abstracts
text = """The invention discloses an automobile front-view based 
wireless video transmission system and method..."""
results = patsnap.patents.search.by_semantic_text(
    text=text,
    limit=50,
    relevancy="60%"
)
```

### Image Upload for Patent Search
```python
# Upload patent images and get public URLs for image search
result = patsnap.patents.search.upload_image(image="path/to/patent_diagram.jpg")
print(f"Image URL: {result.url}")
print(f"Expires in: {result.expire} seconds")
```

### Image-Based Patent Search
```python
# Search for visually similar patents using image analysis
results = patsnap.patents.search.by_image(
    url="https://example.com/patent_image.jpg",
    patent_type="D",  # Design patents
    model=1,  # Smart Recommendation
    limit=50
)
```

### Multi-Image Patent Search
```python
# Search using multiple images for comprehensive analysis (up to 4 images)
results = patsnap.patents.search.by_multiple_images(
    urls=[
        "https://example.com/front_view.jpg",
        "https://example.com/back_view.jpg",
        "https://example.com/side_view.jpg"
    ],
    patent_type="D",  # Design patents
    model=1,  # Smart Recommendation (first image used for LOC prediction)
    limit=75
)
```

## Common Use Cases

- **Patent Validation** - Verify patent existence and status
- **Portfolio Analysis** - Analyze company patent portfolios
- **Competitive Intelligence** - Compare patent activity between companies
- **Technology Landscape** - Map patent activity in technology areas
- **Due Diligence** - Research patent ownership and history
