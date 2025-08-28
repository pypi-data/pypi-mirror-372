# Analytics Examples

Examples for patent analytics and trend analysis operations.

## Available Examples

- **query_search_count.py** - Get total search patent count for analytics queries
- **query_search.py** - Search patents using analytics queries and get full patent data
- **query_filter.py** - Get aggregated field statistics from analytics queries

## Planned Examples

- **trends_analysis.py** - Application and issued trends
- **company_analysis.py** - Company patent portfolios and strategies  
- **innovation_metrics.py** - Innovation word clouds and metrics
- **citation_analysis.py** - Patent citation patterns

## API Preview

```python
import patsnap_pythonSDK as patsnap

# Configure credentials
patsnap.configure(client_id="...", client_secret="...")

# Trend analysis
trends = patsnap.analytics.trends.application_issued(query="AI")
companies = patsnap.analytics.companies.word_cloud(assignee="Google")
citations = patsnap.analytics.innovation.most_cited(technology="machine learning")
```
