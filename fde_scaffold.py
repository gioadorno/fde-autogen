import autogen
import argparse
import os
import re

parser = argparse.ArgumentParser(description="AI-Powered Dual-Repo Scaffolder")
parser.add_argument("--ticket", help="Linear Ticket ID to scaffold", required=False)
parser.add_argument("--fix", action="store_true", help="Trigger the Fixer Agent")
parser.add_argument("--error-log", help="Path to the Bazel error log", required=False)
args = parser.parse_args()

# Mock Fetcher for Linear Ticket (In production, use requests against GraphQL API)
def fetch_ticket_context(ticket_id):
    print(f"[Linear API] Fetching context for {ticket_id}...")
    # Simulated response
    return f"""
    Ticket: {ticket_id} - Backend: Implement PTC Feedback Service
    Description: We need a new gRPC service in client-systems to handle PTC Feedback. 
    It requires a feedback.proto file. We also need the Angular frontend in monkey-see to have a basic feedback.service.ts to call it.
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
    max_consecutive_auto_reply=1,
    code_execution_config=False,
)

if args.fix and args.error_log:
    print(f"🛠️  Initializing Fixer Agent with log: {args.error_log}")
    with open(args.error_log, "r") as f:
        errors = f.read()
    
    fixer = autogen.AssistantAgent(
        name="Fixer_Agent",
        system_message="You are a Senior Go and Bazel Engineer. Diagnose the following compiler error and provide the updated Go code blocks to fix it.",
        llm_config=llm_config
    )
    user_proxy.initiate_chat(fixer, message=f"Bazel build failed. Fix this code:\n\n{errors}")
    
elif args.ticket:
    ticket_context = fetch_ticket_context(args.ticket)
    scaffolder = autogen.AssistantAgent(
        name="Scaffolder",
        system_message="""You are a Dual-Monorepo Architect.
        Generate the exact file contents required for this ticket.
        You MUST format your output strictly as:
        ### FILE: client-systems/api/feedback.proto
        ```proto
        ...code...
        ```
        ### FILE: monkey-see/src/feedback.service.ts
        ```typescript
        ...code...
        ```
        """,
        llm_config=llm_config
    )
    
    user_proxy.initiate_chat(scaffolder, message=f"Generate the scaffold for this ticket:\n{ticket_context}")
    
    # Parse the output into a staging directory
    response = user_proxy.last_message(scaffolder)["content"]
    staging_dir = f"{args.ticket}_Scaffold"
    os.makedirs(staging_dir, exist_ok=True)
    
    # Simple regex to extract ### FILE: <path> and ```...```
    files = re.findall(r'### FILE: (.*?)\n.*?```.*?\n(.*?)```', response, re.DOTALL)
    for file_path, content in files:
        full_path = os.path.join(staging_dir, file_path.strip())
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content.strip() + "\n")
    
    print(f"\n✅ Scaffold generated safely in ./{staging_dir}/")