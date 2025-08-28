"""
Example usage of analytics query search count endpoint.

This demonstrates how to get total search patent count for analytics queries
using PatSnap's global patent database with various search parameters.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_query_count():
    """Basic analytics query search count."""
    print("=== Basic Analytics Query Search Count ===")
    
    try:
        # Simple query count
        result = patsnap.analytics.search.query_count(
            query_text="TACD: virtual reality"
        )
        
        print(f"Query: 'TACD: virtual reality'")
        print(f"Total patent count: {result.total_search_result_count:,}")
        
    except Exception as e:
        print(f"Error in basic query count: {e}")


def advanced_query_count():
    """Advanced analytics query with collapse and stemming options."""
    print("\n=== Advanced Analytics Query with Options ===")
    
    try:
        # Advanced query with collapse and stemming
        result = patsnap.analytics.search.query_count(
            query_text="TACD: artificial intelligence AND machine learning",
            collapse_by="PBD",  # Collapse by publication date
            collapse_order="LATEST",  # Keep latest patents
            stemming=1,  # Enable stemming
            collapse_type="DOCDB"  # Use simple family collapse
        )
        
        print(f"Query: 'TACD: artificial intelligence AND machine learning'")
        print(f"Collapse by: Publication Date (Latest)")
        print(f"Stemming: Enabled")
        print(f"Collapse type: DOCDB (Simple Family)")
        print(f"Total patent count: {result.total_search_result_count:,}")
        
    except Exception as e:
        print(f"Error in advanced query count: {e}")


def authority_based_collapse():
    """Query count with authority-based collapse ordering."""
    print("\n=== Authority-Based Collapse Example ===")
    
    try:
        # Query with authority priority collapse
        result = patsnap.analytics.search.query_count(
            query_text="TACD: renewable energy OR solar power",
            collapse_by="AUTHORITY",  # Collapse by authority
            collapse_order_authority=["US", "CN", "EP", "JP", "KR"],  # Authority priority
            collapse_type="INPADOC"  # Use INPADOC family collapse
        )
        
        print(f"Query: 'TACD: renewable energy OR solar power'")
        print(f"Collapse by: Authority")
        print(f"Authority priority: US > CN > EP > JP > KR")
        print(f"Collapse type: INPADOC Family")
        print(f"Total patent count: {result.total_search_result_count:,}")
        
    except Exception as e:
        print(f"Error in authority-based collapse: {e}")


def compare_different_queries():
    """Compare patent counts for different technology areas."""
    print("\n=== Technology Area Comparison ===")
    
    technologies = [
        "TACD: blockchain",
        "TACD: quantum computing",
        "TACD: 5G technology",
        "TACD: electric vehicle",
        "TACD: gene therapy"
    ]
    
    results = {}
    
    for tech_query in technologies:
        try:
            result = patsnap.analytics.search.query_count(
                query_text=tech_query,
                collapse_by="APD",  # Collapse by application date
                collapse_order="LATEST",
                stemming=1
            )
            
            # Extract technology name for display
            tech_name = tech_query.replace("TACD: ", "").title()
            results[tech_name] = result.total_search_result_count
            
        except Exception as e:
            print(f"Error querying {tech_query}: {e}")
    
    # Display results sorted by count
    print("\nTechnology Patent Counts (with stemming and latest collapse):")
    for tech, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tech:<20}: {count:>8,} patents")


def stemming_comparison():
    """Compare results with and without stemming."""
    print("\n=== Stemming Effect Comparison ===")
    
    query = "TACD: computer AND processing"
    
    try:
        # Without stemming
        result_no_stem = patsnap.analytics.search.query_count(
            query_text=query,
            stemming=0
        )
        
        # With stemming
        result_with_stem = patsnap.analytics.search.query_count(
            query_text=query,
            stemming=1
        )
        
        print(f"Query: '{query}'")
        print(f"Without stemming: {result_no_stem.total_search_result_count:,} patents")
        print(f"With stemming:    {result_with_stem.total_search_result_count:,} patents")
        
        difference = result_with_stem.total_search_result_count - result_no_stem.total_search_result_count
        percentage = (difference / result_no_stem.total_search_result_count) * 100 if result_no_stem.total_search_result_count > 0 else 0
        
        print(f"Difference:       {difference:+,} patents ({percentage:+.1f}%)")
        
    except Exception as e:
        print(f"Error in stemming comparison: {e}")


def collapse_type_comparison():
    """Compare different collapse types for the same query."""
    print("\n=== Collapse Type Comparison ===")
    
    query = "TACD: smartphone AND camera"
    collapse_types = ["ALL", "APNO", "DOCDB", "INPADOC", "EXTEND"]
    
    print(f"Query: '{query}'")
    print("Collapse Type Results:")
    
    for collapse_type in collapse_types:
        try:
            result = patsnap.analytics.search.query_count(
                query_text=query,
                collapse_type=collapse_type,
                collapse_by="PBD" if collapse_type != "ALL" else None,
                collapse_order="LATEST" if collapse_type != "ALL" else None
            )
            
            print(f"  {collapse_type:<8}: {result.total_search_result_count:>8,} patents")
            
        except Exception as e:
            print(f"  {collapse_type:<8}: Error - {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation error - query too long
    try:
        long_query = "TACD: " + "artificial intelligence " * 100  # Very long query
        result = patsnap.analytics.search.query_count(query_text=long_query)
    except Exception as e:
        print(f"Long query error (expected): {type(e).__name__}: {str(e)[:100]}...")
    
    # Test validation error - missing required parameter
    try:
        result = patsnap.analytics.search.query_count()  # Missing query_text
    except Exception as e:
        print(f"Missing parameter error (expected): {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("Patsnap Analytics Query Search Count Examples")
    print("=" * 50)
    
    basic_query_count()
    advanced_query_count()
    authority_based_collapse()
    compare_different_queries()
    stemming_comparison()
    collapse_type_comparison()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.analytics.search.query_count()")
    print("- Get total patent counts for analytics queries")
    print("- Support for various collapse and stemming options")
    print("- Full parameter validation and error handling")
    print("- Clean, discoverable namespace-based API")
