from playwright.sync_api import sync_playwright
import json

# Just test with first listing
listing_id = '4146676'
name = 'Spacious Beach House'

print(f"Testing with {name} (ID: {listing_id})")
print("Capturing all network requests...\n")

all_urls = []

with sync_playwright() as p:
    # Try non-headless to see what's happening
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    def log_request(request):
        url = request.url
        if '.jpg' in url or '.jpeg' in url or '.png' in url or '.webp' in url:
            all_urls.append(url)
            print(f"IMAGE: {url[:100]}")
    
    page.on('request', log_request)
    
    url = f'https://www.vrbo.com/{listing_id}?pwaThumbnailDialog=thumbnail-gallery'
    print(f"Navigating to: {url}\n")
    
    try:
        page.goto(url, timeout=30000)
        print("\nPage loaded. Waiting for images...")
        page.wait_for_timeout(5000)
        
        # Try clicking on gallery thumbnails if present
        thumbnails = page.query_selector_all('[data-stid*="gallery"], [class*="thumbnail"], [class*="gallery"]')
        print(f"\nFound {len(thumbnails)} potential gallery elements")
        
        # Wait more
        page.wait_for_timeout(3000)
        
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n{'='*50}")
    print(f"Total image URLs captured: {len(all_urls)}")
    
    # Show unique URLs
    unique = list(dict.fromkeys(all_urls))
    print(f"Unique image URLs: {len(unique)}")
    
    for i, u in enumerate(unique[:10]):
        print(f"  [{i+1}] {u}")
    
    input("\nPress Enter to close browser...")
    browser.close()


