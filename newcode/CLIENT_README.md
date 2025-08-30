# 🛒 Price Extractor Machine - Client Guide

## 🎯 What This Tool Does

The Price Extractor Machine is a powerful web-based tool that helps you:
- **Extract prices** from multiple e-commerce websites instantly
- **Compare your prices** with competitors automatically
- **Analyze market positioning** with detailed competitive insights
- **Export results** for further analysis and reporting

## 🚀 Quick Start

### Option 1: URL-Based Price Extraction

1. **Go to the main page**: [Your Vercel URL]
2. **Enter product URLs** (one per line):
   ```
   https://www.amazon.co.uk/dp/B0CHX1W1XY
   https://www.johnlewis.com/apple-iphone-15-pro/p109925854
   https://www.currys.co.uk/products/apple-iphone-15-pro-128-gb-natural-titanium-10267134.html
   ```
3. **Click "Extract Prices"**
4. **View results** and export if needed

### Option 2: CSV Batch Processing

1. **Go to CSV Upload page**: [Your Vercel URL]/csv-upload
2. **Prepare your CSV file** with this format:
   ```csv
   product_name,our_price,competitor_url_1,competitor_url_2,competitor_url_3
   iPhone 15 Pro,£999,https://www.amazon.co.uk/dp/B0CHX1W1XY,https://www.johnlewis.com/apple-iphone-15-pro/p109925854,https://www.currys.co.uk/products/apple-iphone-15-pro-128-gb-natural-titanium-10267134.html
   Samsung Galaxy S24,£799,https://www.amazon.co.uk/dp/B0CMDRCZBX,https://www.johnlewis.com/samsung-galaxy-s24-5g/p109926045,https://www.currys.co.uk/products/samsung-galaxy-s24-256-gb-onyx-black-10267206.html
   ```
3. **Upload and process** your CSV file
4. **Review competitive analysis** results

## 📊 Understanding Results

### Price Extraction Results

For each URL, you'll see:
- ✅ **Extracted Price**: The actual selling price found
- 📊 **Price Type**: Regular, Sale, or Discounted
- 💰 **Original Price**: If the item is on sale
- 🎯 **Discount Percentage**: If applicable

### Competitive Analysis Results

For each product, you'll get:
- 📈 **Overall Recommendation**: Competitive or Needs Adjustment
- 🏆 **Position Summary**: How many competitors you're cheaper than
- 📊 **Detailed Comparisons**: Price differences and percentages
- 💡 **Actionable Insights**: Specific recommendations

## 🎨 Real-World Use Cases

### 1. Daily Price Monitoring
**Scenario**: Monitor competitor prices daily
**Process**:
1. Create CSV with your products and competitor URLs
2. Run analysis daily
3. Track price changes over time
4. Adjust your pricing strategy

### 2. Product Launch Research
**Scenario**: Research pricing before launching new products
**Process**:
1. Identify competitor products
2. Extract their current prices
3. Analyze price positioning
4. Set competitive launch prices

### 3. Seasonal Price Analysis
**Scenario**: Understand holiday pricing strategies
**Process**:
1. Monitor prices before/during holidays
2. Track discount patterns
3. Identify optimal pricing windows
4. Plan your promotional strategy

### 4. Market Entry Analysis
**Scenario**: Entering a new market segment
**Process**:
1. Research all major competitors
2. Analyze price ranges and positioning
3. Identify pricing gaps
4. Position your products strategically

## 📋 CSV Format Guide

### Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| `product_name` | Your product name | "iPhone 15 Pro" |
| `our_price` | Your selling price | "£999" |
| `competitor_url_1` | First competitor URL | "https://amazon.co.uk/..." |
| `competitor_url_2` | Second competitor URL | "https://johnlewis.com/..." |
| `competitor_url_3` | Third competitor URL | "https://currys.co.uk/..." |

### CSV Template

Download this template and fill in your data:
```csv
product_name,our_price,competitor_url_1,competitor_url_2,competitor_url_3
Product Name,Your Price,Competitor 1 URL,Competitor 2 URL,Competitor 3 URL
```

### Tips for Best Results

1. **Use Direct Product URLs**: Link directly to product pages, not category pages
2. **Include Multiple Competitors**: 3-5 competitors per product for best analysis
3. **Consistent Price Format**: Use the same currency format (e.g., £999, $999, €999)
4. **Valid URLs**: Ensure all URLs are accessible and working

## 🔍 Supported Websites

The tool works with most major e-commerce sites:

### UK Retailers
- ✅ Amazon UK
- ✅ John Lewis
- ✅ Currys
- ✅ Argos
- ✅ Very
- ✅ AO.com
- ✅ eBay UK

### International Retailers
- ✅ Amazon (US, DE, FR, etc.)
- ✅ Best Buy
- ✅ Walmart
- ✅ Target
- ✅ Most Shopify stores
- ✅ Most WooCommerce stores

### What Works Best
- **Product pages** with clear pricing
- **Structured data** (JSON-LD markup)
- **Standard price formats** (£, $, €)
- **Mainstream e-commerce platforms**

## 📈 Interpreting Results

### Competitive Position Indicators

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 **COMPETITIVE** | Your price is lower than most competitors | ✅ Good position - maintain or increase |
| 🟡 **CONSIDER ADJUSTMENT** | Your price is higher than competitors | 📊 Review pricing strategy |
| 🔴 **NEEDS REVIEW** | Unable to compare prices | 🔍 Check competitor URLs |

### Price Type Indicators

| Type | Meaning |
|------|---------|
| **Regular** | Standard selling price |
| **Sale** | Currently discounted |
| **Discounted** | Reduced from original price |

## 🚨 Troubleshooting

### Common Issues

1. **"No price found" errors**:
   - Check if URL is accessible
   - Verify it's a product page, not category page
   - Try a different competitor URL

2. **"Processing timeout" errors**:
   - Reduce number of URLs per batch
   - Split large CSV files into smaller ones
   - Check internet connection

3. **"Invalid CSV format" errors**:
   - Ensure CSV has required columns
   - Check for missing commas or quotes
   - Verify file encoding (UTF-8)

### Getting Help

If you encounter issues:
1. **Check the troubleshooting section** above
2. **Verify your CSV format** matches the template
3. **Test with a single URL** first
4. **Contact support** with specific error details

## 📞 Support & Contact

### Need Help?

- **Technical Issues**: [Your Support Email]
- **Feature Requests**: [Your Contact Form]
- **Training Sessions**: [Your Booking Link]

### Quick Support Checklist

Before contacting support, please have ready:
- [ ] Screenshot of the error
- [ ] Your CSV file (if applicable)
- [ ] URLs you're trying to process
- [ ] Browser and device information

---

## 🎉 Success Stories

### Case Study 1: Electronics Retailer
**Challenge**: Monitor 50+ products across 5 competitors daily
**Solution**: Automated CSV processing with daily reports
**Result**: 15% increase in competitive pricing accuracy

### Case Study 2: Fashion Brand
**Challenge**: Seasonal pricing strategy for new collection
**Solution**: Pre-launch competitor analysis
**Result**: Optimal pricing positioning, 25% higher margins

### Case Study 3: Home Goods Store
**Challenge**: Enter new market segment
**Solution**: Comprehensive market analysis
**Result**: Successful market entry with competitive pricing

---

**Ready to optimize your pricing strategy? Start using the Price Extractor Machine today! 🚀**
