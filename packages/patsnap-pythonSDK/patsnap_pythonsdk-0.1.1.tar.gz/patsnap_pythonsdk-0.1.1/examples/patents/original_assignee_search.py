"""
Example usage of patent original assignee search endpoint.

This demonstrates how to search for patents by original applicant/assignee names,
providing insights into company patent portfolios and innovation strategies.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_company_search():
    """Basic company search - find patents by a single company."""
    print("=== Basic Company Search ===")
    
    try:
        # Search for Apple patents
        results = patsnap.patents.search.by_original_assignee(
            application="Apple, Inc.",
            limit=20
        )
        
        print(f"Company: Apple, Inc.")
        print(f"Total patents found: {results.total_search_result_count:,}")
        print(f"Showing first {len(results.results)} patents:")
        
        for i, patent in enumerate(results.results, 1):
            print(f"{i:2d}. {patent.title}")
            print(f"    Patent: {patent.pn}")
            print(f"    Filed: {patent.apdt} | Published: {patent.pbdt}")
            print(f"    Assignee: {patent.current_assignee}")
            print()
            
    except Exception as e:
        print(f"Error in basic company search: {e}")


def multiple_company_search():
    """Search patents from multiple companies using OR logic."""
    print("=== Multiple Company Search ===")
    
    try:
        # Search for patents from major tech companies
        results = patsnap.patents.search.by_original_assignee(
            application="Apple OR Google OR Microsoft",
            limit=30,
            sort=[{"field": "SCORE", "order": "DESC"}]
        )
        
        print(f"Companies: Apple, Google, Microsoft")
        print(f"Total patents found: {results.total_search_result_count:,}")
        print("Recent patents by relevance:")
        
        # Group by company
        company_patents = {}
        for patent in results.results:
            company = patent.current_assignee
            if company not in company_patents:
                company_patents[company] = []
            company_patents[company].append(patent)
        
        for company, patents in company_patents.items():
            print(f"\n{company} ({len(patents)} patents):")
            for patent in patents[:3]:  # Show top 3 per company
                print(f"  • {patent.title[:60]}...")
                print(f"    {patent.pn} | Filed: {patent.apdt}")
            
    except Exception as e:
        print(f"Error in multiple company search: {e}")


def advanced_company_search():
    """Advanced search with sorting and filtering options."""
    print("\n=== Advanced Company Search ===")
    
    try:
        # Search Tesla patents with advanced options
        results = patsnap.patents.search.by_original_assignee(
            application="Tesla, Inc.",
            collapse_type="DOCDB",  # Group by simple family
            collapse_by="APD",      # Order by application date
            collapse_order="LATEST", # Keep latest in each family
            sort=[{"field": "APD_YEARMONTHDAY", "order": "DESC"}],
            offset=0,
            limit=25
        )
        
        print(f"Company: Tesla, Inc.")
        print(f"Search options: DOCDB family grouping, latest by application date")
        print(f"Total patents: {results.total_search_result_count:,}")
        print("Recent Tesla patents:")
        
        for i, patent in enumerate(results.results, 1):
            # Convert date format for display
            app_date = str(patent.apdt)
            formatted_date = f"{app_date[:4]}-{app_date[4:6]}-{app_date[6:8]}"
            
            print(f"{i:2d}. {patent.title}")
            print(f"    {patent.pn} | Applied: {formatted_date}")
            print(f"    Inventor(s): {patent.inventor}")
            print()
            
    except Exception as e:
        print(f"Error in advanced company search: {e}")


def company_portfolio_analysis():
    """Analyze a company's patent portfolio over time."""
    print("=== Company Portfolio Analysis ===")
    
    try:
        # Get recent Qualcomm patents sorted by publication date
        results = patsnap.patents.search.by_original_assignee(
            application="QUALCOMM INCORPORATED",
            sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}],
            limit=50
        )
        
        print(f"Company: QUALCOMM INCORPORATED")
        print(f"Portfolio size: {results.total_search_result_count:,} patents")
        
        # Analyze by publication year
        year_counts = {}
        technology_areas = {}
        
        for patent in results.results:
            # Extract publication year
            pub_year = str(patent.pbdt)[:4]
            year_counts[pub_year] = year_counts.get(pub_year, 0) + 1
            
            # Simple technology classification based on title keywords
            title_lower = patent.title.lower()
            if any(word in title_lower for word in ['wireless', '5g', 'lte', 'communication']):
                tech = 'Wireless/5G'
            elif any(word in title_lower for word in ['ai', 'machine learning', 'neural']):
                tech = 'AI/ML'
            elif any(word in title_lower for word in ['processor', 'chip', 'semiconductor']):
                tech = 'Semiconductors'
            else:
                tech = 'Other'
            
            technology_areas[tech] = technology_areas.get(tech, 0) + 1
        
        print("\nRecent publication activity:")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"  {year}: {year_counts[year]} patents")
        
        print("\nTechnology focus areas (sample):")
        for tech, count in sorted(technology_areas.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tech}: {count} patents")
            
    except Exception as e:
        print(f"Error in portfolio analysis: {e}")


