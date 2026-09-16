import sys
import json
import os

NEXT_CONFIG = """
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: { domains: ['localhost'] },
}
module.exports = nextConfig
"""

PACKAGE_JSON = """
{
  "name": "headless-woocommerce-storefront",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "13.4.19",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "axios": "1.4.0"
  }
}
"""

INDEX_PAGE = """
import Link from 'next/link';
import products from '../products.json';

export default function Home() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🛍️ Headless WooCommerce Store</h1>
      <p>Migrated successfully. {products.length} products found.</p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
        {products.map((p) => (
          <div key={p.id} style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px' }}>
            <img src={p.images[0] || 'https://via.placeholder.com/150'} alt={p.name} style={{ width: '100%', height: '150px', objectFit: 'cover' }} />
            <h3>{p.name}</h3>
            <p>${p.price}</p>
            <Link href={`/products/${p.slug}`}>View Product →</Link>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

PRODUCT_PAGE = """
import { useRouter } from 'next/router';
import products from '../../products.json';

export default function ProductPage() {
  const router = useRouter();
  const { slug } = router.query;
  const product = products.find((p) => p.slug === slug);

  if (!product) return <div style={{ padding: '2rem' }}>Loading or Not Found...</div>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>{product.name}</h1>
      <img src={product.images[0]} alt={product.name} style={{ maxWidth: '400px' }} />
      <p style={{ fontSize: '1.5rem' }}>${product.price}</p>
      <div dangerouslySetInnerHTML={{ __html: product.description }} />
    </div>
  );
}
"""

def generate_storefront(products_file, output_dir):
    try:
        # Use utf-8-sig to handle Windows PowerShell BOM
        with open(products_file, 'r', encoding='utf-8-sig') as f:
            products = json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Failed to read products file: {e}"}

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "pages", "products"), exist_ok=True)

    # Notice the encoding='utf-8' on all these writes
    with open(os.path.join(output_dir, "next.config.js"), 'w', encoding='utf-8') as f: 
        f.write(NEXT_CONFIG)
    with open(os.path.join(output_dir, "package.json"), 'w', encoding='utf-8') as f: 
        f.write(PACKAGE_JSON)
    
    # Copy the JSON so the frontend can import it
    with open(os.path.join(output_dir, "products.json"), 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2)

    with open(os.path.join(output_dir, "pages", "index.js"), 'w', encoding='utf-8') as f: 
        f.write(INDEX_PAGE)
    with open(os.path.join(output_dir, "pages", "products", "[slug].js"), 'w', encoding='utf-8') as f: 
        f.write(PRODUCT_PAGE)

    return {
        "status": "success",
        "products_generated": len(products),
        "output_dir": output_dir
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python nextjs_generator.py <products_json> <output_dir>"}))
        sys.exit(1)
    
    result = generate_storefront(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))