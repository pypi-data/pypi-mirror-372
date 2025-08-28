"""
Example usage of multi-image patent search endpoint.

This demonstrates how to search for visually similar patents using multiple uploaded images
(up to 4 images). Perfect for comprehensive design patent analysis where multiple views
or perspectives are needed to capture the complete design concept.
"""

import patsnap_pythonSDK as patsnap
from pathlib import Path

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def multi_view_design_search():
    """Search for design patents using multiple views of the same design."""
    print("=== Multi-View Design Patent Search ===")
    
    try:
        # Step 1: Upload multiple views of a design
        print("Step 1: Uploading multiple design views...")
        
        # For demo purposes, we'll use placeholder URLs
        # In real usage, you would upload your images first:
        # front_view = patsnap.patents.search.upload_image(image="design_front.jpg")
        # back_view = patsnap.patents.search.upload_image(image="design_back.jpg")
        # side_view = patsnap.patents.search.upload_image(image="design_side.jpg")
        
        image_urls = [
            "https://static-open.zhihuiya.com/sample/design_front.png",
            "https://static-open.zhihuiya.com/sample/design_back.png",
            "https://static-open.zhihuiya.com/sample/design_side.png"
        ]
        
        print(f"Using {len(image_urls)} design views:")
        for i, url in enumerate(image_urls, 1):
            print(f"  {i}. {url}")
        
        # Step 2: Search for similar design patents using multiple views
        print("Step 2: Searching for similar design patents...")
        results = patsnap.patents.search.by_multiple_images(
            urls=image_urls,
            patent_type="D",  # Design patents
            model=1,  # Smart Recommendation (uses first image for LOC prediction)
            limit=60,
            country=["US", "EU", "CN", "JP"],
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
        
        # Analyze multi-view search effectiveness
        high_similarity = [p for p in results.patent_messages if p.score and p.score >= 0.85]
        loc_matches = [p for p in results.patent_messages if p.loc_match == 1]
        
        print(f"\nMulti-View Search Analysis:")
        print(f"  High similarity (≥85%): {len(high_similarity)} patents")
        print(f"  LOC classification matches: {len(loc_matches)} patents")
        print(f"  Search effectiveness: {len(high_similarity)/len(results.patent_messages)*100:.1f}% high relevance")
        
        # Note about image order importance
        print(f"\n💡 Note: With Smart Recommendation model (model=1):")
        print(f"   • First image used for LOC prediction and result reordering")
        print(f"   • Image order affects search results")
        print(f"   • Place most representative view first for best results")
        
    except Exception as e:
        print(f"Error in multi-view design search: {e}")


def comprehensive_utility_search():
    """Search for utility patents using multiple technical diagrams."""
    print("\n=== Comprehensive Utility Patent Search ===")
    
    try:
        # Use multiple technical diagrams for comprehensive utility search
        technical_diagrams = [
            "https://static-open.zhihuiya.com/sample/utility_diagram1.png",
            "https://static-open.zhihuiya.com/sample/utility_diagram2.png",
            "https://static-open.zhihuiya.com/sample/utility_detail.png"
        ]
        
        print(f"Searching with {len(technical_diagrams)} technical diagrams:")
        for i, url in enumerate(technical_diagrams, 1):
            print(f"  {i}. {url}")
        
        # Search with shape & color model for comprehensive matching
        results = patsnap.patents.search.by_multiple_images(
            urls=technical_diagrams,
            patent_type="U",  # Utility patents
            model=4,  # Shape & color (recommended for utility)
            limit=50,
            country=["US", "CN", "JP", "DE"],
            apply_start_time="20190101",  # Recent patents
            apply_end_time="20240101"
        )
        
        print(f"Found {results.data.total_search_result_count} similar utility patents")
        print(f"Search timeframe: 2019-2024")
        
        # Analyze by technology complexity
        complexity_analysis = {
            'Simple': 0,
            'Moderate': 0, 
            'Complex': 0
        }
        
        for patent in results.patent_messages:
            title_lower = patent.title.lower()
            # Simple heuristic based on title complexity
            if any(word in title_lower for word in ['system', 'apparatus', 'assembly', 'device']):
                if any(word in title_lower for word in ['multi', 'integrated', 'advanced', 'intelligent']):
                    complexity_analysis['Complex'] += 1
                else:
                    complexity_analysis['Moderate'] += 1
            else:
                complexity_analysis['Simple'] += 1
        
        print(f"\nTechnology Complexity Distribution:")
        for complexity, count in complexity_analysis.items():
            percentage = (count / len(results.patent_messages)) * 100 if results.patent_messages else 0
            print(f"  {complexity}: {count} patents ({percentage:.1f}%)")
        
        # Show top similar utility patents
        if results.patent_messages:
            print(f"\nTop Similar Utility Patents:")
            for patent in results.patent_messages[:5]:
                print(f"  • {patent.title}")
                print(f"    {patent.patent_pn} | Score: {patent.score:.4f}")
                print(f"    Assignee: {patent.current_assignee}")
                
    except Exception as e:
        print(f"Error in comprehensive utility search: {e}")


def maximum_image_search():
    """Demonstrate search with maximum 4 images."""
    print("\n=== Maximum Image Search (4 Images) ===")
    
    try:
        # Use maximum allowed 4 images for most comprehensive search
        max_images = [
            "https://static-open.zhihuiya.com/sample/view_front.png",
            "https://static-open.zhihuiya.com/sample/view_back.png", 
            "https://static-open.zhihuiya.com/sample/view_side.png",
            "https://static-open.zhihuiya.com/sample/view_detail.png"
        ]
        
        print(f"Using maximum {len(max_images)} images for comprehensive search:")
        for i, url in enumerate(max_images, 1):
            print(f"  {i}. {url}")
        
        # Comprehensive search with all filtering options
        results = patsnap.patents.search.by_multiple_images(
            urls=max_images,
            patent_type="D",
            model=1,  # Smart Recommendation
            
            # Comprehensive filtering
            country=["US", "EU", "CN", "JP", "KR"],
            apply_start_time="20200101",
            apply_end_time="20240101",
            assignees="Apple",
            loc="(14-03 OR 14-02)",  # Mobile device designs
            legal_status="3,2",  # Granted, Examining
            simple_legal_status="1,2",  # Active, Pending
            
            # Search parameters
            limit=100,  # Maximum results
            field="SCORE",
            order="desc",
            lang="en",
            stemming=1
        )
        
        print(f"Comprehensive search results: {results.data.total_search_result_count}")
        print(f"Filters applied:")
        print(f"  • 4 image views for complete coverage")
        print(f"  • Date range: 2020-2024")
        print(f"  • Assignee: Apple")
        print(f"  • LOC: Mobile device designs")
        print(f"  • Status: Active/Pending, Granted/Examining")
        print(f"  • Geographic: 5 major jurisdictions")
        
        # Analyze comprehensive results
        if results.patent_messages:
            # Similarity distribution
            similarity_ranges = {
                'Excellent (90-100%)': 0,
                'High (80-89%)': 0,
                'Good (70-79%)': 0,
                'Moderate (60-69%)': 0,
                'Lower (<60%)': 0
            }
            
            for patent in results.patent_messages:
                if patent.score:
                    score_pct = patent.score * 100
                    if score_pct >= 90:
                        similarity_ranges['Excellent (90-100%)'] += 1
                    elif score_pct >= 80:
                        similarity_ranges['High (80-89%)'] += 1
                    elif score_pct >= 70:
                        similarity_ranges['Good (70-79%)'] += 1
                    elif score_pct >= 60:
                        similarity_ranges['Moderate (60-69%)'] += 1
                    else:
                        similarity_ranges['Lower (<60%)'] += 1
            
            print(f"\nSimilarity Distribution (4-Image Search):")
            for range_name, count in similarity_ranges.items():
                if count > 0:
                    print(f"  {range_name}: {count} patents")
            
            # Geographic distribution
            geo_dist = {}
            for patent in results.patent_messages:
                country_code = patent.patent_pn[:2]
                geo_dist[country_code] = geo_dist.get(country_code, 0) + 1
            
            print(f"\nGeographic Distribution:")
            for country, count in sorted(geo_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count} patents")
                
    except Exception as e:
        print(f"Error in maximum image search: {e}")


def image_order_comparison():
    """Demonstrate how image order affects Smart Recommendation results."""
    print("\n=== Image Order Impact Analysis ===")
    
    try:
        # Same images in different orders
        base_images = [
            "https://static-open.zhihuiya.com/sample/primary_view.png",
            "https://static-open.zhihuiya.com/sample/secondary_view.png",
            "https://static-open.zhihuiya.com/sample/detail_view.png"
        ]
        
        print("Testing impact of image order on Smart Recommendation model:")
        print("Same images, different order...")
        
        # Order 1: Primary view first
        print(f"\n--- Order 1: Primary → Secondary → Detail ---")
        results1 = patsnap.patents.search.by_multiple_images(
            urls=base_images,  # Original order
            patent_type="D",
            model=1,  # Smart Recommendation - order sensitive
            limit=30
        )
        
        print(f"Results with primary view first: {results1.total_search_result_count}")
        if results1.patent_messages:
            avg_score_1 = sum(p.score for p in results1.patent_messages if p.score) / len([p for p in results1.patent_messages if p.score])
            loc_matches_1 = sum(1 for p in results1.patent_messages if p.loc_match == 1)
            print(f"  Average similarity: {avg_score_1:.4f}")
            print(f"  LOC matches: {loc_matches_1}")
        
        # Order 2: Detail view first
        print(f"\n--- Order 2: Detail → Primary → Secondary ---")
        reordered_images = [base_images[2], base_images[0], base_images[1]]
        results2 = patsnap.patents.search.by_multiple_images(
            urls=reordered_images,  # Reordered
            patent_type="D",
            model=1,  # Smart Recommendation - order sensitive
            limit=30
        )
        
        print(f"Results with detail view first: {results2.total_search_result_count}")
        if results2.patent_messages:
            avg_score_2 = sum(p.score for p in results2.patent_messages if p.score) / len([p for p in results2.patent_messages if p.score])
            loc_matches_2 = sum(1 for p in results2.patent_messages if p.loc_match == 1)
            print(f"  Average similarity: {avg_score_2:.4f}")
            print(f"  LOC matches: {loc_matches_2}")
        
        # Compare results
        print(f"\n--- Order Impact Analysis ---")
        if results1.patent_messages and results2.patent_messages:
            print(f"Result count difference: {abs(results1.total_search_result_count - results2.total_search_result_count)}")
            print(f"Average score difference: {abs(avg_score_1 - avg_score_2):.4f}")
            print(f"LOC match difference: {abs(loc_matches_1 - loc_matches_2)}")
        
        print(f"\n💡 Key Insights:")
        print(f"  • Smart Recommendation model uses first image for LOC prediction")
        print(f"  • Different first images can lead to different result sets")
        print(f"  • Place most representative/characteristic view first")
        print(f"  • Consider primary use case when ordering images")
        
        # Recommendation
        print(f"\n📋 Best Practices:")
        print(f"  1. Primary/front view first for general similarity")
        print(f"  2. Most distinctive feature first for specific matching")
        print(f"  3. Highest quality image first for better LOC prediction")
        print(f"  4. Test different orders for optimal results")
        
    except Exception as e:
        print(f"Error in image order comparison: {e}")


def competitive_portfolio_analysis():
    """Comprehensive competitive analysis using multiple product images."""
    print("\n=== Competitive Portfolio Analysis ===")
    
    try:
        competitor = "Samsung"
        
        print(f"Competitive Analysis: {competitor}")
        print("Using multiple product images for comprehensive portfolio analysis...")
        
        # Multiple views of competitor's product
        competitor_images = [
            "https://static-open.zhihuiya.com/sample/competitor_front.png",
            "https://static-open.zhihuiya.com/sample/competitor_back.png",
            "https://static-open.zhihuiya.com/sample/competitor_side.png"
        ]
        
        print(f"Analyzing {len(competitor_images)} product views:")
        for i, url in enumerate(competitor_images, 1):
            print(f"  {i}. {url}")
        
        # Comprehensive competitive search
        results = patsnap.patents.search.by_multiple_images(
            urls=competitor_images,
            patent_type="D",
            model=1,
            assignees=competitor,
            limit=80,
            country=["US", "EU", "CN", "KR"],  # Key markets
            simple_legal_status="1,2",  # Active, Pending
            apply_start_time="20200101"  # Recent designs
        )
        
        print(f"Found {results.data.total_search_result_count} similar patents in {competitor}'s portfolio")
        
        # Timeline analysis
        timeline = {}
        for patent in results.patent_messages:
            year = str(patent.apdt)[:4]
            timeline[year] = timeline.get(year, 0) + 1
        
        print(f"\nDesign Evolution Timeline:")
        for year in sorted(timeline.keys()):
            print(f"  {year}: {timeline[year]} similar designs")
        
        # Similarity clustering
        similarity_clusters = {
            'Highly Similar (≥90%)': [],
            'Similar (80-89%)': [],
            'Related (70-79%)': [],
            'Loosely Related (<70%)': []
        }
        
        for patent in results.patent_messages:
            if patent.score:
                score_pct = patent.score * 100
                if score_pct >= 90:
                    similarity_clusters['Highly Similar (≥90%)'].append(patent)
                elif score_pct >= 80:
                    similarity_clusters['Similar (80-89%)'].append(patent)
                elif score_pct >= 70:
                    similarity_clusters['Related (70-79%)'].append(patent)
                else:
                    similarity_clusters['Loosely Related (<70%)'].append(patent)
        
        print(f"\nSimilarity Clustering:")
        for cluster_name, patents in similarity_clusters.items():
            print(f"  {cluster_name}: {len(patents)} patents")
            if patents and cluster_name.startswith('Highly'):
                print(f"    Top matches:")
                for patent in patents[:3]:
                    print(f"      • {patent.title} ({patent.score:.1%})")
        
        # Geographic strategy analysis
        geo_strategy = {}
        for patent in results.patent_messages:
            country_code = patent.patent_pn[:2]
            geo_strategy[country_code] = geo_strategy.get(country_code, 0) + 1
        
        print(f"\nGeographic Filing Strategy:")
        total_filings = sum(geo_strategy.values())
        for country, count in sorted(geo_strategy.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_filings) * 100
            print(f"  {country}: {count} patents ({percentage:.1f}%)")
        
        # Strategic insights
        print(f"\nStrategic Intelligence Summary:")
        print(f"  • Total similar designs: {results.data.total_search_result_count}")
        print(f"  • High similarity designs: {len(similarity_clusters['Highly Similar (≥90%)'])}")
        print(f"  • Active in {len(geo_strategy)} jurisdictions")
        print(f"  • Design activity span: {min(timeline.keys())}-{max(timeline.keys())}")
        print(f"  • Primary markets: {', '.join(list(geo_strategy.keys())[:3])}")
        
        # Competitive recommendations
        print(f"\n📊 Competitive Recommendations:")
        high_sim_count = len(similarity_clusters['Highly Similar (≥90%)'])
        if high_sim_count > 5:
            print(f"  🔴 HIGH OVERLAP: {high_sim_count} highly similar designs")
            print(f"     Consider differentiation strategies")
        elif high_sim_count > 0:
            print(f"  🟡 MODERATE OVERLAP: {high_sim_count} similar designs")
            print(f"     Monitor for potential conflicts")
        else:
            print(f"  🟢 LOW OVERLAP: Minimal direct design conflicts")
            print(f"     Opportunity for market entry")
            
    except Exception as e:
        print(f"Error in competitive portfolio analysis: {e}")


def design_family_discovery():
    """Discover design families using multiple related images."""
    print("\n=== Design Family Discovery ===")
    
    try:
        print("Design Family Discovery: Finding related design variations")
        
        # Multiple images representing a design family
        family_images = [
            "https://static-open.zhihuiya.com/sample/family_base.png",
            "https://static-open.zhihuiya.com/sample/family_variant1.png",
            "https://static-open.zhihuiya.com/sample/family_variant2.png",
            "https://static-open.zhihuiya.com/sample/family_detail.png"
        ]
        
        print(f"Searching with {len(family_images)} family member images:")
        for i, url in enumerate(family_images, 1):
            print(f"  {i}. {url}")
        
        # Search for design family members
        results = patsnap.patents.search.by_multiple_images(
            urls=family_images,
            patent_type="D",
            model=1,  # Smart Recommendation for family detection
            limit=100,
            country=["US", "EU", "CN"],
            apply_start_time="20180101",  # Broader timeframe for families
            loc="(14-03 OR 14-02 OR 14-04)",  # Related LOC codes
            simple_legal_status="1,2"
        )
        
        print(f"Found {results.data.total_search_result_count} potential family members")
        
        # Family relationship analysis
        family_tiers = {
            'Core Family (≥85%)': [],
            'Extended Family (70-84%)': [],
            'Related Designs (55-69%)': [],
            'Distant Relations (<55%)': []
        }
        
        for patent in results.patent_messages:
            if patent.score:
                score_pct = patent.score * 100
                if score_pct >= 85:
                    family_tiers['Core Family (≥85%)'].append(patent)
                elif score_pct >= 70:
                    family_tiers['Extended Family (70-84%)'].append(patent)
                elif score_pct >= 55:
                    family_tiers['Related Designs (55-69%)'].append(patent)
                else:
                    family_tiers['Distant Relations (<55%)'].append(patent)
        
        print(f"\nDesign Family Structure:")
        for tier_name, patents in family_tiers.items():
            print(f"  {tier_name}: {len(patents)} designs")
            if patents and len(patents) <= 5:  # Show details for smaller groups
                for patent in patents:
                    print(f"    • {patent.title} ({patent.score:.1%}) - {patent.patent_pn}")
        
        # Assignee family analysis
        assignee_families = {}
        for patent in results.patent_messages:
            assignee = patent.current_assignee
            if assignee not in assignee_families:
                assignee_families[assignee] = []
            assignee_families[assignee].append(patent)
        
        print(f"\nDesign Family Ownership:")
        for assignee, patents in sorted(assignee_families.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            avg_similarity = sum(p.score for p in patents if p.score) / len([p for p in patents if p.score])
            print(f"  {assignee}: {len(patents)} designs (avg similarity: {avg_similarity:.1%})")
        
        # Timeline of family development
        family_timeline = {}
        for patent in results.patent_messages:
            year = str(patent.apdt)[:4]
            if year not in family_timeline:
                family_timeline[year] = []
            family_timeline[year].append(patent)
        
        print(f"\nFamily Development Timeline:")
        for year in sorted(family_timeline.keys()):
            patents = family_timeline[year]
            avg_sim = sum(p.score for p in patents if p.score) / len([p for p in patents if p.score])
            print(f"  {year}: {len(patents)} designs (avg similarity: {avg_sim:.1%})")
        
        # Family insights
        core_family_size = len(family_tiers['Core Family (≥85%)'])
        total_family_size = sum(len(patents) for patents in family_tiers.values())
        
        print(f"\nDesign Family Insights:")
        print(f"  • Core family size: {core_family_size} designs")
        print(f"  • Total family size: {total_family_size} designs")
        print(f"  • Family cohesion: {(core_family_size/total_family_size)*100:.1f}% core similarity")
        print(f"  • Development span: {min(family_timeline.keys())}-{max(family_timeline.keys())}")
        print(f"  • Primary owner: {max(assignee_families.keys(), key=lambda x: len(assignee_families[x]))}")
        
        # Family strategy recommendations
        print(f"\n🎯 Family Strategy Recommendations:")
        if core_family_size > 10:
            print(f"  • Large design family detected - consider family-wide analysis")
            print(f"  • Monitor for continuation applications and divisionals")
        elif core_family_size > 3:
            print(f"  • Moderate family size - track design evolution patterns")
        else:
            print(f"  • Small family - opportunity for expansion or variation")
            
    except Exception as e:
        print(f"Error in design family discovery: {e}")


def complete_multi_image_workflow():
    """Demonstrate complete workflow from upload to multi-image analysis."""
    print("\n=== Complete Multi-Image Workflow ===")
    
    try:
        print("Complete Multi-Image Workflow: Upload → Search → Analyze")
        
        # Step 1: Upload multiple images
        print("\nStep 1: Upload Multiple Patent Images")
        image_paths = [
            "path/to/design_front.jpg",
            "path/to/design_back.jpg", 
            "path/to/design_side.jpg"
        ]
        
        print(f"  Uploading {len(image_paths)} images:")
        for i, path in enumerate(image_paths, 1):
            print(f"    {i}. {path}")
        
        # For demo, simulate uploads
        # upload_results = []
        # for path in image_paths:
        #     result = patsnap.patents.search.upload_image(image=path)
        #     upload_results.append(result)
        #     print(f"    ✓ Uploaded: {result.url}")
        
        # Using demo URLs
        demo_urls = [
            "https://static-open.zhihuiya.com/sample/workflow_front.png",
            "https://static-open.zhihuiya.com/sample/workflow_back.png",
            "https://static-open.zhihuiya.com/sample/workflow_side.png"
        ]
        
        print(f"  Using demo URLs:")
        for i, url in enumerate(demo_urls, 1):
            print(f"    {i}. {url}")
        
        # Step 2: Perform multi-image search
        print(f"\nStep 2: Multi-Image Patent Search")
        results = patsnap.patents.search.by_multiple_images(
            urls=demo_urls,
            patent_type="D",
            model=1,  # Smart Recommendation
            limit=75,
            country=["US", "EU", "CN"],
            simple_legal_status="1,2"  # Active, Pending
        )
        
        print(f"  ✓ Found: {results.data.total_search_result_count} similar patents")
        
        # Step 3: Comprehensive analysis
        print(f"\nStep 3: Multi-Image Analysis")
        
        # Image contribution analysis (simulated)
        print(f"  Image Contribution Analysis:")
        print(f"    • Front view: Primary LOC prediction and base matching")
        print(f"    • Back view: Additional perspective validation")
        print(f"    • Side view: Profile and edge detail matching")
        print(f"    • Combined effect: Enhanced similarity confidence")
        
        # Similarity distribution
        similarity_analysis = {'90-100%': 0, '80-89%': 0, '70-79%': 0, '60-69%': 0, '<60%': 0}
        for patent in results.patent_messages:
            if patent.score:
                score_pct = patent.score * 100
                if score_pct >= 90:
                    similarity_analysis['90-100%'] += 1
                elif score_pct >= 80:
                    similarity_analysis['80-89%'] += 1
                elif score_pct >= 70:
                    similarity_analysis['70-79%'] += 1
                elif score_pct >= 60:
                    similarity_analysis['60-69%'] += 1
                else:
                    similarity_analysis['<60%'] += 1
        
        print(f"  Multi-Image Similarity Distribution:")
        for range_name, count in similarity_analysis.items():
            if count > 0:
                print(f"    {range_name}: {count} patents")
        
        # LOC match analysis
        loc_matches = sum(1 for p in results.patent_messages if p.loc_match == 1)
        loc_match_rate = (loc_matches / len(results.patent_messages)) * 100 if results.patent_messages else 0
        
        print(f"  LOC Classification Analysis:")
        print(f"    • LOC matches: {loc_matches}/{len(results.patent_messages)} ({loc_match_rate:.1f}%)")
        print(f"    • Classification accuracy: {'High' if loc_match_rate > 70 else 'Moderate' if loc_match_rate > 40 else 'Low'}")
        
        # Step 4: Generate comprehensive insights
        print(f"\nStep 4: Generate Multi-Image Insights")
        
        high_similarity = [p for p in results.patent_messages if p.score and p.score >= 0.8]
        
        print(f"  Key Multi-Image Findings:")
        print(f"    • Total similar patents: {results.data.total_search_result_count}")
        print(f"    • High similarity (≥80%): {len(high_similarity)} patents")
        print(f"    • LOC classification matches: {loc_matches} patents")
        print(f"    • Multi-view coverage: {len(demo_urls)} perspectives")
        print(f"    • Search confidence: Enhanced by multiple views")
        
        # Comparative advantage
        print(f"\n📈 Multi-Image Search Advantages:")
        print(f"    • Comprehensive coverage: Multiple perspectives reduce blind spots")
        print(f"    • Enhanced accuracy: Cross-validation between views")
        print(f"    • Better LOC prediction: Primary view optimizes classification")
        print(f"    • Reduced false positives: Multiple views filter irrelevant matches")
        print(f"    • Complete design capture: Full design concept representation")
        
        if high_similarity:
            print(f"\n🎯 Multi-Image Recommendations:")
            print(f"    • Review {len(high_similarity)} high-similarity patents for comprehensive analysis")
            print(f"    • Consider all views when assessing design similarity")
            print(f"    • Use image order strategically for optimal LOC prediction")
            print(f"    • Leverage multiple perspectives for thorough prior art assessment")
        
    except Exception as e:
        print(f"Error in complete multi-image workflow: {e}")


if __name__ == "__main__":
    print("Patsnap Multi-Image Patent Search Examples")
    print("=" * 60)
    
    multi_view_design_search()
    comprehensive_utility_search()
    maximum_image_search()
    image_order_comparison()
    competitive_portfolio_analysis()
    design_family_discovery()
    complete_multi_image_workflow()
    
    print("\n" + "=" * 60)
    print("Multi-Image Search Examples Complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_multiple_images()")
    print("- Multi-image visual patent similarity search (up to 4 images)")
    print("- Enhanced accuracy through multiple perspectives")
    print("- Smart Recommendation model uses first image for LOC prediction")
    print("- Image order affects results - place most representative view first")
    print("- Perfect for comprehensive design patent analysis")
    print("- Ideal for competitive intelligence and design family discovery")
    print("- Clean, discoverable namespace-based API")