def competitive_analysis():
    """Compare patent activity between competing companies."""
    print("\n=== Competitive Analysis ===")
    
    companies = ["Samsung", "Apple", "Huawei"]
    
    try:
        company_stats = {}
        
        for company in companies:
            # Get basic stats for each company
            results = patsnap.patents.search.by_original_assignee(
                application=f"{company}",
                limit=10  # Just need total count and recent examples
            )
            
            company_stats[company] = {
                'total': results.total_search_result_count,
                'recent_patents': results.results
            }
        
        print("Smartphone Patent Leaders Comparison:")
        print("-" * 50)
        
        # Sort by total patent count
        sorted_companies = sorted(company_stats.items(), 
                                key=lambda x: x[1]['total'], reverse=True)
        
        for rank, (company, stats) in enumerate(sorted_companies, 1):
            print(f"{rank}. {company}")
            print(f"   Total patents: {stats['total']:,}")
            
            if stats['recent_patents']:
                latest = stats['recent_patents'][0]
                pub_date = str(latest.pbdt)
                formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
                print(f"   Latest: {latest.title[:50]}... ({formatted_date})")
            print()
            
    except Exception as e:
        print(f"Error in competitive analysis: {e}")


def authority_focused_search():
    """Search company patents with authority-specific ordering."""
    print("=== Authority-Focused Search ===")
    
    try:
        # Search IBM patents with US priority
        results = patsnap.patents.search.by_original_assignee(
            application="International Business Machines Corporation",
            collapse_by="AUTHORITY",
            collapse_order_authority=["US", "EP", "JP", "CN"],  # US priority
            limit=20
        )
        
        print(f"Company: IBM")
        print(f"Authority priority: US > EP > JP > CN")
        print(f"Total patents: {results.total_search_result_count:,}")
        
        # Group by patent authority
        authority_groups = {}
        for patent in results.results:
            # Extract authority from patent number
            authority = patent.pn[:2] if len(patent.pn) >= 2 else "Unknown"
            if authority not in authority_groups:
                authority_groups[authority] = []
            authority_groups[authority].append(patent)
        
        print("\nPatents by authority:")
        for authority in ["US", "EP", "JP", "CN"]:
            if authority in authority_groups:
                patents = authority_groups[authority]
                print(f"\n{authority} Patents ({len(patents)}):")
                for patent in patents[:3]:  # Show top 3
                    print(f"  • {patent.pn}: {patent.title[:50]}...")
                    
    except Exception as e:
        print(f"Error in authority-focused search: {e}")


def paginated_company_search():
    """Demonstrate pagination through large patent portfolios."""
    print("\n=== Paginated Company Search ===")
    
    company = "Sony Corporation"
    page_size = 25
    max_pages = 3
    
    try:
        all_patents = []
        
        print(f"Retrieving {company} patents (paginated)...")
        
        for page in range(max_pages):
            offset = page * page_size
            
            results = patsnap.patents.search.by_original_assignee(
                application=company,
                offset=offset,
                limit=page_size,
                sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}]
            )
            
            print(f"Page {page + 1}: Retrieved {len(results.results)} patents (offset: {offset})")
            
            all_patents.extend(results.results)
            
            # Show sample from this page
            if results.results:
                sample = results.results[0]
                print(f"  Sample: {sample.title[:40]}... ({sample.pn})")
            
            # Check if we've reached the end
            if len(results.results) < page_size:
                print("  (Last page reached)")
                break
        
        print(f"\nTotal patents collected: {len(all_patents)}")
        print(f"Total available: {results.total_search_result_count:,}")
        
        # Analyze publication years
        years = [str(p.pbdt)[:4] for p in all_patents]
        year_counts = {year: years.count(year) for year in set(years)}
        
        print("\nPublication year distribution (sample):")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"  {year}: {year_counts[year]} patents")
            
    except Exception as e:
        print(f"Error in paginated search: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation errors
    try:
        results = patsnap.patents.search.by_original_assignee()  # Missing required application
    except Exception as e:
        print(f"Missing application error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_original_assignee(
            application="Test Company",
            limit=2000  # Exceeds maximum of 1000
        )
    except Exception as e:
        print(f"Limit validation error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_original_assignee(
            application="Test Company",
            offset=-1  # Negative offset
        )
    except Exception as e:
        print(f"Offset validation error (expected): {type(e).__name__}")


if __name__ == "__main__":
    print("Patsnap Patent Company Search Examples")
    print("=" * 50)
    
    basic_company_search()
    multiple_company_search()
    advanced_company_search()
    company_portfolio_analysis()
    competitive_analysis()
    authority_focused_search()
    paginated_company_search()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_company()")
    print("- Search patents by original applicant/assignee names")
    print("- Support for up to 100 companies with OR logic")
    print("- Advanced sorting and collapse options")
    print("- Pagination support for large portfolios")
    print("- Clean, discoverable namespace-based API")
