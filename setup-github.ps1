# GitHub Repository Setup Script
# Run this AFTER creating the repository on GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "beach-house-comparison"
)

Write-Host "Setting up GitHub repository connection..." -ForegroundColor Cyan
Write-Host ""

# Check if remote already exists
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "Remote 'origin' already exists: $existingRemote" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Aborting. Please remove the existing remote manually if needed." -ForegroundColor Red
        exit 1
    }
    git remote remove origin
}

# Add remote
$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"
Write-Host "Adding remote: $remoteUrl" -ForegroundColor Green
git remote add origin $remoteUrl

# Check current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin $currentBranch

Write-Host ""
Write-Host "✓ Repository setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/$GitHubUsername/$RepoName/settings/pages"
Write-Host "2. Under 'Source', select branch: $currentBranch"
Write-Host "3. Select folder: / (root)"
Write-Host "4. Click Save"
Write-Host ""
Write-Host "Your site will be available at:" -ForegroundColor Cyan
Write-Host "https://$GitHubUsername.github.io/$RepoName/" -ForegroundColor White

