from sincpro_framework import ApplicationService as _ApplicationService
from sincpro_framework import DataTransferObject
from sincpro_framework import Feature as _Feature
from sincpro_framework import UseFramework

from .dependencies import DependencyContextType, register_dependencies


class Feature(_Feature, DependencyContextType):
    pass


class ApplicationService(_ApplicationService, DependencyContextType):
    pass


def config_framework(name: str) -> UseFramework:
    framework_instance = UseFramework(name)
    register_dependencies(framework_instance)
    return framework_instance


__all__ = ["config_framework", "Feature", "ApplicationService", "DataTransferObject"]
