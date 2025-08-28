"""
Example usage of semantic patent search endpoint.

This demonstrates how to find patents using semantic analysis of technical text,
abstracts, or descriptions. Ideal for prior art research, technology discovery,
and patent landscape analysis using natural language descriptions.
"""

import patsnap_pythonSDK as patsnap

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_semantic_search():
    """Basic semantic search using technical description."""
    print("=== Basic Semantic Patent Search ===")
    
    try:
        # Example technical description (>200 words recommended)
        technical_description = """
        The invention discloses an automobile front-view based wireless video transmission system and method. 
        The system comprises a front-view camera, a wireless video transmitting module, a wireless video 
        receiving module, a display screen, a display triggering device, a first controller, a wireless 
        command transmitting module, a wireless command receiving module, a second controller and an automobile 
        starting detecting module, wherein the display screen is connected with the wireless video receiving 
        module; the front-view camera is connected with the wireless video transmitting module; the wireless 
        video transmitting module is wirelessly connected with the wireless video receiving module and 
        wirelessly transmits a video shot by the front-view camera; and the wireless video receiving module 
        receives and sends the video and displays the video on the display screen, so that the mounting time 
        of the front-view camera is shortened greatly, no damage can be caused to an original automobile, 
        the front-view camera can be mounted without a threading manner, and great convenience is brought 
        to the owner of the automobile.
        """
        
        results = patsnap.patents.search.by_semantic_text(
            text=technical_description,
            limit=20,
            relevancy="70%"
        )
        
        print(f"Search Query: Automobile wireless video transmission system")
        print(f"Minimum relevancy: 70%")
        print(f"Total semantically similar patents: {results.data.total_search_result_count:,}")
        print(f"Showing first {len(results.data.results)} patents:")
        
        for i, patent in enumerate(results.data.results, 1):
            print(f"{i:2d}. {patent.title}")
            print(f"    Patent: {patent.pn} | Relevancy: {patent.relevancy}")
            print(f"    Filed: {patent.apdt} | Published: {patent.pbdt}")
            print(f"    Assignee: {patent.current_assignee}")
            print(f"    Inventors: {patent.inventor}")
            print()
            
    except Exception as e:
        print(f"Error in basic semantic search: {e}")


def ai_machine_learning_search():
    """Search for AI/ML patents using technical abstract."""
    print("=== AI/Machine Learning Semantic Search ===")
    
    try:
        # AI/ML technical abstract
        ai_abstract = """
        This invention presents a novel deep learning architecture for real-time object detection and 
        classification in autonomous vehicles. The system employs a multi-scale convolutional neural 
        network (CNN) with attention mechanisms to process high-resolution camera feeds and LiDAR data 
        simultaneously. The architecture includes a feature pyramid network for detecting objects at 
        various scales, from pedestrians to large vehicles, with improved accuracy in challenging 
        weather conditions. The model incorporates transfer learning techniques using pre-trained 
        weights and implements a custom loss function that balances detection accuracy with inference 
        speed. Additionally, the system features an adaptive learning rate scheduler and data 
        augmentation strategies specifically designed for automotive scenarios. The invention addresses 
        critical safety requirements in autonomous driving by providing robust object detection 
        capabilities with sub-100ms latency, enabling real-time decision making for collision 
        avoidance and path planning systems.
        """
        
        results = patsnap.patents.search.by_semantic_text(
            text=ai_abstract,
            limit=30,
            relevancy="60%",
            country=["USA", "USB", "EPA", "EPB", "CNA", "CNB"]
        )
        
        print(f"Search Domain: AI/Machine Learning for Autonomous Vehicles")
        print(f"Geographic scope: US, EP, CN")
        print(f"Semantically related patents: {results.data.total_search_result_count:,}")
        
        # Analyze by technology focus
        ai_keywords = {
            'deep_learning': ['deep learning', 'neural network', 'cnn', 'convolutional'],
            'computer_vision': ['object detection', 'image processing', 'computer vision', 'recognition'],
            'autonomous_vehicles': ['autonomous', 'self-driving', 'vehicle', 'automotive'],
            'machine_learning': ['machine learning', 'artificial intelligence', 'algorithm', 'training']
        }
        
        tech_categories = {category: [] for category in ai_keywords.keys()}
        
        for patent in results.data.results:
            title_lower = patent.title.lower()
            for category, keywords in ai_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    tech_categories[category].append(patent)
                    break
        
        print(f"\nTechnology Distribution:")
        for category, patents in tech_categories.items():
            if patents:
                print(f"  {category.replace('_', ' ').title()}: {len(patents)} patents")
                # Show top patent in each category
                top_patent = max(patents, key=lambda x: int(x.relevancy.replace('%', '')))
                print(f"    Top: {top_patent.title[:50]}... (Relevancy: {top_patent.relevancy})")
            
    except Exception as e:
        print(f"Error in AI/ML search: {e}")


