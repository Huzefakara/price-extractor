#!/usr/bin/env python3
"""
Test script for CSV price comparison API
"""

import requests
import json

def test_csv_upload():
    """Test the CSV upload and price comparison endpoint"""
    
    # API endpoint (adjust URL based on your deployment)
    url = "http://localhost:5000/api/compare-csv"  # For local testing
    # url = "https://your-vercel-app.vercel.app/api/compare-csv"  # For Vercel deployment
    
    # Path to your CSV file
    csv_file_path = "sample_products.csv"
    
    try:
        # Open and upload the CSV file
        with open(csv_file_path, 'rb') as file:
            files = {'file': file}
            
            print("Uploading CSV and processing price comparisons...")
            print("This may take a while as we extract prices from competitor websites...")
            
            response = requests.post(url, files=files, timeout=300)  # 5 minute timeout
            
            if response.status_code == 200:
                result = response.json()
                print("\n" + "="*60)
                print("PRICE COMPARISON RESULTS")
                print("="*60)
                
                # Print overall summary
                summary = result.get('summary', {})
                print(f"\nOVERALL SUMMARY:")
                print(f"Total Products: {summary.get('total_products', 0)}")
                print(f"Successful Comparisons: {summary.get('successful_comparisons', 0)}")
                print(f"Competitive Products: {summary.get('competitive_products', 0)}")
                print(f"Need Price Adjustment: {summary.get('needs_adjustment', 0)}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown').upper()}")
                
                # Print detailed results for each product
                for product in result.get('results', []):
                    print(f"\n{'-'*50}")
                    print(f"PRODUCT: {product['product_name']}")
                    print(f"OUR PRICE: {product['our_price']}")
                    print(f"STATUS: {product['status'].upper()}")
                    
                    if product['status'] == 'success':
                        prod_summary = product.get('summary', {})
                        print(f"\nCOMPETITOR ANALYSIS:")
                        print(f"  • Total Competitors Checked: {prod_summary.get('total_competitors', 0)}")
                        print(f"  • Successful Price Extractions: {prod_summary.get('successful_extractions', 0)}")
                        print(f"  • We are CHEAPER than: {prod_summary.get('lower_than_competitors', 0)} competitors")
                        print(f"  • We are MORE EXPENSIVE than: {prod_summary.get('higher_than_competitors', 0)} competitors")
                        print(f"  • Equal pricing: {prod_summary.get('equal_to_competitors', 0)} competitors")
                        print(f"  • Recommendation: {prod_summary.get('overall_recommendation', '').upper()}")
                        
                        # Show individual competitor results
                        print(f"\nDETAILED COMPETITOR COMPARISON:")
                        for competitor in product.get('competitor_results', []):
                            print(f"  • {competitor['url'][:50]}...")
                            if competitor['status'] == 'success':
                                print(f"    Price: {competitor['price']}")
                                print(f"    Comparison: {competitor['comparison'].upper()}")
                                
                                # Show price details if available
                                price_details = competitor.get('price_details', {})
                                if price_details.get('price_type'):
                                    price_type = price_details['price_type'].upper()
                                    print(f"    Price Type: {price_type}")
                                    
                                    if price_details.get('discount_percentage'):
                                        print(f"    Discount: {price_details['discount_percentage']}% off")
                                    
                                    if price_details.get('original_price') and price_details['original_price'] != competitor['price']:
                                        print(f"    Original Price: {price_details['original_price']}")
                                
                                details = competitor.get('details', {})
                                print(f"    Status: {details.get('status', 'unknown')}")
                                print(f"    Message: {details.get('message', 'No details')}")
                                if 'recommendation' in details:
                                    print(f"    Recommendation: {details['recommendation']}")
                                if 'competitor_discount' in details:
                                    print(f"    ⚠️  {details['competitor_discount']}")
                            else:
                                print(f"    Status: {competitor['status']} - Could not extract price")
                    else:
                        print(f"ERROR: {product.get('error', 'Unknown error')}")
                
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError:
        print(f"Error: Could not find CSV file '{csv_file_path}'")
        print("Make sure the sample_products.csv file exists in the same directory")
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server might be processing too many URLs.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_csv_upload()