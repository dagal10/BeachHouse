# VRBO Scraping Scripts

Two scripts for updating VRBO listing data and downloading images with anti-bot detection.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Scripts

### 1. `update_vrbo_data.py`
Updates property information from each VRBO listing.

**Features:**
- ✅ Headed mode (visible browser) with anti-bot detection
- ✅ Slow navigation with random jittering delays
- ✅ Human-like scrolling and mouse movements
- ✅ Extracts: title, price, rating, bedrooms, bathrooms, amenities, description, images
- ✅ Saves results to `vrbo_updated_data.json`

**Usage:**
```bash
python update_vrbo_data.py
```

**Configuration (in script):**
- `HEADLESS = False` - Set to `True` for headless mode
- `USER_DATA_DIR = None` - Set to your Chrome profile path to use your existing profile
  - Windows: `C:\\Users\\YourUsername\\AppData\\Local\\Google\\Chrome\\User Data`
  - Leave as `None` to use default Playwright profile
- `MIN_DELAY` / `MAX_DELAY` - Adjust jitter timing (default: 2-5 seconds)

### 2. `download_vrbo_images.py`
Downloads images from each VRBO listing and organizes them into folders.

**Features:**
- ✅ Downloads images with anti-bot detection
- ✅ Automatically categorizes images as pool or exterior
- ✅ Organizes into `images/option-X/` folders
- ✅ Skips already downloaded images
- ✅ Saves results to `image_download_results.json`

**Usage:**
```bash
python download_vrbo_images.py
```

**Image Organization:**
- Pool images: `pool.png`, `pool2.png`, `pool3.png`, etc.
- Exterior images: `exterior.png`, `exterior2.png`, `exterior3.png`, etc.
- Images are saved in: `images/option-1/`, `images/option-2/`, etc.

## Anti-Bot Detection Features

Both scripts include:
- Stealth JavaScript injection to hide automation
- Realistic user agent and browser fingerprint
- Random delays (jittering) between actions
- Human-like scrolling and interactions
- Proper geolocation settings (Galveston coordinates)

## Using Your Chrome Profile

To use your existing Chrome profile (with cookies, login, etc.):

1. Find your Chrome profile path:
   - Windows: `C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data`
   - Or open Chrome, go to `chrome://version/` and look for "Profile Path"

2. Update the script:
   ```python
   USER_DATA_DIR = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
   ```

3. **Important:** Close Chrome completely before running the script, or use a different profile directory.

## Troubleshooting

**If you get "browser closed" errors:**
- Make sure Chrome is completely closed
- Try using `USER_DATA_DIR = None` first
- Check that Playwright browsers are installed: `playwright install chromium`

**If images aren't downloading:**
- VRBO may have changed their page structure
- Try running `update_vrbo_data.py` first to see if it can access the pages
- Check the browser window (if headed) to see what's happening

**If you get rate-limited:**
- Increase the delays: `MIN_DELAY = 5`, `MAX_DELAY = 10`
- Run scripts at different times
- Consider using a VPN or different network

## Output Files

- `vrbo_updated_data.json` - Property data from update script
- `image_download_results.json` - Download statistics from image script
- `images/option-X/` - Downloaded images organized by property
