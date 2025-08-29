"""OpenAI API provider implementation."""

import json
import httpx
from typing import List, Dict, Any, Optional, AsyncIterator
import asyncio

from .base import LLMProvider, CompletionResponse, ModelLimits, LLMProviderError, ProviderRegistry


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for GPT models."""
    
    # Token limits for different models
    MODEL_LIMITS = {
        # GPT-3.5 models
        'gpt-3.5-turbo': {'max_tokens': 4096, 'context_window': 16385},
        'gpt-3.5-turbo-16k': {'max_tokens': 16384, 'context_window': 16384},
        'gpt-3.5-turbo-instruct': {'max_tokens': 4096, 'context_window': 4096},
        
        # GPT-4 models
        'gpt-4': {'max_tokens': 8192, 'context_window': 8192},
        'gpt-4-32k': {'max_tokens': 32768, 'context_window': 32768},
        'gpt-4-turbo-preview': {'max_tokens': 128000, 'context_window': 128000},
        'gpt-4-turbo': {'max_tokens': 128000, 'context_window': 128000},
        'gpt-4-turbo-2024-04-09': {'max_tokens': 128000, 'context_window': 128000},
        
        # GPT-4o models  
        'gpt-4o': {'max_tokens': 128000, 'context_window': 128000},
        'gpt-4o-2024-08-06': {'max_tokens': 128000, 'context_window': 128000},
        'gpt-4o-mini': {'max_tokens': 128000, 'context_window': 128000},
        'gpt-4o-mini-2024-07-18': {'max_tokens': 128000, 'context_window': 128000},
        
        # GPT-4o1 models (latest reasoning models)
        'o1-preview': {'max_tokens': 32768, 'context_window': 128000},
        'o1-mini': {'max_tokens': 65536, 'context_window': 128000},
    }
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.openai.com/v1')
        self.organization = kwargs.get('organization')
        self.timeout = kwargs.get('timeout', 60.0)
        
        # Validate model - check MODEL_LIMITS first, then allow API validation
        self._model_validated_via_api = False
        if model not in self.MODEL_LIMITS:
            # Model not in predefined list - we'll validate it during first API call
            # Store a flag to indicate this model needs API validation
            self._model_validated_via_api = True
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'memory-chatbot/0.1.0',
        }
        
        if self.organization:
            headers['OpenAI-Organization'] = self.organization
            
        return headers
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7, 
                            max_tokens: Optional[int] = None,
                            **kwargs) -> CompletionResponse:
        """Generate a chat completion response."""
        self.validate_messages(messages)
        
        # Prepare request payload
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
        }
        
        if max_tokens:
            payload['max_tokens'] = max_tokens
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        try:
            # Configure client for custom APIs
            client_config = {
                'timeout': httpx.Timeout(self.timeout),
                'follow_redirects': True
            }
            if not self.base_url.startswith('https://api.openai.com'):
                client_config['verify'] = False
            
            async with httpx.AsyncClient(**client_config) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
        
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenAI API error ({e.response.status_code})"
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg += f": {error_data['error'].get('message', 'Unknown error')}"
            except:
                error_msg += f": {e.response.text}"
            raise LLMProviderError(error_msg)
        
        except httpx.RequestError as e:
            raise LLMProviderError(f"Request error: {e}")
        
        except json.JSONDecodeError as e:
            raise LLMProviderError(f"Invalid JSON response: {e}")
        
        # Parse response
        try:
            choice = data['choices'][0]
            return CompletionResponse(
                content=choice['message']['content'],
                tokens_used=data['usage']['total_tokens'],
                model=data['model'],
                finish_reason=choice.get('finish_reason', 'stop'),
                metadata={
                    'prompt_tokens': data['usage']['prompt_tokens'],
                    'completion_tokens': data['usage']['completion_tokens'],
                    'raw_response': data
                }
            )
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Unexpected response format: {e}")
    
    async def stream_completion(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.7, 
                              max_tokens: Optional[int] = None,
                              **kwargs) -> AsyncIterator[str]:
        """Generate a streaming chat completion response."""
        self.validate_messages(messages)
        
        # Prepare request payload
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'stream': True,
        }
        
        if max_tokens:
            payload['max_tokens'] = max_tokens
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        try:
            # Configure client for custom APIs
            client_config = {
                'timeout': httpx.Timeout(self.timeout),
                'follow_redirects': True
            }
            if not self.base_url.startswith('https://api.openai.com'):
                client_config['verify'] = False
            
            async with httpx.AsyncClient(**client_config) as client:
                async with client.stream(
                    'POST',
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            
                            if data_str == '[DONE]':
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and data['choices']:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue  # Skip invalid JSON lines
        
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenAI API error ({e.response.status_code})"
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg += f": {error_data['error'].get('message', 'Unknown error')}"
            except:
                error_msg += f": {e.response.text}"
            raise LLMProviderError(error_msg)
        
        except httpx.RequestError as e:
            raise LLMProviderError(f"Request error: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using rough estimation."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        # This is a simplified approach; for production, use tiktoken library
        return max(1, len(text) // 4)
    
    def get_model_limits(self) -> ModelLimits:
        """Get model limitations and capabilities."""
        if self.model in self.MODEL_LIMITS:
            limits = self.MODEL_LIMITS[self.model]
        else:
            # For models not in predefined list, use reasonable defaults
            # Most modern models have at least 4K context and 2K max tokens
            limits = {'max_tokens': 4096, 'context_window': 32000}
        
        return ModelLimits(
            max_tokens=limits['max_tokens'],
            context_window=limits['context_window'],
            supports_streaming=True,
            supports_system_message=True
        )
    
    async def validate_api_key(self) -> bool:
        """Validate that the API key is working."""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(test_messages, max_tokens=1)
            return True
        except LLMProviderError:
            return False
    
    def get_supported_models(self) -> List[str]:
        """Get list of models supported by this provider."""
        return list(self.MODEL_LIMITS.keys())
    
    async def list_available_models(self) -> List[str]:
        """List available models from OpenAI API."""
        try:
            # Configure client for custom APIs
            client_config = {
                'timeout': httpx.Timeout(self.timeout),
                'follow_redirects': True,
                'limits': httpx.Limits(max_keepalive_connections=5, max_connections=10)
            }
            
            # For custom APIs, disable SSL verification if needed
            if not self.base_url.startswith('https://api.openai.com'):
                client_config['verify'] = False
            
            async with httpx.AsyncClient(**client_config) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                # Filter for chat models
                chat_models = []
                
                # Check if data has expected structure
                if 'data' not in data:
                    # Some custom APIs might return different format
                    # Try to handle as direct list or other formats
                    if isinstance(data, list):
                        # Direct list of models
                        for model in data:
                            if isinstance(model, dict) and 'id' in model:
                                chat_models.append(model['id'])
                            elif isinstance(model, str):
                                chat_models.append(model)
                    else:
                        raise LLMProviderError(f"Unexpected API response format: {data}")
                    return sorted(chat_models)
                
                for model in data['data']:
                    if not isinstance(model, dict) or 'id' not in model:
                        continue  # Skip invalid model entries
                        
                    model_id = model['id']
                    
                    # For custom APIs, include all models instead of filtering
                    # This allows flexibility with different model naming conventions
                    if self.base_url != 'https://api.openai.com/v1':
                        # Custom API - include all models
                        chat_models.append(model_id)
                    else:
                        # Standard OpenAI API - filter for chat models
                        if any(model_id.startswith(prefix) for prefix in ['gpt-3.5', 'gpt-4', 'o1-']):
                            chat_models.append(model_id)
                return sorted(chat_models)
        
        except httpx.HTTPStatusError as e:
            error_msg = f"API error ({e.response.status_code})"
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg += f": {error_data['error'].get('message', 'Unknown error')}"
            except:
                error_msg += f": {e.response.text}"
            raise LLMProviderError(error_msg)
        
        except httpx.RequestError as e:
            raise LLMProviderError(f"Request error: {e}")
        
        except json.JSONDecodeError as e:
            raise LLMProviderError(f"Invalid JSON response: {e}")
        
        except Exception as e:
            raise LLMProviderError(f"Failed to list models: {str(e)}")
    
    async def list_models(self) -> List[str]:
        """Legacy method - use list_available_models instead."""
        return await self.list_available_models()


# Register the provider
ProviderRegistry.register('openai', OpenAIProvider)