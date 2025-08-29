"""
Configuration Management for Homodyne Scattering Analysis
=========================================================

Centralized configuration system for XPCS analysis under nonequilibrium conditions.
Provides JSON-based configuration management with validation, hierarchical parameter
organization, and performance optimization features.

Key Features:
- Hierarchical JSON configuration with validation
- Runtime parameter override capabilities
- Performance-optimized configuration access with caching
- Comprehensive logging system with rotation and formatting
- Physical parameter validation and bounds checking
- Angle filtering configuration for computational efficiency
- Test configuration management for different analysis scenarios

Configuration Structure:
- analyzer_parameters: Core physics parameters (q-vector, time steps, geometry)
- experimental_data: Data paths, file formats, and loading options
- analysis_settings: Mode selection (static vs laminar flow)
- optimization_config: Method settings, hyperparameters, angle filtering
- parameter_space: Physical bounds, priors, and parameter constraints
- performance_settings: Computational optimization flags

Authors: Wei Chen, Hongrui He
Institution: Argonne National Laboratory
"""

import gc
import json
import logging
import multiprocessing as mp
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, NotRequired, Optional, Tuple, TypedDict, Union, cast

# Default parallelization setting - balance performance and resource usage
# Limit to 16 threads to avoid overwhelming system resources while providing
# substantial speedup for computational kernels
DEFAULT_NUM_THREADS = min(16, mp.cpu_count())

# Module-level logger for configuration-related messages
logger = logging.getLogger(__name__)


# TypedDict definitions for strong typing of configuration structures
class LoggingConfig(TypedDict, total=False):
    """Typed configuration for logging system."""

    log_to_file: bool
    log_to_console: bool
    log_filename: str
    level: str
    format: str
    rotation: Dict[str, Union[int, str]]


class AngleRange(TypedDict):
    """Typed configuration for angle filtering ranges."""

    min_angle: float
    max_angle: float


class AngleFilteringConfig(TypedDict, total=False):
    """Typed configuration for angle filtering."""

    enabled: bool
    target_ranges: List[AngleRange]
    fallback_to_all_angles: bool


class OptimizationMethodConfig(TypedDict, total=False):
    """Typed configuration for optimization method parameters."""

    maxiter: int
    xatol: float
    fatol: float


class ClassicalOptimizationConfig(TypedDict, total=False):
    """Typed configuration for classical optimization methods."""

    methods: List[str]
    method_options: Dict[str, OptimizationMethodConfig]


class BayesianInferenceConfig(TypedDict, total=False):
    """Typed configuration for Bayesian MCMC inference."""

    mcmc_draws: int
    mcmc_tune: int


class OptimizationConfig(TypedDict, total=False):
    """Typed configuration for optimization settings."""

    angle_filtering: AngleFilteringConfig
    classical_optimization: ClassicalOptimizationConfig
    bayesian_inference: BayesianInferenceConfig


class ParameterBound(TypedDict):
    """Typed configuration for parameter bounds."""

    name: str
    min: float
    max: float
    type: str  # "uniform" or "log-uniform"


class ParameterSpaceConfig(TypedDict, total=False):
    """Typed configuration for parameter space definition."""

    bounds: List[ParameterBound]


class InitialParametersConfig(TypedDict, total=False):
    """Typed configuration for initial parameter values."""

    values: List[float]
    parameter_names: List[str]
    active_parameters: NotRequired[List[str]]


class AnalysisSettings(TypedDict, total=False):
    """Typed configuration for analysis mode settings."""

    static_mode: bool
    static_submode: NotRequired[str]  # "isotropic" or "anisotropic"
    model_description: Dict[str, str]


class ExperimentalDataConfig(TypedDict, total=False):
    """Typed configuration for experimental data paths."""

    data_folder_path: str
    data_file_name: str
    phi_angles_path: str
    phi_angles_file: str
    exchange_key: str
    cache_file_path: str
    cache_filename_template: str


