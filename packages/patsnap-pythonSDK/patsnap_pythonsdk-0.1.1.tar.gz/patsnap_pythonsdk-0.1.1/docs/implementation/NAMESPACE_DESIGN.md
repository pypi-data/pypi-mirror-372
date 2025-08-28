# Patsnap SDK Namespace Design

## Overview
Based on the 250+ endpoints, here's a clean, intuitive namespace structure:

## 🎯 Main Namespaces

### 1. **AI Operations** (`patsnap.ai`)
```python
# AI Agent Operations
patsnap.ai.agent.create_weekly_analysis()
patsnap.ai.agent.create_monthly_analysis()
patsnap.ai.agent.get_interpretation()
patsnap.ai.agent.find_solution()

# AI Processing
patsnap.ai.ocr.create_task()
patsnap.ai.ocr.download_results()
patsnap.ai.translation.translate()
patsnap.ai.ner.extract_entities()

# AI Reports & Analysis
patsnap.ai.reports.quick_search()
patsnap.ai.reports.novelty_search()
patsnap.ai.reports.infringement_detection()
patsnap.ai.analysis.technical_qa()
patsnap.ai.analysis.feasibility()
```

### 2. **Patent Operations** (`patsnap.patents`)
```python
# Patent Search
patsnap.patents.search.by_number()           # [P069] Standard Patent Number
patsnap.patents.search.analytics_query()     # [P001-P003] Analytics Query
patsnap.patents.search.by_assignee()         # [P004-P005] Assignee Search
patsnap.patents.search.similar_patents()     # [P007-P008] Similar Patent
patsnap.patents.search.by_image()            # [P010, P060-P061] Image Search

# Patent Data
patsnap.patents.data.biblio()                # [P011-P012] Biblio
patsnap.patents.data.legal_status()          # [P013, P041] Legal Status
patsnap.patents.data.family()                # [P014] Patent Family
patsnap.patents.data.citations()             # [P015-P016] Citations
patsnap.patents.data.claims()                # [P018, P063] Claims
patsnap.patents.data.description()           # [P019] Description
patsnap.patents.data.pdf()                   # [P020] PDF

# Patent Legal
patsnap.patents.legal.information()          # [P026] Legal Information
patsnap.patents.legal.reexamination()        # [P027] Re-examination
patsnap.patents.legal.license()              # [P028] License
patsnap.patents.legal.transfer()             # [P029] Transfer
patsnap.patents.legal.litigation()           # [P034] Litigation

# Patent Valuation
patsnap.patents.valuation.overview()         # [P035] Patent Valuation
patsnap.patents.valuation.technology()       # [P036] Technology Indicators
patsnap.patents.valuation.market()           # [P038] Market Indicators

# Patent Classification
patsnap.patents.classification.seic()        # [P022] SEIC
patsnap.patents.classification.domain()      # [P023] Application Domain
patsnap.patents.classification.topic()       # [P024] Technology Topic
```

### 3. **Analytics & Reports** (`patsnap.analytics`)
```python
# Trend Analysis
patsnap.analytics.trends.application_issued() # [A001] Application and Issued Trend
patsnap.analytics.trends.patent_type()        # [A011] Patent Type Trend

# Innovation Analysis
patsnap.analytics.innovation.word_cloud()     # [A002] Innovation Word Cloud
patsnap.analytics.innovation.wheel()          # [A003] Wheel of Innovation
patsnap.analytics.innovation.top_authorities() # [A004] Top authorities

# Company Analysis
patsnap.analytics.companies.word_cloud()      # [A101] Company Innovation Word Cloud
patsnap.analytics.companies.strategy_radar()  # [A102] Company Portfolio Strategy
patsnap.analytics.companies.key_technologies() # [A103] Company Key Technologies
patsnap.analytics.companies.trends()          # [A104] Company Patent Trends

# Citation Analysis
patsnap.analytics.citations.most_cited()      # [A005] Most Cited Patents
patsnap.analytics.citations.citing_companies() # [A107] Most Citing Companies
```

### 4. **Literature & Research** (`patsnap.literature`)
```python
# Literature Search & Data
patsnap.literature.search.query()            # [L001] Literature Search
patsnap.literature.data.biblio()             # [L010] Literature Bibliographic
patsnap.literature.data.citations()          # [L012] Literature Citation
patsnap.literature.data.authors()            # [L011] Literature Author
patsnap.literature.data.journal()            # [L014] Journal
```

