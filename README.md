# AutoGen FDE Workflow Prototype

This repository contains a prototype demonstrating how to use **Microsoft AutoGen** to supercharge your Forward Deployed Engineering (FDE) workflow. 

It takes the concept of your "fde-orchestrator" and simulates a virtual team of AI agents that debate, refine, and execute the conversion of raw meeting notes into engineering tickets.

## What is AutoGen?

[AutoGen](https://microsoft.github.io/autogen/) is a framework that enables the development of LLM applications using multiple agents that can converse with each other to solve tasks. 

Instead of writing one massive, complex prompt and hoping the LLM gets everything right in one shot, AutoGen lets you build specialized **personas**. These personas operate like a real software team: they talk to each other, hand off tasks, write code, execute tools, and review each other's work before presenting the final result.

### Key Concepts
*   **Agents**: Individual AI instances with specific system prompts (e.g., a "Product Manager" agent, a "Senior Architect" agent).
*   **GroupChat**: A virtual room where multiple agents converse.
*   **Manager**: An orchestration agent that decides who speaks next (or forces them to speak in a specific order).
*   **Proxy (UserProxyAgent)**: Represents *you*. It can automatically execute code the other agents write, or pause the conversation to ask for your human feedback.

## How This FDE Prototype Works

In this prototype (`autogen_fde_prototype.py`), we have set up a 4-step pipeline using a `GroupChat` with `round_robin` speaker selection. The virtual team consists of:

1.  **User_Proxy (You):** Initiates the workflow by providing the raw meeting notes.
2.  **Discovery_Agent (The PM):** Parses the messy notes to extract the core business problem and desired features, outputting a structured Product Spec.
3.  **Architect_Agent (The Tech Lead):** Reviews the PM's spec, stress-tests the architecture, and points out missing backend constraints (like needing Docker/Kubernetes, database choices, or offline-sync logic).
4.  **Ticket_Agent (The Agile Delivery Manager):** Takes the spec and the Architect's warnings, and writes highly detailed Linear-style tickets with Acceptance Criteria.

## How to Use It

Because your system enforces a clean Python environment, we have set this project up inside a Virtual Environment (`venv`).

### 1. Set Your API Key
AutoGen needs an LLM to power the agents. This script uses OpenAI by default, but you can swap the config to use Gemini, Claude, or local models. 
Export your API key in your terminal:
```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
```
*(If you open `autogen_fde_prototype.py`, you can also edit the `config_list` to point to a different model/provider).*

### 2. Activate the Virtual Environment
Activate the environment where AutoGen is installed:
```bash
cd ~/fde-autogen
source venv/bin/activate
```

### 3. Run the Workflow!
Kick off the FDE pipeline:
```bash
python autogen_fde_prototype.py
```

Watch the terminal as the agents collaborate to turn the sample raw meeting notes into ready-to-work engineering tickets!
