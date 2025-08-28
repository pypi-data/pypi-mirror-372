"""
Example usage of defense patent search endpoint.

This demonstrates how to search for defense/military patents by applicant names,
providing insights into defense technology innovation and research activities.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_defense_patent_search():
    """Basic defense patent search - find patents by defense organization."""
    print("=== Basic Defense Patent Search ===")
    
    try:
        # Search for defense patents from Lockheed Martin Corporation
        results = patsnap.patents.search.by_defense_applicant(
            application="Lockheed Martin Corporation",
            limit=20
        )
        
        print(f"Defense Organization: Lockheed Martin Corporation")
        print(f"Total defense patents found: {results.total_search_result_count:,}")
        print(f"Showing first {len(results.results)} patents:")
        
        for i, patent in enumerate(results.results, 1):
            print(f"{i:2d}. {patent.title}")
            print(f"    Patent: {patent.pn}")
            print(f"    Filed: {patent.apdt} | Published: {patent.pbdt}")
            print(f"    Applicant: {patent.original_assignee}")
            print(f"    Inventors: {patent.inventor}")
            print()
            
    except Exception as e:
        print(f"Error in basic defense patent search: {e}")


def multiple_defense_organizations():
    """Search defense patents from multiple organizations using OR logic."""
    print("=== Multiple Defense Organizations Search ===")
    
    try:
        # Search for patents from multiple major defense contractors
        results = patsnap.patents.search.by_defense_applicant(
            application="Lockheed Martin Corporation OR Boeing Company OR Raytheon Technologies",
            limit=30,
            sort=[{"field": "PBDT_YEARMONTHDAY", "order": "DESC"}]
        )
        
        print(f"Organizations: Lockheed Martin, Boeing, Raytheon Technologies")
        print(f"Total defense patents found: {results.total_search_result_count:,}")
        print("Recent defense patents:")
        
        # Group by organization
        org_patents = {}
        for patent in results.results:
            org = patent.original_assignee
            if org not in org_patents:
                org_patents[org] = []
            org_patents[org].append(patent)
        
        for org, patents in org_patents.items():
            print(f"\n{org} ({len(patents)} patents):")
            for patent in patents[:2]:  # Show top 2 per organization
                pub_date = str(patent.pbdt)
                formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
                print(f"  • {patent.title[:50]}...")
                print(f"    {patent.pn} | Published: {formatted_date}")
            
    except Exception as e:
        print(f"Error in multiple organizations search: {e}")


def defense_technology_analysis():
    """Analyze defense technology trends and focus areas."""
    print("\n=== Defense Technology Analysis ===")
    
    try:
        # Get recent defense patents with advanced sorting
        results = patsnap.patents.search.by_defense_applicant(
            application="General Dynamics Corporation",
            collapse_type="DOCDB",
            collapse_by="APD",
            collapse_order="LATEST",
            sort=[{"field": "APD_YEARMONTHDAY", "order": "DESC"}],
            limit=40
        )
        
        print(f"Organization: General Dynamics Corporation")
        print(f"Defense portfolio size: {results.total_search_result_count:,} patents")
        
        # Analyze technology focus areas based on titles
        tech_areas = {}
        recent_years = {}
        
        for patent in results.results:
            # Simple technology classification based on title keywords
            title_lower = patent.title.lower()
            if any(word in title_lower for word in ['satellite', 'space', 'aerospace', 'orbital']):
                tech = 'Satellite/Space Technology'
            elif any(word in title_lower for word in ['missile', 'rocket', 'propulsion', 'launch']):
                tech = 'Missile/Rocket Systems'
            elif any(word in title_lower for word in ['radar', 'communication', 'signal', 'antenna']):
                tech = 'Radar/Communication'
            elif any(word in title_lower for word in ['navigation', 'guidance', 'control', 'targeting']):
                tech = 'Navigation/Guidance'
            elif any(word in title_lower for word in ['armor', 'vehicle', 'tank', 'combat']):
                tech = 'Combat Vehicles/Systems'
            else:
                tech = 'Other Defense Technology'
            
            tech_areas[tech] = tech_areas.get(tech, 0) + 1
            
            # Application year analysis
            app_year = str(patent.apdt)[:4]
            recent_years[app_year] = recent_years.get(app_year, 0) + 1
        
        print(f"\nTechnology focus areas (sample analysis):")
        for tech, count in sorted(tech_areas.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tech}: {count} patents")
        
        print(f"\nRecent filing activity:")
        for year in sorted(recent_years.keys(), reverse=True)[:5]:
            print(f"  {year}: {recent_years[year]} patents")
            
    except Exception as e:
        print(f"Error in technology analysis: {e}")


def defense_authority_analysis():
    """Analyze defense patents by filing authority/jurisdiction."""
    print("\n=== Defense Authority Analysis ===")
    
    try:
        # Search with authority-specific ordering
        results = patsnap.patents.search.by_defense_applicant(
            application="Northrop Grumman Corporation",
            collapse_by="AUTHORITY",
            collapse_order_authority=["US", "EP", "JP", "CN"],
            limit=25
        )
        
        print(f"Organization: Northrop Grumman Corporation")
        print(f"Authority priority: US > EP > JP > CN")
        print(f"Total defense patents: {results.total_search_result_count:,}")
        
        # Group by authority
        authority_stats = {}
        for patent in results.results:
            # Extract authority from patent number
            authority = patent.pn[:2] if len(patent.pn) >= 2 else "Unknown"
            if authority not in authority_stats:
                authority_stats[authority] = []
            authority_stats[authority].append(patent)
        
        print(f"\nPatents by filing authority:")
        for authority in ["US", "EP", "JP", "CN"]:
            if authority in authority_stats:
                patents = authority_stats[authority]
                print(f"\n{authority} Patents ({len(patents)}):")
                for patent in patents[:3]:  # Show top 3
                    print(f"  • {patent.pn}: {patent.title[:45]}...")
                    app_date = str(patent.apdt)
                    formatted_date = f"{app_date[:4]}-{app_date[4:6]}-{app_date[6:8]}"
                    print(f"    Filed: {formatted_date}")
                    
    except Exception as e:
        print(f"Error in authority analysis: {e}")


def defense_innovation_timeline():
    """Analyze defense innovation timeline and patent evolution."""
    print("\n=== Defense Innovation Timeline ===")
    
    try:
        # Get chronologically sorted defense patents
        results = patsnap.patents.search.by_defense_applicant(
            application="BAE Systems plc",
            sort=[{"field": "APD_YEARMONTHDAY", "order": "ASC"}],  # Oldest first
            limit=30
        )
        
        print(f"Organization: BAE Systems plc")
        print(f"Innovation timeline analysis:")
        
        # Group patents by decade for timeline analysis
        decades = {}
        for patent in results.results:
            app_year = int(str(patent.apdt)[:4])
            decade = (app_year // 10) * 10  # Round down to decade
            decade_key = f"{decade}s"
            
            if decade_key not in decades:
                decades[decade_key] = []
            decades[decade_key].append(patent)
        
        print(f"\nInnovation evolution by decade:")
        for decade in sorted(decades.keys()):
            patents = decades[decade]
            print(f"\n{decade} ({len(patents)} patents in sample):")
            
            # Show representative patents from each decade
            for patent in patents[:2]:
                app_date = str(patent.apdt)
                formatted_date = f"{app_date[:4]}-{app_date[4:6]}-{app_date[6:8]}"
                print(f"  • {patent.title}")
                print(f"    {patent.pn} | Filed: {formatted_date}")
                print(f"    Inventors: {patent.inventor}")
        
        print(f"\nTotal portfolio: {results.total_search_result_count:,} defense patents")
            
    except Exception as e:
        print(f"Error in innovation timeline analysis: {e}")


def international_defense_comparison():
    """Compare defense patent activity across different countries/regions."""
    print("\n=== International Defense Comparison ===")
    
    try:
        # Search for international defense organizations
        results = patsnap.patents.search.by_defense_applicant(
            application="MIT Lincoln Laboratory OR Johns Hopkins Applied Physics Laboratory",
            collapse_type="EXTEND",  # Patsnap family grouping
            limit=35
        )
        
        print(f"Defense Research Labs: MIT Lincoln Laboratory, Johns Hopkins Applied Physics Laboratory")
        print(f"Total defense research patents: {results.total_search_result_count:,}")
        
        # Analyze international filing patterns
        international_filings = {}
        domestic_filings = {}
        
        for patent in results.results:
            authority = patent.pn[:2] if len(patent.pn) >= 2 else "Unknown"
            
            if authority == "US":
                domestic_filings[patent.original_assignee] = domestic_filings.get(patent.original_assignee, 0) + 1
            else:
                if patent.original_assignee not in international_filings:
                    international_filings[patent.original_assignee] = {}
                international_filings[patent.original_assignee][authority] = international_filings[patent.original_assignee].get(authority, 0) + 1
        
        print(f"\nDomestic filings (US):")
        for org, count in domestic_filings.items():
            print(f"  {org}: {count} patents")
        
        if international_filings:
            print(f"\nInternational filings:")
            for org, authorities in international_filings.items():
                print(f"  {org}:")
                for auth, count in authorities.items():
                    print(f"    {auth}: {count} patents")
            
    except Exception as e:
        print(f"Error in international comparison: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("\n=== Error Handling Examples ===")
    
    # Test validation errors
    try:
        results = patsnap.patents.search.by_defense_applicant()  # Missing required application
    except Exception as e:
        print(f"Missing application error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_defense_applicant(
            application="Test Defense Organization",
            limit=2000  # Exceeds maximum of 1000
        )
    except Exception as e:
        print(f"Limit validation error (expected): {type(e).__name__}")
    
    try:
        results = patsnap.patents.search.by_defense_applicant(
            application="Test Defense Organization",
            offset=-1  # Negative offset
        )
    except Exception as e:
        print(f"Offset validation error (expected): {type(e).__name__}")


if __name__ == "__main__":
    print("Patsnap Defense Patent Search Examples")
    print("=" * 50)
    
    basic_defense_patent_search()
    multiple_defense_organizations()
    defense_technology_analysis()
    defense_authority_analysis()
    defense_innovation_timeline()
    international_defense_comparison()
    demonstrate_error_handling()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_defense_applicant()")
    print("- Search defense/military patents by applicant names")
    print("- Support for up to 100 organizations with OR logic")
    print("- Analyze defense technology trends and innovation")
    print("- Track international defense patent strategies")
    print("- Clean, discoverable namespace-based API")
