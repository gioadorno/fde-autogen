# Nexus Orchestrator # FDE AutoGen Orchestrator & CLI

> 📖 **Real-World Usage:** Check out [EXAMPLES.md](EXAMPLES.md) for practical FDE workflows and terminal outputs.

> **Highlight:** This repository demonstrates Forward Deployed Engineering (FDE) principles, Developer Experience (DevEx), and LLM Orchestration. It simulates a multi-agent AI workflow wrapped in a custom **Go CLI (Cobra)**. It accelerates the discovery-to-delivery lifecycle by automating the conversion of raw meeting notes into structured product specs, and autonomously scaffolding code across frontend and backend monorepos.

## Core Capabilities

### 1. The FDE Meeting-to-Ticket Pipeline
- **Command:** `nexus process <notes.md> [--interactive]`
- **Workflow:** An `autogen.GroupChat` powers a collaborative debate between PM and Architect agents. It enriches raw meeting notes -> Drafts Product Spec -> Stress-tests Architecture (with rejection cycles) -> Generates Gherkin-style Linear Tickets using native tool calling.
- **Semantic Memory:** Utilizes a local ChromaDB vector database to intelligently retrieve context via RAG, learning from past executions and storing architectural rules in a visible `fde_knowledge_base.md`.

### 2. The Dual-Monorepo Scaffolder
- **Command:** `nexus scaffold <Ticket-ID>`
- **Workflow:** Fetches ticket details from the Linear API and orchestrates a `Scaffolder` agent to generate cross-repository boilerplate (gRPC, Protobufs, Go, and Angular).
- **Airgap Safety (Git Worktrees):** Code is generated into a safe, isolated Git worktree lane (`.fde/worktrees/<Ticket-ID>`). Path-traversal protection prevents the AI from touching the actual Git repositories.

### 3. The Autonomous Bazel Build & Fix Loop
- **Command:** `nexus apply <Ticket-ID>`
- **Workflow:**
  1. Prompts the user for review and approval of the staged files in the worktree lane.
  2. Copies the files into the actual `backend` and `frontend` workspaces.
  3. Executes `bazel run //:gazelle` and `bazel build //...`.
  4. **Self-Healing:** If the Bazel build fails, the Go CLI automatically deletes the copied files to keep the workspace pristine, captures the compiler error log, and passes it back to an AutoGen `Fixer_Agent`. The AI diagnoses the error, rewrites the staged files using tool calling inside the worktree, and prepares for another apply.

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
nexus process ~/Obsidian/Meetings/Acme_Kickoff.md --interactive
nexus scaffold CMS-4953
nexus apply CMS-4953
```
