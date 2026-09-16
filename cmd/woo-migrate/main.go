package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

type MigrationStep struct {
	Step   string `json:"step"`
	Count  int    `json:"count"`
	Target string `json:"target"`
}

type StoreReport struct {
	StoreURL      string          `json:"store_url"`
	Status        string          `json:"status"`
	Products      int             `json:"products"`
	Categories    int             `json:"categories"`
	Orders        int             `json:"orders"`
	MigrationPlan []MigrationStep `json:"migration_plan"`
	Error         string          `json:"error,omitempty"`
}

type SyncResult struct {
	Status        string `json:"status"`
	TotalProducts int    `json:"total_products"`
	OutputFile    string `json:"output_file"`
	Message       string `json:"message,omitempty"`
}

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]

	exePath, _ := os.Executable()
	exeDir := filepath.Dir(exePath)

	switch command {
	case "analyze":
		if len(os.Args) < 5 {
			fmt.Println("❌ Usage: woo-migrate analyze <store_url> <consumer_key> <consumer_secret>")
			os.Exit(1)
		}
		runAnalyze(exeDir, os.Args[2], os.Args[3], os.Args[4])

	case "sync":
		if len(os.Args) < 6 {
			fmt.Println("❌ Usage: woo-migrate sync <store_url> <consumer_key> <consumer_secret> <output_dir>")
			os.Exit(1)
		}
		runSync(exeDir, os.Args[2], os.Args[3], os.Args[4], os.Args[5])

	case "generate":
		if len(os.Args) < 4 {
			fmt.Println("❌ Usage: woo-migrate generate <products_json> <output_dir>")
			os.Exit(1)
		}
		runGenerate(exeDir, os.Args[2], os.Args[3])

	default:
		fmt.Println("❌ Unknown command. Use 'analyze', 'sync', or 'generate'.")
		os.Exit(1)
	}
}

func runAnalyze(exeDir, url, ck, cs string) {
	fmt.Printf("🔍 Analyzing WooCommerce store: %s\n\n", url)
	pythonScript := filepath.Join(exeDir, "engine", "woo_analyzer.py")
	cmd := exec.Command("python", pythonScript, url, ck, cs)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Error running analyzer: %v\n", err)
		os.Exit(1)
	}

	var report StoreReport
	if err := json.Unmarshal(output, &report); err != nil {
		fmt.Printf("❌ Error parsing output: %v\nRaw: %s\n", err, string(output))
		os.Exit(1)
	}

	if report.Status == "error" {
		fmt.Printf("❌ Error: %s\n", report.Error)
		os.Exit(1)
	}

	fmt.Printf("✅ Store Analysis Complete\n")
	fmt.Printf("📦 Products:   %d\n", report.Products)
	fmt.Printf("📁 Categories: %d\n", report.Categories)
	fmt.Printf("🛒 Orders:     %d\n\n", report.Orders)
	fmt.Println("📋 Migration Plan:")
	for _, step := range report.MigrationPlan {
		fmt.Printf("   - %s (%d items) → %s\n", step.Step, step.Count, step.Target)
	}
}

func runSync(exeDir, url, ck, cs, outputDir string) {
	fmt.Printf("🚀 Syncing products from: %s\n\n", url)
	pythonScript := filepath.Join(exeDir, "engine", "woo_syncer.py")
	cmd := exec.Command("python", pythonScript, url, ck, cs, outputDir)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Error running syncer: %v\n", err)
		os.Exit(1)
	}

	var result SyncResult
	if err := json.Unmarshal(output, &result); err != nil {
		fmt.Printf("❌ Error parsing output: %v\nRaw: %s\n", err, string(output))
		os.Exit(1)
	}

	if result.Status == "error" {
		fmt.Printf("❌ Error: %s\n", result.Message)
		os.Exit(1)
	}

	fmt.Printf("✅ Sync Complete\n")
	fmt.Printf("📦 Total Products: %d\n", result.TotalProducts)
	fmt.Printf("📁 Output File:    %s\n", result.OutputFile)
}

func runGenerate(exeDir, productsFile, outputDir string) {
	fmt.Printf("🏗️  Generating Next.js storefront from %s...\n\n", productsFile)
	pythonScript := filepath.Join(exeDir, "engine", "nextjs_generator.py")
	cmd := exec.Command("python", pythonScript, productsFile, outputDir)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Error running generator: %v\n", err)
		fmt.Printf("📄 Python Output (The REAL error):\n%s\n", string(output))
		os.Exit(1)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		fmt.Printf("❌ Error parsing output: %v\nRaw: %s\n", err, string(output))
		os.Exit(1)
	}

	if result["status"] == "error" {
		fmt.Printf("❌ Error: %s\n", result["message"])
		os.Exit(1)
	}

	fmt.Printf("✅ Storefront Generated\n")
	fmt.Printf("📁 Output Directory: %s\n", result["output_dir"])
	fmt.Printf("📦 Products:         %v\n", result["products_generated"])
}

func printUsage() {
	fmt.Println("WooCommerce Migration Toolkit")
	fmt.Println("")
	fmt.Println("Usage:")
	fmt.Println("  woo-migrate analyze <store_url> <consumer_key> <consumer_secret>")
	fmt.Println("  woo-migrate sync <store_url> <consumer_key> <consumer_secret> <output_dir>")
	fmt.Println("  woo-migrate generate <products_json> <output_dir>")
}