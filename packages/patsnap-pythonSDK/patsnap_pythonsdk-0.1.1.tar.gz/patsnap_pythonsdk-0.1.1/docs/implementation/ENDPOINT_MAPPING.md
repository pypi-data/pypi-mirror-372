# Endpoint Code to Namespace Mapping

## AI Operations (`patsnap.ai`)

### AI Agent
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [AI64-1] | `patsnap.ai.agent.create_weekly_differentiation()` | Create AI Weekly Differentiation Analysis |
| [AI64-3] | `patsnap.ai.agent.get_differentiation_content()` | Get AI Differentiation Analysis Content |
| [AI63-1] | `patsnap.ai.agent.create_weekly_brief()` | Create AI Weekly Brief |
| [AI63-2] | `patsnap.ai.agent.create_monthly_brief()` | Create AI Monthly Brief |
| [AI63-3] | `patsnap.ai.agent.get_interpretation()` | Get AI Interpretation Content |
| [AI64-2] | `patsnap.ai.agent.create_monthly_differentiation()` | Create AI Monthly Differentiation Analysis |

### AI Processing
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [AI60] | `patsnap.ai.ocr.create_task()` | Create an OCR recognition task |
| [AI60] | `patsnap.ai.ocr.download_results()` | Download OCR recognition results |
| [AI61] | `patsnap.ai.translation.translate()` | AI Translation |
| [AI01] | `patsnap.ai.ner.drug_entities()` | Drug DDT NER |
| [AI11] | `patsnap.ai.ner.news_entities()` | News Entity Recognition |

### AI Analysis & Reports
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [AI33-1] | `patsnap.ai.analysis.create_solution()` | Find-solution Creation |
| [AI33-2] | `patsnap.ai.analysis.query_solution()` | Find-solution Query |
| [AI34] | `patsnap.ai.reports.create_quick_search()` | Quick-search report creation |
| [AI34] | `patsnap.ai.reports.query_quick_search()` | Quick-search report Query |
| [AI35-1] | `patsnap.ai.reports.novelty_tech_features()` | Novelty-search tech features |
| [AI35-2] | `patsnap.ai.reports.novelty_create_query()` | Novelty-search create search query |
| [AI35-3] | `patsnap.ai.reports.novelty_search()` | Novelty-search query |
| [AI35-4] | `patsnap.ai.reports.novelty_create_report()` | Novelty-search Create a report |
| [AI35-5] | `patsnap.ai.reports.novelty_download()` | Novelty-search download report |
| [AI36-1] | `patsnap.ai.analysis.technical_qa()` | Technical Q&A |
| [AI36-2] | `patsnap.ai.analysis.technical_qa_result()` | Technical Q&A Result |
| [AI39-1] | `patsnap.ai.analysis.create_infringement_detection()` | Infringement detection search creation |
| [AI39-2] | `patsnap.ai.analysis.query_infringement_detection()` | Infringement detection search query |
| [AI40-1] | `patsnap.ai.analysis.create_feasibility()` | Solution feasibility analysis creation |
| [AI40-2] | `patsnap.ai.analysis.query_feasibility()` | Solution feasibility analysis query |

## Patent Operations (`patsnap.patents`)

### Patent Search
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [P069] | `patsnap.patents.search.by_number()` | Patsnap Standard Patent Number Search |
| [P001] | `patsnap.patents.search.analytics_count()` | Analytics Query Search Count |
| [P002] | `patsnap.patents.search.analytics_query()` | Analytics Query Search |
| [P003] | `patsnap.patents.search.analytics_filtered()` | Analytics Query Search and Filter |
| [P004] | `patsnap.patents.search.by_original_applicant()` | Original Applicant Search |
| [P005] | `patsnap.patents.search.by_current_assignee()` | Current Assignee Search |
| [P006] | `patsnap.patents.search.defense_patents()` | Current Assignee Search Defense Patent |
| [P007] | `patsnap.patents.search.similar_by_number()` | Patent Number Search Similar Patent |
| [P008] | `patsnap.patents.search.similar_semantic()` | Semantic Search Similar Patent |
| [P010] | `patsnap.patents.search.image_url()` | Image Search Get Image Url |
| [P060] | `patsnap.patents.search.similar_by_single_image()` | Image Search Similar Patent - Single image |
| [P061] | `patsnap.patents.search.similar_by_multiple_images()` | Image Search Similar Patent - Multiple images |

