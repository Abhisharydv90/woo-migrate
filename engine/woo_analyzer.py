import sys
import json
import requests
from requests.auth import HTTPBasicAuth

def analyze_store(url, consumer_key, consumer_secret):
    """
    Connects to a WooCommerce store and extracts structure for migration.
    """
    auth = HTTPBasicAuth(consumer_key, consumer_secret)
    base_url = f"{url.rstrip('/')}/wp-json/wc/v3"
    
    report = {
        "store_url": url,
        "status": "success",
        "products": 0,
        "categories": 0,
        "orders": 0,
        "migration_plan": []
    }

    try:
        # Fetch Categories
        cat_resp = requests.get(f"{base_url}/products/categories", auth=auth, params={"per_page": 100})
        if cat_resp.status_code == 200:
            categories = cat_resp.json()
            report["categories"] = len(categories)
            report["migration_plan"].append({
                "step": "migrate_categories",
                "count": len(categories),
                "target": "WPGraphQL Categories"
            })

        # Fetch Products
        prod_resp = requests.get(f"{base_url}/products", auth=auth, params={"per_page": 100})
        if prod_resp.status_code == 200:
            products = prod_resp.json()
            report["products"] = len(products)
            report["migration_plan"].append({
                "step": "migrate_products",
                "count": len(products),
                "target": "Next.js Product Pages"
            })

        # Fetch Orders (just count)
        order_resp = requests.get(f"{base_url}/orders", auth=auth, params={"per_page": 1})
        if order_resp.status_code == 200:
            # WooCommerce returns total in headers
            total_orders = order_resp.headers.get('X-WP-Total', 0)
            report["orders"] = int(total_orders)
            report["migration_plan"].append({
                "step": "migrate_orders",
                "count": int(total_orders),
                "target": "Stripe + WooCommerce Checkout"
            })

    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)

    return report

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: python woo_analyzer.py <url> <consumer_key> <consumer_secret>"}))
        sys.exit(1)

    url = sys.argv[1]
    ck = sys.argv[2]
    cs = sys.argv[3]
    
    result = analyze_store(url, ck, cs)
    print(json.dumps(result, indent=2))