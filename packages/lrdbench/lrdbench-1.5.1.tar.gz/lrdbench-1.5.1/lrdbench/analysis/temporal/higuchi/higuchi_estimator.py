import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from models.estimators.base_estimator import BaseEstimator


class HiguchiEstimator(BaseEstimator):
    """
    Higuchi Method estimator for fractal dimension and Hurst parameter.

    The Higuchi method is an efficient algorithm for estimating the fractal
    dimension of a time series. It is based on the relationship between the
    length of the curve and the time interval used to measure it.

    The method works by:
    1. Computing the curve length for different time intervals k
    2. Fitting a power law relationship: L(k) ~ k^(-D)
    3. The fractal dimension D is related to the Hurst parameter H by: H = 2 - D

    Parameters
    ----------
    min_k : int, default=2
        Minimum time interval for curve length calculation.
    max_k : int, optional
        Maximum time interval. If None, uses n/4 where n is data length.
    k_values : List[int], optional
        Specific k values to use. If provided, overrides min/max.
    """

    def __init__(self, min_k: int = 2, max_k: int = None, k_values: List[int] = None):
        super().__init__(min_k=min_k, max_k=max_k, k_values=k_values)
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if self.parameters["min_k"] < 2:
            raise ValueError("min_k must be at least 2")

        if self.parameters["max_k"] is not None:
            if self.parameters["max_k"] <= self.parameters["min_k"]:
                raise ValueError("max_k must be greater than min_k")

        if self.parameters["k_values"] is not None:
            if not all(k >= 2 for k in self.parameters["k_values"]):
                raise ValueError("All k values must be at least 2")
            if not all(
                k1 < k2
                for k1, k2 in zip(
                    self.parameters["k_values"][:-1], self.parameters["k_values"][1:]
                )
            ):
                raise ValueError("k values must be in ascending order")

    def estimate(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the fractal dimension and Hurst parameter using Higuchi method.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing estimation results:
            - 'fractal_dimension': Estimated fractal dimension
            - 'hurst_parameter': Estimated Hurst parameter (H = 2 - D)
            - 'k_values': List of k values used
            - 'curve_lengths': List of average curve lengths for each k
            - 'r_squared': R-squared value of the linear fit
            - 'std_error': Standard error of the fractal dimension estimate
            - 'confidence_interval': 95% confidence interval for D
        """
        if len(data) < 10:
            raise ValueError("Data length must be at least 10 for Higuchi method")

        # Determine k values
        if self.parameters["k_values"] is not None:
            k_values = self.parameters["k_values"]
        else:
            max_k = self.parameters["max_k"]
            if max_k is None:
                max_k = len(data) // 4

            # Generate k values (typically powers of 2 or similar)
            k_values = []
            k = self.parameters["min_k"]
            while k <= max_k and k <= len(data) // 2:
                k_values.append(k)
                k = int(k * 1.5)  # Geometric progression

        if len(k_values) < 3:
            raise ValueError("Need at least 3 k values for reliable estimation")

        # Calculate curve lengths for each k
        curve_lengths = []
        for k in k_values:
            length = self._calculate_curve_length(data, k)
            curve_lengths.append(length)

        # Filter invalid points (non-positive curve lengths)
        k_arr = np.asarray(k_values, dtype=float)
        lengths_arr = np.asarray(curve_lengths, dtype=float)
        valid_mask = (
            np.isfinite(lengths_arr)
            & (lengths_arr > 0)
            & np.isfinite(k_arr)
            & (k_arr > 1)
        )
        valid_k = k_arr[valid_mask]
        valid_lengths = lengths_arr[valid_mask]

        if valid_k.size < 3:
            raise ValueError(
                "Insufficient valid Higuchi points (need >=3 after filtering non-positive values)"
            )

        # Fit power law relationship: log(L) = -D * log(k) + c
        log_k = np.log(valid_k)
        log_lengths = np.log(valid_lengths)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_k, log_lengths
        )

        # Fractal dimension is the negative of the slope
        D = -slope

        # Hurst parameter: H = 2 - D
        H = 2 - D

        # Calculate confidence interval for fractal dimension
        n_points = len(k_values)
        t_critical = stats.t.ppf(0.975, n_points - 2)  # 95% CI
        ci_lower = D - t_critical * std_err
        ci_upper = D + t_critical * std_err

        self.results = {
            "fractal_dimension": D,
            "hurst_parameter": H,
            "k_values": valid_k.tolist(),
            "curve_lengths": valid_lengths.tolist(),
            "r_squared": r_value**2,
            "std_error": std_err,
            "confidence_interval": (ci_lower, ci_upper),
            "p_value": p_value,
            "intercept": intercept,
            "slope": slope,
            "log_k": log_k,
            "log_lengths": log_lengths,
        }

        return self.results

    def _calculate_curve_length(self, data: np.ndarray, k: int) -> float:
        """
        Calculate the average curve length for a given time interval k.

        Parameters
        ----------
        data : np.ndarray
            Input time series data.
        k : int
            Time interval for curve length calculation.

        Returns
        -------
        float
            Average curve length across all possible starting points.
        """
        n = len(data)
        lengths = []

        # Calculate curve length for each starting point
        for m in range(k):
            # Number of points in this segment
            n_m = (n - m - 1) // k

            if n_m < 1:
                continue

            # Calculate curve length for this segment
            length = 0
            for i in range(n_m):
                idx1 = m + i * k
                idx2 = m + (i + 1) * k

                if idx2 < n:
                    # Add the distance between consecutive points
                    length += abs(data[idx2] - data[idx1])

            # Normalize by the number of intervals
            if n_m > 0:
                length = length * (n - 1) / (k**2 * n_m)
                lengths.append(length)

        # Return average length
        if not lengths:
            raise ValueError(f"No valid curve lengths calculated for k = {k}")

        return np.mean(lengths)

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

        # Calculate confidence interval for fractal dimension
        n_points = len(self.results["k_values"])
        t_critical = stats.t.ppf((1 + confidence_level) / 2, n_points - 2)

        D = self.results["fractal_dimension"]
        std_err = self.results["std_error"]

        ci_lower_D = D - t_critical * std_err
        ci_upper_D = D + t_critical * std_err

        # Convert to Hurst parameter confidence interval
        ci_upper_H = 2 - ci_lower_D  # Note the reversal due to H = 2 - D
        ci_lower_H = 2 - ci_upper_D

        return {
            "fractal_dimension": (ci_lower_D, ci_upper_D),
            "hurst_parameter": (ci_lower_H, ci_upper_H),
        }

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
            "n_k_values": len(self.results["k_values"]),
        }

    def plot_scaling(self, save_path: str = None) -> None:
        """
        Plot the Higuchi scaling relationship.

        Parameters
        ----------
        save_path : str, optional
            Path to save the plot. If None, displays the plot.
        """
        if not self.results:
            raise ValueError("No estimation results available. Run estimate() first.")

        import matplotlib.pyplot as plt

        k_values = self.results["k_values"]
        curve_lengths = self.results["curve_lengths"]
        D = self.results["fractal_dimension"]
        H = self.results["hurst_parameter"]
        r_squared = self.results["r_squared"]

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Curve length vs k (log-log)
        log_k = np.log(k_values)
        log_lengths = np.log(curve_lengths)

        ax1.scatter(log_k, log_lengths, color="blue", alpha=0.7, label="Data points")

        # Plot fitted line
        x_fit = np.array([min(log_k), max(log_k)])
        y_fit = -D * x_fit + self.results["intercept"]
        ax1.plot(
            x_fit,
            y_fit,
            "r--",
            linewidth=2,
            label=f"Fit: D = {D:.3f} (R² = {r_squared:.3f})",
        )

        ax1.set_xlabel("log(k)")
        ax1.set_ylabel("log(Curve Length)")
        ax1.set_title("Higuchi Scaling Relationship")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Curve length vs k (linear scale)
        ax2.scatter(
            k_values, curve_lengths, color="green", alpha=0.7, label="Data points"
        )

        # Plot fitted curve
        x_fit_linear = np.linspace(min(k_values), max(k_values), 100)
        y_fit_linear = np.exp(self.results["intercept"]) * (x_fit_linear ** (-D))
        ax2.plot(
            x_fit_linear,
            y_fit_linear,
            "r--",
            linewidth=2,
            label=f"Power law fit: D = {D:.3f}",
        )

        ax2.set_xlabel("Time Interval k")
        ax2.set_ylabel("Curve Length")
        ax2.set_title("Curve Length vs Time Interval")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Add text box with results
        textstr = (
            f"Fractal Dimension: {D:.3f}\nHurst Parameter: {H:.3f}\nR²: {r_squared:.3f}"
        )
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        ax2.text(
            0.05,
            0.95,
            textstr,
            transform=ax2.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=props,
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

        plt.close()
