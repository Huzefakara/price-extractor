# Enhanced Price Detection: Original vs Discounted Prices

## 🎯 **Problem Solved**

Your CSV price comparison system now intelligently distinguishes between **original prices** and **discounted/sale prices** on competitor websites, ensuring you're always comparing against the actual selling price.

## ✨ **New Features**

### **1. Smart Price Type Detection**

The system now automatically identifies:

| Price Type | Description | Example |
|------------|-------------|---------|
| **`REGULAR`** | Standard price with no discounts | £299.99 |
| **`SALE`** | Actively discounted price | £199.99 (was £299.99) |
| **`DISCOUNTED`** | Current price lower than original | £249.99 (25% off) |
| **`ERROR`** | Could not extract or classify | N/A |

### **2. Intelligent Price Selection**

**Priority Order:**
1. **Sale Price** (highest priority) - The actual discounted price customers pay
2. **Current Price** - The active selling price 
3. **Original Price** - Fallback if others not available

### **3. Enhanced Results Structure**

Each competitor result now includes detailed price information:

```json
{
  "price": "£199.99",                    // The actual selling price used for comparison
  "price_details": {
    "current_price": "£199.99",          // Current selling price
    "original_price": "£299.99",         // Original/regular price (if available)
    "sale_price": "£199.99",             // Sale price (if on sale)
    "price_type": "sale",                // Type classification
    "discount_percentage": 33.3          // Discount percentage (if applicable)
  },
  "details": {
    "competitor_price_info": {
      "actual_price": "£199.99",
      "price_type": "sale",
      "original_price": "£299.99",
      "discount_percentage": 33.3
    },
    "competitor_discount": "Competitor has 33.3% discount"
  }
}
```

## 🔍 **Detection Strategies**

### **1. JSON-LD Structured Data Analysis**
```javascript
// Automatically detects price structures like:
{
  "@type": "Product",
  "offers": {
    "price": "199.99",        // Current price
    "highPrice": "299.99",    // Original price
    "lowPrice": "199.99"      // Sale price
  }
}
```

### **2. Smart CSS Selector Recognition**

**Sale Price Selectors:**
- `.sale-price`, `.price-sale`, `.discounted-price`
- `.deal-price`, `.reduced-price`, `.special-price`
- `.price-now`, `.price-current`, `.final-price`
- `[data-testid*="sale"]`, `[data-testid*="current"]`

**Original Price Selectors:**
- `.original-price`, `.regular-price`, `.was-price`
- `.old-price`, `.price-was`, `.list-price`
- `.crossed-price`, `.strike-price`, `.rrp`
- `[data-testid*="was"]`, `[data-testid*="original"]`

### **3. Visual Cue Analysis**
- Detects crossed-out/strikethrough prices
- Identifies hidden elements (display: none)
- Analyzes CSS classes for price indicators

## 📊 **Enhanced Comparison Logic**

### **Before Enhancement:**
```
Our Price: £299 vs Competitor: £199 → "We are 50% more expensive"
```

### **After Enhancement:**
```
Our Price: £299 vs Competitor: £199 [SALE] (Was: £299, -33% discount)
→ "We are 50% more expensive BUT competitor is on sale"
→ "Competitor has 33.3% discount"
→ Recommendation: "Monitor competitor's regular pricing"
```

## 🚀 **Real-World Examples**

### **Example 1: Amazon Product Page**
```html
<span class="a-price-whole">199</span>               <!-- Current/Sale Price -->
<span class="a-text-price">Was: £299.99</span>      <!-- Original Price -->
```

**Detection Result:**
- **Current Price:** £199
- **Original Price:** £299.99
- **Price Type:** `discounted`
- **Discount:** 33.3%
- **Used for Comparison:** £199 (actual selling price)

### **Example 2: John Lewis Sale**
```html
<div class="price-current">£149.99</div>             <!-- Sale Price -->
<div class="price-was">£199.99</div>                 <!-- Original Price -->
```

**Detection Result:**
- **Sale Price:** £149.99
- **Original Price:** £199.99
- **Price Type:** `sale`
- **Discount:** 25%
- **Used for Comparison:** £149.99 (sale price)

## 🎯 **Business Benefits**

### **1. Accurate Competitive Intelligence**
- Compare against actual selling prices, not inflated MSRPs
- Understand when competitors are running promotions
- Track competitor discount strategies

### **2. Strategic Pricing Decisions**
- Know if you're competing against temporary sales or permanent prices
- Identify opportunities when competitors return to regular pricing
- Adjust pricing strategy based on competitor discount patterns

### **3. Market Positioning**
- Understand true market positioning vs promotional pricing
- Track competitor price elasticity through discount analysis
- Monitor competitor margin strategies

## 📈 **Enhanced Web Interface**

The web interface now displays:

```
✅ amazon.co.uk/product... - £199.99 (HIGHER) [SALE] (-33%) (Was: £299.99)
```

**Legend:**
- **Price:** £199.99 (actual selling price)
- **Comparison:** (HIGHER/LOWER/EQUAL) vs your price
- **Type:** [SALE/REGULAR/DISCOUNTED]
- **Discount:** (-33%) if applicable
- **Original:** (Was: £299.99) if different

## ⚙️ **API Usage**

### **Testing Enhanced Detection:**
```python
import requests

# Test with a product that has both original and sale prices
csv_content = """product_name,our_price,competitor_url_1
iPhone 15,£999,https://www.amazon.co.uk/dp/B0CHX1W1XY"""

with open('test.csv', 'w') as f:
    f.write(csv_content)

with open('test.csv', 'rb') as file:
    files = {'file': file}
    response = requests.post('http://localhost:5000/api/compare-csv', files=files)
    
result = response.json()
for product in result['results']:
    for competitor in product['competitor_results']:
        if competitor['status'] == 'success':
            details = competitor['price_details']
            print(f"Price: {competitor['price']}")
            print(f"Type: {details['price_type']}")
            print(f"Original: {details['original_price']}")
            print(f"Discount: {details['discount_percentage']}%")
```

## 🔧 **Configuration Options**

The system automatically handles:
- **Currency Detection:** £, $, € symbols
- **Regional Formats:** US vs UK price formatting  
- **Decimal Separators:** Commas vs periods
- **Hidden Elements:** Skips display:none elements
- **Multiple Currencies:** Consistent comparison within same currency

## 🚨 **Edge Cases Handled**

1. **No Original Price Available** → Uses current price as regular
2. **Sale Price = Original Price** → Classified as regular pricing
3. **Multiple Sale Prices** → Uses the most prominent/first detected
4. **Invalid Discount Calculation** → Falls back to simple price comparison
5. **Mixed Currency Formats** → Maintains format consistency per competitor

## 📋 **Best Practices**

1. **Monitor Competitor Sales Cycles** - Track when competitors run promotions
2. **Adjust for Seasonal Discounts** - Consider timing when analyzing competitor pricing
3. **Compare Like-for-Like** - Ensure you're comparing similar product variants
4. **Track Price History** - Regular monitoring reveals competitor pricing patterns
5. **Strategic Response** - Use discount intelligence for your own promotional timing

---

## 🎉 **Result**

Your price comparison system now provides **business-grade competitive intelligence** that distinguishes between promotional and regular pricing, giving you the insights needed for strategic pricing decisions!

**Before:** "Competitor is £50 cheaper"
**Now:** "Competitor is £50 cheaper BUT it's a 25% promotional discount - monitor for return to regular pricing"