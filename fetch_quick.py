from playwright.sync_api import sync_playwright
import re

# Test with first 2 listings
listings = [
    ('4146676', 'Spacious Beach House'),
    ('2873463', 'Large Luxurious Home'),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    for listing_id, name in listings:
        print(f"\n{'='*50}")
        print(f"Fetching: {name} (ID: {listing_id})")
        
        url = f'https://www.vrbo.com/{listing_id}?pwaThumbnailDialog=thumbnail-gallery'
        
        try:
            page.goto(url, timeout=20000)
            page.wait_for_timeout(2000)
            
            # Get page content and extract image URLs
            content = page.content()
            
            # Find all image URLs
            patterns = [
                r'https://images\.trvl-media\.com/lodging/[^"\'<>\s]+',
                r'https://[^"\'<>\s]*vrbo[^"\'<>\s]*\.(?:jpg|jpeg|png|webp)',
            ]
            
            all_images = []
            for pattern in patterns:
                found = re.findall(pattern, content)
                all_images.extend(found)
            
            # Deduplicate
            unique = list(dict.fromkeys(all_images))
            
            print(f"Found {len(unique)} images")
            for i, img in enumerate(unique[:5]):
                print(f"  [{i+1}] {img}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    browser.close()

