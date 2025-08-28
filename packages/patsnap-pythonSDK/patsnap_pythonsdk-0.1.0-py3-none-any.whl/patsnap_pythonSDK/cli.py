#!/usr/bin/env python3
"""
Patsnap SDK Command Line Interface

Provides help and information about the Patsnap SDK namespaces and endpoints.
"""

import sys
import argparse
from typing import Dict, List, Any
import inspect
import os
from pathlib import Path

def discover_implemented_namespaces() -> List[str]:
    """Discover which namespaces are actually implemented by checking the namespaces directory."""
    try:
        # Try to find the namespaces directory relative to this file
        current_dir = Path(__file__).parent
        namespaces_dir = current_dir / "namespaces"
        
        if not namespaces_dir.exists():
            # Fallback to checking from current working directory
            namespaces_dir = Path("patsnap_pythonSDK/namespaces")
        
        if not namespaces_dir.exists():
            return ["patents", "analytics"]  # Fallback to known implemented ones
        
        implemented = []
        for file in namespaces_dir.glob("*.py"):
            if file.name != "__init__.py":
                namespace_name = file.stem
                implemented.append(namespace_name)
        
        return implemented
    except Exception:
        return ["patents", "analytics"]  # Fallback to known implemented ones


def get_namespace_info() -> Dict[str, Dict[str, Any]]:
    """Get information about all available namespaces and their methods."""
    
    # Get actually implemented namespaces
    implemented = discover_implemented_namespaces()
    
    all_namespaces = {
        "patents": {
            "description": "Patent operations - search, data retrieval, legal information",
            "categories": {
                "search": {
                    "description": "Patent search operations",
                                            "methods": {
                            "by_number": "Search patents by patent number or application number",
                            "by_original_assignee": "Search patents by original applicant/assignee names",
                            "by_current_assignee": "Search patents by current assignee names",
                            "by_defense_applicant": "Search defense/military patents by applicant names",
                            "by_similarity": "Find patents similar to a given patent by ID or number",
                            "by_semantic_text": "Search patents using semantic analysis of technical text",
                            "upload_image": "Upload patent images and get public URLs for image search",
                            "by_image": "Search patents using image similarity analysis",
                            "by_multiple_images": "Search patents using multiple image similarity analysis (up to 4 images)"
                        }
                },
                "data": "Patent data retrieval (biblio, legal status, citations, etc.)",
                "legal": "Legal information (litigation, licenses, transfers)",
                "valuation": "Patent valuation and market indicators",
                "classification": "Patent classification data"
            },
            "example": "patsnap.patents.search.by_number(pn='US123456')"
        },
        "analytics": {
            "description": "Patent analytics, trends, and statistical analysis",
            "categories": {
                "search": {
                    "description": "Analytics search operations",
                    "methods": {
                        "query_count": "Get total patent count for analytics queries",
                        "query_search": "Search patents using analytics queries with full data",
                        "query_filter": "Get aggregated field statistics from analytics queries"
                    }
                },
                "trends": "Patent application and publication trends",
                "companies": "Company patent portfolios and strategies",
                "innovation": "Innovation metrics and analysis"
            },
            "example": "patsnap.analytics.search.query_count(query_text='TACD: AI')"
        },
        "ai": {
            "description": "AI-powered analysis, processing, and report generation",
            "categories": {
                "agent": "AI agent operations (weekly/monthly analysis)",
                "ocr": "OCR recognition and processing",
                "translation": "AI translation services",
                "reports": "AI report generation (novelty search, infringement detection)",
                "analysis": "AI analysis operations (technical Q&A, feasibility)"
            },
            "example": "patsnap.ai.agent.create_weekly_analysis(topic='AI patents')"
        },
        "drugs": {
            "description": "Drug research, clinical trials, and pharmaceutical data",
            "categories": {
                "search": "Drug and pharmaceutical search operations",
                "data": "Drug basic information and approval data",
                "clinical": "Clinical trial data and analysis",
                "organizations": "R&D organization pipelines and deals",
                "dictionary": "Drug dictionaries and ID lookups"
            },
            "example": "patsnap.drugs.search.clinical_trials(drug_name='aspirin')"
        },
        "literature": {
            "description": "Academic literature search and research analysis",
            "categories": {
                "search": "Literature and paper search operations",
                "data": "Literature data (citations, authors, journals)"
            },
            "example": "patsnap.literature.search.query(keywords='machine learning')"
        },
        "chemical": {
            "description": "Chemical structure and biological sequence analysis",
            "categories": {
                "structure": "Chemical structure search and analysis",
                "sequence": "Biological sequence analysis and extraction"
            },
            "example": "patsnap.chemical.structure.search(smiles='CCO')"
        },
        "monitoring": {
            "description": "Project monitoring and data export operations",
            "categories": {
                "projects": "Monitor project management",
                "exports": "Data export operations"
            },
            "example": "patsnap.monitoring.projects.create(name='AI Monitor')"
        }
    }
    
    # Return only implemented namespaces, but include all for planning
    result = {}
    for namespace, info in all_namespaces.items():
        if namespace in implemented:
            info["status"] = "Implemented"
        else:
            info["status"] = "Planned"
        result[namespace] = info
    
    return result


def print_header():
    """Print the CLI header."""
    print("Patsnap Python SDK - Command Line Help")
    print("=" * 50)


