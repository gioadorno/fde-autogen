import autogen
import os

# ==============================================================================
# 1. Configuration
# This tells AutoGen which LLM to use. You can use OpenAI, Gemini, or local Ollama.
# We're using a placeholder for the API key, which it will read from your environment.
# ==============================================================================
config_list = [
    {
        "model": "gpt-4o", # Or "gemini-1.5-pro", etc.
        "api_key": os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.2, # Keep it low for more deterministic, engineering-focused outputs
}

# ==============================================================================
# 2. Define the Agents
# Each agent gets a specific persona and role in the FDE workflow.
# ==============================================================================

# The User Proxy represents YOU. It initiates the chat and can optionally step in to provide human feedback.
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="A human FDE admin. Initiates the workflow with raw meeting notes.",
    human_input_mode="NEVER", # Set to "TERMINATE" or "ALWAYS" if you want it to pause and ask for your input
    max_consecutive_auto_reply=10,
    code_execution_config=False
)

# The Discovery Agent translates raw, messy notes into a structured spec.
discovery_agent = autogen.AssistantAgent(
    name="Discovery_Agent",
    system_message=(
        "You are an expert Forward Deployed Product Manager. "
        "Your job is to take raw, messy meeting notes and extract the core business problem, "
        "user needs, and a structured list of desired features. "
        "Output a clear 'Product Spec'."
    ),
    llm_config=llm_config,
)

# The Architect Agent looks at the spec and pokes holes in it.
architect_agent = autogen.AssistantAgent(
    name="Architect_Agent",
    system_message=(
        "You are a Senior Systems Architect. You review Product Specs provided by the Discovery_Agent. "
        "Your job is to stress-test the architecture. Think about edge cases, data normalization, "
        "database choices (PostgreSQL vs MongoDB), and cloud infrastructure (Docker, Kubernetes). "
        "Suggest technical constraints or backend-first scaffolding steps that must be addressed."
    ),
    llm_config=llm_config,
)

# The Ticket Agent takes the final agreed-upon spec and technical constraints and writes Linear tickets.
ticket_agent = autogen.AssistantAgent(
    name="Ticket_Agent",
    system_message=(
        "You are an Agile Delivery Manager. You take the Product Spec and the Architect's technical constraints, "
        "and you break them down into ready-to-work Linear tickets. "
        "Each ticket must have a Title, Description, Acceptance Criteria, and Technical Implementation notes."
    ),
    llm_config=llm_config,
)

# ==============================================================================
# 3. Create the Group Chat (The "Room" where they talk)
# ==============================================================================
groupchat = autogen.GroupChat(
    agents=[user_proxy, discovery_agent, architect_agent, ticket_agent],
    messages=[],
    max_round=5, # Limit the conversation to 5 turns so it doesn't loop forever
    speaker_selection_method="round_robin" # Forces them to speak in order: Proxy -> Discovery -> Architect -> Ticket
)

# The Manager handles the group chat and passes messages between agents using the LLM.
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# ==============================================================================
# 4. Run the Workflow!
# ==============================================================================
if __name__ == "__main__":
    raw_meeting_notes = """
    Meeting with Acme Corp Logistics Team - 10/24/2026
    - Drivers are complaining that the current mobile app is too slow when they upload delivery confirmation photos.
    - Sometimes they lose cellular service in rural areas, and the app just crashes and loses the photo.
    - The warehouse managers need a dashboard to see which deliveries are 'pending photo' vs 'completed' in real-time.
    - They mentioned they want this built fast, maybe using Flutter for the mobile app since they have Android and iOS drivers.
    - Backend is currently a messy legacy system. We probably need a new microservice to handle just these photo uploads.
    """

    print("🚀 Initiating FDE AutoGen Workflow...\n")
    
    # The proxy kicks off the conversation by sending the raw notes to the manager
    user_proxy.initiate_chat(
        manager,
        message=f"Here are the raw meeting notes from today. Please process these into a spec, stress-test the architecture, and generate the Linear tickets.\n\nNOTES:\n{raw_meeting_notes}"
    )
