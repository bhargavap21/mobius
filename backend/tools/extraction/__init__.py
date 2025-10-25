"""
Data Extraction Pipeline
Multi-tier data extraction system with intelligent routing
"""

from .data_source_registry import DataSourceRegistry, get_registry

__all__ = ['DataSourceRegistry', 'get_registry']
