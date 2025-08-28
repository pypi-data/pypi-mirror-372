# Patsnap Python SDK

> ⚠️ This is an **unofficial** Python SDK for Patsnap's APIs. This SDK is **NOT officially supported or endorsed** by Patsnap. Use at your own discretion and ensure compliance with Patsnap's terms of service.

A comprehensive Python SDK for accessing Patsnap's patent and innovation intelligence APIs with a clean, intuitive interface.

## 🚀 Installation

```bash
pip install patsnap-pythonSDK
```

## ⚡ Quick Start

```python
import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Search for AI patents
results = patsnap.analytics.search.query_search(
    query_text="TACD: artificial intelligence",
    limit=10
)

print(f"Found {results.data.total_search_result_count:,} AI patents")
for patent in results.data.results[:3]:
    print(f"- {patent.title}")
```



## 📊 Usage Examples

### Patent Search
```python
# Search by patent number
patent = patsnap.patents.search.by_number(patent_number="US10123456B2")

# Search by company
results = patsnap.patents.search.by_current_assignee(
    assignee="Apple Inc.",
    limit=50
)

# Semantic search
similar = patsnap.patents.search.by_semantic_text(
    text="machine learning artificial intelligence neural networks",
    limit=25
)

# Visual search with single image
visual_results = patsnap.patents.search.by_image(
    url="https://example.com/patent_diagram.jpg",
    patent_type="D",  # Design patents
    model=1,  # Smart Recommendation
    limit=50
)

# Multi-image comprehensive search
multi_results = patsnap.patents.search.by_multiple_images(
    urls=[
        "https://example.com/front_view.jpg",
        "https://example.com/back_view.jpg",
        "https://example.com/side_view.jpg"
    ],
    patent_type="D",
    model=1,
    limit=75
)
```

### Analytics Operations
```python
# Get patent count
count = patsnap.analytics.search.count(
    query_text="TACD: artificial intelligence"
)

# Execute analytics query
results = patsnap.analytics.search.query(
    query_text="TACD: machine learning",
    limit=100
)

# Get field statistics
stats = patsnap.analytics.search.filter(
    query="TTL: blockchain",
    field="ASSIGNEE",
    limit=50
)
```

### Image Upload Workflow
```python
# Upload image and get public URL
upload_result = patsnap.patents.search.upload_image(
    image="path/to/patent_diagram.jpg"
)

# Use uploaded image for search
search_results = patsnap.patents.search.by_image(
    url=upload_result.url,
    patent_type="U",  # Utility patents
    model=4,  # Shape & color
    limit=30
)
```

## 🛠️ CLI Interface

The SDK includes a powerful command-line interface for API exploration:

```bash
# Show all available namespaces and methods
patsnap help

# Get detailed help for specific operations
patsnap help patents.search
patsnap help analytics.search

# Explore method details
patsnap help patents.search.by_image
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Implementation Documentation](docs/implementation/)
- [CLI Usage Guide](docs/CLI_USAGE.md)
- [Patent Search Examples](examples/patents/)
- [Analytics Examples](examples/analytics/)

## 📋 Complete Endpoint Checklist

### 🔍 Patent Search Operations (`patsnap.patents.search`)
- ✅`by_number()` - [P069] Patent Number Search (requires higher subscription)
- ✅ `by_original_assignee()` - [P004] Original Applicant Search
- ✅ `by_current_assignee()` - [P005] Current Assignee Search  
- 🔧 `by_defense_applicant()` - [P006] Defense Patent Search
- ✅ `by_similarity()` - [P007] Similar Patent Search
- ✅ `by_semantic_text()` - [P008] Semantic Search
- ✅ `upload_image()` - [P010] Image Upload
- 🔧 `by_image()` - [P060] Single Image Search
- 🔧 `by_multiple_images()` - [P061] Multiple Image Search

### 📊 Analytics Operations (`patsnap.analytics.search`)
- ✅ `query_count()` - [P001] Analytics Query Count
- ✅ `query_search()` - [P002] Analytics Query Search  
- ✅ `query_filter()` - [P003] Analytics Query Filter

### 📄 Patent Data Operations (`patsnap.patents.data`) - *Planned*
- 🚧 `simple_biblio()` - [P011] Simple Biblio
- 🚧 `biblio()` - [P012] Full Biblio
- 🚧 `legal_status()` - [P013] Legal Status
- 🚧 `family()` - [P014] Patent Family
- 🚧 `cited_by()` - [P015] Cited By Patents
- 🚧 `citations()` - [P016] Patent Citations
- 🚧 `claims()` - [P018] Claims
- 🚧 `description()` - [P019] Description
- 🚧 `pdf()` - [P020] PDF Download

### 🧠 AI Operations (`patsnap.ai`) - *Planned*
- 🚧 `agent.create_weekly_brief()` - [AI63-1] Weekly Brief
- 🚧 `agent.create_monthly_brief()` - [AI63-2] Monthly Brief
- 🚧 `ocr.create_task()` - [AI60] OCR Recognition
- 🚧 `translation.translate()` - [AI61] AI Translation
- 🚧 `ner.drug_entities()` - [AI01] Drug NER
- 🚧 `analysis.technical_qa()` - [AI36-1] Technical Q&A

### 🏢 Company Analytics (`patsnap.analytics.companies`) - *Planned*
- 🚧 `word_cloud()` - [A101] Innovation Word Cloud
- 🚧 `strategy_radar()` - [A102] Portfolio Strategy Radar
- 🚧 `key_technologies()` - [A103] Key Technologies
- 🚧 `trends()` - [A104] Application Trends
- 🚧 `portfolio_overview()` - [A105] Portfolio Overview

### 💊 Drug & Life Sciences (`patsnap.drugs`) - *Planned*
- 🚧 `search.general()` - [B007] Drug Search
- 🚧 `search.core_patents()` - [B009] Core Patent Search
- 🚧 `search.literature()` - [B011] Literature Search
- 🚧 `search.clinical_trials()` - [B012] Clinical Trials
- 🚧 `data.basic_info()` - [B018] Drug Basic Info

**Legend:**
- ✅ **Working** - Tested and functional
- ⚠️ **Limited** - Requires higher API subscription
- 🔧 **Implemented** - Code complete, needs testing
- 🚧 **Planned** - Not yet implemented

*Total: 250+ endpoints planned | Current: 11 implemented |*

## 🔧 Requirements

- Python 3.8+
- Valid Patsnap API credentials
- Internet connection for API access

## ⚖️ License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Development setup and guidelines
- Code standards and testing requirements
- How to implement new endpoints
- Documentation and example requirements

## ⚠️ Important Notes

- **Unofficial SDK**: While the author works for Patsnap, this is not officially supported by Patsnap
- **API Compliance**: Ensure your usage complies with Patsnap's terms of service
- **Rate Limits**: Respect API rate limits and usage guidelines
- **Data Privacy**: Handle patent and proprietary data responsibly
- **Testing**: Always test thoroughly in development before production use

## 📞 Support & Community

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- **Examples**: Comprehensive examples available in the [examples/](examples/) directory

---