### 5. **Drug & Life Sciences** (`patsnap.drugs`)
```python
# Drug Search
patsnap.drugs.search.general()               # [B007] Drug search
patsnap.drugs.search.core_patents()          # [B009] Drug core patent search
patsnap.drugs.search.related_patents()       # [B010] Drug related patent search
patsnap.drugs.search.literature()            # [B011] Medical Literature Search
patsnap.drugs.search.clinical_trials()       # [B012] Clinical Trial Search

# Drug Data
patsnap.drugs.data.basic_info()              # [B018] Drug basic information
patsnap.drugs.data.approval()                # [B019] Drug approval information
patsnap.drugs.data.development_status()      # [B020] Drug Dev Status
patsnap.drugs.data.regulatory_review()       # [B021] Drug Regulatory Review

# Clinical Trials
patsnap.drugs.clinical.basic_info()          # [B022] Clinical trial basic information
patsnap.drugs.clinical.entities()            # [B023] Clinical trial related entity
patsnap.drugs.clinical.design()              # [B026] Clinical trial design
patsnap.drugs.clinical.results()             # [B032] Drug clinical result

# Organizations
patsnap.drugs.organizations.pipeline()       # [B033] Organization Pipeline
patsnap.drugs.organizations.basic_info()     # [B034] Organization basic information
patsnap.drugs.organizations.deals()          # [B039] Drug deal information

# Dictionary & IDs
patsnap.drugs.dictionary.drug_types()        # [B049] Drug type ID search
patsnap.drugs.dictionary.diseases()          # [B050] Disease ID search
patsnap.drugs.dictionary.targets()           # [B051] Target ID search
```

### 6. **Monitoring & Export** (`patsnap.monitoring`)
```python
# Project Management
patsnap.monitoring.projects.create()         # [P056] Create Patent Monitor Project
patsnap.monitoring.projects.edit()           # [P058] Edit Patent Monitor Project
patsnap.monitoring.projects.delete()         # [P059] Delete Patent Monitor Project
patsnap.monitoring.projects.status()         # [P057] Check Monitor Project Status

# Export Operations
patsnap.monitoring.exports.create_task()     # [P055] Create export task by query
patsnap.monitoring.exports.get_results()     # [P055] Get Export Results
```

### 7. **Chemical & Bio** (`patsnap.chemical`)
```python
# Chemical Structure
patsnap.chemical.structure.search()          # Chemical Structure Search
patsnap.chemical.structure.details()         # [B014] Chemical Structure Details

# Sequence Analysis
patsnap.chemical.sequence.motif_search()     # [B003] Motif Sequence Search
patsnap.chemical.sequence.normal_search()    # [B004] Normal Sequence Search
patsnap.chemical.sequence.extract_single()   # [B062] Extract Single Patent Sequence
patsnap.chemical.sequence.extract_multiple() # [B063] Extract Multiple Patent Sequence
```

## 🎨 API Design Principles

### 1. **Intuitive Hierarchy**
- Domain → Category → Action
- `patsnap.patents.search.by_number()`
- `patsnap.analytics.trends.application_issued()`

### 2. **Consistent Naming**
- Use clear, descriptive method names
- Avoid cryptic codes like [P069], [AI64-1]
- Group related functionality together

### 3. **Logical Grouping**
- **Search operations** under `.search`
- **Data retrieval** under `.data`
- **Analysis operations** under `.analytics`
- **Management operations** under `.projects`/`.exports`

### 4. **Scalable Structure**
- Easy to add new endpoints
- Clear separation of concerns
- Consistent patterns across domains

## 🚀 Usage Examples

```python
import patsnap_pythonSDK as patsnap

# Configure
patsnap.configure(client_id="...", client_secret="...")

# Patent operations
results = patsnap.patents.search.by_number(pn="US123456")
biblio = patsnap.patents.data.biblio(patent_id="123")
status = patsnap.patents.legal.information(patent_id="123")

# Analytics
trends = patsnap.analytics.trends.application_issued(query="AI")
companies = patsnap.analytics.companies.word_cloud(assignee="Google")

# AI operations
analysis = patsnap.ai.agent.create_weekly_analysis(topic="AI")
ocr_task = patsnap.ai.ocr.create_task(image_url="...")

# Drug research
drug_info = patsnap.drugs.data.basic_info(drug_id="123")
trials = patsnap.drugs.clinical.basic_info(drug_name="aspirin")

# Literature
papers = patsnap.literature.search.query(keywords="machine learning")
citations = patsnap.literature.data.citations(paper_id="123")
```

This structure transforms 250+ cryptic endpoints into an intuitive, discoverable API! 🎉
