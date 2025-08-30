from wxo_agentic_evaluation.service_provider.ollama_provider import OllamaProvider
from wxo_agentic_evaluation.service_provider.watsonx_provider import WatsonXProvider
from wxo_agentic_evaluation.service_provider.model_proxy_provider import ModelProxyProvider
from wxo_agentic_evaluation.arg_configs import ProviderConfig

import os

def _instantiate_provider(config: ProviderConfig, **kwargs):
    if config.provider == "watsonx":
        return WatsonXProvider(model_id=config.model_id, **kwargs)
    elif config.provider == "ollama":
        return OllamaProvider(model_id=config.model_id, **kwargs)
    elif config.provider == "model_proxy":
        return ModelProxyProvider(model_id=config.model_id, **kwargs)
    else:
        raise RuntimeError(f"target provider is not supported {config.provider}")
    
def get_provider(config: ProviderConfig = None, model_id: str = None, **kwargs):
    if config:
        return _instantiate_provider(config, **kwargs)

    if not model_id:
        raise ValueError("model_id must be provided if config is not supplied")

    if "WATSONX_APIKEY" in os.environ and "WATSONX_SPACE_ID" in os.environ:
        config = ProviderConfig(provider="watsonx", model_id=model_id)
        return _instantiate_provider(config, **kwargs)

    if "WO_API_KEY" in os.environ and "WO_INSTANCE" in os.environ:
        config = ProviderConfig(provider="model_proxy", model_id=model_id)
        return _instantiate_provider(config, **kwargs)

    raise RuntimeError(
        "No provider found. Please either provide a config or set the required environment variables."
    )