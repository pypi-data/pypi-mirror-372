"""
Example usage of analytics query filter endpoint.

This demonstrates how to get aggregated statistical results of specified field dimensions
according to search results, providing insights into patent distributions across various fields.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_field_statistics():
    """Basic field statistics - top assignees for a technology."""
    print("=== Basic Field Statistics - Top Assignees ===")
    
    try:
        # Get top assignees for automotive patents
        results = patsnap.analytics.search.query_filter(
            query="TTL:汽车",  # Title contains "汽车" (automobile in Chinese)
            field="ASSIGNEE",
            offset=0,
            limit=10
        )
        
        print(f"Query: 'TTL:汽车' (automotive patents)")
        print(f"Field: ASSIGNEE")
        print("Top Assignees:")
        
        for result in results:
            if hasattr(result, 'assignee'):
                for i, assignee in enumerate(result.assignee, 1):
                    print(f"{i:2d}. {assignee.name:<30} {assignee.count:>8,} patents")
            
    except Exception as e:
        print(f"Error in basic field statistics: {e}")


def publication_year_trends():
    """Analyze publication year trends for a technology."""
    print("\n=== Publication Year Trends ===")
    
    try:
        # Get publication year distribution for AI patents
        results = patsnap.analytics.search.query_filter(
            query="TACD: artificial intelligence",
            field="PUBLICATION_YEAR",
            offset=0,
            limit=20,
            stemming=1
        )
        
        print(f"Query: 'TACD: artificial intelligence'")
        print(f"Field: PUBLICATION_YEAR")
        print("Publication Trends:")
        
        for result in results:
            if hasattr(result, 'publication_year'):
                # Sort by year (descending)
                years = sorted(result.publication_year, 
                             key=lambda x: int(x.name), reverse=True)
                
                for year_data in years[:10]:  # Show last 10 years
                    print(f"  {year_data.name}: {year_data.count:>6,} patents")
            
    except Exception as e:
        print(f"Error in publication year trends: {e}")


def authority_distribution():
    """Analyze patent authority distribution."""
    print("\n=== Authority Distribution ===")
    
    try:
        # Get authority distribution for blockchain patents
        results = patsnap.analytics.search.query_filter(
            query="TACD: blockchain",
            field="AUTHORITY",
            offset=0,
            limit=15,
            collapse_by="AUTHORITY",
            collapse_order_authority=["US", "CN", "EP", "JP", "KR"]
        )
        
        print(f"Query: 'TACD: blockchain'")
        print(f"Field: AUTHORITY")
        print("Authority Distribution:")
        
        for result in results:
            if hasattr(result, 'authority'):
                total_patents = sum(auth.count for auth in result.authority)
                
                for authority in result.authority:
                    percentage = (authority.count / total_patents) * 100
                    print(f"  {authority.name:<4}: {authority.count:>8,} patents ({percentage:5.1f}%)")
            
    except Exception as e:
        print(f"Error in authority distribution: {e}")


def ipc_classification_analysis():
    """Analyze IPC classification distribution."""
    print("\n=== IPC Classification Analysis ===")
    
    try:
        # Get IPC section distribution for renewable energy
        results = patsnap.analytics.search.query_filter(
            query="renewable energy OR solar power OR wind energy",
            field="IPC_SECTION",
            offset=0,
            limit=10,
            lang="en"
        )
        
        print(f"Query: 'renewable energy OR solar power OR wind energy'")
        print(f"Field: IPC_SECTION")
        print("IPC Section Distribution:")
        
        for result in results:
            if hasattr(result, 'ipc_section'):
                for ipc in result.ipc_section:
                    print(f"  Section {ipc.name}: {ipc.count:>6,} patents")
            
    except Exception as e:
        print(f"Error in IPC classification analysis: {e}")


def multiple_field_analysis():
    """Analyze multiple fields in one request."""
    print("\n=== Multiple Field Analysis ===")
    
    try:
        # Get both assignee and authority data for electric vehicles
        results = patsnap.analytics.search.query_filter(
            query="electric vehicle OR EV",
            field="ASSIGNEE,AUTHORITY",  # Multiple fields
            offset=0,
            limit=5,
            stemming=1
        )
        
        print(f"Query: 'electric vehicle OR EV'")
        print(f"Fields: ASSIGNEE, AUTHORITY")
        
        for result in results:
            if hasattr(result, 'assignee'):
                print("\nTop Assignees:")
                for assignee in result.assignee[:5]:
                    print(f"  {assignee.name:<25} {assignee.count:>6,}")
            
            if hasattr(result, 'authority'):
                print("\nAuthority Distribution:")
                for authority in result.authority:
                    print(f"  {authority.name:<4} {authority.count:>6,}")
            
    except Exception as e:
        print(f"Error in multiple field analysis: {e}")


def patent_type_analysis():
    """Analyze patent type distribution."""
    print("\n=== Patent Type Analysis ===")
    
    try:
        # Get patent type distribution for 5G technology
        results = patsnap.analytics.search.query_filter(
            query="TACD: 5G technology",
            field="PATENT_TYPE",
            offset=0,
            limit=10
        )
        
        print(f"Query: 'TACD: 5G technology'")
        print(f"Field: PATENT_TYPE")
        print("Patent Type Distribution:")
        
        # Patent type codes explanation
        type_names = {
            "A": "Applications",
            "B": "Granted Patents", 
            "U": "Utility Models",
            "D": "Designs",
            "AB": "Applications + Patents"
        }
        
        for result in results:
            if hasattr(result, 'patent_type'):
                for ptype in result.patent_type:
                    type_desc = type_names.get(ptype.name, ptype.name)
                    print(f"  {ptype.name} ({type_desc}): {ptype.count:>6,}")
            
    except Exception as e:
        print(f"Error in patent type analysis: {e}")


def legal_status_analysis():
    """Analyze legal status distribution."""
    print("\n=== Legal Status Analysis ===")
    
    try:
        # Get simple legal status for quantum computing patents
        results = patsnap.analytics.search.query_filter(
            query="quantum computing OR quantum algorithm",
            field="SIMPLE_LEGAL_STATUS",
            offset=0,
            limit=10,
            collapse_type="DOCDB"
        )
        
        print(f"Query: 'quantum computing OR quantum algorithm'")
        print(f"Field: SIMPLE_LEGAL_STATUS")
        print("Legal Status Distribution:")
        
        # Legal status codes explanation
        status_names = {
            "0": "Inactive",
            "1": "Active",
            "2": "Pending",
            "220": "PCT designated stage expired",
            "221": "PCT designated stage",
            "999": "Undetermined"
        }
        
        for result in results:
            if hasattr(result, 'simple_legal_status'):
                total = sum(status.count for status in result.simple_legal_status)
                
                for status in result.simple_legal_status:
                    status_desc = status_names.get(status.name, status.name)
                    percentage = (status.count / total) * 100
                    print(f"  {status.name} ({status_desc}): {status.count:>6,} ({percentage:5.1f}%)")
            
    except Exception as e:
        print(f"Error in legal status analysis: {e}")


def paginated_field_analysis():
    """Demonstrate pagination through field statistics."""
    print("\n=== Paginated Field Analysis ===")
    
    query = "TACD: machine learning"
    field = "ASSIGNEE"
    page_size = 10
    max_pages = 3
    
    try:
        all_assignees = []
        
        for page in range(max_pages):
            offset = page * page_size
            
            results = patsnap.analytics.search.query_filter(
                query=query,
                field=field,
                offset=offset,
                limit=page_size
            )
            
            print(f"Page {page + 1} (offset: {offset}):")
            
            for result in results:
                if hasattr(result, 'assignee'):
                    for assignee in result.assignee:
                        all_assignees.append(assignee)
                        print(f"  {assignee.name:<30} {assignee.count:>6,}")
                    
                    # Check if we got fewer results than requested (last page)
                    if len(result.assignee) < page_size:
                        print("  (Last page reached)")
                        break
        
        print(f"\nTotal assignees collected: {len(all_assignees)}")
        
    except Exception as e:
        print(f"Error in paginated analysis: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation errors
    try:
        results = patsnap.analytics.search.query_filter()  # Missing required params
    except Exception as e:
        print(f"Missing parameters error (expected): {type(e).__name__}")
    
    try:
        long_query = "A" * 801  # Exceeds 800 character limit
        results = patsnap.analytics.search.query_filter(
            query=long_query,
            field="ASSIGNEE",
            offset=0
        )
    except Exception as e:
        print(f"Query too long error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.analytics.search.query_filter(
            query="test",
            field="ASSIGNEE",
            offset=0,
            limit=150  # Exceeds maximum of 100
        )
    except Exception as e:
        print(f"Limit validation error (expected): {type(e).__name__}")


if __name__ == "__main__":
    print("Patsnap Analytics Query Filter Examples")
    print("=" * 50)
    
    basic_field_statistics()
    publication_year_trends()
    authority_distribution()
    ipc_classification_analysis()
    multiple_field_analysis()
    patent_type_analysis()
    legal_status_analysis()
    paginated_field_analysis()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.analytics.search.query_filter()")
    print("- Get aggregated field statistics from analytics queries")
    print("- Support for 25+ different field dimensions")
    print("- Pagination support (up to 200 total results)")
    print("- Multiple field analysis in single request")
    print("- Clean, discoverable namespace-based API")
