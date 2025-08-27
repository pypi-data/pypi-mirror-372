#!/usr/bin/env python3
"""
Provider Registry for LiteLLM-supported LLM providers.
Organizes 100+ providers into categories for better UI navigation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os


@dataclass
class ProviderInfo:
    """Information about a provider"""
    name: str
    litellm_prefix: str
    category: str
    requires_api_key: bool
    api_key_env_var: Optional[str] = None
    default_models: Optional[List[str]] = None
    documentation_url: Optional[str] = None
    description: Optional[str] = None
    api_base_url: Optional[str] = None
    priority: int = 100  # Lower number = higher priority in category


class ProviderRegistry:
    """Registry of all LiteLLM-supported providers organized by category"""
    
    # Provider categories
    CATEGORY_LOCAL = "Local Models"
    CATEGORY_MAJOR_CLOUD = "Major Cloud Providers"
    CATEGORY_FAST_INFERENCE = "Fast Inference"
    CATEGORY_OPEN_SOURCE = "Open Source Models"
    CATEGORY_ENTERPRISE = "Enterprise Solutions"
    CATEGORY_REGIONAL = "Regional Providers"
    CATEGORY_SPECIALIZED = "Specialized Models"
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.categories = self._organize_by_category()
    
    def _initialize_providers(self) -> Dict[str, ProviderInfo]:
        """Initialize all provider definitions"""
        providers = {}
        
        # Local Models
        providers["LM Studio"] = ProviderInfo(
            name="LM Studio",
            litellm_prefix="openai",  # Uses OpenAI-compatible API
            category=self.CATEGORY_LOCAL,
            requires_api_key=False,
            api_base_url="http://localhost:1234/v1",
            description="Local models via LM Studio",
            priority=1
        )
        
        providers["Ollama"] = ProviderInfo(
            name="Ollama",
            litellm_prefix="ollama",
            category=self.CATEGORY_LOCAL,
            requires_api_key=False,
            api_base_url="http://localhost:11434",
            default_models=["gemma2:latest", "llama3.2:1b", "mistral"],
            description="Local models via Ollama",
            priority=2
        )
        
        providers["Llamafile"] = ProviderInfo(
            name="Llamafile",
            litellm_prefix="openai",
            category=self.CATEGORY_LOCAL,
            requires_api_key=False,
            api_base_url="http://localhost:8080/v1",
            description="Single-file executable LLMs",
            priority=3
        )
        
        providers["LocalAI"] = ProviderInfo(
            name="LocalAI",
            litellm_prefix="openai",
            category=self.CATEGORY_LOCAL,
            requires_api_key=False,
            api_base_url="http://localhost:8080/v1",
            description="OpenAI-compatible local API",
            priority=4
        )
        
        # Major Cloud Providers
        providers["OpenAI"] = ProviderInfo(
            name="OpenAI",
            litellm_prefix="openai",
            category=self.CATEGORY_MAJOR_CLOUD,
            requires_api_key=True,
            api_key_env_var="OPENAI_API_KEY",
            default_models=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            documentation_url="https://platform.openai.com/docs",
            description="GPT models from OpenAI",
            priority=1
        )
        
        providers["Anthropic"] = ProviderInfo(
            name="Anthropic",
            litellm_prefix="anthropic",
            category=self.CATEGORY_MAJOR_CLOUD,
            requires_api_key=True,
            api_key_env_var="ANTHROPIC_API_KEY",
            default_models=["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            documentation_url="https://docs.anthropic.com",
            description="Claude models from Anthropic",
            priority=2
        )
        
        providers["Google Vertex AI"] = ProviderInfo(
            name="Google Vertex AI",
            litellm_prefix="vertex_ai",
            category=self.CATEGORY_MAJOR_CLOUD,
            requires_api_key=True,
            api_key_env_var="GOOGLE_APPLICATION_CREDENTIALS",
            default_models=["gemini-pro", "gemini-pro-vision"],
            documentation_url="https://cloud.google.com/vertex-ai",
            description="Google's Gemini models",
            priority=3
        )
        
        providers["Azure OpenAI"] = ProviderInfo(
            name="Azure OpenAI",
            litellm_prefix="azure",
            category=self.CATEGORY_MAJOR_CLOUD,
            requires_api_key=True,
            api_key_env_var="AZURE_API_KEY",
            documentation_url="https://azure.microsoft.com/en-us/products/ai-services/openai-service",
            description="OpenAI models via Azure",
            priority=4
        )
        
        providers["AWS Bedrock"] = ProviderInfo(
            name="AWS Bedrock",
            litellm_prefix="bedrock",
            category=self.CATEGORY_MAJOR_CLOUD,
            requires_api_key=True,
            api_key_env_var="AWS_ACCESS_KEY_ID",
            default_models=["anthropic.claude-3-sonnet", "amazon.titan-text-express-v1"],
            documentation_url="https://aws.amazon.com/bedrock/",
            description="Multiple models via AWS",
            priority=5
        )
        
        # Fast Inference
        providers["Groq"] = ProviderInfo(
            name="Groq",
            litellm_prefix="groq",
            category=self.CATEGORY_FAST_INFERENCE,
            requires_api_key=True,
            api_key_env_var="GROQ_API_KEY",
            default_models=["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
            documentation_url="https://groq.com/",
            description="Ultra-fast inference",
            priority=1
        )
        
        providers["Together AI"] = ProviderInfo(
            name="Together AI",
            litellm_prefix="together_ai",
            category=self.CATEGORY_FAST_INFERENCE,
            requires_api_key=True,
            api_key_env_var="TOGETHERAI_API_KEY",
            default_models=["meta-llama/Llama-3-70b-chat-hf"],
            documentation_url="https://www.together.ai/",
            description="Fast open model inference",
            priority=2
        )
        
        providers["Anyscale"] = ProviderInfo(
            name="Anyscale",
            litellm_prefix="anyscale",
            category=self.CATEGORY_FAST_INFERENCE,
            requires_api_key=True,
            api_key_env_var="ANYSCALE_API_KEY",
            default_models=["meta-llama/Llama-2-70b-chat-hf"],
            documentation_url="https://www.anyscale.com/",
            description="Scalable model serving",
            priority=3
        )
        
        providers["Fireworks AI"] = ProviderInfo(
            name="Fireworks AI",
            litellm_prefix="fireworks_ai",
            category=self.CATEGORY_FAST_INFERENCE,
            requires_api_key=True,
            api_key_env_var="FIREWORKS_API_KEY",
            default_models=["accounts/fireworks/models/llama-v3-70b-instruct"],
            documentation_url="https://fireworks.ai/",
            description="Fast inference platform",
            priority=4
        )
        
        # Open Source Models
        providers["HuggingFace"] = ProviderInfo(
            name="HuggingFace",
            litellm_prefix="huggingface",
            category=self.CATEGORY_OPEN_SOURCE,
            requires_api_key=True,
            api_key_env_var="HUGGINGFACE_API_KEY",
            default_models=["microsoft/phi-2", "google/flan-t5-xxl"],
            documentation_url="https://huggingface.co/",
            description="Open source model hub",
            priority=1
        )
        
        providers["Replicate"] = ProviderInfo(
            name="Replicate",
            litellm_prefix="replicate",
            category=self.CATEGORY_OPEN_SOURCE,
            requires_api_key=True,
            api_key_env_var="REPLICATE_API_KEY",
            default_models=["meta/llama-2-70b-chat"],
            documentation_url="https://replicate.com/",
            description="Run open source models",
            priority=2
        )
        
        providers["Perplexity"] = ProviderInfo(
            name="Perplexity",
            litellm_prefix="perplexity",
            category=self.CATEGORY_OPEN_SOURCE,
            requires_api_key=True,
            api_key_env_var="PERPLEXITY_API_KEY",
            default_models=["llama-3.1-sonar-small-128k-online"],
            documentation_url="https://www.perplexity.ai/",
            description="Models with web search",
            priority=3
        )
        
        providers["DeepInfra"] = ProviderInfo(
            name="DeepInfra",
            litellm_prefix="deepinfra",
            category=self.CATEGORY_OPEN_SOURCE,
            requires_api_key=True,
            api_key_env_var="DEEPINFRA_API_KEY",
            default_models=["meta-llama/Llama-2-70b-chat-hf"],
            documentation_url="https://deepinfra.com/",
            description="Serverless inference",
            priority=4
        )
        
        # Enterprise Solutions
        providers["Cohere"] = ProviderInfo(
            name="Cohere",
            litellm_prefix="cohere",
            category=self.CATEGORY_ENTERPRISE,
            requires_api_key=True,
            api_key_env_var="COHERE_API_KEY",
            default_models=["command-r", "command-r-plus"],
            documentation_url="https://cohere.com/",
            description="Enterprise language AI",
            priority=1
        )
        
        providers["AI21"] = ProviderInfo(
            name="AI21",
            litellm_prefix="ai21",
            category=self.CATEGORY_ENTERPRISE,
            requires_api_key=True,
            api_key_env_var="AI21_API_KEY",
            default_models=["jamba-1.5-mini", "jamba-1.5-large"],
            documentation_url="https://www.ai21.com/",
            description="Jurassic models",
            priority=2
        )
        
        providers["Databricks"] = ProviderInfo(
            name="Databricks",
            litellm_prefix="databricks",
            category=self.CATEGORY_ENTERPRISE,
            requires_api_key=True,
            api_key_env_var="DATABRICKS_API_KEY",
            default_models=["databricks-dbrx-instruct"],
            documentation_url="https://www.databricks.com/",
            description="Enterprise data AI",
            priority=3
        )
        
        providers["IBM WatsonX"] = ProviderInfo(
            name="IBM WatsonX",
            litellm_prefix="watsonx",
            category=self.CATEGORY_ENTERPRISE,
            requires_api_key=True,
            api_key_env_var="WATSONX_API_KEY",
            default_models=["ibm/granite-13b-chat-v2"],
            documentation_url="https://www.ibm.com/watsonx",
            description="IBM's enterprise AI",
            priority=4
        )
        
        providers["Voyage AI"] = ProviderInfo(
            name="Voyage AI",
            litellm_prefix="voyage",
            category=self.CATEGORY_ENTERPRISE,
            requires_api_key=True,
            api_key_env_var="VOYAGE_API_KEY",
            default_models=["voyage-3"],
            documentation_url="https://www.voyageai.com/",
            description="Embedding models",
            priority=5
        )
        
        # Specialized Models
        providers["Mistral"] = ProviderInfo(
            name="Mistral",
            litellm_prefix="mistral",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="MISTRAL_API_KEY",
            default_models=["mistral-large-latest", "mistral-medium"],
            documentation_url="https://mistral.ai/",
            description="Mistral AI models",
            priority=1
        )
        
        providers["Grok"] = ProviderInfo(
            name="Grok",
            litellm_prefix="xai",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="XAI_API_KEY",
            default_models=["grok-2-1212", "grok-2-vision-1212"],
            documentation_url="https://x.ai/",
            description="xAI's Grok models",
            priority=2
        )
        
        providers["DeepSeek"] = ProviderInfo(
            name="DeepSeek",
            litellm_prefix="deepseek",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="DEEPSEEK_API_KEY",
            default_models=["deepseek-chat", "deepseek-coder"],
            documentation_url="https://www.deepseek.com/",
            description="Code and chat models",
            priority=3
        )
        
        providers["Cloudflare"] = ProviderInfo(
            name="Cloudflare Workers AI",
            litellm_prefix="cloudflare",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="CLOUDFLARE_API_KEY",
            default_models=["@cf/meta/llama-3-8b-instruct"],
            documentation_url="https://developers.cloudflare.com/workers-ai/",
            description="Edge AI models",
            priority=4
        )
        
        providers["Palm"] = ProviderInfo(
            name="Palm",
            litellm_prefix="palm",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="PALM_API_KEY",
            default_models=["chat-bison-001"],
            documentation_url="https://developers.generativeai.google/",
            description="Google PaLM models",
            priority=5
        )
        
        providers["NLP Cloud"] = ProviderInfo(
            name="NLP Cloud",
            litellm_prefix="nlp_cloud",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="NLP_CLOUD_API_KEY",
            default_models=["dolphin"],
            documentation_url="https://nlpcloud.com/",
            description="Specialized NLP models",
            priority=6
        )
        
        providers["AlephAlpha"] = ProviderInfo(
            name="Aleph Alpha",
            litellm_prefix="aleph_alpha",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="ALEPHALPHA_API_KEY",
            default_models=["luminous-supreme"],
            documentation_url="https://www.aleph-alpha.com/",
            description="European AI models",
            priority=7
        )
        
        providers["Baseten"] = ProviderInfo(
            name="Baseten",
            litellm_prefix="baseten",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="BASETEN_API_KEY",
            documentation_url="https://www.baseten.co/",
            description="Custom model deployment",
            priority=8
        )
        
        providers["Vllm"] = ProviderInfo(
            name="vLLM",
            litellm_prefix="vllm",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=False,
            documentation_url="https://vllm.ai/",
            description="High-throughput serving",
            priority=9
        )
        
        providers["SageMaker"] = ProviderInfo(
            name="AWS SageMaker",
            litellm_prefix="sagemaker",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=True,
            api_key_env_var="AWS_ACCESS_KEY_ID",
            documentation_url="https://aws.amazon.com/sagemaker/",
            description="Custom model endpoints",
            priority=10
        )
        
        providers["Petals"] = ProviderInfo(
            name="Petals",
            litellm_prefix="petals",
            category=self.CATEGORY_SPECIALIZED,
            requires_api_key=False,
            default_models=["bigscience/bloom"],
            documentation_url="https://petals.dev/",
            description="Distributed inference",
            priority=11
        )
        
        return providers
    
    def _organize_by_category(self) -> Dict[str, List[ProviderInfo]]:
        """Organize providers by category"""
        categories = {}
        for provider in self.providers.values():
            if provider.category not in categories:
                categories[provider.category] = []
            categories[provider.category].append(provider)
        
        # Sort providers within each category by priority
        for category in categories:
            categories[category].sort(key=lambda p: p.priority)
        
        return categories
    
    def get_provider(self, name: str) -> Optional[ProviderInfo]:
        """Get a specific provider by name"""
        return self.providers.get(name)
    
    def get_category_providers(self, category: str) -> List[ProviderInfo]:
        """Get all providers in a category"""
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all category names in display order"""
        # Return in a specific order for better UX
        order = [
            self.CATEGORY_LOCAL,
            self.CATEGORY_MAJOR_CLOUD,
            self.CATEGORY_FAST_INFERENCE,
            self.CATEGORY_OPEN_SOURCE,
            self.CATEGORY_ENTERPRISE,
            self.CATEGORY_SPECIALIZED
        ]
        # Add any categories not in the predefined order
        for cat in self.categories:
            if cat not in order:
                order.append(cat)
        return order
    
    def get_configured_providers(self) -> List[ProviderInfo]:
        """Get providers that have their API keys configured"""
        configured = []
        for provider in self.providers.values():
            if not provider.requires_api_key:
                # Local providers don't need API keys
                configured.append(provider)
            elif provider.api_key_env_var and os.environ.get(provider.api_key_env_var):
                configured.append(provider)
        return configured
    
    def get_available_providers(self) -> List[ProviderInfo]:
        """Get providers that are available (running for local, configured for cloud)"""
        available = []
        for provider in self.providers.values():
            if provider.category == self.CATEGORY_LOCAL:
                # Check if local service is running
                if self._check_local_service(provider):
                    available.append(provider)
            elif not provider.requires_api_key or (
                provider.api_key_env_var and os.environ.get(provider.api_key_env_var)
            ):
                available.append(provider)
        return available
    
    def _check_local_service(self, provider: ProviderInfo) -> bool:
        """Check if a local service is running"""
        if not provider.api_base_url:
            return False
        
        try:
            import requests
            # Try to reach the service
            response = requests.get(provider.api_base_url, timeout=1)
            return response.status_code < 500
        except:
            return False
    
    def search_providers(self, query: str) -> List[ProviderInfo]:
        """Search providers by name or description"""
        query = query.lower()
        results = []
        for provider in self.providers.values():
            if (query in provider.name.lower() or 
                (provider.description and query in provider.description.lower()) or
                query in provider.litellm_prefix.lower()):
                results.append(provider)
        return results


# Singleton instance
_registry = None

def get_registry() -> ProviderRegistry:
    """Get the singleton provider registry"""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry