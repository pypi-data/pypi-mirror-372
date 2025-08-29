"""Cryptographic utilities for secure storage of API keys."""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoError(Exception):
    """Cryptographic operation errors."""
    pass


class CryptoManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self):
        self.key_file = Path.home() / ".memory-chatbot" / ".key"
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = None
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create a new one."""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                raise CryptoError(f"Failed to read encryption key: {e}")
        else:
            # Generate new key
            key = Fernet.generate_key()
            try:
                # Set restrictive permissions before writing
                self.key_file.touch(mode=0o600)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                return key
            except Exception as e:
                raise CryptoError(f"Failed to create encryption key: {e}")
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption."""
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded result."""
        try:
            fernet = self._get_fernet()
            encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('ascii')
        except Exception as e:
            raise CryptoError(f"Encryption failed: {e}")
    
    def decrypt(self, encrypted_b64: str) -> str:
        """Decrypt a base64 encoded encrypted string."""
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.b64decode(encrypted_b64.encode('ascii'))
            plaintext_bytes = fernet.decrypt(encrypted_bytes)
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise CryptoError(f"Decryption failed: {e}")
    
    def is_encrypted(self, data: str) -> bool:
        """Check if a string appears to be encrypted data."""
        try:
            # Try to decode as base64 and decrypt
            base64.b64decode(data.encode('ascii'))
            return True
        except:
            return False
    
    def rotate_key(self) -> None:
        """Generate a new encryption key (old data will be unreadable)."""
        try:
            if self.key_file.exists():
                # Backup old key
                backup_path = Path(str(self.key_file) + '.backup')
                self.key_file.rename(backup_path)
            
            # Generate new key
            self._fernet = None  # Reset instance
            self._get_or_create_key()
            
        except Exception as e:
            raise CryptoError(f"Key rotation failed: {e}")


class SecureStorage:
    """Secure storage for sensitive configuration data."""
    
    def __init__(self):
        self.crypto = CryptoManager()
    
    def store_api_key(self, provider: str, api_key: str) -> str:
        """Store an API key securely and return encrypted value."""
        if not api_key or not api_key.strip():
            raise CryptoError("API key cannot be empty")
        
        return self.crypto.encrypt(api_key.strip())
    
    def retrieve_api_key(self, encrypted_key: str) -> str:
        """Retrieve and decrypt an API key."""
        if not encrypted_key:
            raise CryptoError("Encrypted key cannot be empty")
        
        return self.crypto.decrypt(encrypted_key)
    
    def validate_api_key_format(self, provider: str, api_key: str) -> bool:
        """Validate API key format for different providers."""
        if not api_key or not api_key.strip():
            return False
        
        api_key = api_key.strip()
        
        if provider == 'openai':
            # OpenAI keys start with 'sk-' and are typically 51 characters
            return api_key.startswith('sk-') and len(api_key) >= 40
        
        elif provider == 'claude':
            # Anthropic keys start with 'sk-ant-' 
            return api_key.startswith('sk-ant-') and len(api_key) >= 40
        
        else:
            # Generic validation - just check it's not empty and has reasonable length
            return len(api_key) >= 10
    
    def get_masked_key(self, encrypted_key: str) -> str:
        """Get a masked version of the API key for display."""
        try:
            key = self.retrieve_api_key(encrypted_key)
            if len(key) > 8:
                return key[:4] + '*' * (len(key) - 8) + key[-4:]
            else:
                return '*' * len(key)
        except:
            return "***INVALID***"