from playwright.sync_api import sync_playwright
import json
import time

# VRBO listing IDs with their names
listings = [
    ('4146676', 'Spacious Beach House'),
    ('2873463', 'Large Luxurious Home'),
    ('3737974', 'Family Retreat'),
    ('2156016', 'Galveston Gem'),
    ('3142857', 'Charming Classic'),
    ('3252017', 'Beachside Comfort'),
    ('1269804', 'Family-Friendly'),
    ('3284616', 'Island Time'),
    ('4379912', 'Sandpiper House'),
    ('2757575', 'Cozy Home 2 Pools'),
    ('3975201', 'The Oasis'),
]

def fetch_images():
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        for i, (listing_id, name) in enumerate(listings):
            print(f"[{i+1}/11] Fetching images for Option {i+1}: {name} (ID: {listing_id})...")
            
            # URL with gallery parameter
            url = f'https://www.vrbo.com/{listing_id}?pwaThumbnailDialog=thumbnail-gallery'
            
            try:
                page = context.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait a bit for images to load
                time.sleep(3)
                
                # Get all image elements
                images = page.query_selector_all('img')
                
                image_urls = []
                for img in images:
                    src = img.get_attribute('src')
                    if src and ('trvl-media' in src or 'vrbo' in src or 'expedia' in src):
                        # Clean and get high-res version
                        if '?' in src:
                            base_url = src.split('?')[0]
                        else:
                            base_url = src
                        
                        # Skip tiny thumbnails and icons
                        if 'logo' not in src.lower() and 'icon' not in src.lower():
                            image_urls.append(src)
                
                # Also check for background images in style attributes
                all_elements = page.query_selector_all('[style*="background"]')
                for el in all_elements:
                    style = el.get_attribute('style')
                    if style and 'url(' in style:
                        import re
                        urls = re.findall(r'url\(["\']?([^"\')\s]+)["\']?\)', style)
                        for u in urls:
                            if 'trvl-media' in u or 'vrbo' in u or 'expedia' in u:
                                image_urls.append(u)
                
                # Deduplicate
                unique_urls = list(dict.fromkeys(image_urls))
                
                # Store results
                results[listing_id] = {
                    'name': name,
                    'option': i + 1,
                    'images': unique_urls[:10]  # Store first 10
                }
                
                print(f"   Found {len(unique_urls)} images")
                if unique_urls:
                    print(f"   First image: {unique_urls[0][:80]}...")
                
                page.close()
                
            except Exception as e:
                print(f"   Error: {e}")
                results[listing_id] = {
                    'name': name,
                    'option': i + 1,
                    'images': [],
                    'error': str(e)
                }
        
        browser.close()
    
    # Save results
    with open('pool_images.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("Results saved to pool_images.json")
    print("="*60)
    
    # Print summary
    for listing_id, data in results.items():
        print(f"\nOption {data['option']}: {data['name']}")
        if data.get('images'):
            print(f"  Pool/Exterior image: {data['images'][0]}")
        else:
            print(f"  No images found")

if __name__ == '__main__':
    fetch_images()

