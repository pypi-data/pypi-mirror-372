"""
Classical Optimization Methods for Homodyne Scattering Analysis
===============================================================

This module contains multiple classical optimization algorithms for
parameter estimation in homodyne scattering analysis:

1. **Nelder-Mead Simplex**: Derivative-free optimization algorithm that
   works well for noisy objective functions and doesn't require gradient
   information, making it ideal for correlation function fitting.

2. **Gurobi Quadratic Programming**: Advanced optimization using quadratic
   approximation of the chi-squared objective function. Particularly effective
   for smooth problems with parameter bounds constraints. Requires Gurobi license.

Key Features:
- Consistent parameter bounds with MCMC for all methods
- Automatic Gurobi detection and graceful fallback
- Optimized configurations for different analysis modes
- Comprehensive error handling and status reporting

Authors: Wei Chen, Hongrui He
Institution: Argonne National Laboratory
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import scipy.optimize as optimize

try:
    import gurobipy as gp
    from gurobipy import GRB

    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False
    # Type stubs for when Gurobi is not available
    gp = None  # type: ignore
    GRB = None  # type: ignore

# Import robust optimization with graceful degradation
try:
    from .robust import RobustHomodyneOptimizer  # type: ignore
    from .robust import create_robust_optimizer

    ROBUST_OPTIMIZATION_AVAILABLE = True
except ImportError:
    RobustHomodyneOptimizer = None  # type: ignore
    create_robust_optimizer = None  # type: ignore
    ROBUST_OPTIMIZATION_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global optimization counter for tracking iterations
OPTIMIZATION_COUNTER = 0


class ClassicalOptimizer:
    """
    Classical optimization algorithms for parameter estimation.

    This class provides robust parameter estimation using multiple optimization
    algorithms:

    1. Nelder-Mead simplex method: Well-suited for noisy objective functions
       and doesn't require derivative information.

    2. Gurobi quadratic programming (optional): Uses quadratic approximation
       of the chi-squared objective function for potentially faster convergence
       on smooth problems with bounds constraints. Requires Gurobi license.

    The Gurobi method approximates the objective function using finite differences
    to estimate gradients and Hessian, then solves the resulting quadratic program.
    This approach can be particularly effective for least squares problems where
    the objective function is approximately quadratic near the optimum.

    Important: Both optimization methods use the same parameter bounds defined in
    the configuration's parameter_space.bounds section, ensuring consistency with
    MCMC and maintaining the same physical constraints across all optimization methods.
    """

    def __init__(self, analysis_core, config: Dict[str, Any]):
        """
        Initialize classical optimizer.

        Parameters
        ----------
        analysis_core : HomodyneAnalysisCore
            Core analysis engine instance
        config : Dict[str, Any]
            Configuration dictionary
        """
        self.core = analysis_core
        self.config = config
        self.best_params_classical = None

        # Extract optimization configuration
        self.optimization_config = config.get("optimization_config", {}).get(
            "classical_optimization", {}
        )

    def run_classical_optimization_optimized(
        self,
        initial_parameters: Optional[np.ndarray] = None,
        methods: Optional[List[str]] = None,
        phi_angles: Optional[np.ndarray] = None,
        c2_experimental: Optional[np.ndarray] = None,
    ) -> Tuple[Optional[np.ndarray], Any]:
        """
        Run Nelder-Mead optimization method.

        This method uses the Nelder-Mead simplex algorithm for parameter
        estimation. Nelder-Mead is well-suited for noisy objective functions
        and doesn't require gradient information.

        Parameters
        ----------
        initial_parameters : np.ndarray, optional
            Starting parameters for optimization
        methods : list, optional
            List of optimization methods to try
        phi_angles : np.ndarray, optional
            Scattering angles
        c2_experimental : np.ndarray, optional
            Experimental data

        Returns
        -------
        tuple
            (best_parameters, optimization_result)

        Raises
        ------
        RuntimeError
            If all classical methods fail
        """
        logger.info("Starting classical optimization")
        start_time = time.time()
        print("\n═══ Classical Optimization ═══")

        # Determine analysis mode and effective parameter count
        if hasattr(self.core, "config_manager") and self.core.config_manager:
            is_static_mode = self.core.config_manager.is_static_mode_enabled()
            analysis_mode = self.core.config_manager.get_analysis_mode()
            effective_param_count = (
                self.core.config_manager.get_effective_parameter_count()
            )
        else:
            # Fallback to core method
            is_static_mode = getattr(self.core, "is_static_mode", lambda: False)()
            analysis_mode = "static" if is_static_mode else "laminar_flow"
            effective_param_count = 3 if is_static_mode else 7

        print(f"  Analysis mode: {analysis_mode} ({effective_param_count} parameters)")
        logger.info(
            f"Classical optimization using {analysis_mode} mode with {effective_param_count} parameters"
        )

        # Load defaults if not provided
        if methods is None:
            available_methods = ["Nelder-Mead"]
            if GUROBI_AVAILABLE:
                available_methods.append("Gurobi")
            methods = self.optimization_config.get(
                "methods",
                available_methods,
            )

        # Ensure methods is not None for type checker
        assert methods is not None, "Optimization methods list cannot be None"

        if initial_parameters is None:
            initial_parameters = np.array(
                self.config["initial_parameters"]["values"], dtype=np.float64
            )

        # Adjust parameters based on analysis mode
        if is_static_mode and len(initial_parameters) > effective_param_count:
            # For static mode, only use diffusion parameters (first 3)
            initial_parameters = initial_parameters[:effective_param_count]
            print(
                f"  Using first {effective_param_count} parameters for static mode: {initial_parameters}"
            )
        elif not is_static_mode and len(initial_parameters) < effective_param_count:
            # For laminar flow mode, ensure we have all 7 parameters
            full_parameters = np.zeros(effective_param_count)
            full_parameters[: len(initial_parameters)] = initial_parameters
            initial_parameters = full_parameters
            print(
                f"  Extended to {effective_param_count} parameters for laminar flow mode"
            )

        if phi_angles is None or c2_experimental is None:
            c2_experimental, _, phi_angles, _ = self.core.load_experimental_data()

        # Type assertion after loading data to satisfy type checker
        assert (
            phi_angles is not None and c2_experimental is not None
        ), "Failed to load experimental data"

        best_result = None
        best_params = None
        best_chi2 = np.inf
        best_method = None  # Track which method produced the best result
        all_results = []  # Store all results for analysis

        # Create objective function using utility method
        objective = self.create_objective_function(
            phi_angles,
            c2_experimental,
            f"Classical-{analysis_mode.capitalize()}",
        )

        # Try each method
        for method in methods:
            print(f"  Trying {method}...")

            try:
                start = time.time()

                # Use single method utility
                success, result = self.run_single_method(
                    method=method,
                    objective_func=objective,
                    initial_parameters=initial_parameters,
                    bounds=None,  # Nelder-Mead doesn't use bounds
                    method_options=self.optimization_config.get(
                        "method_options", {}
                    ).get(method, {}),
                )

                elapsed = time.time() - start

                # Store result for analysis
                if success and isinstance(result, optimize.OptimizeResult):
                    # Add timing info to result object
                    setattr(result, "execution_time", elapsed)
                    all_results.append((method, result))

                    if result.fun < best_chi2:
                        best_result = result
                        best_params = result.x
                        best_chi2 = result.fun
                        best_method = method  # Track which method produced this result
                        print(
                            f"    ✓ New best: χ²_red = {
                                result.fun:.6e} ({
                                elapsed:.1f}s)"
                        )
                    else:
                        print(
                            f"    χ²_red = {
                                result.fun:.6e} ({
                                elapsed:.1f}s)"
                        )
                else:
                    # Store exception for analysis
                    all_results.append((method, result))
                    print(f"    ✗ Failed: {result}")
                    logger.warning(
                        f"Classical optimization method {method} failed: {result}"
                    )

            except Exception as e:
                all_results.append((method, e))
                print(f"    ✗ Failed: {e}")
                logger.warning(f"Classical optimization method {method} failed: {e}")
                logger.exception(f"Full traceback for {method} optimization failure:")

        if (
            best_result is not None
            and best_params is not None
            and isinstance(best_result, optimize.OptimizeResult)
        ):
            total_time = time.time() - start_time

            # best_method is already tracked when the best result was found
            if best_method is None:
                best_method = "Unknown"

            # Generate comprehensive summary (for future use)
            summary = self.get_optimization_summary(
                best_params, best_result, total_time, best_method
            )
            summary["optimization_method"] = best_method
            summary["all_methods_tried"] = [method for method, _ in all_results]

            # Create method-specific results dictionary
            method_results = {}
            for method, result in all_results:
                if hasattr(result, "fun"):  # Successful result
                    method_results[method] = {
                        "parameters": (
                            result.x.tolist() if hasattr(result, "x") else None
                        ),
                        "chi_squared": result.fun,
                        "success": (
                            result.success if hasattr(result, "success") else True
                        ),
                        "iterations": getattr(result, "nit", None),
                        "function_evaluations": getattr(result, "nfev", None),
                        "message": getattr(result, "message", ""),
                        "method": getattr(result, "method", method),
                    }
                else:  # Failed result (exception)
                    method_results[method] = {
                        "parameters": None,
                        "chi_squared": float("inf"),
                        "success": False,
                        "error": str(result),
                    }

            # Log results
            logger.info(
                f"Classical optimization completed in {
                    total_time:.2f}s, best χ²_red = {
                    best_chi2:.6e} (method: {best_method})"
            )
            print(
                f"  Best result: χ²_red = {
                    best_chi2:.6e} (method: {best_method})"
            )

            # Store best parameters
            self.best_params_classical = best_params

            # Log detailed analysis if debug logging is enabled
            if logger.isEnabledFor(logging.DEBUG):
                analysis = self.analyze_optimization_results(
                    [
                        (method, True, result)
                        for method, result in all_results
                        if hasattr(result, "fun")
                    ]
                )
                logger.debug(f"Classical optimization analysis: {analysis}")

            # Return enhanced result with method information
            enhanced_result = best_result
            enhanced_result.method_results = (
                method_results  # Add method-specific results
            )
            enhanced_result.best_method = best_method  # Add best method info

            return best_params, enhanced_result
        else:
            total_time = time.time() - start_time

            # Analyze failed results
            failed_analysis = self.analyze_optimization_results(
                [(method, False, result) for method, result in all_results]
            )

            logger.error(
                f"Classical optimization failed after {
                    total_time:.2f}s - all methods failed"
            )
            logger.error(f"Failure analysis: {failed_analysis}")

            raise RuntimeError(
                f"All classical methods failed. "
                f"Failed methods: {[method for method, _ in all_results]}"
            )

    def get_available_methods(self) -> List[str]:
        """
        Get list of available classical optimization methods.

        Returns
        -------
        List[str]
            List containing available optimization methods
        """
        methods = ["Nelder-Mead"]  # Nelder-Mead simplex algorithm
        if GUROBI_AVAILABLE:
            methods.append("Gurobi")  # Gurobi quadratic programming solver
        if ROBUST_OPTIMIZATION_AVAILABLE:
            methods.extend(
                ["Robust-Wasserstein", "Robust-Scenario", "Robust-Ellipsoidal"]
            )
        return methods

    def validate_method_compatibility(
        self, method: str, has_bounds: bool = True
    ) -> bool:
        """
        Validate if optimization method is compatible with current setup.

        Parameters
        ----------
        method : str
            Optimization method name
        has_bounds : bool
            Whether parameter bounds are defined (unused but kept for compatibility)

        Returns
        -------
        bool
            True if method is supported
        """
        # Note: has_bounds parameter is unused but kept for API compatibility
        _ = has_bounds  # Explicitly mark as unused for type checker

        if method == "Nelder-Mead":
            return True
        elif method == "Gurobi":
            return GUROBI_AVAILABLE
        return False

    def get_method_recommendations(self) -> Dict[str, List[str]]:
        """
        Get method recommendations based on problem characteristics.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping scenarios to recommended methods
        """
        recommendations = {
            "with_bounds": (
                ["Gurobi", "Nelder-Mead"] if GUROBI_AVAILABLE else ["Nelder-Mead"]
            ),
            "without_bounds": ["Nelder-Mead"],
            "high_dimensional": ["Nelder-Mead"],
            "low_dimensional": (
                ["Gurobi", "Nelder-Mead"] if GUROBI_AVAILABLE else ["Nelder-Mead"]
            ),
            # Excellent for noisy functions
            "noisy_objective": ["Nelder-Mead"],
            "smooth_objective": (
                ["Gurobi", "Nelder-Mead"] if GUROBI_AVAILABLE else ["Nelder-Mead"]
            ),
        }
        return recommendations

    def validate_parameters(
        self, parameters: np.ndarray, method_name: str = ""
    ) -> Tuple[bool, str]:
        """
        Validate physical parameters and bounds.

        Parameters
        ----------
        parameters : np.ndarray
            Model parameters to validate
        method_name : str
            Name of optimization method for logging (currently unused)

        Returns
        -------
        Tuple[bool, str]
            (is_valid, reason_if_invalid)
        """
        _ = method_name  # Suppress unused parameter warning
        # Get validation configuration
        validation = (
            self.config.get("advanced_settings", {})
            .get("chi_squared_calculation", {})
            .get("validity_check", {})
        )

        # Extract parameter sections
        num_diffusion_params = getattr(self.core, "num_diffusion_params", 3)
        num_shear_params = getattr(self.core, "num_shear_rate_params", 3)

        diffusion_params = parameters[:num_diffusion_params]
        shear_params = parameters[
            num_diffusion_params : num_diffusion_params + num_shear_params
        ]

        # Check positive D0
        if validation.get("check_positive_D0", True) and diffusion_params[0] <= 0:
            return False, f"Negative D0: {diffusion_params[0]}"

        # Check positive gamma_dot_t0
        if validation.get("check_positive_gamma_dot_t0", True) and shear_params[0] <= 0:
            return False, f"Negative gamma_dot_t0: {shear_params[0]}"

        # Check parameter bounds
        if validation.get("check_parameter_bounds", True):
            bounds = self.config.get("parameter_space", {}).get("bounds", [])
            for i, bound in enumerate(bounds):
                if i < len(parameters):
                    param_val = parameters[i]
                    param_min = bound.get("min", -np.inf)
                    param_max = bound.get("max", np.inf)

                    if not (param_min <= param_val <= param_max):
                        param_name = bound.get("name", f"p{i}")
                        return (
                            False,
                            f"Parameter {param_name} out of bounds: {param_val} not in [{param_min}, {param_max}]",
                        )

        return True, ""

    def create_objective_function(
        self,
        phi_angles: np.ndarray,
        c2_experimental: np.ndarray,
        method_name: str = "Classical",
    ):
        """
        Create objective function for optimization.

        Parameters
        ----------
        phi_angles : np.ndarray
            Scattering angles
        c2_experimental : np.ndarray
            Experimental correlation data
        method_name : str
            Name for logging purposes

        Returns
        -------
        callable
            Objective function for optimization
        """
        # Get angle filtering setting from configuration
        use_angle_filtering = True
        if hasattr(self.core, "config_manager") and self.core.config_manager:
            use_angle_filtering = self.core.config_manager.is_angle_filtering_enabled()
        elif "angle_filtering" in self.config.get("optimization_config", {}):
            use_angle_filtering = self.config["optimization_config"][
                "angle_filtering"
            ].get("enabled", True)

        def objective(params):
            return self.core.calculate_chi_squared_optimized(
                params,
                phi_angles,
                c2_experimental,
                method_name,
                filter_angles_for_optimization=use_angle_filtering,
            )

        return objective

    def run_single_method(
        self,
        method: str,
        objective_func,
        initial_parameters: np.ndarray,
        bounds: Optional[List[Tuple[float, float]]] = None,
        method_options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Union[optimize.OptimizeResult, Exception]]:
        """
        Run a single optimization method.

        Parameters
        ----------
        method : str
            Optimization method name
        objective_func : callable
            Objective function to minimize
        initial_parameters : np.ndarray
            Starting parameters
        bounds : List[Tuple[float, float]], optional
            Parameter bounds
        method_options : Dict[str, Any], optional
            Method-specific options

        Returns
        -------
        Tuple[bool, Union[OptimizeResult, Exception]]
            (success, result_or_exception)
        """
        try:
            if method == "Gurobi":
                return self._run_gurobi_optimization(
                    objective_func, initial_parameters, bounds, method_options
                )
            elif method.startswith("Robust-"):
                return self._run_robust_optimization(
                    method,
                    objective_func,
                    initial_parameters,
                    bounds,
                    method_options,
                )
            else:
                # Filter out comment fields (keys starting with '_' and ending
                # with '_note')
                filtered_options = {}
                if method_options:
                    filtered_options = {
                        k: v
                        for k, v in method_options.items()
                        if not (k.startswith("_") and k.endswith("_note"))
                    }

                kwargs = {
                    "fun": objective_func,
                    "x0": initial_parameters,
                    "method": method,
                    "options": filtered_options,
                }

                # Nelder-Mead doesn't use explicit bounds
                # The method handles constraints through the objective function

                result = optimize.minimize(**kwargs)
                return True, result

        except Exception as e:
            return False, e

    def _run_gurobi_optimization(
        self,
        objective_func,
        initial_parameters: np.ndarray,
        bounds: Optional[List[Tuple[float, float]]] = None,
        method_options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Union[optimize.OptimizeResult, Exception]]:
        """
        Run iterative Gurobi-based optimization using trust region approach.

        This method uses successive quadratic approximations (SQP-like approach) where:
        1. Build quadratic approximation around current point
        2. Solve QP subproblem with trust region constraints
        3. Evaluate actual objective at new point
        4. Update trust region and iterate until convergence

        Parameters
        ----------
        objective_func : callable
            Chi-squared objective function to minimize
        initial_parameters : np.ndarray
            Starting parameters
        bounds : List[Tuple[float, float]], optional
            Parameter bounds for optimization. If None, extracts bounds from the same
            configuration section used by MCMC (parameter_space.bounds).
        method_options : Dict[str, Any], optional
            Gurobi-specific options

        Returns
        -------
        Tuple[bool, Union[OptimizeResult, Exception]]
            (success, result_or_exception)
        """
        try:
            if not GUROBI_AVAILABLE or gp is None or GRB is None:
                raise ImportError("Gurobi is not available. Please install gurobipy.")

            # Get parameter bounds
            if bounds is None:
                bounds = self.get_parameter_bounds()

            n_params = len(initial_parameters)

            # Default Gurobi options with iterative settings
            gurobi_options = {
                "max_iterations": 50,  # Outer iterations for SQP
                "tolerance": 1e-6,
                "output_flag": 0,  # Suppress output by default
                "method": 2,  # Use barrier method for QP
                "time_limit": 300,  # 5 minute time limit
                "trust_region_initial": 0.1,  # Initial trust region radius
                "trust_region_min": 1e-8,  # Minimum trust region radius
                "trust_region_max": 1.0,  # Maximum trust region radius
            }

            # Update with user options
            if method_options:
                filtered_options = {
                    k: v
                    for k, v in method_options.items()
                    if not (k.startswith("_") and k.endswith("_note"))
                }
                gurobi_options.update(filtered_options)

            # Initialize iterative optimization
            x_current = initial_parameters.copy()
            f_current = objective_func(x_current)
            trust_radius = gurobi_options["trust_region_initial"]

            # Convergence tracking
            iteration = 0
            max_iter = gurobi_options["max_iterations"]
            tolerance = gurobi_options["tolerance"]
            function_evaluations = 1  # Already evaluated f_current
            grad_norm = float("inf")  # Initialize for later use

            logger.debug(
                f"Starting Gurobi iterative optimization with initial χ² = {f_current:.6e}"
            )

            # Iterative trust region optimization
            for iteration in range(max_iter):
                # Choose appropriate epsilon based on parameter magnitudes and trust region
                base_epsilon = max(1e-8, trust_radius / 100)

                # Estimate gradient using finite differences
                grad = np.zeros(n_params)
                for i in range(n_params):
                    epsilon = base_epsilon * max(1.0, abs(x_current[i]))
                    x_plus = x_current.copy()
                    x_plus[i] += epsilon
                    x_minus = x_current.copy()
                    x_minus[i] -= epsilon

                    f_plus = objective_func(x_plus)
                    f_minus = objective_func(x_minus)
                    grad[i] = (f_plus - f_minus) / (2 * epsilon)
                    function_evaluations += 2

                # Check for convergence based on gradient norm
                grad_norm = np.linalg.norm(grad)
                if grad_norm < tolerance:
                    logger.debug(
                        f"Gurobi optimization converged at iteration {iteration}: ||grad|| = {grad_norm:.2e}"
                    )
                    break

                # Estimate diagonal Hessian approximation (BFGS-like)
                hessian_diag = np.ones(n_params)
                for i in range(n_params):
                    epsilon = base_epsilon * max(1.0, abs(x_current[i]))
                    x_plus = x_current.copy()
                    x_plus[i] += epsilon
                    x_minus = x_current.copy()
                    x_minus[i] -= epsilon

                    f_plus = objective_func(x_plus)
                    f_minus = objective_func(x_minus)
                    second_deriv = (f_plus - 2 * f_current + f_minus) / (epsilon**2)
                    hessian_diag[i] = max(1e-6, second_deriv)  # Ensure positive
                    function_evaluations += 2

                try:
                    # Create Gurobi model for trust region subproblem
                    with gp.Env(empty=True) as env:
                        if gurobi_options.get("output_flag", 0) == 0:
                            env.setParam("OutputFlag", 0)
                        env.start()

                        with gp.Model(env=env) as model:
                            # Set Gurobi parameters
                            model.setParam(GRB.Param.OptimalityTol, tolerance)
                            model.setParam(
                                GRB.Param.Method, gurobi_options.get("method", 2)
                            )
                            model.setParam(
                                GRB.Param.TimeLimit,
                                gurobi_options.get("time_limit", 300),
                            )

                            # Create decision variables for step
                            step = model.addVars(
                                n_params,
                                lb=-gp.GRB.INFINITY,
                                ub=gp.GRB.INFINITY,
                                name="step",
                            )

                            # Trust region constraint: ||step||_2 <= trust_radius
                            model.addQConstr(
                                gp.quicksum(step[i] * step[i] for i in range(n_params))
                                <= trust_radius**2,
                                "trust_region",
                            )

                            # Parameter bounds constraints: bounds[i][0] <= x_current[i] + step[i] <= bounds[i][1]
                            for i in range(n_params):
                                if i < len(bounds):
                                    lb, ub = bounds[i]
                                    if lb != -np.inf:
                                        model.addConstr(
                                            step[i] >= lb - x_current[i],
                                            f"lower_bound_{i}",
                                        )
                                    if ub != np.inf:
                                        model.addConstr(
                                            step[i] <= ub - x_current[i],
                                            f"upper_bound_{i}",
                                        )

                            # Quadratic approximation: grad^T * step + 0.5 * step^T * H_diag * step
                            obj = gp.LinExpr()
                            for i in range(n_params):
                                obj += grad[i] * step[i]  # Linear term
                                obj += (
                                    0.5 * hessian_diag[i] * step[i] * step[i]
                                )  # Quadratic term

                            model.setObjective(obj, GRB.MINIMIZE)

                            # Optimize subproblem
                            model.optimize()

                            if model.status == GRB.OPTIMAL:
                                # Extract step
                                step_values = np.array([step[i].x for i in range(n_params)])  # type: ignore[attr-defined]
                                x_new = x_current + step_values
                                f_new = objective_func(x_new)
                                function_evaluations += 1

                                # Trust region update logic
                                predicted_reduction = (
                                    model.objVal
                                )  # Should be negative for minimization
                                actual_reduction = f_current - f_new

                                if actual_reduction > 0:
                                    # Accept step
                                    step_norm = np.linalg.norm(step_values)
                                    logger.debug(
                                        f"Iteration {iteration}: χ² = {f_new:.6e} (improvement: {actual_reduction:.2e}, step: {step_norm:.3f})"
                                    )

                                    x_current = x_new
                                    f_current = f_new

                                    # Expand trust region if step is successful and near boundary
                                    if step_norm > 0.8 * trust_radius:
                                        trust_radius = min(
                                            gurobi_options["trust_region_max"],
                                            2 * trust_radius,
                                        )
                                else:
                                    # Reject step and shrink trust region
                                    trust_radius = max(
                                        gurobi_options["trust_region_min"],
                                        0.5 * trust_radius,
                                    )
                                    logger.debug(
                                        f"Iteration {iteration}: Step rejected, shrinking trust region to {trust_radius:.6f}"
                                    )

                                # Check convergence
                                if (
                                    actual_reduction > 0
                                    and abs(actual_reduction) < tolerance
                                ):
                                    logger.debug(
                                        f"Gurobi optimization converged at iteration {iteration}: improvement = {actual_reduction:.2e}"
                                    )
                                    break

                                if trust_radius < gurobi_options["trust_region_min"]:
                                    logger.debug(
                                        f"Gurobi optimization terminated: trust region too small ({trust_radius:.2e})"
                                    )
                                    break
                            else:
                                # QP solve failed, shrink trust region and try again
                                trust_radius = max(
                                    gurobi_options["trust_region_min"],
                                    0.25 * trust_radius,
                                )
                                logger.debug(
                                    f"QP subproblem failed with status {model.status}, shrinking trust region to {trust_radius:.6f}"
                                )
                                if trust_radius < gurobi_options["trust_region_min"]:
                                    break

                except Exception as e:
                    logger.warning(
                        f"Gurobi subproblem failed at iteration {iteration}: {e}"
                    )
                    break

            # Create final result
            if iteration < max_iter or grad_norm < tolerance:
                result = optimize.OptimizeResult(
                    x=x_current,
                    fun=f_current,
                    success=True,
                    status=0,
                    message=f"Iterative Gurobi optimization converged after {iteration} iterations.",
                    nit=iteration,
                    nfev=function_evaluations,
                    method="Gurobi-Iterative-QP",
                )
                logger.debug(
                    f"Gurobi optimization completed: χ² = {f_current:.6e} after {iteration} iterations"
                )
                return True, result
            else:
                result = optimize.OptimizeResult(
                    x=x_current,
                    fun=f_current,
                    success=False,
                    status=1,
                    message=f"Iterative Gurobi optimization reached maximum iterations ({max_iter}).",
                    nit=iteration,
                    nfev=function_evaluations,
                    method="Gurobi-Iterative-QP",
                )
                return False, result

        except Exception as e:
            logger.error(f"Gurobi optimization failed: {e}")
            return False, e

    def _run_robust_optimization(
        self,
        method: str,
        objective_func,
        initial_parameters: np.ndarray,
        bounds: Optional[
            List[Tuple[float, float]]
        ] = None,  # Used by robust optimizer internally
        method_options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Union[optimize.OptimizeResult, Exception]]:
        """
        Run robust optimization using CVXPY + Gurobi.

        Parameters
        ----------
        method : str
            Robust optimization method ("Robust-Wasserstein", "Robust-Scenario", "Robust-Ellipsoidal")
        objective_func : callable
            Chi-squared objective function to minimize
        initial_parameters : np.ndarray
            Starting parameters
        bounds : List[Tuple[float, float]], optional
            Parameter bounds for optimization
        method_options : Dict[str, Any], optional
            Robust optimization specific options

        Returns
        -------
        Tuple[bool, Union[OptimizeResult, Exception]]
            (success, result_or_exception)
        """
        try:
            if not ROBUST_OPTIMIZATION_AVAILABLE or create_robust_optimizer is None:
                raise ImportError(
                    "Robust optimization not available. Please install cvxpy."
                )

            # Create robust optimizer instance
            robust_optimizer = create_robust_optimizer(self.core, self.config)

            # Extract phi_angles and c2_experimental from the objective function context
            # Check both the direct attributes and the cached versions
            phi_angles = getattr(self.core, "phi_angles", None)
            c2_experimental = getattr(self.core, "c2_experimental", None)

            # If not found, try the cached versions from load_experimental_data
            if phi_angles is None:
                phi_angles = getattr(self.core, "_last_phi_angles", None)
            if c2_experimental is None:
                c2_experimental = getattr(self.core, "_last_experimental_data", None)

            if phi_angles is None or c2_experimental is None:
                raise ValueError(
                    "Robust optimization requires phi_angles and c2_experimental "
                    "to be available in the analysis core. "
                    f"Found phi_angles: {
                        'present' if phi_angles is not None else 'missing'}, "
                    f"c2_experimental: {
                        'present' if c2_experimental is not None else 'missing'}"
                )

            # Map method names to robust optimization types
            method_mapping = {
                "Robust-Wasserstein": "wasserstein",
                "Robust-Scenario": "scenario",
                "Robust-Ellipsoidal": "ellipsoidal",
            }

            robust_method = method_mapping.get(method)
            if robust_method is None:
                raise ValueError(f"Unknown robust optimization method: {method}")

            # Run robust optimization
            optimal_params, info = robust_optimizer.run_robust_optimization(
                initial_parameters=initial_parameters,
                phi_angles=phi_angles,
                c2_experimental=c2_experimental,
                method=robust_method,
                **(method_options or {}),
            )

            if optimal_params is not None:
                # Create OptimizeResult compatible object
                result = optimize.OptimizeResult(
                    x=optimal_params,
                    fun=info.get("final_chi_squared", objective_func(optimal_params)),
                    success=True,
                    status=info.get("status", "success"),
                    message=f"Robust optimization ({robust_method}) converged",
                    nit=info.get("n_iterations"),
                    nfev=info.get("function_evaluations", None),
                    method=f"Robust-{robust_method.capitalize()}",
                )

                return True, result
            else:
                # Optimization failed
                error_msg = info.get(
                    "error", f"Robust optimization ({robust_method}) failed"
                )
                result = optimize.OptimizeResult(
                    x=initial_parameters,
                    fun=float("inf"),
                    success=False,
                    status=info.get("status", "failed"),
                    message=error_msg,
                    method=f"Robust-{robust_method.capitalize()}",
                )

                return False, result

        except Exception as e:
            logger.error(f"Robust optimization error: {e}")
            return False, e

    def analyze_optimization_results(
        self,
        results: List[Tuple[str, bool, Union[optimize.OptimizeResult, Exception]]],
    ) -> Dict[str, Any]:
        """
        Analyze and summarize optimization results from Nelder-Mead method.

        Parameters
        ----------
        results : List[Tuple[str, bool, Union[OptimizeResult, Exception]]]
            List of (method_name, success, result_or_exception) tuples (typically one entry for Nelder-Mead)

        Returns
        -------
        Dict[str, Any]
            Analysis summary including best method, convergence stats, etc.
        """
        successful_results = []
        failed_methods = []

        for method, success, result in results:
            if success and hasattr(result, "fun"):
                successful_results.append((method, result))
            else:
                failed_methods.append((method, result))

        if not successful_results:
            return {
                "success": False,
                "failed_methods": failed_methods,
                "error": "All methods failed",
            }

        # Find best result
        best_method, best_result = min(successful_results, key=lambda x: x[1].fun)

        # Compute statistics
        chi2_values = [result.fun for _, result in successful_results]

        return {
            "success": True,
            "best_method": best_method,
            "best_result": best_result,
            "best_chi2": best_result.fun,
            "successful_methods": len(successful_results),
            "failed_methods": failed_methods,
            "chi2_statistics": {
                "min": np.min(chi2_values),
                "max": np.max(chi2_values),
                "mean": np.mean(chi2_values),
                "std": np.std(chi2_values),
            },
            "convergence_info": {
                method: {
                    "converged": result.success,
                    "iterations": getattr(result, "nit", None),
                    "function_evaluations": getattr(result, "nfev", None),
                    "message": getattr(result, "message", None),
                }
                for method, result in successful_results
            },
        }

    def get_parameter_bounds(
        self,
        effective_param_count: Optional[int] = None,
        is_static_mode: Optional[bool] = None,
    ) -> List[Tuple[float, float]]:
        """
        Extract parameter bounds from configuration (unused by Nelder-Mead).

        This method is kept for compatibility but is not used by Nelder-Mead
        optimization since it doesn't support explicit bounds.

        Parameters
        ----------
        effective_param_count : int, optional
            Number of parameters to use (3 for static, 7 for laminar flow)
        is_static_mode : bool, optional
            Whether static mode is enabled (unused, kept for compatibility)

        Returns
        -------
        List[Tuple[float, float]]
            List of (min, max) bounds for each parameter
        """
        # Note: is_static_mode parameter is unused but kept for API
        # compatibility
        _ = is_static_mode  # Explicitly mark as unused for type checker

        bounds = []
        param_bounds = self.config.get("parameter_space", {}).get("bounds", [])

        # Determine effective parameter count if not provided
        if effective_param_count is None:
            if hasattr(self.core, "config_manager") and self.core.config_manager:
                effective_param_count = (
                    self.core.config_manager.get_effective_parameter_count()
                )
            else:
                effective_param_count = 7  # Default to laminar flow

        # Ensure effective_param_count is not None for type checking
        if effective_param_count is None:
            effective_param_count = 7  # Final fallback to laminar flow

        # Extract bounds for the effective parameters
        for i, bound in enumerate(param_bounds):
            if i < effective_param_count:
                bounds.append((bound.get("min", -np.inf), bound.get("max", np.inf)))

        # Ensure we have enough bounds
        while len(bounds) < effective_param_count:
            bounds.append((-np.inf, np.inf))

        return bounds[:effective_param_count]

    def compare_optimization_results(
        self,
        results: List[Tuple[str, Union[optimize.OptimizeResult, Exception]]],
    ) -> Dict[str, Any]:
        """
        Compare optimization results (typically just Nelder-Mead).

        Parameters
        ----------
        results : List[Tuple[str, Union[OptimizeResult, Exception]]]
            List of (method_name, result) tuples (typically one entry for Nelder-Mead)

        Returns
        -------
        Dict[str, Any]
            Comparison summary with rankings and statistics
        """
        successful_results = []
        failed_methods = []

        for method, result in results:
            if isinstance(result, optimize.OptimizeResult) and result.success:
                successful_results.append((method, result))
            else:
                failed_methods.append(method)

        if not successful_results:
            return {"error": "No successful optimizations to compare"}

        # Sort by chi-squared value
        successful_results.sort(key=lambda x: x[1].fun)

        comparison = {
            "ranking": [
                {
                    "rank": i + 1,
                    "method": method,
                    "chi_squared": result.fun,
                    "converged": result.success,
                    "iterations": getattr(result, "nit", None),
                    "function_evaluations": getattr(result, "nfev", None),
                    "time_elapsed": getattr(result, "execution_time", None),
                }
                for i, (method, result) in enumerate(successful_results)
            ],
            "best_method": successful_results[0][0],
            "best_chi_squared": successful_results[0][1].fun,
            "failed_methods": failed_methods,
            "success_rate": len(successful_results) / len(results),
        }

        return comparison

    def get_optimization_summary(
        self,
        best_params: np.ndarray,
        best_result: optimize.OptimizeResult,
        total_time: float,
        method_name: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Generate comprehensive optimization summary.

        Parameters
        ----------
        best_params : np.ndarray
            Best parameters found
        best_result : OptimizeResult
            Best optimization result
        total_time : float
            Total optimization time in seconds

        Returns
        -------
        Dict[str, Any]
            Comprehensive optimization summary
        """
        # Parameter names (if available in config)
        param_names = []
        param_bounds = self.config.get("parameter_space", {}).get("bounds", [])
        for i, bound in enumerate(param_bounds):
            param_names.append(bound.get("name", f"param_{i}"))

        summary = {
            "optimization_successful": True,
            "best_chi_squared": best_result.fun,
            "best_parameters": {
                (param_names[i] if i < len(param_names) else f"param_{i}"): float(param)
                for i, param in enumerate(best_params)
            },
            "optimization_details": {
                "method": method_name,
                "converged": best_result.success,
                "iterations": getattr(best_result, "nit", None),
                "function_evaluations": getattr(best_result, "nfev", None),
                "message": getattr(best_result, "message", None),
            },
            "timing": {
                "total_time_seconds": total_time,
                "average_evaluation_time": (
                    total_time / (getattr(best_result, "nfev", None) or 1)
                ),
            },
            "parameter_validation": {},
        }

        # Add parameter validation info
        is_valid, reason = self.validate_parameters(best_params, "Summary")
        summary["parameter_validation"] = {
            "valid": is_valid,
            "reason": (reason if not is_valid else "All parameters within bounds"),
        }

        return summary

    def reset_optimization_counter(self):
        """Reset the global optimization counter."""
        global OPTIMIZATION_COUNTER
        OPTIMIZATION_COUNTER = 0

    def get_optimization_counter(self) -> int:
        """Get current optimization counter value."""
        return OPTIMIZATION_COUNTER
