"""
Example usage of image-based patent search endpoint.

This demonstrates how to search for visually similar patents using uploaded images.
Supports both design patents and utility patents with different search models
optimized for each type. Perfect for visual prior art research and competitive analysis.
"""

import patsnap_pythonSDK as patsnap
from pathlib import Path

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def design_patent_search():
    """Search for design patents using image similarity."""
    print("=== Design Patent Image Search ===")
    
    try:
        # Step 1: Upload the design image
        print("Step 1: Uploading design image...")
        image_path = "path/to/design_patent_image.jpg"
        
        # For demo purposes, we'll use a placeholder URL
        # In real usage, you would upload your image first:
        # upload_result = patsnap.patents.search.upload_image(image=image_path)
        # image_url = upload_result.url
        
        image_url = "https://static-open.zhihuiya.com/sample/design_demo.png"
        
        print(f"Using image URL: {image_url}")
        
        # Step 2: Search for similar design patents
        print("Step 2: Searching for similar design patents...")
        results = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="D",  # Design patents
            model=1,  # Smart Recommendation (recommended for designs)
            limit=50,
            country=["US", "EU", "CN"],
            lang="en"
        )
        
        print(f"Found {results.data.total_search_result_count} similar design patents")
        print(f"Showing first {len(results.patent_messages)} results:")
        
        for i, patent in enumerate(results.patent_messages[:10], 1):
            print(f"\n{i:2d}. {patent.title}")
            print(f"    Patent: {patent.patent_pn}")
            print(f"    Similarity Score: {patent.score:.4f}")
            print(f"    LOC Match: {'Yes' if patent.loc_match == 1 else 'No'}")
            print(f"    Filed: {patent.apdt} | Published: {patent.pbdt}")
            print(f"    Assignee: {patent.current_assignee}")
            print(f"    Image: {patent.url[:60]}...")
        
        # Analyze similarity distribution
        high_similarity = [p for p in results.patent_messages if p.score and p.score >= 0.8]
        medium_similarity = [p for p in results.patent_messages if p.score and 0.6 <= p.score < 0.8]
        low_similarity = [p for p in results.patent_messages if p.score and p.score < 0.6]
        
        print(f"\nSimilarity Analysis:")
        print(f"  High similarity (≥80%): {len(high_similarity)} patents")
        print(f"  Medium similarity (60-79%): {len(medium_similarity)} patents")
        print(f"  Lower similarity (<60%): {len(low_similarity)} patents")
        
    except Exception as e:
        print(f"Error in design patent search: {e}")


def utility_patent_search():
    """Search for utility patents using image similarity."""
    print("\n=== Utility Patent Image Search ===")
    
    try:
        # Use a utility patent image (technical diagram, mechanical drawing)
        image_url = "https://static-open.zhihuiya.com/sample/utility_demo.png"
        
        print(f"Searching for utility patents similar to: {image_url}")
        
        # Search with shape & color model (recommended for utility patents)
        results = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="U",  # Utility patents
            model=4,  # Search by shape & color (recommended)
            limit=30,
            country=["US", "CN", "JP"],
            apply_start_time="20180101",  # Recent patents
            apply_end_time="20240101"
        )
        
        print(f"Found {results.data.total_search_result_count} similar utility patents")
        print(f"Search timeframe: 2018-2024")
        
        # Analyze by technology area based on titles
        tech_areas = {}
        for patent in results.patent_messages:
            title_lower = patent.title.lower()
            if any(word in title_lower for word in ['mechanical', 'machine', 'device', 'apparatus']):
                tech = 'Mechanical Engineering'
            elif any(word in title_lower for word in ['electronic', 'circuit', 'sensor', 'semiconductor']):
                tech = 'Electronics'
            elif any(word in title_lower for word in ['optical', 'lens', 'laser', 'light']):
                tech = 'Optics'
            elif any(word in title_lower for word in ['chemical', 'compound', 'material', 'polymer']):
                tech = 'Materials/Chemistry'
            else:
                tech = 'Other Technology'
            
            tech_areas[tech] = tech_areas.get(tech, 0) + 1
        
        print(f"\nTechnology Distribution:")
        for tech, count in sorted(tech_areas.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tech}: {count} patents")
        
        # Show top similar patents
        if results.patent_messages:
            print(f"\nTop Similar Utility Patents:")
            for patent in results.patent_messages[:5]:
                print(f"  • {patent.title}")
                print(f"    {patent.patent_pn} | Score: {patent.score:.4f}")
                print(f"    Assignee: {patent.current_assignee}")
                
    except Exception as e:
        print(f"Error in utility patent search: {e}")


