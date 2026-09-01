import logging
import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

from tools import user_functions


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.WARNING)

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Azure Authentication
# ---------------------------------------------------------

credential = DefaultAzureCredential(
    exclude_environment_credential=False,
    exclude_managed_identity_credential=False,
    exclude_shared_token_cache_credential=True,
    exclude_visual_studio_code_credential=True,
)


# ---------------------------------------------------------
# Azure Key Vault
# ---------------------------------------------------------

key_vault_url = os.environ.get("KEYVAULT_URL")

if not key_vault_url:
    raise RuntimeError("KEYVAULT_URL environment variable is not set.")

key_vault = SecretClient(
    vault_url=key_vault_url,
    credential=credential,
)


# ---------------------------------------------------------
# Get required configuration from Key Vault
# ---------------------------------------------------------

ai_project_connection_string = key_vault.get_secret(
    "ai-project-conn-string"
).value

model_deployment_name = key_vault.get_secret(
    "model-deployment-name"
).value


if not model_deployment_name:
    raise RuntimeError(
        "Key Vault secret 'model-deployment-name' is empty."
    )


# ---------------------------------------------------------
# Create Agent ToolSet
# ---------------------------------------------------------

functions = FunctionTool(user_functions)

toolset = ToolSet()
toolset.add(functions)


# ---------------------------------------------------------
# Azure AI Project Client
# ---------------------------------------------------------

agents_client = AIProjectClient.from_connection_string(
    ai_project_connection_string,
    credential=credential,
)

agent_client = agents_client.agents


# ---------------------------------------------------------
# Application Insights / OpenTelemetry
# ---------------------------------------------------------

application_insights_connection_string = (
    agents_client.telemetry.get_connection_string()
)

if application_insights_connection_string:
    configure_azure_monitor(
        connection_string=application_insights_connection_string
    )


scenario = Path(__file__).name
tracer = trace.get_tracer(__name__)


# ---------------------------------------------------------
# Create Healthcare Agent
# ---------------------------------------------------------

def creating_agent():

    logger.info("Starting healthcare agent creation...")

    try:

        # -------------------------------------------------
        # Read agent instructions
        # -------------------------------------------------

        instructions_file = Path(__file__).parent / "instructions.txt"

        if not instructions_file.exists():
            raise FileNotFoundError(
                f"Instructions file not found: {instructions_file}"
            )

        instructions = instructions_file.read_text(
            encoding="utf-8"
        )


        # -------------------------------------------------
        # Create agent
        # -------------------------------------------------

        with tracer.start_as_current_span(scenario):

            agent = agent_client.create_agent(
                model=model_deployment_name,
                name="healthcare_agent",
                instructions=instructions,
                toolset=toolset,
            )


        print(f"Created agent successfully.")
        print(f"Agent ID: {agent.id}")


        # -------------------------------------------------
        # Save Agent ID to Key Vault
        # -------------------------------------------------

        key_vault.set_secret(
            name="agent-id",
            value=agent.id,
        )

        print("Agent ID saved to Azure Key Vault.")

    except Exception as e:

        logger.error(
            "An error occurred while creating the agent: %s",
            str(e),
        )

        raise


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    creating_agent()
