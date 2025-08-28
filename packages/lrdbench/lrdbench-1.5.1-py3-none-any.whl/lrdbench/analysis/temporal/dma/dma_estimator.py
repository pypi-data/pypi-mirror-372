import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class DMAEstimator(BaseEstimator):
    """
    Detrended Moving Average (DMA) estimator for Hurst parameter.

    The DMA method is a variant of DFA that uses a moving average instead
    of polynomial fitting for detrending. It is computationally efficient
    and robust to various types of non-stationarity.

    The method works by:
    1. Computing the cumulative sum of the time series
    2. For each window size, calculating the moving average
    3. Detrending by subtracting the moving average
    4. Computing the fluctuation function
    5. Fitting a power law relationship: F(n) ~ n^H

    Parameters
    ----------
    min_window_size : int, default=4
        Minimum window size for DMA calculation.
    max_window_size : int, optional
        Maximum window size. If None, uses n/4 where n is data length.
    window_sizes : List[int], optional
        Specific window sizes to use. If provided, overrides min/max.
    overlap : bool, default=True
        Whether to use overlapping windows for moving average.
    """

    def __init__(
        self,
        min_window_size: int = 4,
        max_window_size: int = None,
        window_sizes: List[int] = None,
        overlap: bool = True,
    ):
        super().__init__(
            min_window_size=min_window_size,
            max_window_size=max_window_size,
            window_sizes=window_sizes,
            overlap=overlap,
        )
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["min_window_size"] < 3:
            raise ValueError("min_window_size must be at least 3")

        if self.parameters["max_window_size"] is not None:
            if self.parameters["max_window_size"] <= self.parameters["min_window_size"]:
                raise ValueError("max_window_size must be greater than min_window_size")

        if self.parameters["window_sizes"] is not None:
            if not all(size >= 3 for size in self.parameters["window_sizes"]):
                raise ValueError("All window sizes must be at least 3")
            if not all(
                size1 < size2
                for size1, size2 in zip(
                    self.parameters["window_sizes"][:-1],
                    self.parameters["window_sizes"][1:],
                )
            ):
                raise ValueError("Window sizes must be in ascending order")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using DMA method.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing estimation results:
            - 'hurst_parameter': Estimated Hurst parameter
            - 'window_sizes': List of window sizes used
            - 'fluctuation_values': List of fluctuation values for each window size
            - 'r_squared': R-squared value of the linear fit
            - 'std_error': Standard error of the Hurst parameter estimate
            - 'confidence_interval': 95% confidence interval for H
        """
        if len(data) < 10:
            raise ValueError("Data length must be at least 10 for DMA analysis")

        # Determine window sizes
        if self.parameters["window_sizes"] is not None:
            window_sizes = self.parameters["window_sizes"]
        else:
            max_size = self.parameters["max_window_size"]
            if max_size is None:
                max_size = len(data) // 4

            # Generate window sizes (powers of 2 or similar)
            window_sizes = []
            size = self.parameters["min_window_size"]
            while size <= max_size and size <= len(data) // 2:
                window_sizes.append(size)
                size = int(size * 1.5)  # Geometric progression

        if len(window_sizes) < 3:
            raise ValueError("Need at least 3 window sizes for reliable estimation")

        # Calculate fluctuation values for each window size
        fluctuation_values = []
        for window_size in window_sizes:
            fluctuation = self._calculate_fluctuation(data, window_size)
            fluctuation_values.append(fluctuation)

        # Filter out non-positive or non-finite fluctuations before log
        window_sizes_arr = np.asarray(window_sizes, dtype=float)
        fluct_arr = np.asarray(fluctuation_values, dtype=float)
        valid_mask = (
            np.isfinite(fluct_arr)
            & (fluct_arr > 0)
            & np.isfinite(window_sizes_arr)
            & (window_sizes_arr > 1)
        )
        valid_sizes = window_sizes_arr[valid_mask]
        valid_fluct = fluct_arr[valid_mask]

        if valid_sizes.size < 3:
            raise ValueError(
                "Insufficient valid fluctuation points for DMA (need >=3 after filtering non-positive values)"
            )

        # Fit power law relationship: log(F) = H * log(n) + c using filtered points
        log_sizes = np.log(valid_sizes)
        log_fluctuations = np.log(valid_fluct)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_sizes, log_fluctuations
        )

        # Hurst parameter is the slope
        H = slope

        # Calculate confidence interval
        n_points = len(window_sizes)
        t_critical = stats.t.ppf(0.975, n_points - 2)  # 95% CI
        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err

        self.results = {
            "hurst_parameter": H,
            "window_sizes": valid_sizes.tolist(),
            "fluctuation_values": valid_fluct.tolist(),
            "r_squared": r_value**2,
            "std_error": std_err,
            "confidence_interval": (ci_lower, ci_upper),
            "p_value": p_value,
            "intercept": intercept,
            "slope": slope,
            "log_sizes": log_sizes,
            "log_fluctuations": log_fluctuations,
        }

        return self.results

    def _calculate_fluctuation(self, data: np.ndarray, window_size: int) -> float:
        """
        Calculate the fluctuation function for a given window size.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.
        window_size : int
            Size of the window for DMA calculation.

        Returns
        -------
        float
            Fluctuation value for the given window size.
        """
        n = len(data)

        # Calculate cumulative sum
        cumsum = np.cumsum(data - np.mean(data))

        # Calculate moving average
        if self.parameters["overlap"]:
            # Overlapping windows
            moving_avg = np.zeros_like(cumsum)
            half_window = window_size // 2

            for i in range(n):
                start = max(0, i - half_window)
                end = min(n, i + half_window + 1)
                moving_avg[i] = np.mean(cumsum[start:end])
        else:
            # Non-overlapping windows
            moving_avg = np.zeros_like(cumsum)
            for i in range(0, n, window_size):
                end = min(i + window_size, n)
                moving_avg[i:end] = np.mean(cumsum[i:end])

        # Calculate detrended series
        detrended = cumsum - moving_avg

        # Calculate fluctuation (root mean square)
        fluctuation = np.sqrt(np.mean(detrended**2))

        return fluctuation

    def get_confidence_intervals(
        self, confidence_level: float = 0.95
    ) -> Dict[str, Tuple[float, float]]:
        """
        Get confidence intervals for the estimated parameters.

        Parameters
        ----------
        confidence_level : float, default=0.95
            Confidence level for the intervals.

        Returns
        -------
        Dict[str, Tuple[float, float]]
            Dictionary containing confidence intervals.
        """
        if not self.results:
            return {}

        # Calculate confidence interval for Hurst parameter
        n_points = len(self.results["window_sizes"])
        t_critical = stats.t.ppf((1 + confidence_level) / 2, n_points - 2)

        H = self.results["hurst_parameter"]
        std_err = self.results["std_error"]

        ci_lower = H - t_critical * std_err
        ci_upper = H + t_critical * std_err

        return {"hurst_parameter": (ci_lower, ci_upper)}

    def get_estimation_quality(self) -> Dict[str, Any]:
        """
        Get quality metrics for the estimation.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing quality metrics.
        """
        if not self.results:
            return {}

        return {
            "r_squared": self.results["r_squared"],
            "p_value": self.results["p_value"],
            "std_error": self.results["std_error"],
            "n_windows": len(self.results["window_sizes"]),
        }

    def plot_scaling(self, save_path: str = None) -> None:
        """
        Plot the DMA scaling relationship.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot. If None, displays the plot.
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        window_sizes = self.results["window_sizes"]
        fluctuation_values = self.results["fluctuation_values"]
        H = self.results["hurst_parameter"]
        r_squared = self.results["r_squared"]

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Fluctuation vs window size (log-log)
        log_sizes = np.log(window_sizes)
        log_fluctuations = np.log(fluctuation_values)

        ax1.scatter(
            log_sizes, log_fluctuations, color="blue", alpha=0.7, label="Data points"
        )

        # Plot fitted line
        x_fit = np.array([min(log_sizes), max(log_sizes)])
        y_fit = H * x_fit + self.results["intercept"]
        ax1.plot(
            x_fit,
            y_fit,
            "r--",
            linewidth=2,
            label=f"Fit: H = {H:.3f} (R² = {r_squared:.3f})",
        )

        ax1.set_xlabel("log(Window Size)")
        ax1.set_ylabel("log(Fluctuation)")
        ax1.set_title("DMA Scaling Relationship")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Fluctuation vs window size (linear scale)
        ax2.scatter(
            window_sizes,
            fluctuation_values,
            color="green",
            alpha=0.7,
            label="Data points",
        )

        # Plot fitted curve
        x_fit_linear = np.linspace(min(window_sizes), max(window_sizes), 100)
        y_fit_linear = np.exp(self.results["intercept"]) * (x_fit_linear**H)
        ax2.plot(
            x_fit_linear,
            y_fit_linear,
            "r--",
            linewidth=2,
            label=f"Power law fit: H = {H:.3f}",
        )

        ax2.set_xlabel("Window Size")
        ax2.set_ylabel("Fluctuation")
        ax2.set_title("Fluctuation vs Window Size")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

        plt.close()
