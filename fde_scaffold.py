import autogen
import argparse
import os
import subprocess
from typing import Annotated

parser = argparse.ArgumentParser(description="AI-Powered Dual-Repo Scaffolder using Worktrees")
parser.add_argument("--ticket", help="Linear Ticket ID to scaffold", required=False)
parser.add_argument("--fix", action="store_true", help="Trigger the Fixer Agent")
parser.add_argument("--error-log", help="Path to the Bazel error log", required=False)
args = parser.parse_args()

# Mock Fetcher for Linear Ticket (In production, use requests against GraphQL API)
def fetch_ticket_context(ticket_id):
    print(f"[Linear API] Fetching context for {ticket_id}...")
    return f"""
    Ticket: {ticket_id} - Backend: Implement PTC Feedback Service
    Description: We need a new gRPC service in backend to handle PTC Feedback. 
    It requires a feedback.proto file. We also need the Angular frontend in frontend to have a basic feedback.service.ts to call it.
    """

llm_config = {
    "config_list": [
        {
            "model": os.environ.get("VERTEX_MODEL_NAME", "gemini-3.1-pro-preview"),
            "api_type": "google",
            "project": os.environ.get("GOOGLE_VERTEX_PROJECT", "extreme-karma-gm"),
            "location": os.environ.get("GOOGLE_VERTEX_LOCATION", "global")
        }
    ],
    "temperature": 0.1,
    "max_tokens": 8000,
}

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3, # Give it a few turns to call multiple tools if needed
    code_execution_config=False,
    is_termination_msg=lambda x: "TERMINATE" in str(x.get("content", "")).upper()
)

# ==============================================================================
# Worktree & Scaffolding Tools
# ==============================================================================

@user_proxy.register_for_execution()
def git_worktree_add(slug: Annotated[str, "The ticket slug to use for the worktree (e.g. CMS-4953)"]) -> str:
    """Creates a new git worktree for isolated scaffolding."""
    target_dir = f".fde/worktrees/{slug}"
    branch_name = f"fde-scaffold-{slug}"
    
    os.makedirs(".fde/worktrees", exist_ok=True)
    
    try:
        # Create worktree
        subprocess.run(["git", "worktree", "add", "-b", branch_name, target_dir], check=True, capture_output=True, text=True)
        return f"Worktree successfully created at {target_dir} on branch {branch_name}."
    except subprocess.CalledProcessError as e:
        # If it fails, maybe it already exists
        if "already exists" in e.stderr:
            return f"Worktree {target_dir} already exists. You can proceed with writing files."
        return f"Error creating worktree: {e.stderr}"

@user_proxy.register_for_execution()
def write_file(
    slug: Annotated[str, "The ticket slug matching the worktree"],
    path: Annotated[str, "The file path relative to the repository root (e.g. backend/api/feedback.proto)"],
    content: Annotated[str, "The exact file contents"]
) -> str:
    """Writes a file strictly inside the designated worktree lane."""
    target_dir = os.path.abspath(f".fde/worktrees/{slug}")
    full_path = os.path.abspath(os.path.join(target_dir, path))
    
    # Path traversal security check
    if not full_path.startswith(target_dir):
        return f"Error: Security violation. Path '{path}' escapes the worktree lane."
        
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content.strip() + "\n")
        return f"Success: Wrote file to {full_path}"
    except Exception as e:
        return f"Error writing file: {e}"

# ==============================================================================
# Agents
# ==============================================================================

if args.fix and args.error_log and args.ticket:
    print(f"🛠️  Initializing Fixer Agent with log: {args.error_log}")
    with open(args.error_log, "r") as f:
        errors = f.read()
    
    fixer = autogen.AssistantAgent(
        name="Fixer_Agent",
        system_message=f"""You are a Senior Go and Bazel Engineer. 
        Diagnose compiler errors and fix the files using the `write_file` tool.
        Your designated lane slug is: {args.ticket}
        Once you have written the fixed files, reply with 'TERMINATE'.""",
        llm_config=llm_config
    )
    
    autogen.agentchat.register_function(write_file, caller=fixer, executor=user_proxy, name="write_file", description="Writes a file to the worktree.")
    
    user_proxy.initiate_chat(fixer, message=f"Bazel build failed. Fix these errors by rewriting the affected files:\n\n{errors}")
    print(f"\n✅ Fixes applied safely in .fde/worktrees/{args.ticket}/")
    
elif args.ticket:
    ticket_context = fetch_ticket_context(args.ticket)
    
    scaffolder = autogen.AssistantAgent(
        name="Scaffolder",
        system_message=f"""You are a Dual-Monorepo Architect.
        Your task is to generate the exact file contents required for the ticket.
        You MUST use the `git_worktree_add` tool to create a safe lane using slug: {args.ticket}.
        Then you MUST use the `write_file` tool to scaffold the necessary files inside that lane.
        Do not output markdown code blocks. Use the tools.
        Reply with 'TERMINATE' when finished.""",
        llm_config=llm_config
    )
    
    # Register tools for scaffolder
    autogen.agentchat.register_function(git_worktree_add, caller=scaffolder, executor=user_proxy, name="git_worktree_add", description="Creates a git worktree.")
    autogen.agentchat.register_function(write_file, caller=scaffolder, executor=user_proxy, name="write_file", description="Writes a file to the worktree.")
    
    user_proxy.initiate_chat(scaffolder, message=f"Create a worktree and scaffold this ticket:\n{ticket_context}")
    
    print(f"\n✅ Scaffold generated safely in .fde/worktrees/{args.ticket}/")
else:
    print("Please provide a --ticket ID.")
