package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "nexus",
	Short: "Nexus Orchestrator",
	Long:  `A CLI tool to orchestrate the Forward Deployed Engineering AI workflow.`,
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	// Global flags can go here
}