def biotech_pharmaceutical_search():
    """Search for biotech/pharmaceutical patents using research description."""
    print("\n=== Biotech/Pharmaceutical Semantic Search ===")
    
    try:
        # Biotech research description
        biotech_description = """
        The present invention relates to a novel gene therapy approach for treating inherited retinal 
        diseases using CRISPR-Cas9 gene editing technology. The method involves the delivery of 
        therapeutic genes to photoreceptor cells in the retina through adeno-associated virus (AAV) 
        vectors specifically engineered for retinal targeting. The invention includes optimized guide 
        RNA sequences designed to correct mutations in genes such as RPE65, LHON, and ABCA4 that 
        cause various forms of blindness. The therapeutic system incorporates a dual-vector approach 
        where the Cas9 protein and guide RNAs are delivered separately to enhance safety and reduce 
        immunogenic responses. Additionally, the invention features novel promoter sequences that 
        ensure cell-type-specific expression in retinal pigment epithelium and photoreceptor cells. 
        The method demonstrates improved efficacy in animal models with sustained gene expression 
        for over 12 months and minimal off-target effects. Clinical applications include treatment 
        of Leber congenital amaurosis, Stargardt disease, and age-related macular degeneration.
        """
        
        results = patsnap.patents.search.by_semantic_text(
            text=biotech_description,
            limit=25,
            relevancy="65%",
            pbd_from="20180101",  # Recent publications
            pbd_to="20240101"
        )
        
        print(f"Search Domain: Gene Therapy & CRISPR Technology")
        print(f"Publication timeframe: 2018-2024")
        print(f"Related biotech patents: {results.data.total_search_result_count:,}")
        
        # Analyze by assignee type
        assignee_types = {'academic': [], 'pharma': [], 'biotech': [], 'other': []}
        
        for patent in results.data.results:
            assignee = patent.current_assignee.lower()
            if any(word in assignee for word in ['university', 'institute', 'college', 'research']):
                assignee_types['academic'].append(patent)
            elif any(word in assignee for word in ['pharma', 'pharmaceutical', 'roche', 'pfizer', 'novartis']):
                assignee_types['pharma'].append(patent)
            elif any(word in assignee for word in ['biotech', 'bio', 'therapeutics', 'genetics']):
                assignee_types['biotech'].append(patent)
            else:
                assignee_types['other'].append(patent)
        
        print(f"\nPatent Holders by Type:")
        for org_type, patents in assignee_types.items():
            if patents:
                print(f"  {org_type.title()}: {len(patents)} patents")
                avg_relevancy = sum(int(p.relevancy.replace('%', '')) for p in patents) / len(patents)
                print(f"    Average relevancy: {avg_relevancy:.1f}%")
        
        # Show most recent innovations
        recent_patents = sorted(results.data.results, key=lambda x: x.pbdt, reverse=True)[:3]
        print(f"\nMost Recent Innovations:")
        for patent in recent_patents:
            pub_date = str(patent.pbdt)
            formatted_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:8]}"
            print(f"  • {patent.title[:55]}...")
            print(f"    {patent.pn} | Published: {formatted_date} | Relevancy: {patent.relevancy}")
            print(f"    Assignee: {patent.current_assignee}")
            
    except Exception as e:
        print(f"Error in biotech search: {e}")