def advanced_filtering_search():
    """Demonstrate advanced filtering options for image search."""
    print("\n=== Advanced Filtering Image Search ===")
    
    try:
        image_url = "https://static-open.zhihuiya.com/sample/advanced_demo.png"
        
        # Search with comprehensive filtering
        results = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="D",
            model=1,
            
            # Date filters
            apply_start_time="20200101",
            apply_end_time="20230101",
            public_start_time="20200601",
            public_end_time="20230601",
            
            # Company and legal status filters
            assignees="Apple",
            legal_status="3,2",  # Granted, Examining
            simple_legal_status="1,2",  # Active, Pending
            
            # Design classification filter
            loc="(14-03 OR 14-02)",  # Mobile phone designs
            
            # Search parameters
            field="SCORE",  # Sort by similarity
            order="desc",
            limit=40,
            offset=0,
            
            # Language and display options
            lang="en",
            is_https=1,  # Return HTTPS image URLs
            include_machine_translation=True,
            
            # Advanced options
            stemming=1,  # Enable stemming
            pre_filter=1  # Enable pre-filtering
        )
        
        print(f"Advanced filtered search results: {results.data.total_search_result_count}")
        print(f"Filters applied:")
        print(f"  • Date range: 2020-2023 (application and publication)")
        print(f"  • Assignee: Apple")
        print(f"  • Legal status: Granted, Examining")
        print(f"  • LOC classification: Mobile phone designs")
        print(f"  • Language: English")
        print(f"  • HTTPS images enabled")
        
        if results.patent_messages:
            print(f"\nFiltered Results:")
            for i, patent in enumerate(results.patent_messages[:5], 1):
                print(f"{i}. {patent.title}")
                print(f"   Score: {patent.score:.4f} | LOC Match: {patent.loc_match}")
                print(f"   Filed: {patent.apdt} | {patent.current_assignee}")
                
    except Exception as e:
        print(f"Error in advanced filtering search: {e}")


def competitive_analysis_workflow():
    """Complete workflow for competitive patent analysis using images."""
    print("\n=== Competitive Analysis Workflow ===")
    
    try:
        # Scenario: Analyzing competitor's design patent portfolio
        competitor_name = "Samsung"
        
        print(f"Competitive Analysis Target: {competitor_name}")
        
        # Step 1: Upload competitor's product image
        image_url = "https://static-open.zhihuiya.com/sample/competitor_product.png"
        print(f"Step 1: Analyzing product image: {image_url}")
        
        # Step 2: Find similar patents in competitor's portfolio
        results = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="D",
            model=1,
            assignees=competitor_name,
            limit=50,
            country=["US", "EU", "CN", "KR"],  # Key markets
            simple_legal_status="1,2"  # Active, Pending only
        )
        
        print(f"Step 2: Found {results.data.total_search_result_count} similar patents in {competitor_name}'s portfolio")
        
        # Step 3: Analyze patent timeline
        timeline = {}
        for patent in results.patent_messages:
            year = str(patent.apdt)[:4]
            timeline[year] = timeline.get(year, 0) + 1
        
        print(f"\nStep 3: Patent Timeline Analysis")
        for year in sorted(timeline.keys()):
            print(f"  {year}: {timeline[year]} similar patents")
        
        # Step 4: Identify design evolution patterns
        high_similarity_patents = [p for p in results.patent_messages if p.score and p.score >= 0.8]
        
        if high_similarity_patents:
            print(f"\nStep 4: High Similarity Patents ({len(high_similarity_patents)} found)")
            print("These patents show strong visual similarity to the analyzed product:")
            
            for patent in high_similarity_patents[:3]:
                print(f"  • {patent.title}")
                print(f"    {patent.patent_pn} | Score: {patent.score:.4f}")
                print(f"    Filed: {patent.apdt} | Status: Active")
        
        # Step 5: Geographic distribution analysis
        geo_distribution = {}
        for patent in results.patent_messages:
            country_code = patent.patent_pn[:2]
            geo_distribution[country_code] = geo_distribution.get(country_code, 0) + 1
        
        print(f"\nStep 5: Geographic Distribution")
        for country, count in sorted(geo_distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"  {country}: {count} patents")
        
        print(f"\nCompetitive Intelligence Summary:")
        print(f"  • Total similar designs: {results.data.total_search_result_count}")
        print(f"  • High similarity matches: {len(high_similarity_patents)}")
        print(f"  • Active in {len(geo_distribution)} jurisdictions")
        print(f"  • Design activity span: {min(timeline.keys())}-{max(timeline.keys())}")
        
    except Exception as e:
        print(f"Error in competitive analysis: {e}")


