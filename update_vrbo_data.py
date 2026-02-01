"""
VRBO Data Update Script
Uses Playwright with anti-bot detection, slow navigation, and jittering
to visit each VRBO listing and update information.
"""

from playwright.sync_api import sync_playwright
import json
import random
import time
import os
from pathlib import Path

# VRBO listing IDs mapped to option numbers
listings = [
    ('4146676', 'Spacious Beach House', 1),
    ('2873463', 'Large Luxurious Home', 2),
    ('3737974', 'Family Retreat', 3),
    ('3142857', 'Charming Classic', 4),
    ('3252017', 'Beachside Comfort', 5),
    ('3284616', 'Island Time', 6),
    ('4379912', 'Sandpiper House', 7),
    ('2757575', 'Cozy Home 2 Pools', 8),
]

# Configuration
# For Windows Chrome profile, use: C:\\Users\\YourUsername\\AppData\\Local\\Google\\Chrome\\User Data
# Leave as None to use default Playwright profile (recommended for first run)
USER_DATA_DIR = None  # Set to your Chrome profile path if you want to use your existing profile
HEADLESS = False  # Set to True for headless mode
MIN_DELAY = 2  # Minimum delay between actions (seconds)
MAX_DELAY = 5  # Maximum delay between actions (seconds)
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds


def jitter_delay(min_seconds=MIN_DELAY, max_seconds=MAX_DELAY):
    """Add random jitter delay to mimic human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def human_like_scroll(page):
    """Scroll the page in a human-like manner"""
    # Random scroll amount
    scroll_amount = random.randint(300, 800)
    # Random scroll direction (mostly down, sometimes up)
    direction = random.choice([1, 1, 1, -1])  # 75% down, 25% up
    
    page.evaluate(f"window.scrollBy(0, {scroll_amount * direction})")
    jitter_delay(0.5, 1.5)


def extract_property_data(page, listing_id, name, option_num):
    """Extract property data from the VRBO page"""
    data = {
        'listing_id': listing_id,
        'name': name,
        'option': option_num,
        'url': page.url,
        'title': '',
        'price': '',
        'rating': '',
        'reviews': '',
        'bedrooms': '',
        'bathrooms': '',
        'sleeps': '',
        'sqft': '',
        'amenities': [],
        'description': '',
        'images': []
    }
    
    try:
        # Wait for page to be interactive
        page.wait_for_load_state('networkidle', timeout=10000)
        jitter_delay(1, 2)
        
        # Extract title
        try:
            title_selectors = [
                'h1[data-testid="property-title"]',
                'h1',
                '[data-testid="property-name"]',
                '.property-title'
            ]
            for selector in title_selectors:
                element = page.query_selector(selector)
                if element:
                    data['title'] = element.inner_text().strip()
                    break
        except:
            pass
        
        # Extract price
        try:
            price_selectors = [
                '[data-testid="price-summary-total"]',
                '[data-testid="price"]',
                '.price',
                '[class*="price"]'
            ]
            for selector in price_selectors:
                element = page.query_selector(selector)
                if element:
                    data['price'] = element.inner_text().strip()
                    break
        except:
            pass
        
        # Extract rating and reviews
        try:
            rating_selectors = [
                '[data-testid="rating"]',
                '[class*="rating"]',
                '[class*="review"]'
            ]
            for selector in rating_selectors:
                elements = page.query_selector_all(selector)
                for elem in elements:
                    text = elem.inner_text()
                    if '★' in text or 'rating' in text.lower():
                        data['rating'] = text.strip()
                        break
        except:
            pass
        
        # Extract property details (bedrooms, bathrooms, sleeps, sqft)
        try:
            detail_selectors = [
                '[data-testid="property-details"]',
                '[class*="property-detail"]',
                '[class*="bedroom"]',
                '[class*="bathroom"]'
            ]
            for selector in detail_selectors:
                elements = page.query_selector_all(selector)
                for elem in elements:
                    text = elem.inner_text().lower()
                    if 'bedroom' in text:
                        data['bedrooms'] = text.strip()
                    elif 'bath' in text:
                        data['bathrooms'] = text.strip()
                    elif 'sleep' in text:
                        data['sleeps'] = text.strip()
                    elif 'sq' in text or 'square' in text:
                        data['sqft'] = text.strip()
        except:
            pass
        
        # Extract amenities
        try:
            amenity_selectors = [
                '[data-testid="amenity"]',
                '[class*="amenity"]',
                '[class*="feature"]'
            ]
            for selector in amenity_selectors:
                elements = page.query_selector_all(selector)
                for elem in elements[:20]:  # Limit to first 20
                    text = elem.inner_text().strip()
                    if text and len(text) < 100:  # Reasonable amenity length
                        data['amenities'].append(text)
        except:
            pass
        
        # Extract description
        try:
            desc_selectors = [
                '[data-testid="property-description"]',
                '[class*="description"]',
                '[class*="overview"]'
            ]
            for selector in desc_selectors:
                element = page.query_selector(selector)
                if element:
                    data['description'] = element.inner_text().strip()[:500]  # Limit length
                    break
        except:
            pass
        
        # Extract image URLs
        try:
            # Look for images in the page content
            image_urls = page.evaluate("""
                () => {
                    const images = [];
                    const imgElements = document.querySelectorAll('img');
                    imgElements.forEach(img => {
                        const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
                        if (src && (src.includes('trvl-media.com') || src.includes('vrbo') || src.includes('expedia'))) {
                            if (!src.includes('logo') && !src.includes('icon') && !src.includes('avatar')) {
                                images.push(src);
                            }
                        }
                    });
                    return [...new Set(images)].slice(0, 20); // Return unique URLs, max 20
                }
            """)
            data['images'] = image_urls
        except:
            pass
        
        # Human-like scroll to trigger lazy loading
        for _ in range(random.randint(2, 4)):
            human_like_scroll(page)
        
    except Exception as e:
        print(f"  ⚠️  Error extracting data: {e}")
    
    return data


def main():
    """Main function to update VRBO data"""
    print("=" * 70)
    print("VRBO Data Update Script")
    print("=" * 70)
    print(f"Mode: {'Headed' if not HEADLESS else 'Headless'}")
    print(f"User Profile: {USER_DATA_DIR}")
    print(f"Listings to process: {len(listings)}")
    print("=" * 70)
    print()
    
    results = {}
    
    with sync_playwright() as p:
        # Launch browser with persistent context (user profile) if specified
        launch_options = {
            'headless': HEADLESS,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        }
        
        # Add user data directory if specified
        if USER_DATA_DIR:
            launch_options['args'].append(f'--user-data-dir={USER_DATA_DIR}')
        
        browser = p.chromium.launch(**launch_options)
        
        # Create context with realistic settings
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Chicago',
            permissions=['geolocation'],
            geolocation={'latitude': 29.3013, 'longitude': -94.7977},  # Galveston coordinates
            color_scheme='light',
        )
        
        # Add stealth scripts to avoid detection
        context.add_init_script("""
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Chrome runtime
            window.chrome = {
                runtime: {}
            };
        """)
        
        page = context.new_page()
        
        for i, (listing_id, name, option_num) in enumerate(listings, 1):
            print(f"\n[{i}/{len(listings)}] Processing: {name} (ID: {listing_id})")
            print("-" * 70)
            
            url = f'https://www.vrbo.com/{listing_id}'
            
            try:
                # Navigate to page with slow, human-like behavior
                print(f"  🌐 Navigating to {url}...")
                page.goto(url, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
                
                # Wait with jitter
                delay = jitter_delay(2, 4)
                print(f"  ⏱️  Waited {delay:.1f}s (jitter)")
                
                # Wait for page to be ready
                print("  ⏳ Waiting for page to load...")
                page.wait_for_load_state('networkidle', timeout=15000)
                jitter_delay(1, 2)
                
                # Human-like interaction: scroll and move mouse
                print("  🖱️  Simulating human interaction...")
                human_like_scroll(page)
                
                # Extract data
                print("  📊 Extracting property data...")
                data = extract_property_data(page, listing_id, name, option_num)
                results[listing_id] = data
                
                # Print summary
                print(f"  ✅ Title: {data['title'][:50] if data['title'] else 'N/A'}...")
                print(f"  ✅ Price: {data['price'] if data['price'] else 'N/A'}")
                print(f"  ✅ Images found: {len(data['images'])}")
                print(f"  ✅ Amenities: {len(data['amenities'])}")
                
                # Random delay before next listing
                if i < len(listings):
                    delay = jitter_delay(3, 6)
                    print(f"  ⏱️  Waiting {delay:.1f}s before next listing...")
                
            except Exception as e:
                print(f"  ❌ Error processing {name}: {e}")
                results[listing_id] = {
                    'listing_id': listing_id,
                    'name': name,
                    'option': option_num,
                    'error': str(e)
                }
        
        browser.close()
    
    # Save results to JSON
    output_file = 'vrbo_updated_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print(f"✅ Results saved to {output_file}")
    print("=" * 70)
    
    # Print summary
    print("\nSummary:")
    for listing_id, data in results.items():
        if 'error' not in data:
            print(f"  Option {data.get('option', '?')}: {data.get('name', 'Unknown')} - {len(data.get('images', []))} images")
        else:
            print(f"  {data.get('name', 'Unknown')} - ERROR: {data['error']}")


if __name__ == '__main__':
    main()