def print_overview():
    """Print SDK overview."""
    print("\nOverview:")
    print("The Patsnap SDK provides access to patent data, analytics, AI analysis,")
    print("drug research, literature search, and more through a clean namespace-based API.")
    print("\nQuick Start:")
    print("  import patsnap_pythonSDK as patsnap")
    print("  patsnap.configure(client_id='...', client_secret='...')")
    print("  results = patsnap.patents.search.by_number(pn='US123456')")


def print_all_namespaces():
    """Print information about all namespaces."""
    namespaces = get_namespace_info()
    
    print("\nAvailable Namespaces:")
    print("-" * 30)
    
    for namespace, info in namespaces.items():
        status = info.get('status', 'Unknown')
        print(f"\n{namespace.upper()} [{status}]")
        print(f"   {info['description']}")
        
        if isinstance(info['categories'], dict):
            print("   Categories:")
            for category, cat_info in info['categories'].items():
                if isinstance(cat_info, dict) and 'methods' in cat_info:
                    print(f"     * {category}: {cat_info['description']}")
                    for method, method_desc in cat_info['methods'].items():
                        print(f"       - {method}(): {method_desc}")
                else:
                    print(f"     * {category}: {cat_info}")
        
        print(f"   Example: {info['example']}")


def print_namespace_details(namespace: str):
    """Print detailed information about a specific namespace."""
    namespaces = get_namespace_info()
    
    if namespace not in namespaces:
        print(f"Error: Unknown namespace: {namespace}")
        print(f"Available namespaces: {', '.join(namespaces.keys())}")
        return
    
    info = namespaces[namespace]
    status = info.get('status', 'Unknown')
    print(f"\n{namespace.upper()} Namespace [{status}]")
    print("=" * 40)
    print(f"Description: {info['description']}")
    
    print(f"\nCategories:")
    if isinstance(info['categories'], dict):
        for category, cat_info in info['categories'].items():
            print(f"\n  {category}")
            if isinstance(cat_info, dict) and 'description' in cat_info:
                print(f"     {cat_info['description']}")
                if 'methods' in cat_info:
                    print("     Available methods:")
                    for method, method_desc in cat_info['methods'].items():
                        print(f"       * {method}(): {method_desc}")
            else:
                print(f"     {cat_info}")
    
    print(f"\nExample Usage:")
    print(f"  {info['example']}")
    
    print(f"\nMore Information:")
    print(f"  * Examples: examples/{namespace}/")
    print(f"  * Tests: tests/{namespace}/")
    print(f"  * Documentation: docs/implementation/")


def print_usage_examples():
    """Print common usage examples."""
    print("\nCommon Usage Examples:")
    print("-" * 30)
    
    examples = [
        {
            "title": "Patent Search",
            "code": [
                "# Search for patents by number",
                "results = patsnap.patents.search.by_number(",
                "    pn='US11205304B2',",
                "    authority=['US'],",
                "    limit=10",
                ")"
            ]
        },
        {
            "title": "Analytics Query",
            "code": [
                "# Get patent count for a technology",
                "count = patsnap.analytics.search.query_count(",
                "    query_text='TACD: artificial intelligence',",
                "    stemming=1",
                ")"
            ]
        },
        {
            "title": "Full Analytics Search",
            "code": [
                "# Search with full patent data",
                "results = patsnap.analytics.search.query_search(",
                "    query_text='TACD: blockchain',",
                "    limit=20,",
                "    sort=[{'field': 'SCORE', 'order': 'DESC'}]",
                ")"
            ]
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        for line in example['code']:
            print(f"  {line}")


def print_getting_started():
    """Print getting started guide."""
    print("\nGetting Started:")
    print("-" * 20)
    print("1. Install the SDK:")
    print("   pip install patsnap-pythonsdk")
    print("\n2. Configure your credentials:")
    print("   import patsnap_pythonSDK as patsnap")
    print("   patsnap.configure(")
    print("       client_id='your_client_id',")
    print("       client_secret='your_client_secret'")
    print("   )")
    print("\n3. Start using the API:")
    print("   results = patsnap.patents.search.by_number(pn='US123456')")
    print("   print(f'Found {len(results.results)} patents')")
    print("\n4. Explore examples:")
    print("   python examples/patents/search_by_number.py")
    print("   python examples/analytics/query_search_count.py")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Patsnap SDK Command Line Help",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='help',
        choices=['help', 'namespaces', 'examples', 'start'],
        help='Command to run (default: help)'
    )
    
    parser.add_argument(
        '--namespace',
        '-n',
        help='Show detailed information about a specific namespace'
    )
    
    parser.add_argument(
        '--list',
        '-l',
        action='store_true',
        help='List all available namespaces'
    )
    
    args = parser.parse_args()
    
    print_header()
    
    if args.namespace:
        print_namespace_details(args.namespace)
    elif args.list or args.command == 'namespaces':
        print_all_namespaces()
    elif args.command == 'examples':
        print_usage_examples()
    elif args.command == 'start':
        print_getting_started()
    else:
        # Default help
        print_overview()
        print_all_namespaces()
        print_usage_examples()
        print_getting_started()
        
        print("\nAdditional Commands:")
        print("  patsnap help namespaces  - List all namespaces")
        print("  patsnap help examples    - Show usage examples")  
        print("  patsnap help start       - Getting started guide")
        print("  patsnap help -n patents  - Details about patents namespace")
        print("  patsnap help --list      - List all namespaces")


if __name__ == "__main__":
    main()