### Patent Data
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [P011] | `patsnap.patents.data.simple_biblio()` | Simple Biblio |
| [P012] | `patsnap.patents.data.biblio()` | Biblio |
| [P013] | `patsnap.patents.data.legal_status()` | Patent Legal Status |
| [P014] | `patsnap.patents.data.family()` | Patent Family |
| [P015] | `patsnap.patents.data.cited_by()` | Cited By Patents |
| [P016] | `patsnap.patents.data.citations()` | Patent Citation |
| [P018] | `patsnap.patents.data.claims()` | Claim |
| [P019] | `patsnap.patents.data.description()` | Description |
| [P020] | `patsnap.patents.data.pdf()` | PDF |
| [P021] | `patsnap.patents.data.abstract_image()` | Abstract Image |
| [P041] | `patsnap.patents.data.simple_legal_status()` | Simple Legal Status |
| [P042] | `patsnap.patents.data.fulltext_image()` | Fulltext Image |
| [P043] | `patsnap.patents.data.abstract_translated()` | Abstract (Translated) |
| [P044] | `patsnap.patents.data.claims_translated()` | Claim (Translated) |
| [P045] | `patsnap.patents.data.description_translated()` | Description (Translated) |

### Patent Analysis
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [P100] | `patsnap.patents.analysis.claim_similarity()` | Claim Similarity Analysis |
| [P101] | `patsnap.patents.analysis.claim_parser()` | Claim Parser |
| [P102] | `patsnap.patents.analysis.claim_charting()` | Claim Charting Analysis |
| [P063] | `patsnap.patents.analysis.intelligent_images()` | Patent intelligent attached image |

## Analytics & Reports (`patsnap.analytics`)

### Trend Analysis
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [A011] | `patsnap.analytics.trends.patent_type()` | Patent Type Trend Analysis |
| [A001] | `patsnap.analytics.trends.application_issued()` | Application and Issued Trend |

### Innovation Analysis
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [A002] | `patsnap.analytics.innovation.word_cloud()` | Innovation Word Cloud |
| [A003] | `patsnap.analytics.innovation.wheel()` | Wheel of Innovation |
| [A004] | `patsnap.analytics.innovation.top_authorities()` | Top authorities of Origin |
| [A005] | `patsnap.analytics.innovation.most_cited()` | Most Cited Patents |
| [A006] | `patsnap.analytics.innovation.top_inventors()` | Top Inventors |
| [A007] | `patsnap.analytics.innovation.top_assignees()` | Top Assignees |

### Company Analysis
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [A101] | `patsnap.analytics.companies.word_cloud()` | Company Innovation Word Cloud |
| [A102] | `patsnap.analytics.companies.strategy_radar()` | Company Portfolio Strategy Radar Map |
| [A103] | `patsnap.analytics.companies.key_technologies()` | Company Key Technologies |
| [A104] | `patsnap.analytics.companies.trends()` | Company Patent Application and Issued Trend |
| [A105] | `patsnap.analytics.companies.portfolio_overview()` | Company Patent Portfolio Overview |
| [A106] | `patsnap.analytics.companies.most_cited()` | Company Most Cited Patents |
| [A107] | `patsnap.analytics.companies.citing_companies()` | Most Citing Companies |
| [A108] | `patsnap.analytics.companies.largest_families()` | Company Largest Invention Families |
| [A109] | `patsnap.analytics.companies.legal_status()` | Company Patent Simple Legal Status |
| [A110] | `patsnap.analytics.companies.transfers()` | Company Patent Transfer In or Transfer Out |

## Drug & Life Sciences (`patsnap.drugs`)

### Drug Search
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [B007] | `patsnap.drugs.search.general()` | Drug search |
| [B009] | `patsnap.drugs.search.core_patents()` | Drug core patent search |
| [B010] | `patsnap.drugs.search.related_patents()` | Drug related patent search |
| [B011] | `patsnap.drugs.search.literature()` | Medical Literature Search |
| [B012] | `patsnap.drugs.search.clinical_trials()` | Clinical Trial Search |
| [B043] | `patsnap.drugs.search.news()` | Medical News Search |
| [B044] | `patsnap.drugs.search.clinical_results()` | clinical result search |
| [B045] | `patsnap.drugs.search.deals()` | Medical Deal Search |

### Drug Data
| Current Code | New API Method | Description |
|--------------|----------------|-------------|
| [B018] | `patsnap.drugs.data.basic_info()` | Drug basic information |
| [B019] | `patsnap.drugs.data.approval()` | Drug approval information |
| [B020] | `patsnap.drugs.data.development_status()` | Drug Dev Status |
| [B021] | `patsnap.drugs.data.regulatory_review()` | Drug Regulatory Review |
| [B040] | `patsnap.drugs.data.target_basic()` | Target basic information |
| [B041] | `patsnap.drugs.data.target_analysis()` | Target analysis |
| [B047] | `patsnap.drugs.data.xdc()` | Drug xdc |
| [B059] | `patsnap.drugs.data.approval_file()` | Drug approval file |

This mapping transforms cryptic codes into intuitive, discoverable API methods! 🎯
