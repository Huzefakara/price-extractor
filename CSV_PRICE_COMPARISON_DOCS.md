# CSV Price Comparison API Documentation

## Overview

The CSV Price Comparison API allows you to upload a CSV file containing your products and competitor URLs, then automatically extracts prices from competitor websites and provides detailed comparison analysis.

## Features

- ✅ **CSV File Upload**: Upload a CSV file with product data
- ✅ **Automatic Price Extraction**: Extract prices from competitor websites
- ✅ **Price Comparison**: Compare your prices with competitors
- ✅ **Detailed Analysis**: Get recommendations for pricing strategy
- ✅ **Batch Processing**: Handle multiple products simultaneously
- ✅ **Error Handling**: Robust error handling for failed extractions

## API Endpoint

### POST `/api/compare-csv`

Upload a CSV file and get price comparison results.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: CSV file in form field named `file`

**Response:**
```json
{
  "results": [
    {
      "product_name": "iPhone 15 Pro",
      "our_price": "£999",
      "competitor_results": [
        {
          "url": "https://www.amazon.co.uk/...",
          "price": "£949",
          "comparison": "higher",
          "details": {
            "status": "expensive",
            "message": "Our price is 5.26% higher than competitor",
            "difference": "-50.00",
            "recommendation": "Consider price adjustment to be more competitive"
          },
          "status": "success"
        }
      ],
      "summary": {
        "total_competitors": 3,
        "successful_extractions": 2,
        "lower_than_competitors": 0,
        "higher_than_competitors": 2,
        "equal_to_competitors": 0,
        "overall_recommendation": "consider_adjustment"
      },
      "status": "success"
    }
  ],
  "summary": {
    "total_products": 1,
    "successful_comparisons": 1,
    "competitive_products": 0,
    "needs_adjustment": 1,
    "overall_status": "needs_review"
  },
  "status": "success"
}
```

## CSV File Format

Your CSV file should have the following columns:

### Required Columns:
- `product_name` - Name of your product
- `our_price` - Your current price (with currency symbol like £, $, €)

### Competitor URL Columns:
You can include multiple competitor URL columns. The system will automatically detect columns containing "competitor" or "url" in the name.

**Example column names:**
- `competitor_url_1`
- `competitor_url_2` 
- `competitor_url_3`
- `amazon_url`
- `competitor_website_1`

### Sample CSV Format:
```csv
product_name,our_price,competitor_url_1,competitor_url_2,competitor_url_3
iPhone 15 Pro,£999,https://www.amazon.co.uk/dp/B0CHX1W1XY,https://www.johnlewis.com/apple-iphone-15-pro/p109925854,https://www.currys.co.uk/products/apple-iphone-15-pro-128-gb-natural-titanium-10267134.html
Samsung Galaxy S24,£799,https://www.amazon.co.uk/dp/B0CMDRCZBX,https://www.johnlewis.com/samsung-galaxy-s24-5g/p109926045,https://www.currys.co.uk/products/samsung-galaxy-s24-256-gb-onyx-black-10267206.html
```

## Constraints

- **Maximum 5 products per CSV file** (serverless limitations)
- **Maximum 6 competitor URLs per product** (performance optimization)
- **File must be a valid CSV format**
- **CSV file size should be reasonable** (< 1MB recommended)

## Comparison Results

### Comparison Types:
- `lower` - Your price is lower than competitor (✅ Good)
- `higher` - Your price is higher than competitor (⚠️ Consider adjustment)
- `equal` - Prices are equal (➡️ Consider slight reduction)
- `unknown` - Unable to compare (❓ Check formats)

### Status Types:
- `competitive` - You are cheaper than most competitors
- `expensive` - You are more expensive than most competitors
- `equal` - Prices are similar
- `unknown` - Unable to determine

### Recommendations:
- **"Good position - we are cheaper"** - Your pricing is competitive
- **"Consider price adjustment to be more competitive"** - You might want to lower prices
- **"Consider slight reduction to gain competitive edge"** - Small adjustment could help

## Error Handling

The API handles various error scenarios:

### File Upload Errors:
- No file provided
- Invalid file format (not CSV)
- Empty file

### CSV Processing Errors:
- Invalid CSV structure
- Missing required columns
- No valid products found

### Price Extraction Errors:
- Website unavailable
- Price not found on page
- Invalid price format

## Usage Examples

### Using curl:
```bash
curl -X POST \
  -F "file=@sample_products.csv" \
  http://localhost:5000/api/compare-csv
```

### Using Python requests:
```python
import requests

with open('sample_products.csv', 'rb') as file:
    files = {'file': file}
    response = requests.post('http://localhost:5000/api/compare-csv', files=files)
    result = response.json()
    print(result)
```

### Using JavaScript/fetch:
```javascript
const formData = new FormData();
formData.append('file', csvFile);

fetch('/api/compare-csv', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Best Practices

1. **Use valid URLs**: Ensure competitor URLs are accessible and contain product pages
2. **Consistent pricing format**: Use the same currency symbol (£, $, €) throughout
3. **Test with small batches**: Start with 1-2 products to test the format
4. **Handle timeouts**: Price extraction can take time, set appropriate timeouts
5. **Review results**: Always review the extracted prices for accuracy

## Performance Notes

- Price extraction is done in parallel for better performance
- Each product is processed with up to 3 concurrent threads
- Total processing time depends on the number of competitors and website response times
- Typical processing time: 10-30 seconds per product (depending on competitor URLs)

## Troubleshooting

### Common Issues:

1. **"No valid products found"**
   - Check CSV column names match expected format
   - Ensure required columns are present

2. **"No price found"**
   - Competitor website might have changed structure
   - Product might be out of stock
   - URL might be invalid

3. **"Request timeout"**
   - Reduce number of products or competitor URLs
   - Some websites might be slow to respond

4. **"Unable to compare prices"**
   - Check price format consistency
   - Ensure currency symbols are correct