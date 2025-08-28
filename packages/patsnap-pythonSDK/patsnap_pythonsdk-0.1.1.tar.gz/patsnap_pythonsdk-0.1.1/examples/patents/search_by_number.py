"""
Example usage of patent search by number endpoint.

This demonstrates how to search for patents using patent numbers
or application numbers with the new namespace-based API.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_patent_search():
    """Basic patent search by patent number."""
    print("=== Basic Patent Search by Number ===")
    
    try:
        # Search for a specific patent
        results = patsnap.patents.search.by_number(
            pn="US11205304B2",
            authority=["US"],
            limit=10
        )
        
        print(f"Found {results.total_search_result_count} total patents")
        print(f"Showing {results.result_count} results:")
        
        for i, patent in enumerate(results.results, 1):
            print(f"\n{i}. {patent.title}")
            print(f"   Patent Number: {patent.pn}")
            print(f"   Application Number: {patent.apno}")
            print(f"   Current Assignee: {patent.current_assignee}")
            print(f"   Inventor: {patent.inventor}")
            print(f"   Application Date: {patent.apdt}")
            print(f"   Publication Date: {patent.pbdt}")
            
    except Exception as e:
        print(f"Error in basic search: {e}")


def search_by_application_number():
    """Search patents by application number."""
    print("\n=== Search by Application Number ===")
    
    try:
        results = patsnap.patents.search.by_number(
            apno="US17/521392",
            authority=["US"],
            limit=5
        )
        
        print(f"Found {results.total_search_result_count} patents for application")
        
        for patent in results.results:
            print(f"- {patent.title} ({patent.pn})")
            
    except Exception as e:
        print(f"Error in application number search: {e}")


def advanced_search_with_pagination():
    """Advanced search with multiple authorities and pagination."""
    print("\n=== Advanced Search with Pagination ===")
    
    page_size = 5
    offset = 0
    all_patents = []
    
    try:
        while True:
            results = patsnap.patents.search.by_number(
                pn="US*",  # Search pattern (if supported)
                authority=["US", "CN", "EP"],  # Multiple authorities
                limit=page_size,
                offset=offset
            )
            
            if not results.results:
                break
                
            all_patents.extend(results.results)
            print(f"Fetched page {offset // page_size + 1}, got {len(results.results)} patents")
            
            # Show sample from this page
            for patent in results.results[:2]:  # Show first 2 from each page
                print(f"  - {patent.title[:50]}... ({patent.pn})")
            
            # Check if we have more results
            if len(results.results) < page_size:
                break
                
            offset += page_size
            
            # Limit to 3 pages for demo
            if offset >= 15:
                break
                
        print(f"\nTotal patents collected: {len(all_patents)}")
        
    except Exception as e:
        print(f"Error in advanced search: {e}")


def search_multiple_patents():
    """Search for multiple specific patents."""
    print("\n=== Search Multiple Specific Patents ===")
    
    patent_numbers = [
        "US11205304B2",
        "US10123456A1", 
        "US9876543B2"
    ]
    
    for pn in patent_numbers:
        try:
            results = patsnap.patents.search.by_number(
                pn=pn,
                authority=["US"],
                limit=1
            )
            
            if results.results:
                patent = results.results[0]
                print(f"✓ {pn}: {patent.title}")
                print(f"  Assignee: {patent.current_assignee}")
            else:
                print(f"✗ {pn}: Not found")
                
        except Exception as e:
            print(f"✗ {pn}: Error - {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation error
    try:
        results = patsnap.patents.search.by_number(
            limit=2000  # Exceeds maximum of 1000
        )
    except Exception as e:
        print(f"Validation Error (expected): {type(e).__name__}: {e}")
    
    # Test with invalid parameters
    try:
        results = patsnap.patents.search.by_number(
            pn="",  # Empty patent number
            limit=0  # Invalid limit
        )
    except Exception as e:
        print(f"Invalid Parameters (expected): {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("Patsnap Patent Search Examples")
    print("=" * 40)
    
    basic_patent_search()
    search_by_application_number()
    advanced_search_with_pagination()
    search_multiple_patents()
    demonstrate_error_handling()
    
    print("\n" + "=" * 40)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_number()")
    print("- Clean, discoverable namespace-based API")
    print("- Comprehensive error handling")
    print("- Full type safety with Pydantic models")
