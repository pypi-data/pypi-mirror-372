"""
Example usage of analytics query search endpoint.

This demonstrates how to search PatSnap's global patent database using analytics queries
and retrieve full patent data including titles, assignees, inventors, and more.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_analytics_search():
    """Basic analytics query search with patent data."""
    print("=== Basic Analytics Query Search ===")
    
    try:
        # Simple search with default sorting
        results = patsnap.analytics.search.query_search(
            query_text="TACD: virtual reality",
            limit=5
        )
        
        print(f"Query: 'TACD: virtual reality'")
        print(f"Found {results.data.total_search_result_count:,} total patents")
        print(f"Showing {results.data.result_count} results:")
        
        for i, patent in enumerate(results.data.results, 1):
            print(f"\n{i}. {patent.title}")
            print(f"   Patent Number: {patent.pn}")
            print(f"   Assignee: {patent.current_assignee}")
            print(f"   Inventor: {patent.inventor}")
            print(f"   Application Date: {patent.apdt}")
            
    except Exception as e:
        print(f"Error in basic search: {e}")


def advanced_search_with_sorting():
    """Advanced search with custom sorting and parameters."""
    print("\n=== Advanced Search with Sorting ===")
    
    try:
        # Advanced search with publication date sorting
        results = patsnap.analytics.search.query_search(
            query_text="TACD: artificial intelligence AND machine learning",
            limit=10,
            sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}],
            collapse_by="PBD",
            collapse_order="LATEST",
            stemming=1
        )
        
        print(f"Query: 'TACD: artificial intelligence AND machine learning'")
        print(f"Sorted by: Publication Date (Latest First)")
        print(f"Stemming: Enabled")
        print(f"Found {results.data.total_search_result_count:,} total patents")
        
        for patent in results.data.results[:3]:  # Show first 3
            pub_date = str(patent.pbdt)
            formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
            print(f"- {patent.title[:60]}...")
            print(f"  {patent.pn} | Published: {formatted_date} | {patent.current_assignee}")
            
    except Exception as e:
        print(f"Error in advanced search: {e}")


def paginated_search():
    """Demonstrate pagination through search results."""
    print("\n=== Paginated Search Example ===")
    
    query = "TACD: blockchain"
    page_size = 5
    max_pages = 3
    
    try:
        all_patents = []
        
        for page in range(max_pages):
            offset = page * page_size
            
            results = patsnap.analytics.search.query_search(
                query_text=query,
                limit=page_size,
                offset=offset,
                sort=[{"field": "SCORE", "order": "DESC"}]
            )
            
            print(f"Page {page + 1}: Found {len(results.data.results)} patents (offset: {offset})")
            
            for patent in results.data.results:
                all_patents.append(patent)
                print(f"  - {patent.pn}: {patent.title[:50]}...")
            
            # Check if we've reached the end
            if len(results.data.results) < page_size:
                print("  (Last page reached)")
                break
        
        print(f"\nTotal patents collected: {len(all_patents)}")
        print(f"Total available: {results.data.total_search_result_count:,}")
        
    except Exception as e:
        print(f"Error in paginated search: {e}")


def authority_based_search():
    """Search with authority-based collapse ordering."""
    print("\n=== Authority-Based Search ===")
    
    try:
        # Search with authority priority
        results = patsnap.analytics.search.query_search(
            query_text="TACD: renewable energy OR solar power",
            limit=8,
            collapse_by="AUTHORITY",
            collapse_order_authority=["US", "CN", "EP", "JP", "KR"],
            collapse_type="INPADOC"
        )
        
        print(f"Query: 'TACD: renewable energy OR solar power'")
        print(f"Authority Priority: US > CN > EP > JP > KR")
        print(f"Collapse Type: INPADOC Family")
        
        # Group by authority
        by_authority = {}
        for patent in results.data.results:
            # Extract authority from patent number
            authority = patent.pn[:2] if len(patent.pn) >= 2 else "Unknown"
            if authority not in by_authority:
                by_authority[authority] = []
            by_authority[authority].append(patent)
        
        print(f"\nResults by Authority:")
        for auth in ["US", "CN", "EP", "JP", "KR"]:
            if auth in by_authority:
                print(f"  {auth}: {len(by_authority[auth])} patents")
                for patent in by_authority[auth][:2]:  # Show first 2
                    print(f"    - {patent.pn}: {patent.current_assignee}")
        
    except Exception as e:
        print(f"Error in authority-based search: {e}")


def compare_different_technologies():
    """Compare patent counts and recent patents for different technologies."""
    print("\n=== Technology Comparison ===")
    
    technologies = [
        "TACD: quantum computing",
        "TACD: 5G technology", 
        "TACD: electric vehicle battery",
        "TACD: gene therapy"
    ]
    
    for tech_query in technologies:
        try:
            # Get recent patents for each technology
            results = patsnap.analytics.search.query_search(
                query_text=tech_query,
                limit=3,
                sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}],
                stemming=1
            )
            
            tech_name = tech_query.replace("TACD: ", "").title()
            print(f"\n{tech_name}:")
            print(f"  Total Patents: {results.data.total_search_result_count:,}")
            print(f"  Recent Patents:")
            
            for patent in results.data.results:
                pub_date = str(patent.pbdt)
                year = pub_date[:4]
                print(f"    - {patent.pn} ({year}): {patent.current_assignee}")
                
        except Exception as e:
            print(f"  Error querying {tech_query}: {e}")


def multi_field_sorting():
    """Demonstrate multiple field sorting."""
    print("\n=== Multi-Field Sorting Example ===")
    
    try:
        # Sort by publication date first, then by relevance score
        results = patsnap.analytics.search.query_search(
            query_text="TACD: smartphone AND camera",
            limit=6,
            sort=[
                {"field": "PBDT_YEARMONTHDAY", "order": "DESC"},
                {"field": "SCORE", "order": "DESC"}
            ]
        )
        
        print(f"Query: 'TACD: smartphone AND camera'")
        print(f"Sorted by: Publication Date (DESC), then Relevance Score (DESC)")
        print(f"Found {results.data.total_search_result_count:,} patents")
        
        for patent in results.data.results:
            pub_date = str(patent.pbdt)
            year = pub_date[:4]
            print(f"- {patent.pn} ({year}): {patent.title[:50]}...")
            print(f"  Assignee: {patent.current_assignee}")
        
    except Exception as e:
        print(f"Error in multi-field sorting: {e}")


def collapse_type_comparison():
    """Compare different collapse types for the same query."""
    print("\n=== Collapse Type Comparison ===")
    
    query = "TACD: artificial intelligence"
    collapse_types = ["ALL", "APNO", "DOCDB", "INPADOC"]
    
    print(f"Query: '{query}'")
    print("Collapse Type Results:")
    
    for collapse_type in collapse_types:
        try:
            results = patsnap.analytics.search.query_search(
                query_text=query,
                limit=5,
                collapse_type=collapse_type,
                collapse_by="PBD" if collapse_type != "ALL" else None
            )
            
            print(f"  {collapse_type:<8}: {results.data.total_search_result_count:>6,} patents, showing {results.data.result_count}")
            
            # Show a sample patent
            if results.data.results:
                sample = results.data.results[0]
                print(f"           Sample: {sample.pn} - {sample.current_assignee}")
            
        except Exception as e:
            print(f"  {collapse_type:<8}: Error - {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation errors
    try:
        results = patsnap.analytics.search.query_search()  # Missing query_text
    except Exception as e:
        print(f"Missing parameter error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.analytics.search.query_search(
            query_text="test",
            limit=2000  # Exceeds maximum of 1000
        )
    except Exception as e:
        print(f"Limit validation error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.analytics.search.query_search(
            query_text="test",
            offset=-1  # Negative offset
        )
    except Exception as e:
        print(f"Offset validation error (expected): {type(e).__name__}")


if __name__ == "__main__":
    print("Patsnap Analytics Query Search Examples")
    print("=" * 50)
    
    basic_analytics_search()
    advanced_search_with_sorting()
    paginated_search()
    authority_based_search()
    compare_different_technologies()
    multi_field_sorting()
    collapse_type_comparison()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.analytics.search.query_search()")
    print("- Search patents with analytics queries")
    print("- Get full patent data (titles, assignees, inventors, etc.)")
    print("- Support for sorting, pagination, and collapse options")
    print("- Clean, discoverable namespace-based API")
