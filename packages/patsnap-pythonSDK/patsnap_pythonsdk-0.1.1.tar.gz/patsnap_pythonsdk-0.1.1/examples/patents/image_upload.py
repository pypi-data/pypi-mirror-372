"""
Example usage of image upload endpoint for patent image search.

This demonstrates how to upload patent images (diagrams, figures, drawings)
and obtain public URLs for subsequent image-based patent search operations.
"""

import patsnap_pythonSDK as patsnap
from pathlib import Path
import tempfile
import time

# Configure the SDK
patsnap.configure(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

def basic_image_upload():
    """Basic image upload from file path."""
    print("=== Basic Image Upload ===")
    
    try:
        # Upload a patent diagram or technical drawing
        # Note: Replace with actual image file path
        image_path = "path/to/patent_diagram.jpg"
        
        # Check if file exists (for demo purposes)
        if not Path(image_path).exists():
            print(f"Demo: Image file not found at {image_path}")
            print("Please replace with actual image file path")
            return
        
        result = patsnap.patents.search.upload_image(image=image_path)
        
        print(f"Image uploaded successfully!")
        print(f"Public URL: {result.url}")
        print(f"URL expires in: {result.expire} seconds ({result.expire/3600:.1f} hours)")
        print(f"Expiration time: {time.ctime(time.time() + result.expire)}")
        
        # The URL can now be used for image-based patent searches
        print(f"\nThis URL can be used for:")
        print("- Image-based patent similarity searches")
        print("- Finding patents with similar technical drawings")
        print("- Reverse image search in patent databases")
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Upload error: {e}")


def upload_from_file_object():
    """Upload image from file-like object (BytesIO, file handle)."""
    print("\n=== Upload from File Object ===")
    
    try:
        # Example: Upload from file handle
        image_path = "path/to/technical_drawing.png"
        
        # Check if file exists
        if not Path(image_path).exists():
            print(f"Demo: Creating temporary image file for demonstration")
            
            # Create a temporary image file for demo
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Write minimal JPEG header (for demo only)
                temp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')
                temp_path = temp_file.name
            
            print(f"Using temporary file: {temp_path}")
            image_path = temp_path
        
        # Upload using file object
        with open(image_path, 'rb') as image_file:
            result = patsnap.patents.search.upload_image(image=image_file)
            
            print(f"Upload successful!")
            print(f"Image URL: {result.url}")
            print(f"Valid for: {result.expire/3600:.1f} hours")
        
        # Clean up temporary file if created
        if 'temp_path' in locals():
            Path(temp_path).unlink(missing_ok=True)
            print("Temporary file cleaned up")
            
    except Exception as e:
        print(f"Upload error: {e}")


def upload_multiple_images():
    """Upload multiple patent images for comparison."""
    print("\n=== Multiple Image Upload ===")
    
    try:
        # List of patent images to upload
        image_files = [
            "path/to/patent_figure_1.jpg",
            "path/to/patent_figure_2.png", 
            "path/to/technical_diagram.jpg"
        ]
        
        uploaded_urls = []
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\nUploading image {i}/{len(image_files)}: {Path(image_path).name}")
            
            if not Path(image_path).exists():
                print(f"  Skipping - file not found: {image_path}")
                continue
            
            try:
                result = patsnap.patents.search.upload_image(image=image_path)
                uploaded_urls.append({
                    'filename': Path(image_path).name,
                    'url': result.url,
                    'expire': result.expire
                })
                
                print(f"  ✓ Uploaded: {result.url}")
                print(f"  ✓ Expires: {time.ctime(time.time() + result.expire)}")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        
        print(f"\n=== Upload Summary ===")
        print(f"Successfully uploaded: {len(uploaded_urls)} images")
        
        for upload in uploaded_urls:
            print(f"• {upload['filename']}: {upload['url'][:50]}...")
        
        if uploaded_urls:
            print(f"\nThese URLs can now be used for:")
            print("- Batch image similarity searches")
            print("- Comparative patent analysis")
            print("- Multi-image patent landscape mapping")
            
    except Exception as e:
        print(f"Batch upload error: {e}")


def validate_image_requirements():
    """Demonstrate image validation and requirements."""
    print("\n=== Image Requirements Validation ===")
    
    print("Supported formats: JPG, JPEG, PNG")
    print("Maximum file size: 4MB (4,096 KB)")
    print("URL validity: 9 hours (32,400 seconds)")
    print("Use case: Patent diagrams, technical drawings, flowcharts")
    
    # Demonstrate validation errors
    validation_examples = [
        {
            'description': 'Unsupported format (GIF)',
            'filename': 'image.gif',
            'expected_error': 'Unsupported image format'
        },
        {
            'description': 'File too large (>4MB)',
            'filename': 'large_image.jpg',
            'expected_error': 'Image file too large'
        },
        {
            'description': 'File not found',
            'filename': 'nonexistent.jpg',
            'expected_error': 'Image file not found'
        }
    ]
    
    print(f"\nValidation Examples:")
    for example in validation_examples:
        print(f"• {example['description']}")
        print(f"  File: {example['filename']}")
        print(f"  Expected error: {example['expected_error']}")


def image_upload_best_practices():
    """Demonstrate best practices for image upload."""
    print("\n=== Image Upload Best Practices ===")
    
    best_practices = [
        {
            'category': 'Image Quality',
            'tips': [
                'Use high-resolution images for better search accuracy',
                'Ensure clear, unblurred technical drawings',
                'Crop images to focus on relevant technical content',
                'Use standard image formats (JPG/PNG)'
            ]
        },
        {
            'category': 'File Management',
            'tips': [
                'Keep file sizes under 4MB for faster uploads',
                'Use descriptive filenames for organization',
                'Compress images if necessary while maintaining quality',
                'Store original files locally for reference'
            ]
        },
        {
            'category': 'Search Strategy',
            'tips': [
                'Upload multiple views/angles of the same invention',
                'Include both overview and detail images',
                'Use images with clear technical elements',
                'Consider uploading competitor patent images for comparison'
            ]
        },
        {
            'category': 'URL Management',
            'tips': [
                'URLs expire after 9 hours - plan accordingly',
                'Store URLs temporarily for batch operations',
                'Re-upload if URLs expire during long analysis sessions',
                'Use URLs immediately for best performance'
            ]
        }
    ]
    
    for practice in best_practices:
        print(f"\n{practice['category']}:")
        for tip in practice['tips']:
            print(f"  • {tip}")


def image_search_workflow():
    """Demonstrate complete workflow from upload to search."""
    print("\n=== Complete Image Search Workflow ===")
    
    try:
        # Step 1: Upload patent image
        print("Step 1: Upload Patent Image")
        image_path = "path/to/patent_technical_drawing.jpg"
        
        if not Path(image_path).exists():
            print("  Demo mode - replace with actual image file")
            return
        
        upload_result = patsnap.patents.search.upload_image(image=image_path)
        print(f"  ✓ Image uploaded: {upload_result.url}")
        
        # Step 2: Use URL for image-based patent search
        print(f"\nStep 2: Use URL for Patent Search")
        print(f"  Image URL: {upload_result.url}")
        print(f"  URL expires: {time.ctime(time.time() + upload_result.expire)}")
        
        # Note: Actual image search would use a different endpoint
        print(f"\nStep 3: Perform Image-Based Patent Search")
        print("  # This would use the image search endpoint (not implemented in this example)")
        print("  # results = patsnap.patents.search.by_image(image_url=upload_result.url)")
        
        print(f"\nStep 4: Analyze Results")
        print("  • Find patents with similar technical drawings")
        print("  • Identify potential prior art")
        print("  • Discover related technologies")
        print("  • Analyze competitive landscape")
        
        print(f"\nWorkflow Benefits:")
        print("  • Visual patent discovery")
        print("  • Non-text-based prior art research")
        print("  • Technical drawing similarity analysis")
        print("  • Cross-language patent discovery")
        
    except Exception as e:
        print(f"Workflow error: {e}")


def handle_upload_errors():
    """Demonstrate proper error handling for image uploads."""
    print("\n=== Error Handling Examples ===")
    
    error_scenarios = [
        {
            'scenario': 'File not found',
            'test_file': 'nonexistent_image.jpg',
            'expected': 'FileNotFoundError'
        },
        {
            'scenario': 'Invalid file type',
            'test_file': None,  # We'll create a test case
            'expected': 'ValueError - Unsupported format'
        },
        {
            'scenario': 'Invalid parameter type',
            'test_file': 123,  # Invalid type
            'expected': 'ValueError - Must be file path or file object'
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\nTesting: {scenario['scenario']}")
        print(f"Expected: {scenario['expected']}")
        
        try:
            if scenario['test_file'] == 123:
                # Test invalid parameter type
                result = patsnap.patents.search.upload_image(image=123)
            elif scenario['test_file']:
                # Test file not found
                result = patsnap.patents.search.upload_image(image=scenario['test_file'])
            else:
                print("  Skipping - requires file creation")
                continue
                
        except FileNotFoundError as e:
            print(f"  ✓ Caught expected error: {e}")
        except ValueError as e:
            print(f"  ✓ Caught expected error: {e}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")


if __name__ == "__main__":
    print("Patsnap Image Upload Examples")
    print("=" * 50)
    
    basic_image_upload()
    upload_from_file_object()
    upload_multiple_images()
    validate_image_requirements()
    image_upload_best_practices()
    image_search_workflow()
    handle_upload_errors()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("Remember to replace 'your_client_id' and 'your_client_secret' with actual values.")
    print("\nAPI Usage: patsnap.patents.search.upload_image()")
    print("- Upload patent images for visual search")
    print("- Supports JPG and PNG formats (max 4MB)")
    print("- URLs valid for 9 hours")
    print("- Perfect for technical drawing analysis")
    print("- Enables visual prior art discovery")
    print("- Cross-language patent image search")
    print("- Clean, discoverable namespace-based API")