def configure_logging(cfg: Dict[str, Any]) -> logging.Logger:
    """
    Configure centralized logging system with hierarchy and handlers.

    This function sets up a complete logging infrastructure:
    - Creates a logger hierarchy (root + module logger)
    - Sets up RotatingFileHandler with size-based rotation
    - Optionally creates StreamHandler for console output
    - Applies consistent formatting and log levels

    Parameters
    ----------
    cfg : dict
        Logging configuration dictionary with keys:
        - log_to_file: bool, enable file logging
        - log_to_console: bool, enable console logging
        - log_filename: str, log file path
        - level: str, logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        - format: str, log message format string
        - rotation: dict with 'max_bytes' and 'backup_count'

    Returns
    -------
    logging.Logger
        Configured logger instance for reuse
    """
    # Clear any existing handlers to avoid conflicts
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Get or create module logger
    module_logger = logging.getLogger(__name__)
    for handler in module_logger.handlers[:]:
        module_logger.removeHandler(handler)

    # Parse configuration
    log_level = getattr(logging, cfg.get("level", "INFO").upper(), logging.INFO)
    format_str = cfg.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter = logging.Formatter(format_str)

    # Set up root logger level
    root_logger.setLevel(log_level)
    module_logger.setLevel(log_level)

    # Suppress matplotlib font debug messages to reduce log noise
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

    handlers_created = []

    # File handler with rotation
    if cfg.get("log_to_file", False):
        filename = cfg.get("log_filename", "homodyne_analysis.log")
        rotation_config = cfg.get("rotation", {})
        max_bytes = rotation_config.get("max_bytes", 10 * 1024 * 1024)  # 10MB default
        backup_count = rotation_config.get("backup_count", 3)

        try:
            file_handler = RotatingFileHandler(
                filename=filename,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)

            # Add to both root and module logger
            root_logger.addHandler(file_handler)
            module_logger.addHandler(file_handler)
            handlers_created.append(
                f"RotatingFileHandler({filename}, {
                    max_bytes //
                    1024 //
                    1024}MB, {backup_count} backups)"
            )

        except (OSError, IOError) as e:
            logger.warning(f"Failed to create file handler: {e}")
            logger.info("Continuing with console logging only...")

    # Console handler
    if cfg.get("log_to_console", False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Add to both root and module logger
        root_logger.addHandler(console_handler)
        module_logger.addHandler(console_handler)
        handlers_created.append("StreamHandler(console)")

    # Prevent propagation to avoid duplicate messages
    module_logger.propagate = False

    if handlers_created:
        handler_list = ", ".join(handlers_created)
        logger.info(
            f"Logging configured: {handler_list} (level={
                cfg.get(
                    'level',
                    'INFO')})"
        )

        # Log initial message to verify setup
        module_logger.info(f"Logging system initialized: {handler_list}")
        module_logger.debug(f"Logger hierarchy: root -> {__name__}")
    else:
        logger.info("No logging handlers configured")

    return module_logger


