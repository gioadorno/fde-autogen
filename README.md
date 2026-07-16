# Nexus Orchestrator # FDE AutoGen Orchestrator & CLI CLI

> **Highlight:** This repository demonstrates Forward Deployed Engineering (FDE) principles, Developer Experience (DevEx), and LLM Orchestration. It simulates a multi-agent AI workflow wrapped in a custom **Go CLI (Cobra)**. It accelerates the discovery-to-delivery lifecycle by automating the conversion of raw meeting notes into structured product specs, and autonomously scaffolding code across frontend and backend monorepos.

## Core Capabilities

### 1. The FDE Meeting-to-Ticket Pipeline

- **Command:** `nexus process <notes.md>`
- **Workflow:** Enriches raw meeting notes -> Drafts Product Spec -> Stress-tests Architecture -> Generates Gherkin-style Linear Tickets.
- **Semantic Memory:** Utilizes a local ChromaDB vector database to learn from past executions and store architectural rules in a visible `fde_knowledge_base.md`.

### 2. The Dual-Monorepo Scaffolder

- **Command:** `nexus scaffold <Ticket-ID>`
- **Workflow:** Fetches ticket details from the Linear API and orchestrates a `Backend_Agent` and `Frontend_Agent` to generate cross-repository boilerplate (gRPC, Protobufs, Go, and Angular).
- **Airgap Safety:** Code is generated into a safe, local `[Ticket-ID]_Scaffold/` staging directory. The AI is strictly prohibited from touching the actual Git repositories.

### 3. The Autonomous Bazel Build & Fix Loop

- **Command:** `nexus apply <Staging-Directory>`
- **Workflow:**
  1. Prompts the user for review and approval of the staged files.
  2. Copies the files into the actual `client-systems` and `monkey-see` workspaces.
  3. Executes `bazel run //:gazelle` and `bazel build //...`.
  4. **Self-Healing:** If the Bazel build fails, the Go CLI automatically deletes the copied files to keep the workspace pristine, captures the compiler error log, and passes it back to an AutoGen `Fixer_Agent`. The AI diagnoses the error, rewrites the staged files, and prepares for another apply.

## Getting Started

### 1. Build the Go CLI

```bash
cd cli
go mod tidy
go build -o nexus
mv nexus ~/.local/bin/  # Or anywhere in your PATH
```

### 2. Configure Environment

```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
export LINEAR_API_KEY="lin_api_your_key"
export AGENTOPS_API_KEY="your-agentops-key" # Optional for tracing
```

### 3. Run the Tools

```bash
nexus process ~/Obsidian/Meetings/Acme_Kickoff.md
nexus scaffold CMS-4953
nexus apply ./CMS-4953_Scaffold
```
