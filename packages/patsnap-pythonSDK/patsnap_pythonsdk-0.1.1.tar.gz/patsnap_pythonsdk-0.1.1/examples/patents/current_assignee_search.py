"""
Example usage of patent current assignee search endpoint.

This demonstrates how to search for patents by current assignee names,
providing insights into current patent ownership and portfolio analysis.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_current_assignee_search():
    """Basic current assignee search - find patents by current owner."""
    print("=== Basic Current Assignee Search ===")
    
    try:
        # Search for patents currently owned by Apple
        results = patsnap.patents.search.by_current_assignee(
            assignee="Apple, Inc.",
            limit=20
        )
        
        print(f"Current Assignee: Apple, Inc.")
        print(f"Total patents currently owned: {results.total_search_result_count:,}")
        print(f"Showing first {len(results.results)} patents:")
        
        for i, patent in enumerate(results.results, 1):
            print(f"{i:2d}. {patent.title}")
            print(f"    Patent: {patent.pn}")
            print(f"    Filed: {patent.apdt} | Published: {patent.pbdt}")
            print(f"    Current Owner: {patent.current_assignee}")
            print(f"    Original Applicant: {patent.original_assignee}")
            print()
            
    except Exception as e:
        print(f"Error in basic current assignee search: {e}")


def ownership_transfer_analysis():
    """Analyze patents that have changed ownership."""
    print("=== Ownership Transfer Analysis ===")
    
    try:
        # Search for patents currently owned by Google
        results = patsnap.patents.search.by_current_assignee(
            assignee="Google LLC",
            limit=30,
            sort=[{"field": "APD_YEARMONTHDAY", "order": "DESC"}]
        )
        
        print(f"Current Assignee: Google LLC")
        print(f"Total patents currently owned: {results.total_search_result_count:,}")
        
        # Analyze ownership transfers
        transferred_patents = []
        original_ownership = []
        
        for patent in results.results:
            if patent.current_assignee != patent.original_assignee:
                transferred_patents.append(patent)
            else:
                original_ownership.append(patent)
        
        print(f"\nOwnership Analysis:")
        print(f"  Originally filed by Google: {len(original_ownership)}")
        print(f"  Acquired from other companies: {len(transferred_patents)}")
        
        if transferred_patents:
            print(f"\nExamples of acquired patents:")
            for patent in transferred_patents[:5]:
                print(f"  • {patent.title[:50]}...")
                print(f"    {patent.pn} | Originally: {patent.original_assignee}")
                print(f"    Now owned by: {patent.current_assignee}")
                print()
            
    except Exception as e:
        print(f"Error in ownership transfer analysis: {e}")


def current_vs_original_comparison():
    """Compare current assignee vs original assignee results."""
    print("\n=== Current vs Original Assignee Comparison ===")
    
    company = "Microsoft Corporation"
    
    try:
        # Search by current assignee
        current_results = patsnap.patents.search.by_current_assignee(
            assignee=company,
            limit=10
        )
        
        # Search by original assignee  
        original_results = patsnap.patents.search.by_original_assignee(
            application=company,
            limit=10
        )
        
        print(f"Company: {company}")
        print(f"Patents currently owned: {current_results.total_search_result_count:,}")
        print(f"Patents originally filed: {original_results.total_search_result_count:,}")
        
        difference = current_results.total_search_result_count - original_results.total_search_result_count
        if difference > 0:
            print(f"Net acquisition: +{difference:,} patents")
        elif difference < 0:
            print(f"Net divestiture: {difference:,} patents")
        else:
            print("No net change in portfolio")
        
        print(f"\nRecent patents currently owned:")
        for i, patent in enumerate(current_results.results[:3], 1):
            print(f"{i}. {patent.title}")
            print(f"   {patent.pn} | Filed: {patent.apdt}")
            if patent.current_assignee != patent.original_assignee:
                print(f"   ⚠️  Acquired from: {patent.original_assignee}")
            print()
            
    except Exception as e:
        print(f"Error in comparison analysis: {e}")


def multi_company_current_ownership():
    """Search current ownership across multiple companies."""
    print("=== Multi-Company Current Ownership ===")
    
    try:
        # Search for patents currently owned by major tech companies
        results = patsnap.patents.search.by_current_assignee(
            assignee="Apple OR Google OR Microsoft OR Amazon",
            limit=40,
            sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}]
        )
        
        print(f"Companies: Apple, Google, Microsoft, Amazon")
        print(f"Total patents currently owned: {results.total_search_result_count:,}")
        
        # Group by current assignee
        ownership_stats = {}
        for patent in results.results:
            current_owner = patent.current_assignee
            if current_owner not in ownership_stats:
                ownership_stats[current_owner] = {
                    'count': 0,
                    'patents': []
                }
            ownership_stats[current_owner]['count'] += 1
            ownership_stats[current_owner]['patents'].append(patent)
        
        print(f"\nCurrent ownership distribution (sample):")
        for owner, stats in sorted(ownership_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"\n{owner} ({stats['count']} patents in sample):")
            for patent in stats['patents'][:2]:  # Show top 2 per company
                print(f"  • {patent.title[:50]}...")
                print(f"    {patent.pn} | Published: {patent.pbdt}")
                if patent.current_assignee != patent.original_assignee:
                    print(f"    Originally filed by: {patent.original_assignee}")
            
    except Exception as e:
        print(f"Error in multi-company analysis: {e}")


def current_assignee_portfolio_trends():
    """Analyze current assignee portfolio trends over time."""
    print("\n=== Current Assignee Portfolio Trends ===")
    
    try:
        # Get Tesla's current patent portfolio
        results = patsnap.patents.search.by_current_assignee(
            assignee="Tesla, Inc.",
            sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}],
            limit=50
        )
        
        print(f"Current Assignee: Tesla, Inc.")
        print(f"Current portfolio size: {results.total_search_result_count:,} patents")
        
        # Analyze by publication year and ownership
        year_analysis = {}
        acquisition_analysis = {}
        
        for patent in results.results:
            # Publication year analysis
            pub_year = str(patent.pbdt)[:4]
            if pub_year not in year_analysis:
                year_analysis[pub_year] = {'total': 0, 'acquired': 0, 'original': 0}
            
            year_analysis[pub_year]['total'] += 1
            
            # Ownership analysis
            if patent.current_assignee != patent.original_assignee:
                year_analysis[pub_year]['acquired'] += 1
                original_company = patent.original_assignee
                acquisition_analysis[original_company] = acquisition_analysis.get(original_company, 0) + 1
            else:
                year_analysis[pub_year]['original'] += 1
        
        print(f"\nRecent portfolio activity:")
        for year in sorted(year_analysis.keys(), reverse=True)[:5]:
            stats = year_analysis[year]
            print(f"  {year}: {stats['total']} patents ({stats['original']} original, {stats['acquired']} acquired)")
        
        if acquisition_analysis:
            print(f"\nTop acquisition sources (sample):")
            sorted_acquisitions = sorted(acquisition_analysis.items(), key=lambda x: x[1], reverse=True)
            for company, count in sorted_acquisitions[:3]:
                print(f"  • {company}: {count} patents")
            
    except Exception as e:
        print(f"Error in portfolio trends analysis: {e}")


def current_assignee_authority_analysis():
    """Analyze current assignee patents by authority."""
    print("\n=== Current Assignee Authority Analysis ===")
    
    try:
        # Search Samsung's current US patents with authority priority
        results = patsnap.patents.search.by_current_assignee(
            assignee="Samsung Electronics Co Ltd",
            collapse_by="AUTHORITY",
            collapse_order_authority=["US", "EP", "JP", "CN", "KR"],
            limit=25
        )
        
        print(f"Current Assignee: Samsung Electronics")
        print(f"Authority priority: US > EP > JP > CN > KR")
        print(f"Total patents: {results.total_search_result_count:,}")
        
        # Group by authority
        authority_stats = {}
        for patent in results.results:
            # Extract authority from patent number
            authority = patent.pn[:2] if len(patent.pn) >= 2 else "Unknown"
            if authority not in authority_stats:
                authority_stats[authority] = []
            authority_stats[authority].append(patent)
        
        print(f"\nPatents by authority:")
        for authority in ["US", "EP", "JP", "CN", "KR"]:
            if authority in authority_stats:
                patents = authority_stats[authority]
                print(f"\n{authority} Patents ({len(patents)}):")
                for patent in patents[:3]:  # Show top 3
                    print(f"  • {patent.pn}: {patent.title[:45]}...")
                    if patent.current_assignee != patent.original_assignee:
                        print(f"    Originally filed by: {patent.original_assignee}")
                    
    except Exception as e:
        print(f"Error in authority analysis: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation errors
    try:
        results = patsnap.patents.search.by_current_assignee()  # Missing required assignee
    except Exception as e:
        print(f"Missing assignee error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_current_assignee(
            assignee="Test Company",
            limit=2000  # Exceeds maximum of 1000
        )
    except Exception as e:
        print(f"Limit validation error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_current_assignee(
            assignee="Test Company",
            offset=-1  # Negative offset
        )
    except Exception as e:
        print(f"Offset validation error (expected): {type(e).__name__}")


if __name__ == "__main__":
    print("Patsnap Patent Current Assignee Search Examples")
    print("=" * 55)
    
    basic_current_assignee_search()
    ownership_transfer_analysis()
    current_vs_original_comparison()
    multi_company_current_ownership()
    current_assignee_portfolio_trends()
    current_assignee_authority_analysis()
    demonstrate_error_handling()
    
    print("\n" + "=" * 55)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_current_assignee()")
    print("- Search patents by current assignee/owner names")
    print("- Support for up to 100 companies with OR logic")
    print("- Analyze ownership transfers and acquisitions")
    print("- Compare current vs original ownership")
    print("- Clean, discoverable namespace-based API")