def renewable_energy_search():
    """Search for renewable energy patents using technology description."""
    print("\n=== Renewable Energy Semantic Search ===")
    
    try:
        # Renewable energy technology description
        energy_description = """
        This invention describes an advanced photovoltaic solar panel system with integrated energy 
        storage and smart grid connectivity. The system features high-efficiency perovskite-silicon 
        tandem solar cells that achieve over 30% conversion efficiency under standard test conditions. 
        The innovation includes a novel micro-inverter design with maximum power point tracking (MPPT) 
        algorithms optimized for varying weather conditions and partial shading scenarios. The integrated 
        lithium-ion battery storage system uses advanced battery management software to optimize charging 
        and discharging cycles, extending battery life and improving overall system efficiency. The smart 
        grid interface enables bidirectional power flow, allowing excess energy to be sold back to the 
        utility grid during peak demand periods. Additionally, the system incorporates machine learning 
        algorithms for predictive maintenance, weather forecasting integration, and energy consumption 
        optimization. The invention includes advanced thermal management systems to maintain optimal 
        operating temperatures and prevent efficiency degradation. Applications include residential, 
        commercial, and utility-scale solar installations with enhanced grid stability and energy 
        independence capabilities.
        """
        
        results = patsnap.patents.search.by_semantic_text(
            text=energy_description,
            limit=40,
            relevancy="55%",
            apd_from="20200101",  # Recent applications
            country=["USA", "USB", "EPA", "EPB", "JPA", "JPB"]
        )
        
        print(f"Search Domain: Advanced Solar Energy & Smart Grid Technology")
        print(f"Application timeframe: 2020+")
        print(f"Geographic scope: US, EP, JP")
        print(f"Related energy patents: {results.data.total_search_result_count:,}")
        
        # Technology trend analysis
        tech_trends = {}
        for patent in results.data.results:
            app_year = str(patent.apdt)[:4]
            tech_trends[app_year] = tech_trends.get(app_year, 0) + 1
        
        print(f"\nTechnology Trends by Year:")
        for year in sorted(tech_trends.keys()):
            print(f"  {year}: {tech_trends[year]} patents")
        
        # Identify key innovators
        innovator_counts = {}
        for patent in results.data.results:
            assignee = patent.current_assignee
            innovator_counts[assignee] = innovator_counts.get(assignee, 0) + 1
        
        print(f"\nTop Innovators:")
        sorted_innovators = sorted(innovator_counts.items(), key=lambda x: x[1], reverse=True)
        for assignee, count in sorted_innovators[:5]:
            print(f"  {assignee}: {count} related patents")
        
        # Analyze relevancy distribution
        high_relevancy = [p for p in results.data.results if int(p.relevancy.replace('%', '')) >= 80]
        medium_relevancy = [p for p in results.data.results if 60 <= int(p.relevancy.replace('%', '')) < 80]
        lower_relevancy = [p for p in results.data.results if int(p.relevancy.replace('%', '')) < 60]
        
        print(f"\nRelevancy Analysis:")
        print(f"  High relevancy (80%+): {len(high_relevancy)} patents")
        print(f"  Medium relevancy (60-79%): {len(medium_relevancy)} patents")
        print(f"  Lower relevancy (<60%): {len(lower_relevancy)} patents")
        
        if high_relevancy:
            print(f"\nHighly Relevant Patents:")
            for patent in high_relevancy[:3]:
                print(f"  • {patent.title}")
                print(f"    {patent.pn} | Relevancy: {patent.relevancy} | Assignee: {patent.current_assignee}")
            
    except Exception as e:
        print(f"Error in renewable energy search: {e}")


def prior_art_semantic_search():
    """Use semantic search for comprehensive prior art discovery."""
    print("\n=== Prior Art Discovery via Semantic Search ===")
    
    try:
        # Invention disclosure for prior art search
        invention_disclosure = """
        The proposed invention is a wearable health monitoring device that combines multiple biosensors 
        for continuous physiological monitoring. The device integrates electrocardiogram (ECG) sensors, 
        photoplethysmography (PPG) sensors for heart rate and blood oxygen monitoring, accelerometers 
        and gyroscopes for activity tracking, and skin temperature sensors. The innovation lies in the 
        advanced signal processing algorithms that use machine learning to filter noise and artifacts 
        from the biosensor data, providing medical-grade accuracy in a consumer wearable form factor. 
        The device features a flexible printed circuit board design that conforms to the wrist anatomy, 
        ensuring comfortable long-term wear while maintaining sensor contact quality. The system includes 
        real-time data analysis capabilities for detecting arrhythmias, sleep apnea events, and other 
        health anomalies, with immediate alerts sent to healthcare providers when critical conditions 
        are detected. The device communicates wirelessly with smartphones and cloud-based health platforms 
        for comprehensive health data management and trend analysis. Power management innovations include 
        ultra-low-power sensor operation modes and energy harvesting from body heat and motion.
        """
        
        # Search for potential prior art with broad parameters
        results = patsnap.patents.search.by_semantic_text(
            text=invention_disclosure,
            limit=50,
            relevancy="50%",  # Lower threshold for comprehensive coverage
            apd_to="20230101",  # Filed before our target date
            country=["USA", "USB", "EPA", "EPB", "JPA", "JPB", "CNA", "CNB"]
        )
        
        print(f"Prior Art Search: Wearable Health Monitoring Device")
        print(f"Search scope: Global (US, EP, JP, CN)")
        print(f"Filed before: 2023-01-01")
        print(f"Potential prior art patents: {results.data.total_search_result_count:,}")
        
        # Categorize prior art by technology area
        prior_art_categories = {
            'wearable_devices': [],
            'biosensors': [],
            'health_monitoring': [],
            'signal_processing': [],
            'wireless_communication': []
        }
        
        category_keywords = {
            'wearable_devices': ['wearable', 'watch', 'band', 'bracelet', 'device'],
            'biosensors': ['sensor', 'ecg', 'ppg', 'heart rate', 'biosensor'],
            'health_monitoring': ['health', 'medical', 'monitoring', 'physiological'],
            'signal_processing': ['signal', 'processing', 'algorithm', 'filter'],
            'wireless_communication': ['wireless', 'bluetooth', 'communication', 'transmit']
        }
        
        for patent in results.data.results:
            title_lower = patent.title.lower()
            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    prior_art_categories[category].append(patent)
                    categorized = True
                    break
        
        print(f"\nPrior Art by Technology Area:")
        for category, patents in prior_art_categories.items():
            if patents:
                print(f"  {category.replace('_', ' ').title()}: {len(patents)} patents")
                # Show most relevant in each category
                top_patent = max(patents, key=lambda x: int(x.relevancy.replace('%', '')))
                print(f"    Most relevant: {top_patent.title[:45]}... ({top_patent.relevancy})")
        
        # Identify critical prior art (high relevancy)
        critical_prior_art = [p for p in results.data.results if int(p.relevancy.replace('%', '')) >= 75]
        
        if critical_prior_art:
            print(f"\nCritical Prior Art (75%+ relevancy):")
            for patent in critical_prior_art[:5]:
                app_date = str(patent.apdt)
                formatted_date = f"{app_date[:4]}-{app_date[4:6]}-{app_date[6:8]}"
                print(f"  • {patent.title}")
                print(f"    {patent.pn} | Filed: {formatted_date} | Relevancy: {patent.relevancy}")
                print(f"    Assignee: {patent.original_assignee}")
                print()
        
        # Timeline analysis
        timeline = {}
        for patent in results.data.results:
            year = str(patent.apdt)[:4]
            timeline[year] = timeline.get(year, 0) + 1
        
        print(f"Prior Art Timeline:")
        for year in sorted(timeline.keys())[-10:]:  # Last 10 years
            print(f"  {year}: {timeline[year]} patents")
            
    except Exception as e:
        print(f"Error in prior art search: {e}")


