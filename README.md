# FDE AutoGen Orchestrator & CLI

> **Portfolio Highlight:** This repository demonstrates Forward Deployed Engineering (FDE) principles, Developer Experience (DevEx), and LLM Orchestration. It simulates a multi-agent AI workflow wrapped in a custom **Go CLI (Cobra)**. It accelerates the discovery-to-delivery lifecycle by automating the conversion of raw meeting notes into structured product specs, architectural reviews, and ready-to-work engineering tickets.

## Features

1. **Custom Go CLI (`fde`):** A cross-platform Go wrapper built with Cobra that securely invokes the Python AutoGen pipeline. It provides a flawless developer experience, allowing the pipeline to be executed globally from any directory.
2. **LLM Observability (AgentOps):** Fully instrumented with AgentOps to trace token consumption, agent logic, and execution times, ensuring the AI system is auditable and production-ready.
3. **Dynamic Input/Output:** Point the CLI at any Markdown file containing meeting notes. It generates a clean `[File_Name]_FDE_Plan.md` file in the same directory.
4. **Human-in-the-Loop:** The script pauses before generating tickets, allowing the human FDE to inject feedback or correct the architecture.
5. **Linear API Tool with Fallback:** The Ticket Agent calls a Python function to create tickets in Linear. If the API key is missing or fails, it gracefully falls back to appending the tickets directly into your local Markdown plan.
6. **Hybrid Semantic Memory (ChromaDB):** Agents learn from past executions using a local ChromaDB vector database. A post-execution hook extracts these learned rules and writes them to a visible `fde_knowledge_base.md` file so you can audit the AI's "brain."

## How to Use It

### 1. Build the Go CLI
```bash
cd cli
go build -o fde
mv fde ~/.local/bin/  # Or anywhere in your PATH
```

### 2. Configure Your LLM & Observability
Export your API Keys (or edit `fde_workflow.py` to point to a local Ollama model):
```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
export AGENTOPS_API_KEY="your-agentops-key" # Optional for tracing
```

### 3. Run the Engine
Pass the path to your meeting notes directly via the `fde` command:
```bash
fde process ~/Obsidian/Meetings/Acme_Kickoff.md
```

Watch the terminal as the Discovery Agent, Architect Agent, and Ticket Agent debate and build your plan!
