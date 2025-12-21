import requests
import re
import json

# VRBO listing IDs
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print('Fetching VRBO image URLs...')
print()

results = {}

for listing_id, name in listings:
    url = f'https://www.vrbo.com/{listing_id}'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        
        # Look for image URLs in the response using various patterns
        # VRBO/Expedia uses patterns like https://images.trvl-media.com/...
        patterns = [
            r'https://images\.trvl-media\.com/[^"\'<>\s]+',
            r'https://[^"\'<>\s]*\.vrbo\.com/[^"\'<>\s]+\.(?:jpg|jpeg|png|webp)',
            r'https://[^"\'<>\s]*media[^"\'<>\s]+\.(?:jpg|jpeg|png|webp)',
        ]
        
        all_images = []
        for pattern in patterns:
            found = re.findall(pattern, resp.text, re.IGNORECASE)
            all_images.extend(found)
        
        # Deduplicate and clean
        unique_images = []
        seen = set()
        for img in all_images:
            # Clean up URL
            img = img.split('?')[0] if '?' in img else img
            img = img.rstrip('\\').rstrip('"').rstrip("'")
            if img not in seen and len(img) > 30:
                seen.add(img)
                unique_images.append(img)
        
        print(f'Option {listings.index((listing_id, name)) + 1}: {name} (ID: {listing_id})')
        if unique_images:
            results[listing_id] = unique_images[:8]  # Store first 8
            for i, img in enumerate(unique_images[:5]):
                print(f'  [{i+1}] {img}')
        else:
            print('  No images found - page may require JavaScript')
            results[listing_id] = []
        print()
        
    except Exception as e:
        print(f'Option {listings.index((listing_id, name)) + 1}: {name} - Error: {e}')
        results[listing_id] = []
        print()

# Save results to JSON
with open('image_urls.json', 'w') as f:
    json.dump(results, f, indent=2)
    
print('Results saved to image_urls.json')

