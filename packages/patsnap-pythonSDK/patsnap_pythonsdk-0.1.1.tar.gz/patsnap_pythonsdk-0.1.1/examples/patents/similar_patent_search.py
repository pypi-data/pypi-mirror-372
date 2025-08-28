"""
Example usage of similar patent search endpoint.

This demonstrates how to find patents similar to a given patent by ID or number,
providing insights into related technologies and potential patent landscapes.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_similar_patent_search():
    """Basic similar patent search - find patents similar to a given patent ID."""
    print("=== Basic Similar Patent Search ===")
    
    try:
        # Search for patents similar to a specific patent ID
        results = patsnap.patents.search.by_similarity(
            patent_id="b053642f-3108-4ea9-b629-420b0ab959e3",
            limit=20,
            relevancy="70%"
        )
        
        print(f"Reference Patent ID: b053642f-3108-4ea9-b629-420b0ab959e3")
        print(f"Minimum relevancy: 70%")
        print(f"Total similar patents found: {results.total_search_result_count:,}")
        print(f"Showing first {len(results.results)} patents:")
        
        for i, patent in enumerate(results.results, 1):
            print(f"{i:2d}. {patent.title}")
            print(f"    Patent: {patent.pn} | Relevancy: {patent.relevancy}")
            print(f"    Filed: {patent.apdt} | Published: {patent.pbdt}")
            print(f"    Assignee: {patent.current_assignee}")
            print(f"    Inventors: {patent.inventor}")
            print()
            
    except Exception as e:
        print(f"Error in basic similar patent search: {e}")


def similar_search_by_patent_number():
    """Search for similar patents using patent number instead of ID."""
    print("=== Similar Search by Patent Number ===")
    
    try:
        # Search using patent number when ID is not available
        results = patsnap.patents.search.by_similarity(
            patent_number="CN106185468A",
            limit=15,
            relevancy="60%",
            country=["CNA", "CNB", "USA", "USB"]
        )
        
        print(f"Reference Patent Number: CN106185468A")
        print(f"Country filters: CNA, CNB, USA, USB")
        print(f"Minimum relevancy: 60%")
        print(f"Similar patents found: {results.total_search_result_count:,}")
        
        # Group by relevancy ranges
        high_relevancy = []  # 90%+
        medium_relevancy = []  # 70-89%
        low_relevancy = []  # <70%
        
        for patent in results.results:
            relevancy_num = int(patent.relevancy.replace('%', ''))
            if relevancy_num >= 90:
                high_relevancy.append(patent)
            elif relevancy_num >= 70:
                medium_relevancy.append(patent)
            else:
                low_relevancy.append(patent)
        
        print(f"\nRelevancy Distribution:")
        print(f"  High (90%+): {len(high_relevancy)} patents")
        print(f"  Medium (70-89%): {len(medium_relevancy)} patents")
        print(f"  Lower (60-69%): {len(low_relevancy)} patents")
        
        if high_relevancy:
            print(f"\nHighly Similar Patents:")
            for patent in high_relevancy[:3]:
                print(f"  • {patent.title[:50]}...")
                print(f"    {patent.pn} | Relevancy: {patent.relevancy}")
            
    except Exception as e:
        print(f"Error in patent number search: {e}")


def similar_search_with_date_filters():
    """Search for similar patents with date range filtering."""
    print("\n=== Similar Search with Date Filters ===")
    
    try:
        # Find similar patents within specific date ranges
        results = patsnap.patents.search.by_similarity(
            patent_id="example-patent-id-123",
            pbd_from="20200101",  # Publication date from 2020
            pbd_to="20230101",    # Publication date to 2023
            apd_from="20190101",  # Application date from 2019
            apd_to="20220101",    # Application date to 2022
            limit=25,
            relevancy="65%"
        )
        
        print(f"Reference Patent: example-patent-id-123")
        print(f"Publication date range: 2020-2023")
        print(f"Application date range: 2019-2022")
        print(f"Similar patents in timeframe: {results.total_search_result_count:,}")
        
        # Analyze temporal distribution
        year_distribution = {}
        for patent in results.results:
            pub_year = str(patent.pbdt)[:4]
            year_distribution[pub_year] = year_distribution.get(pub_year, 0) + 1
        
        print(f"\nTemporal Distribution:")
        for year in sorted(year_distribution.keys()):
            print(f"  {year}: {year_distribution[year]} patents")
        
        # Show most recent similar patents
        sorted_by_date = sorted(results.results, key=lambda x: x.pbdt, reverse=True)
        print(f"\nMost Recent Similar Patents:")
        for patent in sorted_by_date[:3]:
            pub_date = str(patent.pbdt)
            formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
            print(f"  • {patent.title[:45]}...")
            print(f"    {patent.pn} | Published: {formatted_date} | Relevancy: {patent.relevancy}")
            
    except Exception as e:
        print(f"Error in date-filtered search: {e}")


def technology_landscape_analysis():
    """Analyze technology landscape around a patent using similarity search."""
    print("\n=== Technology Landscape Analysis ===")
    
    try:
        # Get comprehensive similar patents for landscape analysis
        results = patsnap.patents.search.by_similarity(
            patent_number="US11205304B2",
            limit=50,
            relevancy="50%"  # Lower threshold for broader landscape
        )
        
        print(f"Reference Patent: US11205304B2")
        print(f"Technology landscape size: {results.total_search_result_count:,} similar patents")
        
        # Analyze key players in the technology space
        assignee_counts = {}
        inventor_counts = {}
        
        for patent in results.results:
            # Count assignees
            assignee = patent.current_assignee
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
            
            # Count inventors (split by | separator)
            inventors = patent.inventor.split(' | ')
            for inventor in inventors:
                inventor = inventor.strip()
                inventor_counts[inventor] = inventor_counts.get(inventor, 0) + 1
        
        print(f"\nTop Players in Technology Space:")
        sorted_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)
        for assignee, count in sorted_assignees[:5]:
            print(f"  {assignee}: {count} similar patents")
        
        print(f"\nTop Inventors in Technology Space:")
        sorted_inventors = sorted(inventor_counts.items(), key=lambda x: x[1], reverse=True)
        for inventor, count in sorted_inventors[:5]:
            print(f"  {inventor}: {count} similar patents")
        
        # Analyze relevancy distribution
        relevancy_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '60-69%': 0, '50-59%': 0}
        for patent in results.results:
            rel_num = int(patent.relevancy.replace('%', ''))
            if rel_num >= 90:
                relevancy_ranges['90-100%'] += 1
            elif rel_num >= 80:
                relevancy_ranges['80-89%'] += 1
            elif rel_num >= 70:
                relevancy_ranges['70-79%'] += 1
            elif rel_num >= 60:
                relevancy_ranges['60-69%'] += 1
            else:
                relevancy_ranges['50-59%'] += 1
        
        print(f"\nSimilarity Distribution:")
        for range_name, count in relevancy_ranges.items():
            if count > 0:
                print(f"  {range_name}: {count} patents")
            
    except Exception as e:
        print(f"Error in landscape analysis: {e}")


def competitive_similarity_analysis():
    """Analyze competitive patents using similarity search."""
    print("\n=== Competitive Similarity Analysis ===")
    
    try:
        # Find patents similar to a competitor's key patent
        results = patsnap.patents.search.by_similarity(
            patent_number="JP1999068462A",
            limit=30,
            relevancy="70%",
            country=["USA", "USB", "EPA", "EPB", "JPA", "JPB"]  # Focus on major markets
        )
        
        print(f"Analyzing competitive landscape around: JP1999068462A")
        print(f"Market focus: US, EP, JP")
        print(f"Competitive similar patents: {results.total_search_result_count:,}")
        
        # Analyze competitive positioning
        us_patents = []
        ep_patents = []
        jp_patents = []
        other_patents = []
        
        for patent in results.results:
            authority = patent.pn[:2]
            if authority == "US":
                us_patents.append(patent)
            elif authority == "EP":
                ep_patents.append(patent)
            elif authority == "JP":
                jp_patents.append(patent)
            else:
                other_patents.append(patent)
        
        print(f"\nGeographic Distribution:")
        print(f"  US Patents: {len(us_patents)}")
        print(f"  EP Patents: {len(ep_patents)}")
        print(f"  JP Patents: {len(jp_patents)}")
        print(f"  Other: {len(other_patents)}")
        
        # Show highest relevancy patents by region
        if us_patents:
            top_us = max(us_patents, key=lambda x: int(x.relevancy.replace('%', '')))
            print(f"\nTop US Similar Patent:")
            print(f"  {top_us.title[:50]}...")
            print(f"  {top_us.pn} | Relevancy: {top_us.relevancy}")
            print(f"  Assignee: {top_us.current_assignee}")
        
        if ep_patents:
            top_ep = max(ep_patents, key=lambda x: int(x.relevancy.replace('%', '')))
            print(f"\nTop EP Similar Patent:")
            print(f"  {top_ep.title[:50]}...")
            print(f"  {top_ep.pn} | Relevancy: {top_ep.relevancy}")
            print(f"  Assignee: {top_ep.current_assignee}")
            
    except Exception as e:
        print(f"Error in competitive analysis: {e}")


def prior_art_discovery():
    """Use similarity search for prior art discovery."""
    print("\n=== Prior Art Discovery ===")
    
    try:
        # Search for potential prior art using broad criteria
        results = patsnap.patents.search.by_similarity(
            patent_id="target-patent-for-prior-art",
            apd_to="20200101",  # Only patents filed before target date
            limit=40,
            relevancy="60%"  # Lower threshold to catch more potential prior art
        )
        
        print(f"Prior art search for: target-patent-for-prior-art")
        print(f"Filed before: 2020-01-01")
        print(f"Potential prior art patents: {results.total_search_result_count:,}")
        
        # Categorize by application date (age)
        very_old = []  # Before 2010
        old = []       # 2010-2015
        recent = []    # 2015-2020
        
        for patent in results.results:
            app_year = int(str(patent.apdt)[:4])
            if app_year < 2010:
                very_old.append(patent)
            elif app_year < 2015:
                old.append(patent)
            else:
                recent.append(patent)
        
        print(f"\nPrior Art by Age:")
        print(f"  Very Old (pre-2010): {len(very_old)} patents")
        print(f"  Old (2010-2015): {len(old)} patents")
        print(f"  Recent (2015-2020): {len(recent)} patents")
        
        # Show most relevant prior art by category
        if very_old:
            top_very_old = max(very_old, key=lambda x: int(x.relevancy.replace('%', '')))
            app_date = str(top_very_old.apdt)
            formatted_date = f"{app_date[:4]}-{app_date[4:6]}-{app_date[6:8]}"
            print(f"\nMost Relevant Very Old Prior Art:")
            print(f"  {top_very_old.title}")
            print(f"  {top_very_old.pn} | Filed: {formatted_date} | Relevancy: {top_very_old.relevancy}")
            print(f"  Assignee: {top_very_old.original_assignee}")
        
        # Identify key prior art assignees
        prior_art_assignees = {}
        for patent in results.results:
            assignee = patent.original_assignee
            if assignee not in prior_art_assignees:
                prior_art_assignees[assignee] = []
            prior_art_assignees[assignee].append(patent)
        
        print(f"\nKey Prior Art Holders:")
        sorted_assignees = sorted(prior_art_assignees.items(), key=lambda x: len(x[1]), reverse=True)
        for assignee, patents in sorted_assignees[:3]:
            avg_relevancy = sum(int(p.relevancy.replace('%', '')) for p in patents) / len(patents)
            print(f"  {assignee}: {len(patents)} patents (avg relevancy: {avg_relevancy:.1f}%)")
            
    except Exception as e:
        print(f"Error in prior art discovery: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation errors
    try:
        results = patsnap.patents.search.by_similarity()  # Missing both patent_id and patent_number
    except ValueError as e:
        print(f"Missing parameters error (expected): {e}")
    
    try:
        results = patsnap.patents.search.by_similarity(
            patent_id="test-id",
            limit=2000  # Exceeds maximum of 1000
        )
    except Exception as e:
        print(f"Limit validation error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_similarity(
            patent_id="test-id",
            offset=-1  # Negative offset
        )
    except Exception as e:
        print(f"Offset validation error (expected): {type(e).__name__}")


if __name__ == "__main__":
    print("Patsnap Similar Patent Search Examples")
    print("=" * 50)
    
    basic_similar_patent_search()
    similar_search_by_patent_number()
    similar_search_with_date_filters()
    technology_landscape_analysis()
    competitive_similarity_analysis()
    prior_art_discovery()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_similarity()")
    print("- Find patents similar to a given patent by ID or number")
    print("- Relevancy scoring from high to low similarity")
    print("- Date range filtering for temporal analysis")
    print("- Technology landscape and competitive analysis")
    print("- Prior art discovery and patent research")
    print("- Clean, discoverable namespace-based API")