def demonstrate_text_optimization():
    """Demonstrate the impact of text length and quality on search results."""
    print("\n=== Text Optimization for Semantic Search ===")
    
    # Short text (not recommended)
    short_text = "Machine learning for image recognition."
    
    # Medium text (better)
    medium_text = """
    Machine learning algorithm for real-time image recognition and classification. 
    The system uses convolutional neural networks to process camera input and 
    identify objects with high accuracy.
    """
    
    # Long, detailed text (recommended - >200 words)
    long_text = """
    This invention presents a comprehensive machine learning framework for real-time image recognition 
    and classification in mobile applications. The system employs a sophisticated deep convolutional 
    neural network architecture optimized for edge computing devices with limited computational resources. 
    The framework includes a multi-stage image preprocessing pipeline that enhances image quality through 
    noise reduction, contrast adjustment, and geometric correction algorithms. The core CNN model utilizes 
    a novel attention mechanism that focuses on relevant image regions while suppressing background noise, 
    significantly improving classification accuracy for objects in cluttered environments. The training 
    methodology incorporates advanced data augmentation techniques including rotation, scaling, color 
    space transformations, and synthetic data generation to improve model robustness. The system features 
    an adaptive inference engine that dynamically adjusts model complexity based on available computational 
    resources and battery life constraints. Additionally, the framework includes federated learning 
    capabilities that allow the model to continuously improve through distributed training across 
    multiple devices while preserving user privacy. The invention addresses critical challenges in 
    mobile computer vision including real-time performance requirements, power efficiency, and 
    accuracy in diverse lighting conditions and viewing angles.
    """
    
    print("Comparing search effectiveness with different text lengths:")
    print(f"Short text ({len(short_text)} chars): Basic keywords only")
    print(f"Medium text ({len(medium_text)} chars): Some context provided")
    print(f"Long text ({len(long_text)} chars): Rich semantic context (RECOMMENDED)")
    print("\nNote: Longer, more detailed technical descriptions (>200 words) typically")
    print("produce more accurate and relevant semantic search results.")


if __name__ == "__main__":
    print("Patsnap Semantic Patent Search Examples")
    print("=" * 50)
    
    basic_semantic_search()
    ai_machine_learning_search()
    biotech_pharmaceutical_search()
    renewable_energy_search()
    prior_art_semantic_search()
    demonstrate_text_optimization()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.by_semantic_text()")
    print("- Find patents using natural language technical descriptions")
    print("- Ideal for prior art research and technology discovery")
    print("- Recommend >200 words for optimal semantic matching")
    print("- Relevancy scoring from high to low similarity")
    print("- Date and geographic filtering available")
    print("- Perfect for patent landscape analysis")
    print("- Clean, discoverable namespace-based API")
