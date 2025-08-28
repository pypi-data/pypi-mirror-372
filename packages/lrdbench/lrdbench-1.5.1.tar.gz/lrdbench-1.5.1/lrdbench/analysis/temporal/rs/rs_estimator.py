"""
Rescaled Range (R/S) Analysis estimator.

This module provides the RSEstimator class for estimating the Hurst parameter
using the classic R/S (Rescaled Range) method.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats
import sys
import os

# Add the project root to the path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class RSEstimator(BaseEstimator):
    """
    Rescaled Range (R/S) Analysis estimator.

    The R/S method estimates the Hurst parameter by analyzing the scaling
    behavior of the rescaled range statistic across different time scales.

    Parameters
    ----------
    min_scale : int, optional
        Minimum scale (window size) to use (default: 10)
    max_scale : int, optional
        Maximum scale (window size) to use (default: None, uses n/4)
    num_scales : int, optional
        Number of scales to use (default: 20)
    """

    def __init__(
        self,
        min_window_size: int = 10,
        max_window_size: Optional[int] = None,
        window_sizes: Optional[List[int]] = None,
        overlap: bool = False,
    ):
        """
        Initialize the R/S estimator.

        Parameters
        ----------
        min_window_size : int, optional
            Minimum window size to use (default: 10)
        max_window_size : int, optional
            Maximum window size to use (default: None, uses n/4)
        window_sizes : List[int], optional
            Custom list of window sizes to use (default: None)
        overlap : bool, optional
            Whether to use overlapping windows (default: False)
        """
        super().__init__(
            min_window_size=min_window_size,
            max_window_size=max_window_size,
            window_sizes=window_sizes,
            overlap=overlap,
        )

        # Results storage
        self.scales = []
        self.rs_values = []
        self.estimated_hurst = None
        self.confidence_interval = None
        self.r_squared = None

        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """
        Validate the estimator parameters.

        Raises:
            ValueError: If parameters are invalid
        """
        if self.parameters["window_sizes"] is not None:
            if len(self.parameters["window_sizes"]) < 3:
                raise ValueError("Need at least 3 window sizes")
            if any(w < 4 for w in self.parameters["window_sizes"]):
                raise ValueError("All window sizes must be at least 4")
            if not all(
                self.parameters["window_sizes"][i]
                < self.parameters["window_sizes"][i + 1]
                for i in range(len(self.parameters["window_sizes"]) - 1)
            ):
                raise ValueError("Window sizes must be in ascending order")
        else:
            if self.parameters["min_window_size"] < 4:
                raise ValueError("min_window_size must be at least 4")
            if (
                self.parameters["max_window_size"] is not None
                and self.parameters["max_window_size"]
                <= self.parameters["min_window_size"]
            ):
                raise ValueError("max_window_size must be greater than min_window_size")

    def estimate(self, data: np.ndarray) -> dict:
        """
        Estimate the Hurst parameter using R/S analysis.

        Parameters
        ----------
        data : np.ndarray
            Time series data

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        # Validate parameters
        self._validate_parameters()

        # Determine window sizes
        if self.parameters["window_sizes"] is not None:
            window_sizes = self.parameters["window_sizes"]
        else:
            if self.parameters["max_window_size"] is None:
                max_window_size = len(data) // 4
            else:
                max_window_size = min(
                    self.parameters["max_window_size"], len(data) // 4
                )

            if max_window_size <= self.parameters["min_window_size"]:
                raise ValueError("Need at least 3 window sizes")

            # Generate window sizes
            window_sizes = np.logspace(
                np.log10(self.parameters["min_window_size"]),
                np.log10(max_window_size),
                20,
                dtype=int,
            )
            window_sizes = np.unique(window_sizes)

        if len(data) < min(window_sizes) * 2:
            raise ValueError(
                f"Data length ({len(data)}) must be at least {min(window_sizes) * 2}"
            )

        if len(window_sizes) < 3:
            raise ValueError("Need at least 3 window sizes")

        # Calculate R/S for each window size
        self.scales = window_sizes
        self.rs_values = []
        for scale in self.scales:
            rs = self._calculate_rs(data, scale)
            self.rs_values.append(rs)

        # Fit power law: R/S ~ scale^H
        log_scales = np.log(self.scales)
        log_rs = np.log(self.rs_values)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_scales, log_rs
        )

        # Store results
        self.estimated_hurst = slope
        self.r_squared = r_value**2
        self.confidence_interval = (slope - 1.96 * std_err, slope + 1.96 * std_err)

        # Store additional regression parameters
        self.intercept = intercept
        self.slope = slope
        self.p_value = p_value

        # Store results in base class format
        self.results = {
            "hurst_parameter": self.estimated_hurst,
            "window_sizes": (
                self.scales.tolist() if hasattr(self.scales, "tolist") else self.scales
            ),
            "rs_values": self.rs_values,
            "r_squared": self.r_squared,
            "std_error": std_err,
            "confidence_interval": self.confidence_interval,
            "p_value": self.p_value,
            "intercept": self.intercept,
            "slope": self.slope,
        }

        # Return results dictionary
        return self.results

    def _calculate_rs(self, data: np.ndarray, scale: int) -> float:
        """
        Calculate the R/S statistic for a given scale.

        Parameters
        ----------
        data : np.ndarray
            Time series data
        scale : int
            Window size (scale)

        Returns
        -------
        float
            R/S statistic
        """
        n = len(data)
        num_windows = n // scale

        if num_windows == 0:
            return 0.0

        rs_values = []

        for i in range(num_windows):
            start_idx = i * scale
            end_idx = start_idx + scale
            window = data[start_idx:end_idx]

            # Calculate mean
            mean_val = np.mean(window)

            # Calculate cumulative deviation
            dev = window - mean_val
            cum_dev = np.cumsum(dev)

            # Calculate range
            R = np.max(cum_dev) - np.min(cum_dev)

            # Calculate standard deviation (sample std)
            S = np.std(window, ddof=1)

            # Avoid division by zero
            if S > 0:
                rs_values.append(R / S)

        # Return mean R/S value
        if not rs_values:
            raise ValueError("No valid R/S values calculated")
        return np.mean(rs_values)

    def _calculate_rs_statistic(self, data: np.ndarray, scale: int) -> float:
        """
        Calculate the R/S statistic for a given scale (alias for _calculate_rs).

        Parameters
        ----------
        data : np.ndarray
            Time series data
        scale : int
            Window size (scale)

        Returns
        -------
        float
            R/S statistic
        """
        return self._calculate_rs(data, scale)

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for estimated parameters.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level (default: 0.95)

        Returns
        -------
        dict
            Dictionary containing confidence intervals for each parameter
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # Calculate confidence interval based on confidence level
        alpha = 1 - confidence_level
        z_score = stats.norm.ppf(1 - alpha / 2)

        hurst = self.results["hurst_parameter"]
        std_err = self.results["std_error"]

        margin = z_score * std_err
        lower = hurst - margin
        upper = hurst + margin

        return {"hurst_parameter": (lower, upper)}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        dict
            Dictionary containing quality metrics
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        # Calculate p-value from R-squared and degrees of freedom
        n = len(self.results["window_sizes"])
        if n > 2:
            # F-statistic = (R²/(k-1)) / ((1-R²)/(n-k)) where k=2 (slope + intercept)
            f_stat = (self.results["r_squared"] / 1) / (
                (1 - self.results["r_squared"]) / (n - 2)
            )
            p_value = 1 - stats.f.cdf(f_stat, 1, n - 2)
        else:
            p_value = 1.0

        return {
            "r_squared": self.results["r_squared"],
            "std_error": self.results["std_error"],
            "p_value": p_value,
            "n_windows": len(self.results["window_sizes"]),
        }

    def plot_scaling(self, figsize: Tuple[int, int] = (10, 6)) -> None:
        """
        Plot the scaling relationship between window sizes and R/S values.

        Parameters
        ----------
        figsize : tuple, optional
            Figure size (default: (10, 6))
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        try:
            import matplotlib.pyplot as plt

            plt.switch_backend("Agg")  # Use non-interactive backend

            fig, ax = plt.subplots(figsize=figsize)

            # Plot R/S vs window size (log-log)
            ax.loglog(
                self.results["window_sizes"],
                self.results["rs_values"],
                "bo-",
                markersize=6,
                linewidth=2,
            )

            # Add fitted line if available
            if "hurst_parameter" in self.results:
                log_scales = np.log(self.results["window_sizes"])
                log_rs = np.log(self.results["rs_values"])

                # Fit line
                slope, intercept, _, _, _ = stats.linregress(log_scales, log_rs)
                log_rs_fitted = intercept + slope * log_scales
                rs_fitted = np.exp(log_rs_fitted)

                ax.loglog(
                    self.results["window_sizes"],
                    rs_fitted,
                    "r--",
                    label=f'Fitted line (H={self.results["hurst_parameter"]:.3f})',
                    linewidth=2,
                )
                ax.legend()

            ax.set_xlabel("Window Size")
            ax.set_ylabel("R/S Value")
            ax.set_title("R/S Scaling Analysis")
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.close(fig)  # Close figure to avoid memory leaks

        except ImportError:
            raise ValueError("Matplotlib is required for plotting")

    def get_confidence_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Get confidence interval for the Hurst parameter estimate.

        Parameters
        ----------
        confidence : float, optional
            Confidence level (default: 0.95)

        Returns
        -------
        tuple
            (lower_bound, upper_bound)
        """
        if not hasattr(self, "results"):
            raise ValueError("Must call estimate() first")

        # Calculate confidence interval using standard error
        alpha = 1 - confidence
        z_score = stats.norm.ppf(1 - alpha / 2)

        hurst = self.results["hurst_parameter"]
        std_err = self.results["std_error"]

        margin = z_score * std_err
        lower = hurst - margin
        upper = hurst + margin

        return (lower, upper)

    def plot_analysis(self, figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        Plot the R/S analysis results.

        Parameters
        ----------
        figsize : tuple, optional
            Figure size (default: (12, 8))
        """
        if not hasattr(self, "results"):
            raise ValueError("Must call estimate() first")

        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Plot 1: R/S vs Scale (log-log)
        ax1.loglog(
            self.results["scales"],
            self.results["rs_values"],
            "bo-",
            label="R/S values",
            markersize=6,
        )

        # Plot fitted line
        log_scales = self.results["log_scales"]
        log_rs_fitted = (
            self.results["intercept"] + self.results["hurst_parameter"] * log_scales
        )
        rs_fitted = np.exp(log_rs_fitted)
        ax1.loglog(
            self.results["scales"],
            rs_fitted,
            "r--",
            label=f'Fitted line (H={self.results["hurst_parameter"]:.3f})',
        )

        ax1.set_xlabel("Scale")
        ax1.set_ylabel("R/S")
        ax1.set_title("R/S Analysis")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Log(R/S) vs Log(Scale)
        ax2.plot(
            log_scales,
            self.results["log_rs"],
            "bo-",
            label="Log(R/S) values",
            markersize=6,
        )
        ax2.plot(
            log_scales,
            log_rs_fitted,
            "r--",
            label=f'Fitted line (slope={self.results["hurst_parameter"]:.3f})',
        )

        ax2.set_xlabel("Log(Scale)")
        ax2.set_ylabel("Log(R/S)")
        ax2.set_title("Log-Log Plot")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def get_results_summary(self) -> dict:
        """
        Get a summary of the estimation results.

        Returns
        -------
        dict
            Summary of results
        """
        if not hasattr(self, "results"):
            raise ValueError("Must call estimate() first")

        lower, upper = self.get_confidence_interval()

        return {
            "method": "R/S Analysis",
            "hurst_parameter": self.results["hurst_parameter"],
            "confidence_interval_95": (lower, upper),
            "r_squared": self.results["r_squared"],
            "p_value": self.results["p_value"],
            "std_error": self.results["std_error"],
            "intercept": self.results["intercept"],
            "slope": self.results["slope"],
            "num_scales": len(self.results["window_sizes"]),
            "min_scale": self.results["window_sizes"][0],
            "max_scale": self.results["window_sizes"][-1],
        }
