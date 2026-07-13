package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

var memoryCmd = &cobra.Command{
	Use:   "memory",
	Short: "Manage ChromaDB semantic memory",
}

var clearCmd = &cobra.Command{
	Use:   "clear",
	Short: "Clear the semantic memory database",
	Run: func(cmd *cobra.Command, args []string) {
		homeDir, _ := os.UserHomeDir()
		dbPath := filepath.Join(homeDir, "fde-autogen", "chroma_fde_memory")
		
		fmt.Printf("Clearing memory at: %s\n", dbPath)
		err := os.RemoveAll(dbPath)
		if err != nil {
			fmt.Printf("Error clearing memory: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("Memory successfully cleared.")
	},
}

func init() {
	rootCmd.AddCommand(memoryCmd)
	memoryCmd.AddCommand(clearCmd)
}