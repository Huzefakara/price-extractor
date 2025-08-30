# Price Extractor Machine - Vercel Deployment Guide

## 🚀 Deploy to Vercel

This guide will help you deploy your Price Extractor Machine to Vercel for free hosting.

### 📋 Prerequisites

1. **GitHub Account** - Create one at [github.com](https://github.com)
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (you can use your GitHub account)
3. **Git** - Install from [git-scm.com](https://git-scm.com)

### 🔧 Deployment Steps

#### Step 1: Prepare Your Repository

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Price Extractor Machine"
   ```

2. **Create GitHub Repository**:
   - Go to [github.com](https://github.com) and create a new repository
   - Name it `price-extractor-machine`
   - Don't initialize with README, .gitignore, or license

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/price-extractor-machine.git
   git branch -M main
   git push -u origin main
   ```

#### Step 2: Deploy on Vercel

1. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Deployment**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements-vercel.txt`

3. **Environment Variables** (if needed):
   - No special environment variables required for basic functionality

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete (usually 1-2 minutes)

### 📁 File Structure for Vercel

Your project should have this structure:
```
price-extractor-machine/
├── api/
│   ├── index.py          # Main page handler
│   └── extract.py        # Price extraction API
├── static/
│   ├── style.css         # Styling
│   └── script-vercel.js  # Frontend logic
├── templates/
│   └── index.html        # HTML template
├── vercel.json           # Vercel configuration
├── requirements-vercel.txt # Python dependencies
├── package.json          # Project metadata
└── README-DEPLOYMENT.md  # This file
```

### 🔄 Key Differences from Local Version

**Serverless Architecture:**
- Uses individual API functions instead of a persistent Flask server
- Direct price extraction without session management
- Limited to 10 URLs per request (serverless constraints)
- Uses `requests` + `BeautifulSoup` instead of Playwright (more serverless-friendly)

**Performance Considerations:**
- Cold start delays (first request may be slower)
- 300-second maximum execution time per function
- No persistent state between requests

### 🛠️ Updating Your Deployment

To update your deployed application:

1. **Make Changes Locally**
2. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. **Automatic Deployment**: Vercel will automatically redeploy

### 🔧 Alternative: Direct Vercel CLI Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login and Deploy**:
   ```bash
   vercel login
   vercel
   ```

3. **Follow the prompts** to configure and deploy

### 🌐 Custom Domain (Optional)

1. **In Vercel Dashboard**:
   - Go to your project
   - Click "Domains"
   - Add your custom domain

2. **DNS Configuration**:
   - Point your domain to Vercel's servers
   - Follow Vercel's DNS instructions

### ⚠️ Limitations on Vercel

- **Execution Time**: Max 300 seconds per function
- **Memory**: Limited memory allocation
- **Browser Automation**: Playwright not supported (using requests instead)
- **Concurrent Requests**: Limited concurrent executions
- **URL Limit**: Reduced to 10 URLs per request

### 🎯 Success!

Once deployed, your Price Extractor Machine will be available at:
- `https://your-project-name.vercel.app`

### 🔍 Troubleshooting

**Common Issues:**

1. **Build Failures**:
   - Check `requirements-vercel.txt` for correct dependencies
   - Ensure all files are committed to Git

2. **API Errors**:
   - Check Vercel function logs in the dashboard
   - Verify API endpoints are correctly configured

3. **Timeout Issues**:
   - Reduce number of URLs if extraction times out
   - Some websites may be slower than others

### 📊 Monitoring

- **Vercel Dashboard**: Monitor function executions, errors, and performance
- **Analytics**: View usage statistics and performance metrics
- **Logs**: Debug issues with detailed function logs

---

**🎉 Congratulations!** Your Price Extractor Machine is now live on Vercel!

Share the URL and start extracting prices from anywhere in the world! 🌍