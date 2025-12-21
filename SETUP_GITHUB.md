# GitHub Repository Setup Instructions

Follow these steps to create the GitHub repository and enable GitHub Pages:

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Repository name: `beach-house-comparison` (or your preferred name)
4. Description: "Galveston Beach House Comparison Tool"
5. Set to **Public** (required for free GitHub Pages)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Run these in your terminal:

```bash
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/beach-house-comparison.git

# Push your code
git branch -M main
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under "Source", select:
   - Branch: `main` (or `master` if that's your branch)
   - Folder: `/ (root)`
5. Click **Save**

## Step 4: Access Your Site

Your site will be available at:
```
https://YOUR_USERNAME.github.io/beach-house-comparison/
```

**Note**: It may take a few minutes for the site to be available after enabling Pages.

## Troubleshooting

- If you see a 404 error, wait 5-10 minutes and refresh
- Make sure `index.html` is in the root directory
- Check that the repository is set to Public
- Verify the branch name matches what you selected in Pages settings

