"""
Unified completion client for all AI providers
Extracted and improved from api/completions.py
"""
import os
import logging
from typing import Optional, List, Dict, Any, Union

from .models import ModelManager
from .providers import GoogleCompletions, OpenAICompletions, OllamaCompletions

logger = logging.getLogger(__name__)


class CompletionClient:
    """
    Unified completion client that routes requests to appropriate providers
    based on model names or explicit provider specification
    """
    
    # Model to provider mapping for known models
    MODEL_PROVIDERS = {
        # OpenAI models
        "gpt-4": "openai",
        "gpt-4-turbo": "openai", 
        "gpt-4-turbo-preview": "openai",
        "gpt-4-32k": "openai",
        "gpt-3.5-turbo": "openai",
        "gpt-3.5-turbo-16k": "openai",
        
        # Google models
        "gemini-1.5-flash": "gemini",
        "gemini-1.5-pro": "gemini",
        "gemini-2.0-flash": "gemini",
        "gemini-2.5-pro": "gemini",
        "gemini-2.5-flash": "gemini",
        "gemini-pro": "gemini", 
        "gemini-pro-vision": "gemini",
        "gemini-2.5-flash-image-preview": "gemini",
        "gemini-2.5-flash-image": "gemini",
        "g2.5-flash-image": "gemini",
        
        # Ollama models (common ones)
        "llama2": "ollama",
        "llama2:13b": "ollama",
        "llama2:70b": "ollama",
        "mistral": "ollama",
        "mixtral": "ollama",
        "codellama": "ollama",
        "neural-chat": "ollama",
        "starling-lm": "ollama",
        "yi": "ollama",
    }
    
    def __init__(self, model_manager: Optional[ModelManager] = None, use_secure_storage: bool = False):
        """
        Initialize the unified completion client
        
        Args:
            model_manager: Optional ModelManager instance. If not provided, creates a new one.
            use_secure_storage: Whether to use secure key storage if available.
        """
        self.model_manager = model_manager if model_manager is not None else ModelManager()
        self.use_secure_storage = use_secure_storage or os.environ.get("USE_SECURE_STORAGE", "false").lower() == "true"
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on environment and dependencies"""
        
        # TODO: When security module is complete, check for keys in secure storage
        # has_keys = False
        # if self.use_secure_storage:
        #     try:
        #         from .security import SecureKeyManager
        #         key_manager = SecureKeyManager()
        #         providers_with_keys = await key_manager.list_providers()
        #         has_keys = bool(providers_with_keys)
        #     except (ImportError, Exception):
        #         pass
        
        # Google/Gemini provider - check both GEMINI_API_KEY and GOOGLE_API_KEY
        if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
            try:
                self.providers["gemini"] = GoogleCompletions(use_secure_storage=self.use_secure_storage)
                logger.info(f"Initialized Gemini provider (secure storage: {self.use_secure_storage})")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini provider: {e}")
        
        # OpenAI provider  
        if os.environ.get("OPENAI_API_KEY"):
            try:
                self.providers["openai"] = OpenAICompletions(use_secure_storage=self.use_secure_storage)
                logger.info(f"Initialized OpenAI provider (secure storage: {self.use_secure_storage})")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI provider: {e}")
        
        # Ollama provider (always try to initialize for local models)
        try:
            self.providers["ollama"] = OllamaCompletions()
            logger.info("Initialized Ollama provider")
        except Exception as e:
            logger.warning(f"Could not initialize Ollama provider: {e}")
        
        # Also check if ModelManager has registered providers
        if self.model_manager and hasattr(self.model_manager, 'providers'):
            for provider_name, provider in self.model_manager.providers.items():
                if provider_name not in self.providers:
                    # Map ModelProvider instances to completion handlers
                    if provider_name == "gemini" and "gemini" not in self.providers:
                        self.providers["gemini"] = GoogleCompletions(use_secure_storage=self.use_secure_storage)
                        logger.info(f"Added Gemini provider from ModelManager")
                    elif provider_name == "openai" and "openai" not in self.providers:
                        self.providers["openai"] = OpenAICompletions(use_secure_storage=self.use_secure_storage)
                        logger.info(f"Added OpenAI provider from ModelManager")
                    elif provider_name == "ollama" and "ollama" not in self.providers:
                        self.providers["ollama"] = OllamaCompletions()
                        logger.info(f"Added Ollama provider from ModelManager")
        
        if not self.providers:
            logger.error("No providers available. Set API keys (GEMINI_API_KEY, OPENAI_API_KEY) or ensure Ollama is running.")
    
    def _get_provider_for_model(self, model: str) -> str:
        """Determine provider from model name"""
        
        # Check explicit mapping first
        if model in self.MODEL_PROVIDERS:
            return self.MODEL_PROVIDERS[model]
        
        # Pattern matching for unknown models
        model_lower = model.lower()
        
        if model_lower.startswith("gpt"):
            return "openai"
        elif "gemini" in model_lower:
            return "gemini"  
        elif model_lower.startswith("claude"):
            return "anthropic"  # For future support
        
        # Default to ollama for unknown models (might be local)
        return "ollama"
    
    async def _get_provider_from_model_manager(self, model: str) -> Optional[str]:
        """Try to get provider from model management system"""
        try:
            model_info = await self.model_manager.get_model_info(model)
            return model_info.provider if model_info else None
        except Exception as e:
            logger.debug(f"Could not get provider from model manager for {model}: {e}")
            return None
    
    async def create_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[str, Dict[str, Any]]] = None,
        system_instruction: Optional[str] = None,
        safety_settings: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion using the unified interface
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (e.g., 'gpt-4', 'gemini-1.5-flash', 'llama2')
            provider: Optional explicit provider name ('openai', 'gemini', 'ollama')
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            response_format: Response format ('text' or {'type': 'json_object'})
            system_instruction: System instruction for the model
            safety_settings: Safety settings (for Gemini)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Standardized completion response dictionary
        
        Raises:
            ValueError: If model/provider not available
            Exception: Provider-specific errors
        """
        
        # Determine provider
        if not provider:
            # Try model manager first for accurate detection
            provider = await self._get_provider_from_model_manager(model)
            
            # Fall back to pattern matching
            if not provider:
                provider = self._get_provider_for_model(model)
        
        # Ensure provider is available
        if provider not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(
                f"Provider '{provider}' not available for model '{model}'. "
                f"Available providers: {available}"
            )
        
        # Get the provider instance
        provider_instance = self.providers[provider]
        
        # Ensure model is available (for Ollama this may trigger download)
        if hasattr(self.model_manager, 'providers') and provider in [p.name for p in self.model_manager.providers.values()]:
            try:
                await self.model_manager.ensure_model_ready(model, provider)
            except Exception as e:
                logger.warning(f"Could not ensure model {model} is ready: {e}")
        
        # Handle system_instruction abstraction across providers
        processed_messages = messages.copy()
        provider_kwargs = kwargs.copy()
        
        if system_instruction:
            if provider in ["openai", "ollama"]:
                # For OpenAI and Ollama, prepend system message to messages array
                system_message = {"role": "system", "content": system_instruction}
                processed_messages = [system_message] + processed_messages
                # Don't pass system_instruction as a parameter
            elif provider == "gemini":
                # For Gemini, pass as system_instruction parameter
                provider_kwargs["system_instruction"] = system_instruction
            elif provider == "anthropic":
                # For Anthropic/Claude, use 'system' parameter
                provider_kwargs["system"] = system_instruction
            else:
                # For unknown providers, try passing as parameter
                provider_kwargs["system_instruction"] = system_instruction
                logger.info(f"Provider {provider} may not support system_instruction parameter")
        
        # Handle safety_settings (Gemini-specific)
        if safety_settings and provider == "gemini":
            provider_kwargs["safety_settings"] = safety_settings
        
        # Call the provider's create_completion method
        try:
            result = await provider_instance.create_completion(
                messages=processed_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                **provider_kwargs
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Completion error with {provider} provider for model {model}: {e}")
            raise
    
    async def list_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available models from all providers or a specific provider
        
        Args:
            provider: Optional provider name to filter by
            
        Returns:
            List of model information dictionaries
        """
        if provider:
            if provider not in self.providers:
                raise ValueError(f"Provider '{provider}' not available")
            
            # Use provider's list_models method (handle both sync and async)
            provider_instance = self.providers[provider]
            if hasattr(provider_instance, 'list_models'):
                import asyncio
                import inspect
                
                list_models_method = provider_instance.list_models
                if inspect.iscoroutinefunction(list_models_method):
                    # It's async, await it
                    models = await list_models_method()
                else:
                    # It's sync, call it directly
                    models = list_models_method()
            else:
                models = []
            
            return [{"id": model, "provider": provider} for model in models]
        
        # List from all providers via model manager
        try:
            model_infos = await self.model_manager.list_all_models()
            if model_infos:  # Only return if we actually got models
                return [
                    {
                        "id": model.id,
                        "name": model.name,
                        "provider": model.provider,
                        "context_limit": model.context_limit,
                        "capabilities": model.capabilities,
                        "status": model.status
                    }
                    for model in model_infos
                ]
        except Exception as e:
            logger.warning(f"Could not list models from model manager: {e}")
        
        # Fallback to provider-specific listings (also used when model_infos is empty)
        all_models = []
        for provider_name, provider_instance in self.providers.items():
            try:
                if hasattr(provider_instance, 'list_models'):
                    import inspect
                    
                    list_models_method = provider_instance.list_models
                    if inspect.iscoroutinefunction(list_models_method):
                        # It's async, await it
                        models = await list_models_method()
                    else:
                        # It's sync, call it directly
                        models = list_models_method()
                    
                    for model in models:
                        all_models.append({"id": model, "provider": provider_name})
            except Exception as e:
                logger.warning(f"Could not list models from {provider_name}: {e}")
        
        return all_models
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    async def find_best_model(self, requirements: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find the best model matching requirements using model management
        
        Args:
            requirements: Dictionary of requirements (e.g., {'multimodal': True, 'min_context_limit': 32000})
            
        Returns:
            Best matching model info or None
        """
        try:
            model_info = await self.model_manager.find_best_model(requirements)
            if model_info:
                return {
                    "id": model_info.id,
                    "name": model_info.name,
                    "provider": model_info.provider,
                    "context_limit": model_info.context_limit,
                    "capabilities": model_info.capabilities,
                    "status": model_info.status
                }
            return None
        except Exception as e:
            logger.error(f"Error finding best model: {e}")
            return None
