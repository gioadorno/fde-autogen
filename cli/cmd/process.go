package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/spf13/cobra"
)

var auto bool
var model string

var processCmd = &cobra.Command{
	Use:   "process [file]",
	Short: "Process a meeting notes markdown file",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		inputFile := args[0]

		// Resolve absolute path of input file
		absPath, err := filepath.Abs(inputFile)
		if err != nil {
			fmt.Printf("Error resolving path: %v\n", err)
			os.Exit(1)
		}

		homeDir, _ := os.UserHomeDir()
		projectDir := filepath.Join(homeDir, "fde-autogen")
		pythonBin := filepath.Join(projectDir, "venv", "bin", "python")
		scriptPath := filepath.Join(projectDir, "fde_workflow.py")

		fmt.Printf("Starting FDE workflow for: %s\n", absPath)
		if auto {
			fmt.Println("Mode: Auto (Headless)")
		}
		if model != "" {
			fmt.Printf("Model override: %s\n", model)
		}

		execCmd := exec.Command(pythonBin, scriptPath, absPath)
		
		env := os.Environ()
		if auto {
			env = append(env, "FDE_AUTO_MODE=1")
		}
		if model != "" {
			env = append(env, fmt.Sprintf("FDE_MODEL=%s", model))
		}
		execCmd.Env = env

		execCmd.Stdout = os.Stdout
		execCmd.Stderr = os.Stderr
		execCmd.Stdin = os.Stdin

		err = execCmd.Run()
		if err != nil {
			fmt.Printf("Error executing workflow: %v\n", err)
			os.Exit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(processCmd)
	processCmd.Flags().BoolVar(&auto, "auto", false, "Run headlessly, skipping human-in-the-loop pause")
	processCmd.Flags().StringVar(&model, "model", "", "Override the LLM model (e.g., gpt-4, llama3)")
}