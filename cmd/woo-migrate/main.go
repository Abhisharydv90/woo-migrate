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

func main() {
	if len(os.Args) < 5 {
		fmt.Println("Usage: woo-migrate analyze <store_url> <consumer_key> <consumer_secret>")
		os.Exit(1)
	}

	command := os.Args[1]
	if command != "analyze" {
		fmt.Println("❌ Unknown command. Use 'analyze'.")
		os.Exit(1)
	}

	url := os.Args[2]
	ck := os.Args[3]
	cs := os.Args[4]

	fmt.Printf("🔍 Analyzing WooCommerce store: %s\n\n", url)

	exePath, _ := os.Executable()
	exeDir := filepath.Dir(exePath)
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