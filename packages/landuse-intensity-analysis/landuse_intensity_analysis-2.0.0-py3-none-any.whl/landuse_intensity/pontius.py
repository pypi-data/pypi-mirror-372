"""
Advanced Pontius methodology implementation for land use and land cover change analysis.

This module implements the complete Pontius methodology including:
- Quantity vs Allocation Disagreement
- Advanced Intensity Analysis (3 levels)
- Mathematical formulations from Pontius et al.
- Modern error analysis techniques

References:
- Pontius, R.G. Jr. et al. (2008). Comparing the input, output, and validation maps for several models of land change.
- Aldwaik, S.Z. & Pontius, R.G. Jr. (2012). Intensity analysis to unify measurements of size and stationarity of land changes.
"""

import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Type aliases for clarity
Matrix = np.ndarray
DataFrame = pd.DataFrame


@dataclass
class PontiusMetrics:
    """Container for Pontius disagreement metrics."""

    quantity_disagreement: float
    allocation_disagreement: float
    total_disagreement: float
    exchange: float
    shift: float

    def __post_init__(self):
        """Validate metrics consistency."""
        expected_total = self.quantity_disagreement + self.allocation_disagreement
        if not np.isclose(self.total_disagreement, expected_total, rtol=1e-10):
            warnings.warn(
                f"Total disagreement ({self.total_disagreement}) does not equal "
                f"sum of components ({expected_total})"
            )


@dataclass
class IntensityLevelResults:
    """Results for interval-level intensity analysis."""

    periods: List[str]
    annual_change_rate: List[float]
    uniform_rate: float
    change_intensity: List[float]
    total_change: List[float]
    stationary_test: List[bool]

    def to_dataframe(self) -> DataFrame:
        """Convert to pandas DataFrame for analysis."""
        return pd.DataFrame(
            {
                "Period": self.periods,
                "Annual_Change_Rate": self.annual_change_rate,
                "Uniform_Rate": self.uniform_rate,
                "Change_Intensity": self.change_intensity,
                "Total_Change": self.total_change,
                "Is_Stationary": self.stationary_test,
            }
        )


@dataclass
class CategoryLevelResults:
    """Results for category-level intensity analysis."""

    categories: List[str]
    gain_intensity: List[float]
    loss_intensity: List[float]
    uniform_gain_intensity: float
    uniform_loss_intensity: float
    gain_targeting: List[bool]
    loss_avoiding: List[bool]

    def to_dataframe(self) -> DataFrame:
        """Convert to pandas DataFrame for analysis."""
        return pd.DataFrame(
            {
                "Category": self.categories,
                "Gain_Intensity": self.gain_intensity,
                "Loss_Intensity": self.loss_intensity,
                "Uniform_Gain": self.uniform_gain_intensity,
                "Uniform_Loss": self.uniform_loss_intensity,
                "Is_Gain_Targeting": self.gain_targeting,
                "Is_Loss_Avoiding": self.loss_avoiding,
            }
        )


@dataclass
class TransitionLevelResults:
    """Results for transition-level intensity analysis."""

    transitions: List[Tuple[str, str]]
    transition_intensity: List[float]
    uniform_transition_intensity: List[float]
    targeting_avoiding: List[str]

    def to_dataframe(self) -> DataFrame:
        """Convert to pandas DataFrame for analysis."""
        return pd.DataFrame(
            {
                "From_Category": [t[0] for t in self.transitions],
                "To_Category": [t[1] for t in self.transitions],
                "Transition_Intensity": self.transition_intensity,
                "Uniform_Intensity": self.uniform_transition_intensity,
                "Behavior": self.targeting_avoiding,
            }
        )


