"""
Configuration settings for fastapi-qengine.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .types import SecurityPolicy


@dataclass
class ParserConfig:
    """Configuration for the filter parser."""

    max_nesting_depth: int = 10
    strict_mode: bool = False  # Whether to be strict about unknown keys
    case_sensitive_operators: bool = True
    allow_empty_conditions: bool = False


@dataclass
class ValidatorConfig:
    """Configuration for the filter validator."""

    validate_types: bool = True
    validate_operators: bool = True
    validate_field_names: bool = True
    custom_validators: List[str] = field(default_factory=list)


@dataclass
class OptimizerConfig:
    """Configuration for the AST optimizer."""

    enabled: bool = True
    simplify_logical_operators: bool = True
    combine_range_conditions: bool = True
    remove_redundant_conditions: bool = True
    max_optimization_passes: int = 3


@dataclass
class CacheConfig:
    """Configuration for caching."""

    enabled: bool = False
    ttl_seconds: int = 300  # 5 minutes
    max_size: int = 1000
    cache_parsed_filters: bool = True
    cache_compiled_queries: bool = True


@dataclass
class QEngineConfig:
    """Main configuration for fastapi-qengine."""

    # Core settings
    default_backend: str = "beanie"
    debug: bool = False

    # Security
    security_policy: SecurityPolicy = field(default_factory=SecurityPolicy)

    # Component configurations
    parser: ParserConfig = field(default_factory=ParserConfig)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Backend-specific settings
    backend_settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def get_backend_setting(self, backend: str, key: str, default=None):
        """Get a backend-specific setting."""
        return self.backend_settings.get(backend, {}).get(key, default)

    def set_backend_setting(self, backend: str, key: str, value: Any):
        """Set a backend-specific setting."""
        if backend not in self.backend_settings:
            self.backend_settings[backend] = {}
        self.backend_settings[backend][key] = value


# Global default configuration instance
default_config = QEngineConfig()
