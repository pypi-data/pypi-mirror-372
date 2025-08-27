"""
XTrade-AI Dependency Injection Container

Provides dependency injection capabilities to reduce tight coupling.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type

try:
    from .logger import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


class ServiceLifetime(Enum):
    """Service lifetime enumeration."""

    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Single instance for lifetime
    SCOPED = "scoped"  # Single instance per scope


@dataclass
class ServiceRegistration:
    """Service registration information."""

    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON
    instance: Optional[Any] = None


class DependencyContainer:
    """Dependency injection container."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.services: Dict[str, ServiceRegistration] = {}
        self.singleton_instances: Dict[str, Any] = {}
        self.scoped_instances: Dict[str, Any] = {}
        self._current_scope: Optional[str] = None

    def register(
        self,
        service_name: str,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        factory: Optional[Callable] = None,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None:
        """
        Register a service in the container.

        Args:
            service_name: Name of the service
            service_type: Type of the service
            implementation_type: Implementation type (optional)
            factory: Factory function to create instances (optional)
            lifetime: Service lifetime
        """
        if service_name in self.services:
            self.logger.warning(
                f"Service {service_name} already registered, overwriting"
            )

        self.services[service_name] = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=lifetime,
        )

        self.logger.debug(f"Registered service: {service_name} ({lifetime.value})")

    def register_singleton(
        self,
        service_name: str,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        factory: Optional[Callable] = None,
    ) -> None:
        """Register a singleton service."""
        self.register(
            service_name,
            service_type,
            implementation_type,
            factory,
            ServiceLifetime.SINGLETON,
        )

    def register_transient(
        self,
        service_name: str,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        factory: Optional[Callable] = None,
    ) -> None:
        """Register a transient service."""
        self.register(
            service_name,
            service_type,
            implementation_type,
            factory,
            ServiceLifetime.TRANSIENT,
        )

    def register_scoped(
        self,
        service_name: str,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        factory: Optional[Callable] = None,
    ) -> None:
        """Register a scoped service."""
        self.register(
            service_name,
            service_type,
            implementation_type,
            factory,
            ServiceLifetime.SCOPED,
        )

    def get(self, service_name: str) -> Any:
        """
        Get a service instance.

        Args:
            service_name: Name of the service

        Returns:
            Service instance
        """
        if service_name not in self.services:
            raise KeyError(f"Service {service_name} not registered")

        registration = self.services[service_name]

        # Check if instance already exists based on lifetime
        if registration.lifetime == ServiceLifetime.SINGLETON:
            if service_name in self.singleton_instances:
                return self.singleton_instances[service_name]
        elif registration.lifetime == ServiceLifetime.SCOPED:
            if self._current_scope and service_name in self.scoped_instances:
                return self.scoped_instances[service_name]

        # Create new instance
        instance = self._create_instance(registration)

        # Store instance based on lifetime
        if registration.lifetime == ServiceLifetime.SINGLETON:
            self.singleton_instances[service_name] = instance
        elif registration.lifetime == ServiceLifetime.SCOPED and self._current_scope:
            self.scoped_instances[service_name] = instance

        return instance

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create a new instance of a service."""
        try:
            if registration.factory:
                # Use factory function
                return registration.factory()
            elif registration.implementation_type:
                # Use implementation type
                return registration.implementation_type()
            else:
                # Use service type directly
                return registration.service_type()
        except Exception as e:
            self.logger.error(
                f"Failed to create instance of {registration.service_type}: {e}"
            )
            raise

    def begin_scope(self, scope_name: str) -> "DependencyContainer":
        """Begin a new scope for scoped services."""
        scoped_container = DependencyContainer()
        scoped_container.services = self.services.copy()
        scoped_container.singleton_instances = self.singleton_instances.copy()
        scoped_container._current_scope = scope_name
        return scoped_container

    def end_scope(self) -> None:
        """End the current scope and clean up scoped instances."""
        self.scoped_instances.clear()
        self._current_scope = None

    def resolve_dependencies(self, target_type: Type, **kwargs) -> Any:
        """
        Resolve dependencies for a type.

        Args:
            target_type: Type to resolve dependencies for
            **kwargs: Additional parameters

        Returns:
            Instance with resolved dependencies
        """
        # This is a simplified version - in a full implementation,
        # you would use reflection to inspect constructor parameters
        # and automatically resolve dependencies

        try:
            return target_type(**kwargs)
        except Exception as e:
            self.logger.error(f"Failed to resolve dependencies for {target_type}: {e}")
            raise

    def get_registered_services(self) -> Dict[str, ServiceRegistration]:
        """Get all registered services."""
        return self.services.copy()

    def is_registered(self, service_name: str) -> bool:
        """Check if a service is registered."""
        return service_name in self.services

    def clear(self) -> None:
        """Clear all registrations and instances."""
        self.services.clear()
        self.singleton_instances.clear()
        self.scoped_instances.clear()
        self._current_scope = None
        self.logger.info("Dependency container cleared")


# Global dependency container instance
_container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return _container


def register_service(service_name: str, service_type: Type, **kwargs) -> None:
    """Convenience function for registering services."""
    _container.register(service_name, service_type, **kwargs)


def get_service(service_name: str) -> Any:
    """Convenience function for getting services."""
    return _container.get(service_name)


def begin_scope(scope_name: str) -> DependencyContainer:
    """Convenience function for beginning a scope."""
    return _container.begin_scope(scope_name)
