"""Memory adapter factory for creating and managing memory adapters."""

from typing import Dict, Any, Optional, Type, Union, List
from enum import Enum
import logging

from .memory_adapter import MemoryAdapter, MemoryAdapterConfigError
from .legacy_memory_adapter import LegacyMemoryAdapter
from .mem0_memory_adapter import Mem0MemoryAdapter


class MemoryAdapterType(Enum):
    """Available memory adapter types."""
    LEGACY = "legacy"
    MEM0 = "mem0"


class MemoryAdapterFactory:
    """
    Factory class for creating and managing memory adapters.
    
    Handles adapter configuration, instantiation, and provides
    a unified interface for switching between different memory backends.
    """
    
    # Registry of available adapter types
    _adapters: Dict[MemoryAdapterType, Type[MemoryAdapter]] = {
        MemoryAdapterType.LEGACY: LegacyMemoryAdapter,
        MemoryAdapterType.MEM0: Mem0MemoryAdapter,
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._current_adapter: Optional[MemoryAdapter] = None
        self._current_type: Optional[MemoryAdapterType] = None
    
    @classmethod
    def create_adapter(cls, adapter_type: Union[str, MemoryAdapterType], 
                      config: Optional[Dict[str, Any]] = None) -> MemoryAdapter:
        """
        Create a memory adapter of the specified type.
        
        Args:
            adapter_type: Type of adapter to create
            config: Configuration for the adapter
            
        Returns:
            Configured memory adapter instance
            
        Raises:
            MemoryAdapterConfigError: If adapter type is invalid
        """
        # Convert string to enum if needed
        if isinstance(adapter_type, str):
            try:
                adapter_type = MemoryAdapterType(adapter_type.lower())
            except ValueError:
                valid_types = [t.value for t in MemoryAdapterType]
                raise MemoryAdapterConfigError(
                    f"Invalid adapter type: {adapter_type}. "
                    f"Valid types: {valid_types}"
                )
        
        if adapter_type not in cls._adapters:
            available_types = list(cls._adapters.keys())
            raise MemoryAdapterConfigError(
                f"Adapter type {adapter_type} not registered. "
                f"Available types: {available_types}"
            )
        
        adapter_class = cls._adapters[adapter_type]
        
        try:
            adapter = adapter_class(config or {})
            logging.getLogger(__name__).info(
                f"Created {adapter_type.value} memory adapter"
            )
            return adapter
        except Exception as e:
            raise MemoryAdapterConfigError(
                f"Failed to create {adapter_type.value} adapter: {e}"
            )
    
    def get_adapter(self, adapter_type: Union[str, MemoryAdapterType], 
                   config: Optional[Dict[str, Any]] = None, 
                   force_recreate: bool = False) -> MemoryAdapter:
        """
        Get a memory adapter, reusing existing instance if same type.
        
        Args:
            adapter_type: Type of adapter to get
            config: Configuration for the adapter
            force_recreate: Force creation of new adapter instance
            
        Returns:
            Memory adapter instance
        """
        # Convert string to enum if needed
        if isinstance(adapter_type, str):
            adapter_type = MemoryAdapterType(adapter_type.lower())
        
        # Return existing adapter if same type and not forcing recreation
        if (not force_recreate and 
            self._current_adapter and 
            self._current_type == adapter_type):
            return self._current_adapter
        
        # Create new adapter
        self._current_adapter = self.create_adapter(adapter_type, config)
        self._current_type = adapter_type
        
        return self._current_adapter
    
    def switch_adapter(self, new_type: Union[str, MemoryAdapterType], 
                      config: Optional[Dict[str, Any]] = None) -> MemoryAdapter:
        """
        Switch to a different adapter type.
        
        Args:
            new_type: New adapter type to switch to
            config: Configuration for the new adapter
            
        Returns:
            New adapter instance
        """
        old_type = self._current_type
        new_adapter = self.get_adapter(new_type, config, force_recreate=True)
        
        self.logger.info(f"Switched memory adapter from {old_type} to {new_type}")
        return new_adapter
    
    @property
    def current_adapter_type(self) -> Optional[MemoryAdapterType]:
        """Get the current adapter type."""
        return self._current_type
    
    @property
    def current_adapter(self) -> Optional[MemoryAdapter]:
        """Get the current adapter instance."""
        return self._current_adapter
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available adapter type names."""
        return [adapter_type.value for adapter_type in cls._adapters.keys()]
    
    @classmethod
    def register_adapter(cls, adapter_type: MemoryAdapterType, 
                        adapter_class: Type[MemoryAdapter]) -> None:
        """
        Register a new adapter type.
        
        Args:
            adapter_type: Type identifier for the adapter
            adapter_class: Adapter class to register
        """
        if not issubclass(adapter_class, MemoryAdapter):
            raise MemoryAdapterConfigError(
                f"Adapter class must inherit from MemoryAdapter"
            )
        
        cls._adapters[adapter_type] = adapter_class
        logging.getLogger(__name__).info(
            f"Registered adapter type: {adapter_type.value}"
        )
    
    def create_from_config(self, config: Dict[str, Any]) -> MemoryAdapter:
        """
        Create adapter from configuration dictionary.
        
        Expected config format:
        {
            "memory_adapter": {
                "type": "legacy" | "mem0",
                "config": {
                    # adapter-specific configuration
                }
            }
        }
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured memory adapter
        """
        adapter_config = config.get('memory_adapter', {})
        
        if not adapter_config:
            # Default to legacy adapter if no config specified
            self.logger.info("No memory adapter config found, defaulting to legacy")
            return self.get_adapter(MemoryAdapterType.LEGACY)
        
        adapter_type = adapter_config.get('type', 'legacy')
        adapter_settings = adapter_config.get('config', {})
        
        return self.get_adapter(adapter_type, adapter_settings)
    
    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all available adapter types.
        
        Returns:
            Health check results for each adapter type
        """
        results = {}
        
        for adapter_type in MemoryAdapterType:
            try:
                # Create temporary adapter for health check
                test_adapter = self.create_adapter(adapter_type, {})
                health = test_adapter.health_check()
                results[adapter_type.value] = health
                
            except Exception as e:
                results[adapter_type.value] = {
                    'status': 'error',
                    'error': str(e),
                    'available': False
                }
        
        return results


# Global factory instance
memory_adapter_factory = MemoryAdapterFactory()


def get_memory_adapter(adapter_type: Union[str, MemoryAdapterType] = "legacy", 
                      config: Optional[Dict[str, Any]] = None) -> MemoryAdapter:
    """
    Convenience function to get a memory adapter.
    
    Args:
        adapter_type: Type of adapter to create
        config: Configuration for the adapter
        
    Returns:
        Memory adapter instance
    """
    return memory_adapter_factory.get_adapter(adapter_type, config)


def create_memory_adapter_from_config(config: Dict[str, Any]) -> MemoryAdapter:
    """
    Convenience function to create adapter from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured memory adapter
    """
    return memory_adapter_factory.create_from_config(config)