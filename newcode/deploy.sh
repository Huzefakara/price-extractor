#!/bin/bash

# 🚀 Price Extractor Machine - Deployment Script
# This script automates the deployment process to Vercel

echo "🚀 Starting Price Extractor Machine Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
    print_success "Git repository initialized"
fi

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_status "Committing current changes..."
    git add .
    git commit -m "Deploy: Price Extractor Machine - $(date)"
    print_success "Changes committed"
fi

# Get repository URL
REPO_URL=$(git remote get-url origin 2>/dev/null)

if [ -z "$REPO_URL" ]; then
    print_warning "No remote repository found. You'll need to create one manually."
    echo ""
    echo "To create a GitHub repository:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named 'price-extractor'"
    echo "3. Run these commands:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/price-extractor.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    read -p "Press Enter when you've created the repository and want to continue..."
    
    # Ask for repository URL
    read -p "Enter your GitHub repository URL: " REPO_URL
    git remote add origin "$REPO_URL"
    git branch -M main
    git push -u origin main
fi

print_success "Repository is ready for deployment"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_warning "Vercel CLI is not installed. Installing now..."
    npm install -g vercel
    print_success "Vercel CLI installed"
fi

# Deploy to Vercel
print_status "Deploying to Vercel..."
echo ""
echo "You'll be prompted to:"
echo "1. Log in to Vercel (if not already logged in)"
echo "2. Link to existing project or create new one"
echo "3. Configure deployment settings"
echo ""

# Deploy
vercel --prod

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully!"
    echo ""
    echo "🎉 Your Price Extractor Machine is now live!"
    echo ""
    echo "Next steps:"
    echo "1. Test all features on your live URL"
    echo "2. Share the URL with your clients"
    echo "3. Consider adding a custom domain"
    echo ""
    echo "For client sharing, see CLIENT_README.md"
    echo "For deployment details, see DEPLOYMENT_GUIDE.md"
else
    print_error "Deployment failed. Please check the error messages above."
    exit 1
fi

echo ""
print_success "Deployment script completed! 🚀"
