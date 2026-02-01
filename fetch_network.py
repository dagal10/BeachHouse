from playwright.sync_api import sync_playwright
import json

listings = [
    ('4146676', 'Spacious Beach House'),
    ('2873463', 'Large Luxurious Home'),
    ('3737974', 'Family Retreat'),
    ('3142857', 'Charming Classic'),
    ('3252017', 'Beachside Comfort'),
    ('3284616', 'Island Time'),
    ('4379912', 'Sandpiper House'),
    ('2757575', 'Cozy Home 2 Pools'),
]

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for i, (listing_id, name) in enumerate(listings):
        print(f"[{i+1}/8] {name}...", end=" ", flush=True)
        
        page = browser.new_page()
        
        # Collect image URLs from network requests
        image_urls = []
        
        def handle_response(response):
            url = response.url
            if any(x in url for x in ['trvl-media.com', 'images.vrbo', 'lodging']):
                if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    image_urls.append(url)
        
        page.on('response', handle_response)
        
        try:
            url = f'https://www.vrbo.com/{listing_id}?pwaThumbnailDialog=thumbnail-gallery'
            page.goto(url, timeout=25000)
            page.wait_for_timeout(3000)
            
            # Scroll to trigger more image loads
            page.evaluate('window.scrollBy(0, 500)')
            page.wait_for_timeout(1000)
            
            # Deduplicate
            unique = list(dict.fromkeys(image_urls))
            
            results[listing_id] = {
                'option': i + 1,
                'name': name,
                'images': unique[:8]
            }
            
            print(f"Found {len(unique)} images")
            
        except Exception as e:
            print(f"Error: {e}")
            results[listing_id] = {'option': i + 1, 'name': name, 'images': []}
        
        page.close()
    
    browser.close()

# Save results
with open('vrbo_images.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*60)
print("IMAGE URLS FOR HTML:")
print("="*60)

for listing_id, data in results.items():
    print(f"\nOption {data['option']}: {data['name']}")
    if data['images']:
        # Get the first image (usually the main/pool photo)
        print(f"  {data['images'][0]}")
    else:
        print("  No images captured")


