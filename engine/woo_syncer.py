import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import os

def sync_products(url, consumer_key, consumer_secret, output_dir):
    """
    Fetches all products from a WooCommerce store and saves them as JSON.
    """
    auth = HTTPBasicAuth(consumer_key, consumer_secret)
    base_url = f"{url.rstrip('/')}/wp-json/wc/v3"
    
    all_products = []
    page = 1
    per_page = 100

    print(f"🔄 Syncing products from {url}...")

    try:
        while True:
            response = requests.get(
                f"{base_url}/products",
                auth=auth,
                params={"per_page": per_page, "page": page}
            )
            
            if response.status_code != 200:
                return {"status": "error", "message": f"API Error: {response.status_code}"}
            
            products = response.json()
            if not products:
                break
            
            for p in products:
                # Extract only the fields the frontend needs
                all_products.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "slug": p.get("slug"),
                    "price": p.get("price"),
                    "regular_price": p.get("regular_price"),
                    "sale_price": p.get("sale_price"),
                    "description": p.get("description"),
                    "short_description": p.get("short_description"),
                    "categories": [c.get("name") for c in p.get("categories", [])],
                    "images": [img.get("src") for img in p.get("images", [])],
                    "stock_status": p.get("stock_status")
                })
            
            print(f"   Fetched page {page} ({len(products)} products)")
            page += 1

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "products.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2)

        return {
            "status": "success",
            "total_products": len(all_products),
            "output_file": output_file
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Usage: python woo_syncer.py <url> <consumer_key> <consumer_secret> <output_dir>"}))
        sys.exit(1)

    url = sys.argv[1]
    ck = sys.argv[2]
    cs = sys.argv[3]
    output_dir = sys.argv[4]
    
    result = sync_products(url, ck, cs, output_dir)
    print(json.dumps(result, indent=2))