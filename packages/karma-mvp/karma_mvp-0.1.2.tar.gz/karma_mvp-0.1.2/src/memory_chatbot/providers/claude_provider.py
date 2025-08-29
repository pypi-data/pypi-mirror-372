"""Anthropic Claude API provider implementation."""

import json
import httpx
from typing import List, Dict, Any, Optional, AsyncIterator, Tuple

from .base import LLMProvider, CompletionResponse, ModelLimits, LLMProviderError, ProviderRegistry


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    # Token limits for different models
    MODEL_LIMITS = {
        # Claude 3 Family
        'claude-3-haiku-20240307': {'max_tokens': 4096, 'context_window': 200000},
        'claude-3-sonnet-20240229': {'max_tokens': 4096, 'context_window': 200000},
        'claude-3-opus-20240229': {'max_tokens': 4096, 'context_window': 200000},
        
        # Claude 3.5 Family (latest)
        'claude-3-5-sonnet-20241022': {'max_tokens': 8192, 'context_window': 200000},
        'claude-3-5-sonnet-20240620': {'max_tokens': 8192, 'context_window': 200000},
        'claude-3-5-haiku-20241022': {'max_tokens': 8192, 'context_window': 200000},
        
        # Legacy model names (for compatibility)
        'claude-instant-1': {'max_tokens': 8192, 'context_window': 100000},
        'claude-2': {'max_tokens': 4096, 'context_window': 100000},
        'claude-2.1': {'max_tokens': 4096, 'context_window': 200000},
    }
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://api.anthropic.com/v1')
        self.timeout = kwargs.get('timeout', 60.0)
        self.version = kwargs.get('version', '2023-06-01')
        
        # Validate model
        if model not in self.MODEL_LIMITS:
            available_models = ', '.join(self.MODEL_LIMITS.keys())
            raise LLMProviderError(f"Unsupported model: {model}. Available: {available_models}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            'x-api-key': self.api_key,
            'anthropic-version': self.version,
            'Content-Type': 'application/json',
        }
    
    def _convert_messages_format(self, messages: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
        """
        Convert messages to Claude's format.
        
        Claude expects system message separately and alternating user/assistant messages.
        """
        system_message = ""
        conversation_messages = []
        
        # Extract system message
        for message in messages:
            if message['role'] == 'system':
                system_message += message['content'] + "\n"
            else:
                conversation_messages.append({
                    'role': message['role'],
                    'content': message['content']
                })
        
        # Ensure alternating user/assistant pattern
        formatted_messages = []
        last_role = None
        
        for message in conversation_messages:
            current_role = message['role']
            
            # If we have consecutive messages from the same role, combine them
            if last_role == current_role and formatted_messages:
                formatted_messages[-1]['content'] += f"\n\n{message['content']}"
            else:
                formatted_messages.append({
                    'role': current_role,
                    'content': message['content']
                })
                last_role = current_role
        
        # Ensure conversation starts with user message
        if formatted_messages and formatted_messages[0]['role'] != 'user':
            formatted_messages.insert(0, {
                'role': 'user',
                'content': '[Conversation context]'
            })
        
        return system_message.strip(), formatted_messages
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7, 
                            max_tokens: Optional[int] = None,
                            **kwargs) -> CompletionResponse:
        """Generate a chat completion response."""
        self.validate_messages(messages)
        
        # Convert message format for Claude
        system_message, claude_messages = self._convert_messages_format(messages)
        
        # Prepare request payload
        payload = {
            'model': self.model,
            'messages': claude_messages,
            'max_tokens': max_tokens or 2000,
            'temperature': temperature,
        }
        
        if system_message:
            payload['system'] = system_message
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
        
        except httpx.HTTPStatusError as e:
            error_msg = f"Claude API error ({e.response.status_code})"
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
            content = ""
            for content_block in data['content']:
                if content_block['type'] == 'text':
                    content += content_block['text']
            
            return CompletionResponse(
                content=content,
                tokens_used=data['usage']['input_tokens'] + data['usage']['output_tokens'],
                model=data['model'],
                finish_reason=data.get('stop_reason', 'stop'),
                metadata={
                    'input_tokens': data['usage']['input_tokens'],
                    'output_tokens': data['usage']['output_tokens'],
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
        
        # Convert message format for Claude
        system_message, claude_messages = self._convert_messages_format(messages)
        
        # Prepare request payload
        payload = {
            'model': self.model,
            'messages': claude_messages,
            'max_tokens': max_tokens or 2000,
            'temperature': temperature,
            'stream': True,
        }
        
        if system_message:
            payload['system'] = system_message
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    'POST',
                    f"{self.base_url}/messages",
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: ' prefix
                            
                            try:
                                data = json.loads(data_str)
                                
                                # Handle different event types
                                if data.get('type') == 'content_block_delta':
                                    delta = data.get('delta', {})
                                    if delta.get('type') == 'text_delta':
                                        text = delta.get('text', '')
                                        if text:
                                            yield text
                                            
                                elif data.get('type') == 'message_stop':
                                    break
                                    
                            except json.JSONDecodeError:
                                continue  # Skip invalid JSON lines
        
        except httpx.HTTPStatusError as e:
            error_msg = f"Claude API error ({e.response.status_code})"
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
        # Rough estimation: 1 token ≈ 3.5 characters for English text
        # Claude typically has slightly better tokenization than GPT models
        return max(1, len(text) * 10 // 35)
    
    def get_model_limits(self) -> ModelLimits:
        """Get model limitations and capabilities."""
        limits = self.MODEL_LIMITS.get(self.model, self.MODEL_LIMITS['claude-3-5-sonnet-20241022'])
        
        return ModelLimits(
            max_tokens=limits['max_tokens'],
            context_window=limits['context_window'],
            supports_streaming=True,
            supports_system_message=True
        )
    
    def get_supported_models(self) -> List[str]:
        """Get list of models supported by this provider."""
        return list(self.MODEL_LIMITS.keys())
    
    async def list_available_models(self) -> List[str]:
        """
        List available models from Claude API.
        Note: Claude doesn't provide a models endpoint, so we return supported models.
        """
        # Claude API doesn't have a public models endpoint like OpenAI
        # Return our known supported models
        return self.get_supported_models()
    
    async def validate_api_key(self) -> bool:
        """Validate that the API key is working."""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(test_messages, max_tokens=10)
            return True
        except LLMProviderError:
            return False


# Register the provider
ProviderRegistry.register('claude', ClaudeProvider)