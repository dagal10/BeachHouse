# 🏖️ Galveston Beach House Comparison

A beautiful, interactive comparison tool for 11 Galveston beach house vacation rentals for a group trip (June 26-28, 2026, 14 travelers).

## Features

- **Interactive Photo Galleries**: Browse multiple pool and exterior photos for each property
- **Quick Comparison Table**: See all properties at a glance with key features
- **Detailed Property Cards**: Full details including amenities, ratings, and pricing
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- **Top Picks Highlighted**: Best value, highest rated, and special features

## View the Site

Visit the live site: [Website](https://dagal10.github.io/BeachHouse/)

## Setup Instructions

### For GitHub Pages:

1. Create a new repository on GitHub (e.g., `beach-house-comparison`)
2. Push this code to the repository
3. Go to Settings → Pages
4. Select the `main` or `master` branch as the source
5. Your site will be available at `https://[your-username].github.io/[repo-name]/`

### Local Development:

Simply open `index.html` in your web browser, or use a local server:

```bash
# Python 3
python -m http.server 8000

# Node.js
npx serve
```

Then visit `http://localhost:8000`

## Project Structure

```
├── index.html          # Main HTML file (GitHub Pages entry point)
├── images/            # Property images organized by option
│   ├── option-1/
│   ├── option-2/
│   └── ...
├── *.py               # Python scripts for fetching data/images
└── *.json             # Data files
```

## Image Organization

Images are organized in folders by option number:
- `images/option-X/pool.png` - Main pool image
- `images/option-X/pool2.png`, `pool3.png` - Additional pool images
- `images/option-X/exterior.png` - Main exterior image
- `images/option-X/exterior2.png`, `exterior3.png` - Additional exterior images

The site automatically detects and displays all available images for each property.

## Technologies Used

- Pure HTML, CSS, and JavaScript (no frameworks required)
- Responsive CSS Grid and Flexbox layouts
- Google Fonts (Playfair Display, Source Sans 3)

## License

Personal project for trip planning purposes.

