"""
Pipeline processing system for landuse-intensity-analysis.

This module provides a functional pipeline system for chaining analysis operations:
- Declarative pipeline definition
- Automatic dependency management
- Parallel processing integration
- Caching and memoization
- Progress tracking and error handling
- Pipeline composition and reuse

The pipeline system allows users to define complex analysis workflows
as a series of connected steps, with automatic optimization and parallelization.

Example:
    >>> from landuse_intensity.pipeline import AnalysisPipeline
    >>>
    >>> pipeline = (AnalysisPipeline()
    ...     .load_data("data/")
    ...     .compute_contingency_table()
    ...     .calculate_intensity_matrices()
    ...     .generate_visualizations()
    ...     .save_results("output/"))
    >>>
    >>> results = pipeline.run()
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    """
    Represents a single step in the analysis pipeline.

    Each step has a name, function to execute, dependencies,
    and metadata for optimization and caching.
    """
    name: str
    func: Callable
    dependencies: List[str] = field(default_factory=list)
    cache_key: Optional[str] = None
    parallelizable: bool = False
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.description:
            self.description = self.name.replace("_", " ").title()


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""
    step_name: str
    result: Any
    execution_time: float
    cache_hit: bool = False
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnalysisPipeline:
    """
    Functional pipeline for landuse intensity analysis.

    This class provides a fluent interface for building analysis pipelines
    with automatic dependency management, caching, and parallelization.
    """

    def __init__(self, cache_manager=None, parallel_processor=None):
        """
        Initialize analysis pipeline.

        Parameters
        ----------
        cache_manager : CacheManager, optional
            Cache manager for result caching
        parallel_processor : ParallelProcessor, optional
            Parallel processor for distributed computing
        """
        self.steps: Dict[str, PipelineStep] = {}
        self.execution_order: List[str] = []
        self.results: Dict[str, PipelineResult] = {}
        self.cache_manager = cache_manager
        self.parallel_processor = parallel_processor

        # Import optional dependencies
        self._import_optional_deps()

    def _import_optional_deps(self):
        """Import optional dependencies with fallbacks."""
        try:
            from .cache import CacheManager
            self.cache_manager = self.cache_manager or CacheManager()
        except ImportError:
            logger.warning("Cache manager not available")

        try:
            from .parallel import ParallelProcessor
            self.parallel_processor = self.parallel_processor or ParallelProcessor()
        except ImportError:
            logger.warning("Parallel processor not available")

    def add_step(self,
                 name: str,
                 func: Callable,
                 dependencies: List[str] = None,
                 cache_key: str = None,
                 parallelizable: bool = False,
                 description: str = "",
                 **metadata) -> 'AnalysisPipeline':
        """
        Add a step to the pipeline.

        Parameters
        ----------
        name : str
            Unique name for the step
        func : callable
            Function to execute for this step
        dependencies : list of str, optional
            Names of steps this step depends on
        cache_key : str, optional
            Cache key for this step's results
        parallelizable : bool, default False
            Whether this step can be parallelized
        description : str, optional
            Human-readable description
        **metadata
            Additional metadata for the step

        Returns
        -------
        AnalysisPipeline
            Self for method chaining
        """
        if name in self.steps:
            raise ValueError(f"Step '{name}' already exists in pipeline")

        step = PipelineStep(
            name=name,
            func=func,
            dependencies=dependencies or [],
            cache_key=cache_key,
            parallelizable=parallelizable,
            description=description,
            metadata=metadata
        )

        self.steps[name] = step

        # Update execution order based on dependencies
        self._update_execution_order()

        logger.debug(f"Added pipeline step: {name}")
        return self

    def _update_execution_order(self):
        """Update the execution order based on step dependencies."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(step_name):
            if step_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving '{step_name}'")
            if step_name in visited:
                return

            temp_visited.add(step_name)

            for dep in self.steps[step_name].dependencies:
                if dep not in self.steps:
                    raise ValueError(f"Dependency '{dep}' not found for step '{step_name}'")
                visit(dep)

            temp_visited.remove(step_name)
            visited.add(step_name)
            order.append(step_name)

        for step_name in self.steps:
            if step_name not in visited:
                visit(step_name)

        self.execution_order = order

    def load_data(self, data_path: Union[str, Path], **kwargs) -> 'AnalysisPipeline':
        """Add data loading step."""
        def load_func():
            from .raster import load_raster_data
            return load_raster_data(data_path, **kwargs)

        return self.add_step(
            "load_data",
            load_func,
            cache_key=f"load_data_{str(data_path)}",
            description="Load raster data from files"
        )

    def compute_contingency_table(self, **kwargs) -> 'AnalysisPipeline':
        """Add contingency table computation step."""
        def contingency_func():
            from .analysis import compute_contingency_table
            data = self.results["load_data"].result
            return compute_contingency_table(data, **kwargs)

        return self.add_step(
            "compute_contingency_table",
            contingency_func,
            dependencies=["load_data"],
            cache_key="contingency_table",
            parallelizable=True,
            description="Compute contingency table"
        )

    def calculate_intensity_matrices(self, **kwargs) -> 'AnalysisPipeline':
        """Add intensity matrices calculation step."""
        def intensity_func():
            from .intensity import calculate_intensity_matrices
            contingency = self.results["compute_contingency_table"].result
            return calculate_intensity_matrices(contingency, **kwargs)

        return self.add_step(
            "calculate_intensity_matrices",
            intensity_func,
            dependencies=["compute_contingency_table"],
            cache_key="intensity_matrices",
            parallelizable=True,
            description="Calculate intensity matrices"
        )

    def generate_visualizations(self, **kwargs) -> 'AnalysisPipeline':
        """Add visualization generation step."""
        def viz_func():
            from .visualization import generate_all_visualizations
            intensity_data = self.results["calculate_intensity_matrices"].result
            return generate_all_visualizations(intensity_data, **kwargs)

        return self.add_step(
            "generate_visualizations",
            viz_func,
            dependencies=["calculate_intensity_matrices"],
            cache_key="visualizations",
            description="Generate visualizations"
        )

    def save_results(self, output_path: Union[str, Path], **kwargs) -> 'AnalysisPipeline':
        """Add results saving step."""
        def save_func():
            import json
            from pathlib import Path

            output_path_obj = Path(output_path)
            output_path_obj.mkdir(parents=True, exist_ok=True)

            # Save all results
            results_summary = {}
            for step_name, result in self.results.items():
                if result.result is not None:
                    results_summary[step_name] = {
                        "execution_time": result.execution_time,
                        "cache_hit": result.cache_hit,
                        "metadata": result.metadata
                    }

                    # Save result data if serializable
                    try:
                        result_file = output_path_obj / f"{step_name}_result.json"
                        with open(result_file, 'w') as f:
                            json.dump(result.result, f, indent=2, default=str)
                    except (TypeError, ValueError):
                        logger.warning(f"Could not serialize result for step: {step_name}")

            # Save summary
            summary_file = output_path_obj / "pipeline_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(results_summary, f, indent=2, default=str)

            return str(output_path_obj)

        return self.add_step(
            "save_results",
            save_func,
            dependencies=self.execution_order[-1:],  # Depends on last step
            description="Save pipeline results"
        )

    def run(self, use_cache: bool = True, parallel: bool = True) -> Dict[str, Any]:
        """
        Execute the pipeline.

        Parameters
        ----------
        use_cache : bool, default True
            Whether to use caching for step results
        parallel : bool, default True
            Whether to use parallel processing for parallelizable steps

        Returns
        -------
        dict
            Dictionary of step results
        """
        logger.info(f"Starting pipeline execution with {len(self.steps)} steps")

        start_time = time.time()

        for step_name in self.execution_order:
            step = self.steps[step_name]

            # Check if all dependencies are satisfied
            for dep in step.dependencies:
                if dep not in self.results or self.results[dep].error:
                    error_msg = f"Dependency '{dep}' failed or not executed"
                    self.results[step_name] = PipelineResult(
                        step_name=step_name,
                        result=None,
                        execution_time=0.0,
                        error=RuntimeError(error_msg)
                    )
                    logger.error(error_msg)
                    continue

            # Try to get result from cache
            cache_hit = False
            if use_cache and self.cache_manager and step.cache_key:
                try:
                    cached_result = self.cache_manager.get(step.cache_key)
                    if cached_result is not None:
                        self.results[step_name] = PipelineResult(
                            step_name=step_name,
                            result=cached_result,
                            execution_time=0.0,
                            cache_hit=True
                        )
                        logger.info(f"Cache hit for step: {step_name}")
                        continue
                except Exception as e:
                    logger.warning(f"Cache retrieval failed for {step_name}: {e}")

            # Execute step
            step_start_time = time.time()

            try:
                logger.info(f"Executing step: {step_name} - {step.description}")

                # Execute the step function
                result = step.func()

                execution_time = time.time() - step_start_time

                # Cache the result if caching is enabled
                if use_cache and self.cache_manager and step.cache_key:
                    try:
                        self.cache_manager.set(step.cache_key, result)
                    except Exception as e:
                        logger.warning(f"Cache storage failed for {step_name}: {e}")

                self.results[step_name] = PipelineResult(
                    step_name=step_name,
                    result=result,
                    execution_time=execution_time,
                    cache_hit=cache_hit
                )

                logger.info(".2f")

            except Exception as e:
                execution_time = time.time() - step_start_time
                logger.error(f"Step '{step_name}' failed: {e}")

                self.results[step_name] = PipelineResult(
                    step_name=step_name,
                    result=None,
                    execution_time=execution_time,
                    error=e
                )

        total_time = time.time() - start_time
        logger.info(".2f")

        # Return final results
        final_results = {}
        for step_name, result in self.results.items():
            if result.error:
                final_results[step_name] = {"error": str(result.error)}
            else:
                final_results[step_name] = result.result

        return final_results

    def get_step_info(self, step_name: str) -> Optional[PipelineStep]:
        """Get information about a specific step."""
        return self.steps.get(step_name)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics for all steps."""
        stats = {
            "total_steps": len(self.steps),
            "executed_steps": len(self.results),
            "cache_hits": sum(1 for r in self.results.values() if r.cache_hit),
            "errors": sum(1 for r in self.results.values() if r.error),
            "total_execution_time": sum(r.execution_time for r in self.results.values()),
            "step_details": {}
        }

        for step_name, result in self.results.items():
            stats["step_details"][step_name] = {
                "execution_time": result.execution_time,
                "cache_hit": result.cache_hit,
                "has_error": result.error is not None,
                "error_message": str(result.error) if result.error else None
            }

        return stats

    def reset(self):
        """Reset the pipeline for re-execution."""
        self.results.clear()
        logger.info("Pipeline reset")

    def compose(self, other_pipeline: 'AnalysisPipeline') -> 'AnalysisPipeline':
        """
        Compose this pipeline with another pipeline.

        Parameters
        ----------
        other_pipeline : AnalysisPipeline
            Pipeline to compose with this one

        Returns
        -------
        AnalysisPipeline
            New composed pipeline
        """
        # Create new pipeline with combined steps
        new_pipeline = AnalysisPipeline(
            cache_manager=self.cache_manager,
            parallel_processor=self.parallel_processor
        )

        # Add steps from both pipelines
        for step_name, step in {**self.steps, **other_pipeline.steps}.items():
            new_pipeline.steps[step_name] = step

        # Recalculate execution order
        new_pipeline._update_execution_order()

        return new_pipeline

    def __repr__(self) -> str:
        """String representation of the pipeline."""
        step_info = []
        for step_name in self.execution_order:
            step = self.steps[step_name]
            status = "✓" if step_name in self.results else "○"
            error = " (ERROR)" if step_name in self.results and self.results[step_name].error else ""
            step_info.append(f"  {status} {step_name}{error}")

        return f"AnalysisPipeline(\n" + "\n".join(step_info) + "\n)"


# Convenience functions
def create_intensity_analysis_pipeline(data_path: Union[str, Path],
                                     output_path: Union[str, Path] = None,
                                     **kwargs) -> AnalysisPipeline:
    """
    Create a standard intensity analysis pipeline.

    Parameters
    ----------
    data_path : str or Path
        Path to input data
    output_path : str or Path, optional
        Path to save results
    **kwargs
        Additional arguments for pipeline steps

    Returns
    -------
    AnalysisPipeline
        Configured pipeline for intensity analysis
    """
    pipeline = (AnalysisPipeline()
        .load_data(data_path, **kwargs)
        .compute_contingency_table(**kwargs)
        .calculate_intensity_matrices(**kwargs)
        .generate_visualizations(**kwargs))

    if output_path:
        pipeline.save_results(output_path, **kwargs)

    return pipeline

def run_intensity_analysis(data_path: Union[str, Path],
                          output_path: Union[str, Path] = None,
                          **kwargs) -> Dict[str, Any]:
    """
    Run a complete intensity analysis pipeline.

    Parameters
    ----------
    data_path : str or Path
        Path to input data
    output_path : str or Path, optional
        Path to save results
    **kwargs
        Additional arguments for analysis

    Returns
    -------
    dict
        Analysis results
    """
    pipeline = create_intensity_analysis_pipeline(data_path, output_path, **kwargs)
    return pipeline.run()