class AdvancedPontius:
    """
    Advanced implementation of Pontius methodology for LULC change analysis.

    This class provides comprehensive tools for analyzing land use and land cover
    change using the methodologies developed by Robert Gilmore Pontius Jr.
    """

    def __init__(self, confusion_matrix: Matrix, time_intervals: List[float]):
        """
        Initialize with confusion matrix and time intervals.

        Parameters
        ----------
        confusion_matrix : np.ndarray
            Square confusion matrix where M[i,j] is the area that changed
            from category i to category j.
        time_intervals : List[float]
            Time intervals between observations in years.
        """
        self.confusion_matrix = np.array(confusion_matrix)
        self.time_intervals = time_intervals
        self.n_categories = self.confusion_matrix.shape[0]
        self.total_area = np.sum(self.confusion_matrix)

        # Validate input
        self._validate_inputs()

    def _validate_inputs(self):
        """Validate input data consistency."""
        if self.confusion_matrix.shape[0] != self.confusion_matrix.shape[1]:
            raise ValueError("Confusion matrix must be square")

        if np.any(self.confusion_matrix < 0):
            raise ValueError("Confusion matrix cannot contain negative values")

        if len(self.time_intervals) == 0:
            raise ValueError("At least one time interval must be provided")

    def calculate_disagreement_metrics(
        self, reference_map: Matrix, comparison_map: Matrix
    ) -> PontiusMetrics:
        """
        Calculate Pontius disagreement metrics.

        Parameters
        ----------
        reference_map : np.ndarray
            Reference (ground truth) categorical map
        comparison_map : np.ndarray
            Comparison (predicted/simulated) categorical map

        Returns
        -------
        PontiusMetrics
            Object containing all disagreement metrics
        """
        # Create confusion matrix
        confusion = self._create_confusion_matrix(reference_map, comparison_map)

        # Calculate total disagreement
        total_disagreement = 1 - np.trace(confusion) / np.sum(confusion)

        # Calculate quantity disagreement
        marginal_ref = np.sum(confusion, axis=1)
        marginal_comp = np.sum(confusion, axis=0)
        quantity_disagreement = (
            0.5 * np.sum(np.abs(marginal_ref - marginal_comp)) / np.sum(confusion)
        )

        # Calculate allocation disagreement
        # Minimum of off-diagonal sums for each category
        allocation_components = []
        for k in range(self.n_categories):
            off_diag_row = np.sum(confusion[k, :]) - confusion[k, k]
            off_diag_col = np.sum(confusion[:, k]) - confusion[k, k]
            allocation_components.append(min(off_diag_row, off_diag_col))

        allocation_disagreement = np.sum(allocation_components) / np.sum(confusion)

        # Calculate exchange and shift
        exchange = (
            2
            * min(
                np.sum(confusion)
                - np.trace(confusion)
                - quantity_disagreement * np.sum(confusion),
                quantity_disagreement * np.sum(confusion),
            )
            / np.sum(confusion)
        )

        shift = allocation_disagreement - exchange

        return PontiusMetrics(
            quantity_disagreement=quantity_disagreement,
            allocation_disagreement=allocation_disagreement,
            total_disagreement=total_disagreement,
            exchange=exchange,
            shift=shift,
        )

    def _create_confusion_matrix(self, map1: Matrix, map2: Matrix) -> Matrix:
        """Create confusion matrix from two categorical maps."""
        if map1.shape != map2.shape:
            raise ValueError("Maps must have the same dimensions")

        unique_vals1 = np.unique(map1)
        unique_vals2 = np.unique(map2)
        all_categories = sorted(set(unique_vals1) | set(unique_vals2))

        n_cats = len(all_categories)
        confusion = np.zeros((n_cats, n_cats))

        for i, cat1 in enumerate(all_categories):
            for j, cat2 in enumerate(all_categories):
                confusion[i, j] = np.sum((map1 == cat1) & (map2 == cat2))

        return confusion

    def interval_level_analysis(self) -> IntensityLevelResults:
        """
        Perform interval-level intensity analysis.

        Returns
        -------
        IntensityLevelResults
            Results of interval-level analysis
        """
        periods = [f"Period_{i+1}" for i in range(len(self.time_intervals))]
        annual_change_rates = []
        change_intensities = []
        total_changes = []

        # Calculate uniform rate across all intervals
        total_time = sum(self.time_intervals)
        total_change_area = np.sum(self.confusion_matrix) - np.trace(
            self.confusion_matrix
        )
        uniform_rate = (total_change_area / np.sum(self.confusion_matrix)) / total_time

        for i, dt in enumerate(self.time_intervals):
            # Calculate change for this interval
            change_area = np.sum(self.confusion_matrix) - np.trace(
                self.confusion_matrix
            )
            annual_rate = (change_area / np.sum(self.confusion_matrix)) / dt

            annual_change_rates.append(annual_rate)
            change_intensities.append(
                annual_rate / uniform_rate if uniform_rate > 0 else 1.0
            )
            total_changes.append(change_area)

        # Test for stationarity (simplified)
        stationary_test = [
            abs(rate - uniform_rate) < 0.01 * uniform_rate
            for rate in annual_change_rates
        ]

        return IntensityLevelResults(
            periods=periods,
            annual_change_rate=annual_change_rates,
            uniform_rate=uniform_rate,
            change_intensity=change_intensities,
            total_change=total_changes,
            stationary_test=stationary_test,
        )

    def category_level_analysis(
        self, category_names: Optional[List[str]] = None
    ) -> CategoryLevelResults:
        """
        Perform category-level intensity analysis.

        Parameters
        ----------
        category_names : List[str], optional
            Names for categories. If None, uses generic names.

        Returns
        -------
        CategoryLevelResults
            Results of category-level analysis
        """
        if category_names is None:
            category_names = [f"Category_{i+1}" for i in range(self.n_categories)]

        # Calculate gains and losses for each category
        gains = np.sum(self.confusion_matrix, axis=0) - np.diag(self.confusion_matrix)
        losses = np.sum(self.confusion_matrix, axis=1) - np.diag(self.confusion_matrix)

        # Calculate total non-diagonal area
        total_gain = np.sum(gains)
        total_loss = np.sum(losses)

        # Calculate intensities
        gain_intensities = []
        loss_intensities = []

        for i in range(self.n_categories):
            # Area available for gain (total area minus area already in this category)
            available_for_gain = (
                np.sum(self.confusion_matrix) - np.sum(self.confusion_matrix, axis=0)[i]
            )
            gain_intensity = (
                gains[i] / available_for_gain if available_for_gain > 0 else 0
            )

            # Area available for loss (area currently in this category)
            available_for_loss = np.sum(self.confusion_matrix, axis=1)[i]
            loss_intensity = (
                losses[i] / available_for_loss if available_for_loss > 0 else 0
            )

            gain_intensities.append(gain_intensity)
            loss_intensities.append(loss_intensity)

        # Calculate uniform intensities
        uniform_gain_intensity = total_gain / (
            np.sum(self.confusion_matrix) * (self.n_categories - 1)
        )
        uniform_loss_intensity = total_loss / (
            np.sum(self.confusion_matrix) * (self.n_categories - 1)
        )

        # Determine targeting/avoiding behavior
        gain_targeting = [gi > uniform_gain_intensity for gi in gain_intensities]
        loss_avoiding = [li < uniform_loss_intensity for li in loss_intensities]

        return CategoryLevelResults(
            categories=category_names,
            gain_intensity=gain_intensities,
            loss_intensity=loss_intensities,
            uniform_gain_intensity=uniform_gain_intensity,
            uniform_loss_intensity=uniform_loss_intensity,
            gain_targeting=gain_targeting,
            loss_avoiding=loss_avoiding,
        )

    def transition_level_analysis(
        self,
        gaining_category: int,
        losing_category: int,
        category_names: Optional[List[str]] = None,
    ) -> TransitionLevelResults:
        """
        Perform transition-level intensity analysis for specific transition.

        Parameters
        ----------
        gaining_category : int
            Index of the gaining category
        losing_category : int
            Index of the losing category
        category_names : List[str], optional
            Names for categories

        Returns
        -------
        TransitionLevelResults
            Results of transition-level analysis
        """
        if category_names is None:
            category_names = [f"Category_{i+1}" for i in range(self.n_categories)]

        transitions = []
        transition_intensities = []
        uniform_intensities = []
        targeting_avoiding = []

        # Analyze the specific transition
        from_cat = losing_category
        to_cat = gaining_category

        # Transition size
        transition_size = self.confusion_matrix[from_cat, to_cat]

        # Available area for this transition
        available_area = (
            np.sum(self.confusion_matrix[from_cat, :])
            - self.confusion_matrix[from_cat, from_cat]
        )

        # Transition intensity
        trans_intensity = transition_size / available_area if available_area > 0 else 0

        # Uniform transition intensity
        uniform_intensity = np.sum(self.confusion_matrix[:, to_cat]) / (
            np.sum(self.confusion_matrix) - np.sum(np.diag(self.confusion_matrix))
        )

        # Determine behavior
        if trans_intensity > uniform_intensity:
            behavior = "Targeting"
        elif trans_intensity < uniform_intensity:
            behavior = "Avoiding"
        else:
            behavior = "Uniform"

        transitions.append((category_names[from_cat], category_names[to_cat]))
        transition_intensities.append(trans_intensity)
        uniform_intensities.append(uniform_intensity)
        targeting_avoiding.append(behavior)

        return TransitionLevelResults(
            transitions=transitions,
            transition_intensity=transition_intensities,
            uniform_transition_intensity=uniform_intensities,
            targeting_avoiding=targeting_avoiding,
        )

    def generate_comprehensive_report(
        self,
        category_names: Optional[List[str]] = None,
        output_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive Pontius analysis report.

        Parameters
        ----------
        category_names : List[str], optional
            Names for categories
        output_file : str, optional
            Path to save report as JSON

        Returns
        -------
        Dict[str, Any]
            Complete analysis results
        """
        if category_names is None:
            category_names = [f"Category_{i+1}" for i in range(self.n_categories)]

        # Perform all levels of analysis
        interval_results = self.interval_level_analysis()
        category_results = self.category_level_analysis(category_names)

        # Compile comprehensive report
        report = {
            "metadata": {
                "n_categories": self.n_categories,
                "total_area": self.total_area,
                "time_intervals": self.time_intervals,
                "analysis_date": pd.Timestamp.now().isoformat(),
            },
            "interval_level": {
                "uniform_rate": interval_results.uniform_rate,
                "periods": interval_results.periods,
                "annual_change_rates": interval_results.annual_change_rate,
                "change_intensities": interval_results.change_intensity,
                "stationarity_tests": interval_results.stationary_test,
            },
            "category_level": {
                "categories": category_results.categories,
                "gain_intensities": category_results.gain_intensity,
                "loss_intensities": category_results.loss_intensity,
                "uniform_gain_intensity": category_results.uniform_gain_intensity,
                "uniform_loss_intensity": category_results.uniform_loss_intensity,
                "gain_targeting": category_results.gain_targeting,
                "loss_avoiding": category_results.loss_avoiding,
            },
            "confusion_matrix": self.confusion_matrix.tolist(),
        }

        # Save to file if requested
        if output_file:
            import json

            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)

        return report