class ConfigManager:
    """
    Centralized configuration manager for homodyne scattering analysis.

    This class orchestrates the entire configuration system for XPCS analysis,
    providing structured access to all analysis parameters with validation,
    caching, and runtime override capabilities.

    Core Responsibilities:
    - JSON configuration file loading with comprehensive error handling
    - Hierarchical parameter validation (physics, computation, file paths)
    - Performance-optimized configuration access through intelligent caching
    - Runtime configuration overrides for analysis mode switching
    - Logging system setup with rotation and appropriate formatting
    - Test configuration management for different experimental scenarios

    Configuration Hierarchy:
    - analyzer_parameters: Physics parameters (q-vector, time steps, gap size)
    - experimental_data: Data file paths, loading options, caching settings
    - analysis_settings: Mode selection (static/laminar flow), model descriptions
    - optimization_config: Method settings, angle filtering, hyperparameters
    - parameter_space: Physical parameter bounds, prior distributions
    - performance_settings: Parallelization, computational optimizations
    - validation_rules: Data quality checks and minimum requirements
    - advanced_settings: Fine-tuning options for specialized use cases

    Usage:
        config_manager = ConfigManager('my_config.json')
        is_static = config_manager.is_static_mode_enabled()
        angle_ranges = config_manager.get_target_angle_ranges()
    """

    def __init__(self, config_file: str = "homodyne_config.json"):
        """
        Initialize configuration manager.

        Parameters
        ----------
        config_file : str
            Path to JSON configuration file
        """
        self.config_file = config_file
        self.config: Optional[Dict[str, Any]] = None
        self._cached_values: Dict[str, Any] = {}
        self.load_config()
        self.validate_config()
        self.setup_logging()

    def load_config(self) -> None:
        """
        Load and parse JSON configuration file with comprehensive error handling.

        Implements performance-optimized loading with buffering, structure
        optimization for runtime access, and graceful fallback to default
        configuration if primary config fails.

        Error Handling:
        - FileNotFoundError: Missing configuration file
        - JSONDecodeError: Malformed JSON syntax
        - General exceptions: Unexpected loading issues

        Performance Optimizations:
        - 8KB buffering for efficient file I/O
        - Configuration structure caching for fast access
        - Timing instrumentation for performance monitoring
        """
        with performance_monitor.time_function("config_loading"):
            try:
                if self.config_file is None:
                    raise ValueError("Configuration file path cannot be None")

                config_path = Path(self.config_file)
                if not config_path.exists():
                    raise FileNotFoundError(
                        f"Configuration file not found: {self.config_file}"
                    )

                # Optimized JSON loading with memory pre-allocation hints
                with open(config_path, "r", buffering=8192) as f:
                    self.config = json.load(f)

                # Optimize configuration structure for faster runtime access
                self._optimize_config_structure()

                logger.info(f"Configuration loaded from: {self.config_file}")

                # Display version information if available
                if isinstance(self.config, dict) and "metadata" in self.config:
                    version = self.config["metadata"].get("config_version", "Unknown")
                    logger.info(f"Configuration version: {version}")

            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.info("Using default configuration...")
                self.config = self._get_default_config()
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                logger.exception("Full traceback for configuration loading failure:")
                logger.info("Using default configuration...")
                self.config = self._get_default_config()

    def _optimize_config_structure(self) -> None:
        """
        Pre-compute and cache frequently accessed configuration values.

        This optimization reduces repeated nested dictionary lookups during
        analysis runtime, particularly for values accessed in tight loops
        such as angle filtering settings and parameter bounds.

        Cached Values:
        - angle_filtering_enabled: Boolean flag for optimization filtering
        - target_angle_ranges: Pre-parsed angle ranges for filtering
        - static_mode: Analysis mode flag (static vs laminar flow)
        - parameter_bounds: Parameter constraints for validation
        - effective_param_count: Number of active parameters (3 or 7)
        """
        if not self.config:
            return

        # Initialize cache dictionary for performance-critical values (already
        # initialized in __init__)

        # Cache optimization config paths
        if "optimization_config" in self.config:
            opt_config = self.config["optimization_config"]
            self._cached_values["angle_filtering_enabled"] = opt_config.get(
                "angle_filtering", {}
            ).get("enabled", True)
            self._cached_values["target_angle_ranges"] = opt_config.get(
                "angle_filtering", {}
            ).get("target_ranges", [])

        # Cache analysis settings
        if "analysis_settings" in self.config:
            analysis = self.config["analysis_settings"]
            self._cached_values["static_mode"] = analysis.get("static_mode", False)

            # Cache static submode if static mode is enabled
            if self._cached_values["static_mode"]:
                raw_submode = analysis.get("static_submode", "anisotropic")
                if raw_submode is None:
                    submode = "anisotropic"
                else:
                    submode_str = str(raw_submode).lower().strip()
                    if submode_str in ["isotropic", "iso"]:
                        submode = "isotropic"
                    elif submode_str in ["anisotropic", "aniso"]:
                        submode = "anisotropic"
                    else:
                        submode = "anisotropic"
                self._cached_values["static_submode"] = submode
            else:
                self._cached_values["static_submode"] = None

        # Cache parameter bounds for faster access
        if "parameter_space" in self.config:
            bounds = self.config["parameter_space"].get("bounds", [])
            self._cached_values["parameter_bounds"] = bounds

        # Pre-compute effective parameter count
        self._cached_values["effective_param_count"] = (
            3 if self._cached_values.get("static_mode", False) else 7
        )

    def validate_config(self) -> None:
        """
        Comprehensive validation of configuration parameters.

        Performs multi-level validation to ensure configuration integrity:

        Structural Validation:
        - Required sections presence (analyzer_parameters, experimental_data, etc.)
        - Configuration hierarchy completeness
        - Parameter type consistency

        Physical Parameter Validation:
        - Frame range consistency (start < end, sufficient frames)
        - Wavevector positivity and reasonable magnitude
        - Time step positivity
        - Gap size physical reasonableness

        Data Validation:
        - Minimum frame count requirements
        - Parameter bounds consistency
        - File path accessibility (optional)

        Raises
        ------
        ValueError
            Invalid configuration parameters or structure
        FileNotFoundError
            Missing required data files (if validation enabled)
        """
        if not self.config:
            raise ValueError("Configuration is None")

        # Check required sections
        required_sections = [
            "analyzer_parameters",
            "experimental_data",
            "optimization_config",
        ]
        missing = [s for s in required_sections if s not in self.config]
        if missing:
            raise ValueError(f"Missing required sections: {missing}")

        # Validate frame range
        analyzer = self.config["analyzer_parameters"]
        start = analyzer.get("start_frame", 1)
        end = analyzer.get("end_frame", 100)

        if start >= end:
            raise ValueError(f"Invalid frame range: {start} >= {end}")

        # Check minimum frame count
        min_frames = (
            self.config.get("validation_rules", {})
            .get("frame_range", {})
            .get("minimum_frames", 10)
        )
        if end - start < min_frames:
            raise ValueError(
                f"Insufficient frames: {
                    end - start} < {min_frames}"
            )

        # Validate physical parameters
        self._validate_physical_parameters()

        logger.info(
            f"Configuration validated: frames {start}-{end} ({
                end - start} frames)"
        )

    def _validate_physical_parameters(self) -> None:
        """
        Validate physical parameters for scientific and computational validity.

        Performs detailed validation of core physics parameters to ensure
        they fall within physically meaningful and computationally stable ranges.

        Parameter Checks:
        - Wavevector q: Must be positive, warns if outside typical XPCS range
        - Time step dt: Must be positive for temporal evolution
        - Gap size h: Must be positive for rheometer geometry

        Typical Parameter Ranges:
        - q-vector: 0.001-0.1 Å⁻¹ (typical XPCS range)
        - Time step: 0.01-10 s (depending on dynamics)
        - Gap size: μm-mm range (rheometer geometry)

        Raises
        ------
        ValueError
            Invalid parameter values that would cause computation failure
        """
        if self.config is None or "analyzer_parameters" not in self.config:
            raise ValueError(
                "Configuration or 'analyzer_parameters' section is missing."
            )

        params = self.config["analyzer_parameters"]

        # Wavevector validation
        q = params.get("wavevector_q", 0.0054)
        if q <= 0:
            raise ValueError(f"Wavevector must be positive: {q}")
        if q > 1.0:
            logger.warning(f"Large wavevector: {q} Å⁻¹ (typical: 0.001-0.1)")

        # Time step validation
        dt = params.get("dt", 0.1)
        if dt <= 0:
            raise ValueError(f"Time step must be positive: {dt}")

        # Gap size validation
        h = params.get("stator_rotor_gap", 2000000)
        if h <= 0:
            raise ValueError(f"Gap size must be positive: {h}")

    def setup_logging(self) -> Optional[logging.Logger]:
        """Configure logging based on configuration using centralized configure_logging()."""
        if self.config is None:
            logger.warning("Configuration is None, skipping logging setup.")
            return None

        log_config = self.config.get("logging", {})

        # Skip logging setup if neither file nor console logging is enabled
        if not log_config.get("log_to_file", False) and not log_config.get(
            "log_to_console", False
        ):
            return None

        # Use the centralized configure_logging function
        try:
            configured_logger = configure_logging(log_config)
            return configured_logger
        except Exception as e:
            logger.warning(f"Failed to configure logging: {e}")
            logger.exception("Full traceback for logging configuration failure:")
            logger.info("Continuing without logging...")
            return None

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get nested configuration value.

        Parameters
        ----------
        *keys : str
            Sequence of nested keys
        default : any
            Default value if key not found

        Returns
        -------
        Configuration value or default
        """
        try:
            value = self.config
            for key in keys:
                if value is None or not isinstance(value, dict):
                    return default
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_angle_filtering_config(self) -> Dict[str, Any]:
        """
        Get angle filtering configuration with defaults.

        Returns
        -------
        dict
            Angle filtering configuration including:
            - enabled: bool, whether angle filtering is enabled
            - target_ranges: list of dicts with min_angle and max_angle
            - fallback_to_all_angles: bool, whether to use all angles if no targets found
        """
        angle_filtering = self.get("optimization_config", "angle_filtering", default={})

        # Ensure angle_filtering is a dictionary for unpacking
        if not isinstance(angle_filtering, dict):
            angle_filtering = {}

        # Provide sensible defaults if configuration is missing or incomplete
        default_config = {
            "enabled": True,
            "target_ranges": [
                {"min_angle": -10.0, "max_angle": 10.0},
                {"min_angle": 170.0, "max_angle": 190.0},
            ],
            "fallback_to_all_angles": True,
        }

        # Merge with defaults
        result = {**default_config, **angle_filtering}

        # Validate target_ranges structure
        if "target_ranges" in result:
            valid_ranges = []
            for range_config in result["target_ranges"]:
                if (
                    isinstance(range_config, dict)
                    and "min_angle" in range_config
                    and "max_angle" in range_config
                ):
                    valid_ranges.append(
                        {
                            "min_angle": float(range_config["min_angle"]),
                            "max_angle": float(range_config["max_angle"]),
                        }
                    )
                else:
                    logger.warning(f"Invalid angle range configuration: {range_config}")
            result["target_ranges"] = valid_ranges

        return result

    def is_angle_filtering_enabled(self) -> bool:
        """
        Check if angle filtering is enabled in configuration.

        Automatically returns False for static isotropic mode, regardless of
        configuration setting.

        Returns
        -------
        bool
            True if angle filtering should be used, False otherwise
        """
        # Always disable angle filtering for static isotropic mode
        if self.is_static_isotropic_enabled():
            # Warn if user explicitly enabled angle filtering but it's ignored
            explicit_enabled = self.get_angle_filtering_config().get("enabled", True)
            if explicit_enabled:
                logger.debug(
                    "Angle filtering disabled for static isotropic mode "
                    "(ignoring configuration setting)"
                )
            return False

        return bool(self.get_angle_filtering_config().get("enabled", True))

    def get_target_angle_ranges(self) -> List[Tuple[float, float]]:
        """
        Get list of target angle ranges for optimization.

        Returns
        -------
        list of tuple
            List of (min_angle, max_angle) tuples in degrees
        """
        config = self.get_angle_filtering_config()
        ranges = config.get("target_ranges", [])

        return [(r["min_angle"], r["max_angle"]) for r in ranges]

    def should_fallback_to_all_angles(self) -> bool:
        """
        Check if system should fallback to all angles when no targets found.

        Returns
        -------
        bool
            True if should fallback to all angles, False to raise error
        """
        return bool(
            self.get_angle_filtering_config().get("fallback_to_all_angles", True)
        )

    def is_static_mode_enabled(self) -> bool:
        """
        Check if static mode is enabled in configuration.

        Returns
        -------
        bool
            True if static mode is enabled, False otherwise
        """
        # Use cached value for performance
        if hasattr(self, "_cached_values") and "static_mode" in self._cached_values:
            return bool(self._cached_values["static_mode"])

        result = self.get("analysis_settings", "static_mode", default=False)
        return bool(result)

    def get_static_submode(self) -> Optional[str]:
        """
        Get the static sub-mode for analysis.

        Returns
        -------
        Optional[str]
            "isotropic", "anisotropic", or None if static mode is disabled
        """
        # Return None if static mode is not enabled
        if not self.is_static_mode_enabled():
            return None

        # Use cached value for performance
        if hasattr(self, "_cached_values") and "static_submode" in self._cached_values:
            cached_value = self._cached_values["static_submode"]
            return str(cached_value) if cached_value is not None else None

        # Get submode from configuration (case-insensitive)
        raw_submode = self.get(
            "analysis_settings", "static_submode", default="anisotropic"
        )
        if raw_submode is None:
            submode = "anisotropic"  # Default for backward compatibility
        else:
            submode_str = str(raw_submode).lower().strip()
            if submode_str in ["isotropic", "iso"]:
                submode = "isotropic"
            elif submode_str in ["anisotropic", "aniso"]:
                submode = "anisotropic"
            else:
                logger.warning(
                    f"Invalid static_submode '{raw_submode}', defaulting to 'anisotropic'"
                )
                submode = "anisotropic"

        return submode

    def is_static_isotropic_enabled(self) -> bool:
        """
        Check if static isotropic mode is enabled.

        Returns
        -------
        bool
            True if analysis mode is static isotropic, False otherwise
        """
        return (
            self.is_static_mode_enabled() and self.get_static_submode() == "isotropic"
        )

    def is_static_anisotropic_enabled(self) -> bool:
        """
        Check if static anisotropic mode is enabled.

        Returns
        -------
        bool
            True if analysis mode is static anisotropic, False otherwise
        """
        return (
            self.is_static_mode_enabled() and self.get_static_submode() == "anisotropic"
        )

    def get_analysis_mode(self) -> str:
        """
        Get the current analysis mode.

        Returns
        -------
        str
            "static_isotropic", "static_anisotropic", or "laminar_flow"
        """
        if not self.is_static_mode_enabled():
            return "laminar_flow"

        submode = self.get_static_submode()
        if submode == "isotropic":
            return "static_isotropic"
        else:
            return "static_anisotropic"

    def get_active_parameters(self) -> List[str]:
        """
        Get list of active parameters from configuration.

        Returns
        -------
        List[str]
            List of parameter names to be optimized and displayed in plots.
            Falls back to all parameters if not specified in configuration.
        """
        initial_params = self.get("initial_parameters", default={})
        active_params = cast(List[str], initial_params.get("active_parameters", []))

        # If no active_parameters specified, use all parameter names
        if not active_params:
            param_names = cast(List[str], initial_params.get("parameter_names", []))
            if param_names:
                active_params = param_names
            else:
                # Ultimate fallback to standard parameter names
                active_params = [
                    "D0",
                    "alpha",
                    "D_offset",
                    "gamma_dot_t0",
                    "beta",
                    "gamma_dot_t_offset",
                    "phi0",
                ]

        return active_params

    def get_effective_parameter_count(self) -> int:
        """
        Get the effective number of model parameters based on active_parameters configuration.

        Returns
        -------
        int
            Number of parameters used in the analysis based on active_parameters.
            Falls back to mode-based logic if active_parameters not specified:
            - Static mode: 3 (only diffusion parameters)
            - Laminar flow mode: 7 (all parameters)
        """
        # Use cached value for performance
        if (
            hasattr(self, "_cached_values")
            and "effective_param_count" in self._cached_values
        ):
            return int(self._cached_values["effective_param_count"])

        # Get active parameters from configuration
        active_params = self.get_active_parameters()

        # Use active_parameters if specified, otherwise fall back to mode-based
        # logic
        if active_params:
            count = len(active_params)
        else:
            count = 3 if self.is_static_mode_enabled() else 7

        # Cache the result for performance
        if not hasattr(self, "_cached_values"):
            self._cached_values = {}
        self._cached_values["effective_param_count"] = count

        return count

    def get_analysis_settings(self) -> Dict[str, Any]:
        """
        Get analysis settings with defaults.

        Returns
        -------
        Dict[str, Any]
            Analysis settings including static_mode flag and descriptions
        """
        analysis_settings = self.get("analysis_settings", default={})

        # Ensure analysis_settings is a dictionary for type safety
        if not isinstance(analysis_settings, dict):
            analysis_settings = {}

        # Provide sensible defaults
        default_settings = {
            "static_mode": False,
            "model_description": {
                "static_case": (
                    "g₁(t₁,t₂) = exp(-q² ∫ᵗ²ᵗ¹ D(t)dt) = g₁_diff(t₁,t₂), g₂(t₁,t₂) = [g₁(t₁,t₂)]²"
                ),
                "laminar_flow_case": (
                    "g₁(t₁,t₂) = g₁_diff(t₁,t₂) × g₁_shear(t₁,t₂) where g₁_shear = [sinc(Φ)]² and Φ = (1/2π)qL cos(φ₀-φ) ∫|t₂-t₁| γ̇(t')dt'"
                ),
            },
        }

        # Merge with defaults
        result = {**default_settings, **analysis_settings}
        return result

    def _get_default_config(self) -> Dict[str, Any]:
        """Generate minimal default configuration."""
        return {
            "metadata": {
                "config_version": "5.1-default",
                "description": "Emergency fallback configuration",
            },
            "analyzer_parameters": {
                "temporal": {
                    "dt": 0.1,
                    "start_frame": 1001,
                    "end_frame": 2000,
                },
                "scattering": {"wavevector_q": 0.0054},
                "geometry": {"stator_rotor_gap": 2000000},
                "computational": {
                    "num_threads": DEFAULT_NUM_THREADS,
                    "auto_detect_cores": False,
                    "max_threads_limit": 128,
                },
            },
            "experimental_data": {
                "data_folder_path": "./data/C020/",
                "data_file_name": "default_data.hdf",
                "phi_angles_path": "./data/C020/",
                "phi_angles_file": "phi_list.txt",
                "exchange_key": "exchange",
                "cache_file_path": ".",
                "cache_filename_template": (
                    "cached_c2_frames_{start_frame}_{end_frame}.npz"
                ),
            },
            "analysis_settings": {
                "static_mode": False,
                "model_description": {
                    "static_case": (
                        "g₁(t₁,t₂) = exp(-q² ∫ᵗ²ᵗ¹ D(t)dt) = g₁_diff(t₁,t₂), g₂(t₁,t₂) = [g₁(t₁,t₂)]²"
                    ),
                    "laminar_flow_case": (
                        "g₁(t₁,t₂) = g₁_diff(t₁,t₂) × g₁_shear(t₁,t₂) where g₁_shear = [sinc(Φ)]² and Φ = (1/2π)qL cos(φ₀-φ) ∫|t₂-t₁| γ̇(t')dt'"
                    ),
                },
            },
            "initial_parameters": {
                "values": [1324.1, -0.014, -0.674361, 0.003, -0.909, 0.0, 0.0],
                "parameter_names": [
                    "D0",
                    "alpha",
                    "D_offset",
                    "gamma_dot_t0",
                    "beta",
                    "gamma_dot_t_offset",
                    "phi0",
                ],
            },
            "optimization_config": {
                "angle_filtering": {
                    "enabled": True,
                    "target_ranges": [
                        {"min_angle": -10.0, "max_angle": 10.0},
                        {"min_angle": 170.0, "max_angle": 190.0},
                    ],
                    "fallback_to_all_angles": True,
                },
                "classical_optimization": {
                    "methods": ["Nelder-Mead"],
                    "method_options": {
                        "Nelder-Mead": {
                            "maxiter": 5000,
                            "xatol": 1e-8,
                            "fatol": 1e-8,
                        }
                    },
                },
                "bayesian_inference": {"mcmc_draws": 1000, "mcmc_tune": 500},
            },
            "parameter_space": {
                "bounds": [
                    {
                        "name": "D0",
                        "min": 1.0,
                        "max": 1e6,
                        "type": "Normal",
                    },
                    {
                        "name": "alpha",
                        "min": -2.0,
                        "max": 2.0,
                        "type": "Normal",
                    },
                    {
                        "name": "D_offset",
                        "min": -100,
                        "max": 100,
                        "type": "Normal",
                    },
                    {
                        "name": "gamma_dot_t0",
                        "min": 1e-6,
                        "max": 1.0,
                        "type": "Normal",
                    },
                    {
                        "name": "beta",
                        "min": -2.0,
                        "max": 2.0,
                        "type": "Normal",
                    },
                    {
                        "name": "gamma_dot_t_offset",
                        "min": -1e-2,
                        "max": 1e-2,
                        "type": "Normal",
                    },
                    {
                        "name": "phi0",
                        "min": -10.0,
                        "max": 10.0,
                        "type": "Normal",
                    },
                ]
            },
            "validation_rules": {"frame_range": {"minimum_frames": 10}},
            "performance_settings": {
                "parallel_execution": True,
                "use_threading": True,
                "optimization_counter_log_frequency": 100,
            },
            "advanced_settings": {
                "data_loading": {
                    "use_diagonal_correction": True,
                    "vectorized_diagonal_fix": True,
                },
                "chi_squared_calculation": {
                    "_scaling_optimization_note": "Scaling optimization is always enabled: g₂ = offset + contrast × g₁",
                    "uncertainty_estimation_factor": 0.1,
                    "minimum_sigma": 1e-10,
                    "validity_check": {
                        "check_positive_D0": True,
                        "check_positive_gamma_dot_t0": True,
                        "check_positive_time_dependent": True,
                        "check_parameter_bounds": True,
                    },
                },
            },
            "test_configurations": {
                "production": {
                    "description": "Standard production configuration",
                    "classical_methods": ["Nelder-Mead"],
                    "bo_n_calls": 20,
                    "mcmc_draws": 1000,
                }
            },
        }


class PerformanceMonitor:
    """
    Performance monitoring and profiling utilities.

    Provides lightweight profiling and memory monitoring
    for optimization of computational kernels.
    """

    def __init__(self) -> None:
        self.timings: Dict[str, List[float]] = {}
        self.memory_usage: Dict[str, float] = {}

    def time_function(self, func_name: str) -> "PerformanceMonitor._TimingContext":
        """
        Context manager for timing function execution.

        Parameters
        ----------
        func_name : str
            Name of function being timed

        Usage
        -----
        with monitor.time_function("my_function"):
            # function code here
            pass
        """
        return self._TimingContext(self, func_name)

    class _TimingContext:
        def __init__(self, monitor: "PerformanceMonitor", func_name: str) -> None:
            self.monitor = monitor
            self.func_name = func_name
            self.start_time: Optional[float] = None

        def __enter__(self) -> "PerformanceMonitor._TimingContext":
            gc.collect()  # Clean memory before timing
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            # Suppress unused parameter warnings
            _ = exc_type, exc_val, exc_tb

            if self.start_time is not None:
                elapsed = time.perf_counter() - self.start_time
                if self.func_name not in self.monitor.timings:
                    self.monitor.timings[self.func_name] = []
                self.monitor.timings[self.func_name].append(elapsed)

    def get_timing_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for all timed functions."""
        summary = {}
        for func_name, times in self.timings.items():
            summary[func_name] = {
                "mean": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "total": sum(times),
                "calls": len(times),
            }
        return summary

    def reset_timings(self) -> None:
        """Clear all timing data."""
        self.timings.clear()
        self.memory_usage.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
