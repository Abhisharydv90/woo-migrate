# 🛍️ WooCommerce Migration Toolkit

> Generate a modern Next.js headless storefront from a legacy WooCommerce store in seconds.

WooCommerce is losing merchants to Shopify because headless migration is a nightmare. Developers have to rewrite APIs, sync carts, manage auth, and handle inventory across two systems. 

This tool automates the first step: analyzing the store, syncing the data, and generating a live Next.js frontend.

## 🚀 Features

- 🔍 Store Analyzer — Scans a WooCommerce store and outputs a migration plan
- 📦 Product Syncer — Fetches all products via REST API and saves them as JSON
- 🏗️ Next.js Generator — Generates a working headless storefront from that JSON
- 🎯 Single Binary CLI — Built in Go, wraps a Python engine
- 🛠️ Live Storefront — Renders products, images, prices, and descriptions

## ⚙️ Quick Start

1. Analyze a store:
```bash
woo-migrate analyze https://example.com ck_xxx cs_xxx

2. Sync products:
woo-migrate sync https://example.com ck_xxx cs_xxx ./output

3. Generate the storefront:
woo-migrate generate ./output/products.json ./storefront

4. Run it:
cd storefront
npm install
npm run dev

## 🧠 How It Works

1. Go CLI wraps the core engine
2. Python Analyzer connects to WooCommerce REST API
3. Python Syncer pulls all product data into a clean JSON structure
4. Python Generator scaffolds a Next.js project with the data baked in
5. Next.js renders the headless storefront locally

## 🎯 Why This Matters

- Speed: Skip weeks of manual migration work
- Modernization: Give legacy stores a React frontend instantly
- Proof of Concept: Show WooCommerce merchants what's possible

## 👤 Author

Built by Abhisharydv90 . let's talk.