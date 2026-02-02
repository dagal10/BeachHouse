"""
VRBO Image Download Script
Downloads images from each VRBO listing and organizes them into the correct folders.
Categorizes images as pool or exterior based on filename patterns and content.
"""

from playwright.sync_api import sync_playwright
import requests
import json
import os
import random
import time
from pathlib import Path
from urllib.parse import urlparse
import re

try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[!] Warning: PIL/Pillow not installed. Install with: pip install Pillow")
    print("[!] Images will be saved in original format (may not be PNG)")

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
HEADLESS = False  # Set to True for headless mode
MIN_DELAY = 1  # Minimum delay between downloads (seconds)
MAX_DELAY = 3  # Maximum delay between downloads (seconds)
IMAGES_DIR = Path('images')
DOWNLOAD_TIMEOUT = 30  # Seconds


def jitter_delay(min_seconds=MIN_DELAY, max_seconds=MAX_DELAY):
    """Add random jitter delay to mimic human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def is_pool_image(url, alt_text=''):
    """Determine if an image is likely a pool image based on URL and alt text"""
    url_lower = url.lower()
    alt_lower = alt_text.lower()
    
    pool_keywords = ['pool', 'swimming', 'spa', 'hot tub', 'jacuzzi', 'dive', 'swim']
    exterior_keywords = ['exterior', 'outside', 'front', 'back', 'yard', 'patio', 'deck', 'beach', 'ocean', 'view']
    
    # Check URL
    for keyword in pool_keywords:
        if keyword in url_lower:
            return True
    
    # Check alt text
    for keyword in pool_keywords:
        if keyword in alt_lower:
            return True
    
    # If it has exterior keywords but not pool keywords, it's likely exterior
    for keyword in exterior_keywords:
        if keyword in url_lower or keyword in alt_lower:
            return False
    
    return None  # Unknown


def download_image(url, filepath, headers=None):
    """Download an image from URL to filepath and convert to PNG"""
    try:
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.vrbo.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        
        response = requests.get(url, headers=headers, timeout=DOWNLOAD_TIMEOUT, stream=True)
        response.raise_for_status()
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Download image data
        image_data = response.content
        
        # Convert to PNG using PIL/Pillow
        if HAS_PIL:
            try:
                # Open image from bytes
                img = Image.open(io.BytesIO(image_data))
                
                # Convert RGBA to RGB if necessary (for JPEG compatibility)
                if img.mode == 'RGBA':
                    # Create white background
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = rgb_img
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Save as PNG
                img.save(filepath, 'PNG')
                return True
            except Exception as e:
                # Fallback: save original format
                print(f"      [!] PNG conversion failed, saving original: {e}")
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                return True
        else:
            # If PIL not available, save as-is but with .png extension
            # This might not work perfectly, but better than nothing
            with open(filepath, 'wb') as f:
                f.write(image_data)
            return True
        
    except Exception as e:
        print(f"      [!] Download failed: {e}")
        return False


def extract_image_urls(page):
    """Extract all image URLs from the VRBO page"""
    image_urls = []
    
    try:
        # Wait for images to load (skip networkidle as VRBO has continuous activity)
        jitter_delay(2, 3)  # Give time for lazy-loaded images
        
        # Get all image elements with their URLs and alt text
        images_data = page.evaluate("""
            () => {
                const images = [];
                const imgElements = document.querySelectorAll('img');
                
                imgElements.forEach(img => {
                    const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || img.getAttribute('data-original');
                    const alt = img.alt || '';
                    
                    if (src && (
                        src.includes('trvl-media.com') || 
                        src.includes('vrbo') || 
                        src.includes('expedia') ||
                        src.includes('lodging')
                    )) {
                        // Filter out logos, icons, avatars
                        if (!src.includes('logo') && 
                            !src.includes('icon') && 
                            !src.includes('avatar') &&
                            !src.includes('sprite') &&
                            !src.includes('favicon') &&
                            src.match(/\\.(jpg|jpeg|png|webp)/i)) {
                            images.push({
                                url: src.split('?')[0], // Remove query params
                                alt: alt
                            });
                        }
                    }
                });
                
                return [...new Map(images.map(img => [img.url, img])).values()]; // Deduplicate by URL
            }
        """)
        
        # Also try to find images in gallery/lightbox
        try:
            # Click on main image to open gallery if possible
            gallery_selectors = [
                '[data-testid="property-image"]',
                '.property-image',
                '.gallery-image',
                'img[class*="main"]'
            ]
            
            for selector in gallery_selectors:
                try:
                    main_img = page.query_selector(selector)
                    if main_img:
                        main_img.click()
                        jitter_delay(1, 2)
                        # Extract more images from gallery
                        gallery_images = page.evaluate("""
                            () => {
                                const images = [];
                                const imgElements = document.querySelectorAll('img');
                                imgElements.forEach(img => {
                                    const src = img.src || img.getAttribute('data-src');
                                    if (src && (src.includes('trvl-media.com') || src.includes('vrbo'))) {
                                        if (!src.includes('logo') && !src.includes('icon')) {
                                            images.push({
                                                url: src.split('?')[0],
                                                alt: img.alt || ''
                                            });
                                        }
                                    }
                                });
                                return [...new Map(images.map(img => [img.url, img])).values()];
                            }
                        """)
                        images_data.extend(gallery_images)
                        # Close gallery
                        page.keyboard.press('Escape')
                        jitter_delay(0.5, 1)
                        break
                except:
                    continue
        
        except:
            pass
        
        image_urls = images_data
        
    except Exception as e:
        print(f"      [!] Error extracting images: {e}")
    
    return image_urls


def organize_images(image_urls, option_dir, listing_name):
    """Download and organize images into pool and exterior folders"""
    pool_images = []
    exterior_images = []
    other_images = []
    
    # Categorize images
    for img_data in image_urls:
        url = img_data['url']
        alt = img_data.get('alt', '')
        
        category = is_pool_image(url, alt)
        if category is True:
            pool_images.append(img_data)
        elif category is False:
            exterior_images.append(img_data)
        else:
            other_images.append(img_data)
    
    # If we couldn't categorize, split evenly (or use heuristics)
    if not pool_images and not exterior_images and other_images:
        # Try to categorize based on image order/position
        # Usually first images are exterior, middle are interior, pool might be later
        # For now, assign first half to exterior, rest to pool
        mid = len(other_images) // 2
        exterior_images = other_images[:mid]
        pool_images = other_images[mid:]
        other_images = []
    
    downloaded = {'pool': 0, 'exterior': 0, 'other': 0}
    
    # Download pool images
    print(f"      [*] Downloading pool images...")
    for i, img_data in enumerate(pool_images[:10], 1):  # Limit to 10 pool images
        url = img_data['url']
        filename = f'pool{i}.png' if i > 1 else f'pool.png'
        filepath = option_dir / filename
        
        if not filepath.exists():  # Skip if already exists
            if download_image(url, filepath):
                downloaded['pool'] += 1
                print(f"        [+] {filename}")
            jitter_delay(0.5, 1.5)
        else:
            print(f"        [>] {filename} (already exists)")
    
    # Download exterior images
    print(f"      [*] Downloading exterior images...")
    for i, img_data in enumerate(exterior_images[:10], 1):  # Limit to 10 exterior images
        url = img_data['url']
        filename = f'exterior{i}.png' if i > 1 else f'exterior.png'
        filepath = option_dir / filename
        
        if not filepath.exists():  # Skip if already exists
            if download_image(url, filepath):
                downloaded['exterior'] += 1
                print(f"        [+] {filename}")
            jitter_delay(0.5, 1.5)
        else:
            print(f"        [>] {filename} (already exists)")
    
    # Download other images (uncategorized) as exterior
    if other_images:
        print(f"      [*] Downloading additional images...")
        for i, img_data in enumerate(other_images[:5], 1):  # Limit to 5 additional
            url = img_data['url']
            filename = f'exterior{len(exterior_images) + i}.png'
            filepath = option_dir / filename
            
            if not filepath.exists():
                if download_image(url, filepath):
                    downloaded['exterior'] += 1
                    print(f"        [+] {filename}")
                jitter_delay(0.5, 1.5)
    
    return downloaded


def main():
    """Main function to download VRBO images"""
    print("=" * 70)
    print("VRBO Image Download Script")
    print("=" * 70)
    print(f"Mode: {'Headed' if not HEADLESS else 'Headless'}")
    print(f"Images directory: {IMAGES_DIR}")
    print(f"Listings to process: {len(listings)}")
    print("=" * 70)
    print()
    
    # Ensure images directory exists
    IMAGES_DIR.mkdir(exist_ok=True)
    
    results = {}
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
        )
        
        # Add stealth scripts
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        for i, (listing_id, name, option_num) in enumerate(listings, 1):
            print(f"\n[{i}/{len(listings)}] Processing: {name} (ID: {listing_id})")
            print("-" * 70)
            
            url = f'https://www.vrbo.com/{listing_id}'
            option_dir = IMAGES_DIR / f'option-{option_num}'
            
            try:
                # Navigate to page
                print(f"  [*] Navigating to {url}...")
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait with jitter
                delay = jitter_delay(2, 4)
                print(f"  [*] Waited {delay:.1f}s")
                
                # Wait for page to be ready (use 'load' instead of 'networkidle' as VRBO has continuous network activity)
                print("  [*] Waiting for images to load...")
                try:
                    page.wait_for_load_state('load', timeout=20000)
                except:
                    pass  # Continue even if timeout
                jitter_delay(3, 5)  # Give extra time for images to load
                
                # Extract image URLs
                print("  [*] Extracting image URLs...")
                image_urls = extract_image_urls(page)
                print(f"  [+] Found {len(image_urls)} images")
                
                if not image_urls:
                    print("  [!] No images found, trying alternative method...")
                    # Try scrolling to trigger lazy loading
                    for _ in range(3):
                        page.evaluate("window.scrollBy(0, 500)")
                        jitter_delay(1, 2)
                    image_urls = extract_image_urls(page)
                    print(f"  [+] Found {len(image_urls)} images after scrolling")
                
                # Download and organize images
                if image_urls:
                    downloaded = organize_images(image_urls, option_dir, name)
                    results[listing_id] = {
                        'option': option_num,
                        'name': name,
                        'total_images': len(image_urls),
                        'downloaded': downloaded
                    }
                    print(f"  [+] Downloaded: {downloaded['pool']} pool, {downloaded['exterior']} exterior")
                else:
                    print("  [!] No images to download")
                    results[listing_id] = {
                        'option': option_num,
                        'name': name,
                        'total_images': 0,
                        'downloaded': {'pool': 0, 'exterior': 0, 'other': 0}
                    }
                
                # Random delay before next listing
                if i < len(listings):
                    delay = jitter_delay(3, 6)
                    print(f"  [*] Waiting {delay:.1f}s before next listing...")
                
            except Exception as e:
                print(f"  [!] Error processing {name}: {e}")
                results[listing_id] = {
                    'option': option_num,
                    'name': name,
                    'error': str(e)
                }
        
        browser.close()
    
    # Save results to JSON
    output_file = 'image_download_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print(f"[+] Results saved to {output_file}")
    print("=" * 70)
    
    # Print summary
    print("\nDownload Summary:")
    total_pool = 0
    total_exterior = 0
    for listing_id, data in results.items():
        if 'error' not in data and 'downloaded' in data:
            pool = data['downloaded'].get('pool', 0)
            exterior = data['downloaded'].get('exterior', 0)
            total_pool += pool
            total_exterior += exterior
            print(f"  Option {data.get('option', '?')}: {data.get('name', 'Unknown')} - {pool} pool, {exterior} exterior")
        elif 'error' in data:
            print(f"  {data.get('name', 'Unknown')} - ERROR: {data['error']}")
    
    print(f"\nTotal: {total_pool} pool images, {total_exterior} exterior images")


if __name__ == '__main__':
    main()
