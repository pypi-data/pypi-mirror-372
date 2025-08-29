API Reference
=============

Complete API documentation for the homodyne analysis package.

.. toctree::
   :maxdepth: 2
   :caption: Core Modules

   core
   mcmc
   robust
   utilities

Core Classes
------------

* :class:`~homodyne.analysis.core.HomodyneAnalysisCore` - Main analysis orchestrator
* :class:`~homodyne.core.config.ConfigManager` - Configuration management
* :class:`~homodyne.optimization.classical.ClassicalOptimizer` - Classical optimization
* :class:`~homodyne.optimization.robust.RobustHomodyneOptimizer` - Robust optimization
* :class:`~homodyne.optimization.mcmc.MCMCSampler` - Bayesian analysis

Quick Reference
---------------

**Essential Imports**:

.. code-block:: python

   from homodyne import HomodyneAnalysisCore, ConfigManager
   from homodyne.optimization.classical import ClassicalOptimizer
   from homodyne.optimization.robust import RobustHomodyneOptimizer
   from homodyne.optimization.mcmc import MCMCSampler

**Basic Workflow**:

.. code-block:: python

   # 1. Configuration
   config = ConfigManager("config.json")

   # 2. Analysis setup
   analysis = HomodyneAnalysisCore(config)
   analysis.load_experimental_data()

   # 3. Run optimization methods
   classical_result = analysis.optimize_classical()    # Classical methods
   robust_result = analysis.optimize_robust()         # Robust methods
   mcmc_result = analysis.run_mcmc_sampling()         # MCMC sampling

   # Or run all methods
   all_results = analysis.optimize_all()

Module Index
------------

The package includes the following key modules:

* **homodyne.core** - Core functionality and configuration
* **homodyne.analysis.core** - Main analysis engine
* **homodyne.optimization.classical** - Classical optimization (Nelder-Mead, Gurobi)
* **homodyne.optimization.robust** - Robust optimization (Wasserstein DRO, Scenario-based, Ellipsoidal)
* **homodyne.optimization.mcmc** - Bayesian MCMC sampling (NUTS)
* **homodyne.plotting** - Visualization utilities

.. note::
   For detailed API documentation, see the individual module pages in the navigation.

..
   Temporarily disabled autosummary due to import issues

   .. autosummary::
      :toctree: _autosummary
      :template: module.rst

      homodyne.core
      homodyne.core.config
      homodyne.core.kernels
      homodyne.core.io_utils
      homodyne.analysis.core
      homodyne.optimization.mcmc
      homodyne.optimization.classical
      homodyne.plotting