def prior_art_discovery():
    """Use image search for comprehensive prior art discovery."""
    print("\n=== Prior Art Discovery via Image Search ===")
    
    try:
        # Scenario: Searching for prior art before filing a new design
        invention_image = "https://static-open.zhihuiya.com/sample/new_invention.png"
        
        print(f"Prior Art Search for New Design")
        print(f"Invention image: {invention_image}")
        
        # Comprehensive prior art search
        results = patsnap.patents.search.by_image(
            url=invention_image,
            patent_type="D",
            model=1,  # Smart recommendation for thorough search
            limit=100,  # Maximum results
            
            # Search globally
            country=["US", "EU", "CN", "JP", "KR"],
            
            # Include all time periods (no date filters)
            # Include all legal statuses for comprehensive coverage
            
            # Use original language to avoid translation bias
            lang="original",
            
            # Enable all search enhancements
            stemming=1,
            pre_filter=1
        )
        
        print(f"Prior Art Search Results: {results.data.total_search_result_count} potentially relevant patents")
        
        # Categorize by similarity level for prior art assessment
        critical_prior_art = []  # Very high similarity (>90%)
        relevant_prior_art = []  # High similarity (70-90%)
        reference_prior_art = []  # Moderate similarity (50-70%)
        
        for patent in results.patent_messages:
            if patent.score:
                if patent.score >= 0.9:
                    critical_prior_art.append(patent)
                elif patent.score >= 0.7:
                    relevant_prior_art.append(patent)
                elif patent.score >= 0.5:
                    reference_prior_art.append(patent)
        
        print(f"\nPrior Art Assessment:")
        print(f"  Critical Prior Art (≥90% similarity): {len(critical_prior_art)} patents")
        print(f"  Relevant Prior Art (70-89% similarity): {len(relevant_prior_art)} patents")
        print(f"  Reference Prior Art (50-69% similarity): {len(reference_prior_art)} patents")
        
        if critical_prior_art:
            print(f"\n⚠️  CRITICAL PRIOR ART FOUND:")
            for patent in critical_prior_art:
                print(f"  • {patent.title}")
                print(f"    {patent.patent_pn} | Similarity: {patent.score:.1%}")
                print(f"    Filed: {patent.apdt} | Assignee: {patent.current_assignee}")
                print(f"    ⚠️  HIGH RISK - Review for novelty assessment")
        
        # Timeline analysis for prior art
        if results.patent_messages:
            earliest_patent = min(results.patent_messages, key=lambda x: x.apdt)
            latest_patent = max(results.patent_messages, key=lambda x: x.apdt)
            
            print(f"\nPrior Art Timeline:")
            print(f"  Earliest similar patent: {earliest_patent.apdt} ({earliest_patent.patent_pn})")
            print(f"  Latest similar patent: {latest_patent.apdt} ({latest_patent.patent_pn})")
        
        # Recommendations
        print(f"\nRecommendations:")
        if critical_prior_art:
            print(f"  🔴 HIGH RISK: {len(critical_prior_art)} patents with >90% similarity")
            print(f"     Recommend detailed novelty analysis before filing")
        elif relevant_prior_art:
            print(f"  🟡 MEDIUM RISK: {len(relevant_prior_art)} patents with 70-89% similarity")
            print(f"     Review for distinguishing features")
        else:
            print(f"  🟢 LOW RISK: No high-similarity prior art found")
            print(f"     Proceed with standard prior art review")
            
    except Exception as e:
        print(f"Error in prior art discovery: {e}")


def search_model_comparison():
    """Compare different search models for design and utility patents."""
    print("\n=== Search Model Comparison ===")
    
    try:
        image_url = "https://static-open.zhihuiya.com/sample/comparison_demo.png"
        
        print("Comparing search models for the same image:")
        print(f"Test image: {image_url}")
        
        # Design Patent Models
        print(f"\n--- Design Patent Models ---")
        
        # Model 1: Smart Recommendation
        design_smart = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="D",
            model=1,  # Smart Recommendation
            limit=20
        )
        
        print(f"Model 1 (Smart Recommendation): {design_smart.total_search_result_count} results")
        if design_smart.patent_messages:
            avg_score_1 = sum(p.score for p in design_smart.patent_messages if p.score) / len([p for p in design_smart.patent_messages if p.score])
            print(f"  Average similarity score: {avg_score_1:.4f}")
        
        # Model 2: Image Search
        design_image = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="D",
            model=2,  # Image Search
            limit=20
        )
        
        print(f"Model 2 (Image Search): {design_image.total_search_result_count} results")
        if design_image.patent_messages:
            avg_score_2 = sum(p.score for p in design_image.patent_messages if p.score) / len([p for p in design_image.patent_messages if p.score])
            print(f"  Average similarity score: {avg_score_2:.4f}")
        
        # Utility Patent Models
        print(f"\n--- Utility Patent Models ---")
        
        # Model 3: Shape only
        utility_shape = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="U",
            model=3,  # Shape only
            limit=20
        )
        
        print(f"Model 3 (Shape only): {utility_shape.total_search_result_count} results")
        
        # Model 4: Shape & color
        utility_color = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="U",
            model=4,  # Shape & color
            limit=20
        )
        
        print(f"Model 4 (Shape & color): {utility_color.total_search_result_count} results")
        
        print(f"\nModel Selection Guidelines:")
        print(f"Design Patents:")
        print(f"  • Model 1 (Smart Recommendation): Best for general design searches")
        print(f"  • Model 2 (Image Search): More focused on visual similarity")
        print(f"Utility Patents:")
        print(f"  • Model 3 (Shape only): Focus on structural similarity")
        print(f"  • Model 4 (Shape & color): Comprehensive visual matching (recommended)")
        
    except Exception as e:
        print(f"Error in model comparison: {e}")


