from playwright.sync_api import sync_playwright
import json
import re

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
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    
    for i, (listing_id, name) in enumerate(listings):
        print(f"[{i+1}/8] {name}...", end=" ", flush=True)
        
        page = context.new_page()
        
        try:
            # First load the main page to get cookies/session
            url = f'https://www.vrbo.com/{listing_id}'
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(2000)
            
            # Get page HTML
            html = page.content()
            
            # Look for image URLs in script tags containing JSON data
            # VRBO often embeds property data in __NEXT_DATA__ or similar
            script_pattern = r'<script[^>]*>([^<]*(?:images|photos|gallery)[^<]*)</script>'
            
            # Also search for image URLs directly
            image_patterns = [
                r'"(https://images\.trvl-media\.com/lodging/\d+/[^"]+)"',
                r'"(https://[^"]*\.vrbo\.com/[^"]*\.(?:jpg|jpeg|png|webp))"',
                r'"(https://[^"]*expedia[^"]*lodging[^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
                r'src="(https://[^"]+\.(?:jpg|jpeg|png|webp))"',
            ]
            
            all_images = []
            for pattern in image_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                all_images.extend(matches)
            
            # Deduplicate and filter
            unique = []
            seen = set()
            for img in all_images:
                # Clean URL
                img = img.split('?')[0] if '?' in img else img
                if img not in seen and len(img) > 50:
                    # Skip logos, icons, etc.
                    if not any(x in img.lower() for x in ['logo', 'icon', 'favicon', 'sprite', 'avatar']):
                        seen.add(img)
                        unique.append(img)
            
            results[listing_id] = {
                'option': i + 1,
                'name': name,
                'images': unique[:5]
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

print("\n" + "="*70)
print("IMAGE URLS:")
print("="*70)

for listing_id, data in results.items():
    print(f"\nOption {data['option']}: {data['name']}")
    if data['images']:
        for j, img in enumerate(data['images'][:2]):
            print(f"  [{j+1}] {img}")
    else:
        print("  No images found")


