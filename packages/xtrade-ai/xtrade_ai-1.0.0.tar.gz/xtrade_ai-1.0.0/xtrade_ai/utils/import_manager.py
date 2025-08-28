"""
XTrade-AI Import Manager

Handles safe imports with proper error handling and fallback mechanisms.
"""

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from .logger import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


class ImportManager:
    """Manages safe imports with caching and fallback mechanisms."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.import_cache: Dict[str, Any] = {}
        self.failed_imports: Dict[str, str] = {}
        self.fallback_modules: Dict[str, str] = {}

    def safe_import(
        self,
        module_name: str,
        fallback_module: str = None,
        required_attributes: list = None,
    ) -> Any:
        """
        Safely import a module with fallback support.

        Args:
            module_name: Name of the module to import
            fallback_module: Fallback module name if primary fails
            required_attributes: List of required attributes in the module

        Returns:
            Imported module or None if all imports fail
        """
        # Check cache first
        if module_name in self.import_cache:
            return self.import_cache[module_name]

        # Try primary import
        try:
            module = importlib.import_module(module_name)

            # Validate required attributes
            if required_attributes:
                missing_attrs = [
                    attr for attr in required_attributes if not hasattr(module, attr)
                ]
                if missing_attrs:
                    raise ImportError(
                        f"Module {module_name} missing attributes: {missing_attrs}"
                    )

            self.import_cache[module_name] = module
            self.logger.debug(f"Successfully imported {module_name}")
            return module

        except ImportError as e:
            self.failed_imports[module_name] = str(e)
            self.logger.warning(f"Failed to import {module_name}: {e}")

            # Try fallback module
            if fallback_module and fallback_module != module_name:
                self.logger.info(f"Trying fallback module: {fallback_module}")
                return self.safe_import(
                    fallback_module, required_attributes=required_attributes
                )

            return None

    def import_class(
        self, module_name: str, class_name: str, fallback_module: str = None
    ) -> Optional[type]:
        """
        Import a specific class from a module.

        Args:
            module_name: Name of the module
            class_name: Name of the class to import
            fallback_module: Fallback module name

        Returns:
            Class type or None if import fails
        """
        module = self.safe_import(module_name, fallback_module)
        if module is None:
            return None

        try:
            return getattr(module, class_name)
        except AttributeError as e:
            self.logger.error(f"Class {class_name} not found in {module_name}: {e}")
            return None

    def register_fallback(self, primary_module: str, fallback_module: str):
        """Register a fallback module for a primary module."""
        self.fallback_modules[primary_module] = fallback_module
        self.logger.info(f"Registered fallback {fallback_module} for {primary_module}")

    def get_import_status(self) -> Dict[str, Any]:
        """Get status of all imports."""
        return {
            "cached_modules": list(self.import_cache.keys()),
            "failed_imports": self.failed_imports,
            "fallback_modules": self.fallback_modules,
        }

    def clear_cache(self):
        """Clear the import cache."""
        self.import_cache.clear()
        self.logger.info("Import cache cleared")


# Global import manager instance
_import_manager = ImportManager()


def get_import_manager() -> ImportManager:
    """Get the global import manager instance."""
    return _import_manager


def safe_import(
    module_name: str, fallback_module: str = None, required_attributes: list = None
) -> Any:
    """Convenience function for safe imports."""
    return _import_manager.safe_import(
        module_name, fallback_module, required_attributes
    )


def import_class(
    module_name: str, class_name: str, fallback_module: str = None
) -> Optional[type]:
    """Convenience function for importing classes."""
    return _import_manager.import_class(module_name, class_name, fallback_module)
