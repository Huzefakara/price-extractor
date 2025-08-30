@echo off
REM 🚀 Price Extractor Machine - Windows Deployment Script

echo 🚀 Starting Price Extractor Machine Deployment...
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if we're in a git repository
if not exist ".git" (
    echo [INFO] Initializing Git repository...
    git init
    echo [SUCCESS] Git repository initialized
)

REM Check if we have uncommitted changes
git diff --quiet
if errorlevel 1 (
    echo [INFO] Committing current changes...
    git add .
    git commit -m "Deploy: Price Extractor Machine - %date% %time%"
    echo [SUCCESS] Changes committed
)

REM Check if remote repository exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [WARNING] No remote repository found. You'll need to create one manually.
    echo.
    echo To create a GitHub repository:
    echo 1. Go to https://github.com/new
    echo 2. Create a new repository named 'price-extractor'
    echo 3. Run these commands:
    echo    git remote add origin https://github.com/YOUR_USERNAME/price-extractor.git
    echo    git branch -M main
    echo    git push -u origin main
    echo.
    pause
    echo.
    set /p REPO_URL="Enter your GitHub repository URL: "
    git remote add origin "%REPO_URL%"
    git branch -M main
    git push -u origin main
)

echo [SUCCESS] Repository is ready for deployment

REM Check if Node.js is installed (for Vercel CLI)
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Vercel CLI is not installed. Installing now...
    npm install -g vercel
    echo [SUCCESS] Vercel CLI installed
)

REM Deploy to Vercel
echo [INFO] Deploying to Vercel...
echo.
echo You'll be prompted to:
echo 1. Log in to Vercel (if not already logged in)
echo 2. Link to existing project or create new one
echo 3. Configure deployment settings
echo.

vercel --prod

if errorlevel 1 (
    echo [ERROR] Deployment failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo 🎉 Your Price Extractor Machine is now live!
echo.
echo Next steps:
echo 1. Test all features on your live URL
echo 2. Share the URL with your clients
echo 3. Consider adding a custom domain
echo.
echo For client sharing, see CLIENT_README.md
echo For deployment details, see DEPLOYMENT_GUIDE.md
echo.
echo [SUCCESS] Deployment script completed! 🚀
pause
