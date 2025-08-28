"""
Detrended Fluctuation Analysis (DFA) estimator implementation.

This module provides a class for estimating the Hurst parameter using
Detrended Fluctuation Analysis, which is robust to non-stationarities.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple
import sys
import os

# Add the project root to the path to import BaseEstimator
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class DFAEstimator(BaseEstimator):
    """
    Detrended Fluctuation Analysis (DFA) estimator.

    DFA is a method for quantifying long-range correlations in time series
    that is robust to non-stationarities. It estimates the Hurst parameter
    by analyzing the scaling behavior of detrended fluctuations.

    Parameters
    ----------
    min_box_size : int, optional
        Minimum box size for analysis (default: 4)
    max_box_size : int, optional
        Maximum box size for analysis (default: None, will use n/4)
    box_sizes : array-like, optional
        Specific box sizes to use (default: None)
    polynomial_order : int, optional
        Order of polynomial for detrending (default: 1)
    """

    def __init__(
        self,
        min_box_size: int = 4,
        max_box_size: int = None,
        box_sizes: List[int] = None,
        polynomial_order: int = 1,
    ):
        """
        Initialize the DFA estimator.

        Parameters
        ----------
        min_box_size : int, optional
            Minimum box size for analysis (default: 4)
        max_box_size : int, optional
            Maximum box size for analysis (default: None)
        box_sizes : array-like, optional
            Specific box sizes to use (default: None)
        polynomial_order : int, optional
            Order of polynomial for detrending (default: 1)
        """
        super().__init__(
            min_box_size=min_box_size,
            max_box_size=max_box_size,
            box_sizes=box_sizes,
            polynomial_order=polynomial_order,
        )

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        min_box_size = self.parameters["min_box_size"]
        polynomial_order = self.parameters["polynomial_order"]

        if min_box_size < 2:
            raise ValueError("min_box_size must be at least 2")

        if polynomial_order < 0:
            raise ValueError("polynomial_order must be non-negative")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate Hurst parameter using DFA.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        n = len(data)

        # Determine box sizes
        if self.parameters["box_sizes"] is not None:
            box_sizes = np.array(self.parameters["box_sizes"])
        else:
            min_size = self.parameters["min_box_size"]
            max_size = self.parameters["max_box_size"] or n // 4

            # Create box sizes with approximately equal spacing in log space
            box_sizes = np.unique(
                np.logspace(
                    np.log10(min_size),
                    np.log10(max_size),
                    num=min(20, max_size - min_size + 1),
                    dtype=int,
                )
            )

        # Calculate fluctuations for each box size
        fluctuations = []
        valid_box_sizes = []

        for s in box_sizes:
            if s > n:
                continue

            f = self._calculate_fluctuation(data, s)
            if np.isfinite(f) and f > 0:
                fluctuations.append(f)
                valid_box_sizes.append(s)

        if len(fluctuations) < 3:
            raise ValueError("Insufficient data points for DFA analysis")

        # Linear regression in log-log space (arrays, already filtered >0)
        valid_box_sizes_arr = np.asarray(valid_box_sizes, dtype=float)
        fluctuations_arr = np.asarray(fluctuations, dtype=float)
        log_sizes = np.log(valid_box_sizes_arr)
        log_fluctuations = np.log(fluctuations_arr)

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_sizes, log_fluctuations
        )

        # Hurst parameter is the slope
        H = slope

        # Store results
        self.results = {
            "hurst_parameter": H,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_error": std_err,
            "box_sizes": valid_box_sizes_arr.tolist(),
            "fluctuations": fluctuations_arr.tolist(),
            "log_sizes": log_sizes,
            "log_fluctuations": log_fluctuations,
            "slope": slope,
            "n_points": len(fluctuations),
        }

        return self.results

    def _calculate_fluctuation(self, data: np.ndarray, box_size: int) -> float:
        """
        Calculate detrended fluctuation for a given box size.

        Parameters
        ----------
        data : np.ndarray
            Time series data
        box_size : int
            Size of the box for analysis

        Returns
        -------
        float
            Detrended fluctuation
        """
        n = len(data)
        polynomial_order = self.parameters["polynomial_order"]

        # Calculate cumulative sum
        cumsum = np.cumsum(data - np.mean(data))

        # Number of boxes
        n_boxes = n // box_size

        if n_boxes == 0:
            return 0.0

        # Calculate fluctuations for each box
        fluctuations = []

        for i in range(n_boxes):
            start_idx = i * box_size
            end_idx = start_idx + box_size

            # Extract segment
            segment = cumsum[start_idx:end_idx]
            x = np.arange(box_size)

            # Fit polynomial trend
            if polynomial_order == 0:
                trend = np.mean(segment)
            else:
                coeffs = np.polyfit(x, segment, polynomial_order)
                trend = np.polyval(coeffs, x)

            # Detrend
            detrended = segment - trend

            # Calculate fluctuation
            f = np.mean(detrended**2)
            fluctuations.append(f)

        # Return root mean square fluctuation
        return np.sqrt(np.mean(fluctuations))

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for the estimated Hurst parameter.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level (default: 0.95)

        Returns
        -------
        dict
            Dictionary containing confidence intervals
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # Calculate confidence interval for the slope (Hurst parameter)
        n = self.results["n_points"]
        std_err = self.results["std_error"]
        H = self.results["hurst_parameter"]

        # t-distribution critical value
        alpha = 1 - confidence_level
        t_critical = stats.t.ppf(1 - alpha / 2, n - 2)

        margin_of_error = t_critical * std_err
        ci_lower = H - margin_of_error
        ci_upper = H + margin_of_error

        return {"hurst_parameter": (ci_lower, ci_upper)}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the DFA estimation.

        Returns
        -------
        dict
            Dictionary containing quality metrics
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        return {
            "r_squared": self.results["r_squared"],
            "p_value": self.results["p_value"],
            "std_error": self.results["std_error"],
            "n_points": self.results["n_points"],
            "goodness_of_fit": (
                "excellent"
                if self.results["r_squared"] > 0.95
                else (
                    "good"
                    if self.results["r_squared"] > 0.9
                    else "fair" if self.results["r_squared"] > 0.8 else "poor"
                )
            ),
        }

    def plot_scaling(self, save_path: str = None) -> None:
        """
        Plot the scaling relationship for DFA analysis.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot (default: None)
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot data points
        ax.scatter(
            self.results["log_sizes"],
            self.results["log_fluctuations"],
            alpha=0.7,
            label="Data points",
        )

        # Plot fitted line
        x_fit = np.array(
            [min(self.results["log_sizes"]), max(self.results["log_sizes"])]
        )
        y_fit = self.results["slope"] * x_fit + self.results["intercept"]
        ax.plot(
            x_fit,
            y_fit,
            "r-",
            linewidth=2,
            label=f'Fit: H = {self.results["hurst_parameter"]:.3f}',
        )

        ax.set_xlabel("log(Box Size)")
        ax.set_ylabel("log(Fluctuation)")
        ax.set_title("DFA Scaling Analysis")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add R² value
        ax.text(
            0.05,
            0.95,
            f'R² = {self.results["r_squared"]:.3f}',
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()
