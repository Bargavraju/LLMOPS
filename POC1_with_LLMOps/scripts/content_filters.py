import os
import requests

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


load_dotenv()


# Azure authentication
credential = DefaultAzureCredential(
    exclude_environment_credential=False,
    exclude_managed_identity_credential=False,
    exclude_shared_token_cache_credential=True,
    exclude_visual_studio_code_credential=True,
)

# Azure Key Vault
key_vault = SecretClient(
    vault_url=os.environ["KEYVAULT_URL"],
    credential=credential
)


# Azure AI Management API configuration
subscription_id = key_vault.get_secret("subscription-id").value
resource_group_name = key_vault.get_secret("rgName").value
account_name = key_vault.get_secret("aiName").value

api_version = "2024-04-01-preview"


default_policy_data = {
    "properties": {
        "basePolicyName": "Microsoft.Default",
        "contentFilters": [
            {
                "name": "hate",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Prompt",
            },
            {
                "name": "hate",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Completion",
            },
            {
                "name": "sexual",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Prompt",
            },
            {
                "name": "sexual",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Completion",
            },
            {
                "name": "selfharm",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Prompt",
            },
            {
                "name": "selfharm",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Completion",
            },
            {
                "name": "violence",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Prompt",
            },
            {
                "name": "violence",
                "blocking": True,
                "enabled": True,
                "allowedContentLevel": "Medium",
                "source": "Completion",
            },
            {
                "name": "jailbreak",
                "blocking": True,
                "enabled": True,
                "source": "Prompt",
            },
            {
                "name": "indirect_attack",
                "blocking": True,
                "enabled": True,
                "source": "Prompt",
            },
        ],
    }
}


class AOAIContentFilterManager:

    def __init__(
        self,
        subscription_id,
        resource_group_name,
        account_name,
        credential,
    ):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.account_name = account_name
        self.api_version = api_version
        self.credential = credential
        self.default_policy_data = default_policy_data

        self.access_token = self._get_access_token()

    def _get_access_token(self):
        return self.credential.get_token(
            "https://management.azure.com/.default"
        ).token

    def list_content_filters(self):

        url = (
            f"https://management.azure.com/"
            f"subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/"
            f"providers/Microsoft.CognitiveServices/"
            f"accounts/{self.account_name}/"
            f"raiPolicies?api-version={self.api_version}"
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            filters = [
                filter_item["name"]
                for filter_item in response_data["value"]
            ]
            return filters

        raise Exception(
            f"Failed to retrieve content filters. "
            f"Status code: {response.status_code}, "
            f"Response: {response.text}"
        )

    def get_filter_details(self, rai_policy_name):

        url = (
            f"https://management.azure.com/"
            f"subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/"
            f"providers/Microsoft.CognitiveServices/"
            f"accounts/{self.account_name}/"
            f"raiPolicies/{rai_policy_name}"
            f"?api-version={self.api_version}"
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()

        raise Exception(
            f"Failed to retrieve filter details for "
            f"{rai_policy_name}. "
            f"Status code: {response.status_code}, "
            f"Response: {response.text}"
        )

    def create_or_update_filter(
        self,
        rai_policy_name,
        policy_data=None,
    ):

        if policy_data is None:
            policy_data = self.default_policy_data

        url = (
            f"https://management.azure.com/"
            f"subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/"
            f"providers/Microsoft.CognitiveServices/"
            f"accounts/{self.account_name}/"
            f"raiPolicies/{rai_policy_name}"
            f"?api-version={self.api_version}"
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.put(
            url,
            headers=headers,
            json=policy_data,
        )

        if response.status_code in [200, 201]:
            return response.json()

        raise Exception(
            f"Failed to create or update filter for "
            f"{rai_policy_name}. "
            f"Status code: {response.status_code}, "
            f"Response: {response.text}"
        )

    def delete_filter(self, rai_policy_name):

        url = (
            f"https://management.azure.com/"
            f"subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/"
            f"providers/Microsoft.CognitiveServices/"
            f"accounts/{self.account_name}/"
            f"raiPolicies/{rai_policy_name}"
            f"?api-version={self.api_version}"
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 202:
            return f"Filter {rai_policy_name} successfully deleted."

        elif response.status_code == 204:
            return f"Filter {rai_policy_name} does not exist."

        raise Exception(
            f"Failed to delete filter for {rai_policy_name}. "
            f"Status code: {response.status_code}, "
            f"Response: {response.text}"
        )


# Create manager
cf_manager = AOAIContentFilterManager(
    subscription_id,
    resource_group_name,
    account_name,
    credential,
)


# List existing policies
filters = cf_manager.list_content_filters()
print("Content Filters:", filters)


# Reset/update prompt-shield policy
cf_manager.create_or_update_filter(
    "prompt-shield",
    default_policy_data,
)


# Verify
filters = cf_manager.list_content_filters()
print("Content Filters after update:", filters)
