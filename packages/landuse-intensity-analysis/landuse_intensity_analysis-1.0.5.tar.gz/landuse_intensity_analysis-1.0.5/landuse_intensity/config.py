"""
Configuration management for landuse-intensity-analysis.

This module provides declarative configuration management using Pydantic,
enabling robust validation, type safety, and automatic documentation
of configuration parameters.

Features:
- YAML/JSON configuration file support
- Automatic validation and type checking
- Configuration inheritance and merging
- Environment variable support
- Schema generation for documentation

Example:
    >>> from landuse_intensity.config import AnalysisConfig
    >>>
    >>> # Load from YAML file
    >>> config = AnalysisConfig.from_yaml("config.yaml")
    >>>
    >>> # Or create programmatically
    >>> config = AnalysisConfig(
    ...     pixel_resolution=30.0,
    ...     parallel=True,
    ...     output_dir="./results"
    ... )
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from pydantic import BaseModel, Field, validator, root_validator
    from pydantic import ValidationError as PydanticValidationError
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    # Fallback for when Pydantic is not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class Field:
        def __init__(self, default=None, **kwargs):
            self.default = default

    def validator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def root_validator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    class PydanticValidationError(Exception):
        pass


class ParallelizationConfig(BaseModel):
    """Configuration for parallel processing."""

    backend: str = Field(
        default="dask",
        description="Parallelization backend: 'dask', 'ray', or 'multiprocessing'"
    )
    n_workers: Optional[int] = Field(
        default=None,
        description="Number of worker processes (None = auto-detect)"
    )
    chunk_size: Union[str, int] = Field(
        default="auto",
        description="Chunk size for processing ('auto' or integer)"
    )
    memory_limit: Optional[str] = Field(
        default=None,
        description="Memory limit per worker (e.g., '2GB', '500MB')"
    )
    threads_per_worker: int = Field(
        default=1,
        description="Threads per worker process"
    )

    @validator('backend')
    def validate_backend(cls, v):
        valid_backends = ['dask', 'ray', 'multiprocessing', 'sequential']
        if v not in valid_backends:
            raise ValueError(f"Backend must be one of {valid_backends}")
        return v

    @validator('memory_limit')
    def validate_memory_limit(cls, v):
        if v is None:
            return v
        # Basic validation for memory format (e.g., "2GB", "500MB")
        import re
        if not re.match(r'^\d+(?:MB|GB|KB)$', v.upper()):
            raise ValueError("Memory limit must be in format like '2GB', '500MB', '100KB'")
        return v.upper()


class CacheConfig(BaseModel):
    """Configuration for caching system."""

    enabled: bool = Field(
        default=True,
        description="Enable caching system"
    )
    strategy: str = Field(
        default="smart",
        description="Cache strategy: 'smart', 'aggressive', 'conservative'"
    )
    max_memory: str = Field(
        default="1GB",
        description="Maximum memory for cache"
    )
    compression: str = Field(
        default="lz4",
        description="Compression algorithm for cached data"
    )
    ttl: str = Field(
        default="24h",
        description="Time-to-live for cached items"
    )
    auto_invalidate: bool = Field(
        default=True,
        description="Automatically invalidate stale cache entries"
    )
    cache_dir: Optional[str] = Field(
        default=None,
        description="Directory for disk cache (None = temp directory)"
    )

    @validator('strategy')
    def validate_strategy(cls, v):
        valid_strategies = ['smart', 'aggressive', 'conservative', 'disabled']
        if v not in valid_strategies:
            raise ValueError(f"Strategy must be one of {valid_strategies}")
        return v

    @validator('compression')
    def validate_compression(cls, v):
        valid_compressions = ['lz4', 'gzip', 'bz2', 'none']
        if v not in valid_compressions:
            raise ValueError(f"Compression must be one of {valid_compressions}")
        return v


class OutputConfig(BaseModel):
    """Configuration for output generation."""

    directory: str = Field(
        default="./analysis_output",
        description="Output directory for results"
    )
    formats: List[str] = Field(
        default=["png", "html"],
        description="Output formats for plots and reports"
    )
    generate_plots: bool = Field(
        default=True,
        description="Generate visualization plots"
    )
    generate_reports: bool = Field(
        default=True,
        description="Generate analysis reports"
    )
    overwrite_existing: bool = Field(
        default=False,
        description="Overwrite existing output files"
    )
    create_subdirs: bool = Field(
        default=True,
        description="Create subdirectories for different analysis types"
    )

    @validator('formats')
    def validate_formats(cls, v):
        valid_formats = ['png', 'jpg', 'svg', 'pdf', 'html', 'json', 'csv']
        invalid_formats = [fmt for fmt in v if fmt not in valid_formats]
        if invalid_formats:
            raise ValueError(f"Invalid formats: {invalid_formats}. Valid: {valid_formats}")
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging system."""

    level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    file: Optional[str] = Field(
        default=None,
        description="Log file path (None = console only)"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    max_file_size: str = Field(
        default="10MB",
        description="Maximum log file size before rotation"
    )
    backup_count: int = Field(
        default=5,
        description="Number of backup log files to keep"
    )

    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Level must be one of {valid_levels}")
        return v.upper()


class AnalysisConfig(BaseModel):
    """
    Main configuration class for landuse-intensity-analysis.

    This class defines all configuration parameters for the analysis system,
    with validation, documentation, and sensible defaults.
    """

    # Core analysis parameters
    pixel_resolution: float = Field(
        default=30.0,
        gt=0,
        description="Pixel spatial resolution in meters"
    )
    exclude_classes: List[int] = Field(
        default=[0],
        description="Land use classes to exclude from analysis (e.g., background)"
    )
    name_separator: str = Field(
        default="_",
        description="Separator used in raster filenames"
    )
    year_position: Union[str, int] = Field(
        default="last",
        description="Position of year in filename ('first', 'last', or integer index)"
    )

    # Processing options
    parallel: bool = Field(
        default=True,
        description="Enable parallel processing"
    )
    validate_data: bool = Field(
        default=True,
        description="Validate input data before analysis"
    )
    progress_bar: bool = Field(
        default=True,
        description="Show progress bars during analysis"
    )

    # Sub-configurations
    parallelization: ParallelizationConfig = Field(
        default_factory=ParallelizationConfig,
        description="Parallel processing configuration"
    )
    cache: CacheConfig = Field(
        default_factory=CacheConfig,
        description="Caching system configuration"
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="Output generation configuration"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging system configuration"
    )

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        arbitrary_types_allowed = True

    @root_validator(skip_on_failure=True)
    def validate_configuration(cls, values):
        """Validate overall configuration consistency."""
        parallel = values.get('parallel', True)
        parallelization = values.get('parallelization', ParallelizationConfig())

        # If parallel is False, ensure parallelization settings are consistent
        if not parallel and parallelization.backend != 'sequential':
            # Auto-correct to sequential if parallel=False
            values['parallelization'] = ParallelizationConfig(backend='sequential')

        return values

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'AnalysisConfig':
        """
        Load configuration from YAML file.

        Parameters
        ----------
        path : str or Path
            Path to YAML configuration file

        Returns
        -------
        AnalysisConfig
            Loaded and validated configuration

        Raises
        ------
        FileNotFoundError
            If configuration file doesn't exist
        ValueError
            If configuration is invalid
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML is required to load YAML configuration files")
        except Exception as e:
            raise ValueError(f"Failed to parse YAML file: {e}")

        try:
            return cls(**data)
        except PydanticValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> 'AnalysisConfig':
        """
        Load configuration from JSON file.

        Parameters
        ----------
        path : str or Path
            Path to JSON configuration file

        Returns
        -------
        AnalysisConfig
            Loaded and validated configuration
        """
        import json

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file: {e}")

        try:
            return cls(**data)
        except PydanticValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")

    @classmethod
    def from_env(cls, prefix: str = "LUIA_") -> 'AnalysisConfig':
        """
        Load configuration from environment variables.

        Parameters
        ----------
        prefix : str, default "LUIA_"
            Prefix for environment variable names

        Returns
        -------
        AnalysisConfig
            Configuration loaded from environment
        """
        import os

        env_data = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix):].lower()

                # Try to convert to appropriate type
                if value.lower() in ('true', 'false'):
                    env_data[config_key] = value.lower() == 'true'
                elif value.isdigit():
                    env_data[config_key] = int(value)
                elif value.replace('.', '').isdigit():
                    env_data[config_key] = float(value)
                else:
                    env_data[config_key] = value

        try:
            return cls(**env_data)
        except PydanticValidationError as e:
            raise ValueError(f"Invalid environment configuration: {e}")

    def to_yaml(self, path: Union[str, Path]) -> None:
        """
        Save configuration to YAML file.

        Parameters
        ----------
        path : str or Path
            Path to save YAML configuration
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required to save YAML configuration files")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.dict(), f, default_flow_style=False, sort_keys=False)

    def to_json(self, path: Union[str, Path]) -> None:
        """
        Save configuration to JSON file.

        Parameters
        ----------
        path : str or Path
            Path to save JSON configuration
        """
        import json

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2)

    def get_template(self) -> str:
        """
        Get a YAML configuration template with documentation.

        Returns
        -------
        str
            YAML template with comments and examples
        """
        template = f'''# LandUse Intensity Analysis Configuration Template
# Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Core analysis parameters
pixel_resolution: {self.pixel_resolution}  # Pixel resolution in meters
exclude_classes: {self.exclude_classes}    # Classes to exclude (e.g., background)
name_separator: "{self.name_separator}"    # Filename separator
year_position: "{self.year_position}"       # Year position in filename

# Processing options
parallel: {str(self.parallel).lower()}           # Enable parallel processing
validate_data: {str(self.validate_data).lower()} # Validate input data
progress_bar: {str(self.progress_bar).lower()}   # Show progress bars

# Parallelization settings
parallelization:
  backend: "{self.parallelization.backend}"           # dask, ray, multiprocessing, sequential
  n_workers: {self.parallelization.n_workers or 'null'} # Number of workers (null = auto)
  chunk_size: "{self.parallelization.chunk_size}"     # Chunk size or "auto"
  memory_limit: "{self.parallelization.memory_limit or 'null'}"  # Memory limit per worker
  threads_per_worker: {self.parallelization.threads_per_worker}

# Cache settings
cache:
  enabled: {str(self.cache.enabled).lower()}
  strategy: "{self.cache.strategy}"          # smart, aggressive, conservative, disabled
  max_memory: "{self.cache.max_memory}"      # Maximum cache memory
  compression: "{self.cache.compression}"    # Compression algorithm
  ttl: "{self.cache.ttl}"                    # Cache time-to-live
  auto_invalidate: {str(self.cache.auto_invalidate).lower()}
  cache_dir: {f'"{self.cache.cache_dir}"' if self.cache.cache_dir else 'null'}

# Output settings
output:
  directory: "{self.output.directory}"
  formats: {self.output.formats}
  generate_plots: {str(self.output.generate_plots).lower()}
  generate_reports: {str(self.output.generate_reports).lower()}
  overwrite_existing: {str(self.output.overwrite_existing).lower()}
  create_subdirs: {str(self.output.create_subdirs).lower()}

# Logging settings
logging:
  level: "{self.logging.level}"
  file: {f'"{self.logging.file}"' if self.logging.file else 'null'}
  format: "{self.logging.format}"
  max_file_size: "{self.logging.max_file_size}"
  backup_count: {self.logging.backup_count}
'''
        return template

    def validate_compatibility(self) -> List[str]:
        """
        Validate configuration compatibility and provide recommendations.

        Returns
        -------
        list of str
            List of validation messages and recommendations
        """
        messages = []

        # Check parallelization compatibility
        if self.parallel and self.parallelization.backend == 'sequential':
            messages.append("WARNING: Parallel processing enabled but backend is sequential")

        # Check cache settings
        if self.cache.enabled and self.cache.strategy == 'disabled':
            messages.append("WARNING: Cache enabled but strategy is disabled")

        # Check output directory
        if self.output.directory and not Path(self.output.directory).exists():
            messages.append(f"INFO: Output directory will be created: {self.output.directory}")

        # Memory recommendations
        if self.parallelization.memory_limit:
            # Parse memory limit
            import re
            match = re.match(r'(\d+)(MB|GB|KB)', self.parallelization.memory_limit.upper())
            if match:
                size, unit = match.groups()
                size = int(size)
                if unit == 'GB' and size > 8:
                    messages.append("WARNING: High memory limit per worker may cause issues")

        return messages


# Convenience functions
def load_config(path: Union[str, Path]) -> AnalysisConfig:
    """
    Load configuration from file (auto-detect format).

    Parameters
    ----------
    path : str or Path
        Path to configuration file (.yaml, .yml, or .json)

    Returns
    -------
    AnalysisConfig
        Loaded configuration
    """
    path = Path(path)

    if path.suffix.lower() in ['.yaml', '.yml']:
        return AnalysisConfig.from_yaml(path)
    elif path.suffix.lower() == '.json':
        return AnalysisConfig.from_json(path)
    else:
        raise ValueError(f"Unsupported configuration format: {path.suffix}")


def create_default_config() -> AnalysisConfig:
    """
    Create a default configuration instance.

    Returns
    -------
    AnalysisConfig
        Default configuration
    """
    return AnalysisConfig()


def get_config_template() -> str:
    """
    Get a configuration template.

    Returns
    -------
    str
        YAML configuration template
    """
    config = create_default_config()
    return config.get_template()
