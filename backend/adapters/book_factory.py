from typing import List, Dict, Any, Type
import os
import logging

from .base_adapter import BaseBookAdapter
from .draftkings_adapter import DraftKingsAdapter
from .fanduel_adapter import FanDuelAdapter

logger = logging.getLogger(__name__)

class BookAdapterFactory:
    """Factory for creating sportsbook adapters"""
    
    def __init__(self):
        self.adapters = {
            "DraftKings": DraftKingsAdapter,
            "FanDuel": FanDuelAdapter,
            # Add more adapters as needed
        }
        self.active_adapters = {}
    
    def get_adapter_class(self, book_name: str) -> Type[BaseBookAdapter]:
        """Get adapter class for a book"""
        if book_name not in self.adapters:
            raise ValueError(f"No adapter available for {book_name}")
        return self.adapters[book_name]
    
    async def get_adapters(self, book_names: List[str]) -> List[BaseBookAdapter]:
        """Get active adapters for specified books"""
        adapters = []
        
        for book_name in book_names:
            if book_name in self.active_adapters:
                adapters.append(self.active_adapters[book_name])
                continue
            
            try:
                adapter_class = self.get_adapter_class(book_name)
                adapter = adapter_class()
                
                # Authenticate
                if await adapter.authenticate():
                    self.active_adapters[book_name] = adapter
                    adapters.append(adapter)
                else:
                    logger.warning(f"Failed to authenticate with {book_name}")
                    
            except Exception as e:
                logger.error(f"Error creating adapter for {book_name}: {e}")
                continue
        
        return adapters
    
    async def cleanup(self):
        """Clean up all active adapters"""
        for adapter in self.active_adapters.values():
            await adapter.cleanup()
        self.active_adapters.clear()