def complete_image_workflow():
    """Demonstrate complete workflow from upload to analysis."""
    print("\n=== Complete Image Search Workflow ===")
    
    try:
        print("Complete Workflow: Upload → Search → Analyze")
        
        # Step 1: Upload image
        print("\nStep 1: Upload Patent Image")
        image_path = "path/to/your/patent_image.jpg"
        
        # For demo, we'll simulate the upload
        print(f"  Uploading: {image_path}")
        # upload_result = patsnap.patents.search.upload_image(image=image_path)
        # print(f"  ✓ Uploaded: {upload_result.url}")
        # print(f"  ✓ Expires: {upload_result.expire} seconds")
        
        # Using demo URL
        image_url = "https://static-open.zhihuiya.com/sample/workflow_demo.png"
        print(f"  Using demo URL: {image_url}")
        
        # Step 2: Perform image search
        print(f"\nStep 2: Search for Similar Patents")
        results = patsnap.patents.search.by_image(
            url=image_url,
            patent_type="D",
            model=1,
            limit=50,
            country=["US", "EU", "CN"],
            simple_legal_status="1,2"  # Active, Pending
        )
        
        print(f"  ✓ Found: {results.data.total_search_result_count} similar patents")
        
        # Step 3: Analyze results
        print(f"\nStep 3: Analyze Search Results")
        
        # Similarity analysis
        similarity_ranges = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '60-69%': 0, '<60%': 0}
        for patent in results.patent_messages:
            if patent.score:
                score_pct = patent.score * 100
                if score_pct >= 90:
                    similarity_ranges['90-100%'] += 1
                elif score_pct >= 80:
                    similarity_ranges['80-89%'] += 1
                elif score_pct >= 70:
                    similarity_ranges['70-79%'] += 1
                elif score_pct >= 60:
                    similarity_ranges['60-69%'] += 1
                else:
                    similarity_ranges['<60%'] += 1
        
        print(f"  Similarity Distribution:")
        for range_name, count in similarity_ranges.items():
            if count > 0:
                print(f"    {range_name}: {count} patents")
        
        # Top assignees
        assignee_counts = {}
        for patent in results.patent_messages:
            assignee = patent.current_assignee
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        print(f"  Top Assignees:")
        for assignee, count in sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"    {assignee}: {count} patents")
        
        # Step 4: Generate insights
        print(f"\nStep 4: Generate Insights")
        high_similarity = [p for p in results.patent_messages if p.score and p.score >= 0.8]
        
        print(f"  Key Findings:")
        print(f"    • Total similar patents: {results.data.total_search_result_count}")
        print(f"    • High similarity (≥80%): {len(high_similarity)} patents")
        print(f"    • Active assignees: {len(assignee_counts)}")
        print(f"    • Geographic coverage: {len(set(p.patent_pn[:2] for p in results.patent_messages))}")
        
        if high_similarity:
            print(f"  Recommendations:")
            print(f"    • Review {len(high_similarity)} high-similarity patents for novelty")
            print(f"    • Consider design modifications to increase differentiation")
            print(f"    • Monitor competitor activity in this design space")
        
    except Exception as e:
        print(f"Error in complete workflow: {e}")


if __name__ == "__main__":
    print("Patsnap Image-Based Patent Search Examples")
    print("=" * 60)
    
    design_patent_search()
    utility_patent_search()
    advanced_filtering_search()
    competitive_analysis_workflow()
    prior_art_discovery()
    search_model_comparison()
    complete_image_workflow()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_image()")
    print("- Visual patent similarity search")
    print("- Design patents (D) and Utility patents (U)")
    print("- Multiple search models optimized for each type")
    print("- Up to 100 results per search with similarity scores")
    print("- Comprehensive filtering and geographic coverage")
    print("- Perfect for prior art research and competitive analysis")
    print("- Clean, discoverable namespace-based API")
