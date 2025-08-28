"""
Whittle-based Hurst parameter estimator.

This module implements a Whittle-based estimator for the Hurst parameter
using maximum likelihood estimation in the frequency domain.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats, signal, optimize
from models.estimators.base_estimator import BaseEstimator


class WhittleEstimator(BaseEstimator):
    """
    Whittle-based Hurst parameter estimator.

    This estimator uses maximum likelihood estimation in the frequency domain
    to estimate the Hurst parameter. It can use either the standard Whittle
    likelihood or the local Whittle variant.

    Parameters
    ----------
    min_freq_ratio : float, optional (default=0.01)
        Minimum frequency ratio (relative to Nyquist) for fitting.
    max_freq_ratio : float, optional (default=0.1)
        Maximum frequency ratio (relative to Nyquist) for fitting.
    use_local_whittle : bool, optional (default=True)
        Whether to use local Whittle estimation (more robust).
    use_welch : bool, optional (default=True)
        Whether to use Welch's method for PSD estimation.
    window : str, optional (default='hann')
        Window function for Welch's method.
    nperseg : int, optional (default=None)
        Length of each segment for Welch's method. If None, uses n/8.
    """

    def __init__(
        self,
        min_freq_ratio=0.01,
        max_freq_ratio=0.1,
        use_local_whittle=True,
        use_welch=True,
        window="hann",
        nperseg=None,
    ):
        super().__init__()
        self.min_freq_ratio = min_freq_ratio
        self.max_freq_ratio = max_freq_ratio
        self.use_local_whittle = use_local_whittle
        self.use_welch = use_welch
        self.window = window
        self.nperseg = nperseg
        self.results = {}
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not (0 < self.min_freq_ratio < self.max_freq_ratio < 0.5):
            raise ValueError(
                "Frequency ratios must satisfy: 0 < min_freq_ratio < max_freq_ratio < 0.5"
            )

        if self.nperseg is not None and self.nperseg < 2:
            raise ValueError("nperseg must be at least 2")

    def estimate(self, data):
        """
        Estimate Hurst parameter using Whittle likelihood.

        Parameters
        ----------
        data : array-like
            Time series data.

        Returns
        -------
        dict
            Dictionary containing:
            - hurst_parameter: Estimated Hurst parameter
            - scale_parameter: Estimated scale parameter (if applicable)
            - log_likelihood: Log-likelihood value
            - r_squared: R-squared value of the fit
            - m: Number of frequency points used in fitting
            - log_model: Log model spectrum values
            - log_periodogram: Log periodogram values
        """
        data = np.asarray(data)
        n = len(data)

        if self.nperseg is None:
            # Ensure nperseg is not larger than data length
            self.nperseg = min(max(n // 8, 64), n)

        # Compute periodogram
        if self.use_welch:
            freqs, psd = signal.welch(
                data, window=self.window, nperseg=self.nperseg, scaling="density"
            )
        else:
            freqs, psd = signal.periodogram(data, window=self.window, scaling="density")

        # Select frequency range for fitting
        nyquist = 0.5
        min_freq = self.min_freq_ratio * nyquist
        max_freq = self.max_freq_ratio * nyquist

        mask = (freqs >= min_freq) & (freqs <= max_freq)
        freqs_sel = freqs[mask]
        psd_sel = psd[mask]

        if len(freqs_sel) < 3:
            raise ValueError("Insufficient frequency points for fitting")

        # Filter out zero/negative PSD values
        valid_mask = psd_sel > 0
        freqs_sel = freqs_sel[valid_mask]
        psd_sel = psd_sel[valid_mask]

        if len(freqs_sel) < 3:
            raise ValueError("Insufficient valid PSD points for fitting")

        if self.use_local_whittle:
            hurst, scale, log_lik = self._local_whittle_estimate(freqs_sel, psd_sel)
        else:
            hurst, scale, log_lik = self._standard_whittle_estimate(freqs_sel, psd_sel)

        # Compute R-squared for the fit
        log_model = np.log(self._fgn_spectrum(freqs_sel, hurst, scale))
        log_periodogram = np.log(psd_sel)

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            log_model, log_periodogram
        )
        r_squared = r_value**2

        self.results = {
            "hurst_parameter": float(hurst),
            "d_parameter": float(hurst - 0.5),  # d = H - 0.5 for fGn
            "scale_parameter": float(scale),
            "log_likelihood": float(log_lik),
            "r_squared": float(r_squared),
            "slope": float(slope),
            "intercept": float(intercept),
            "p_value": float(p_value),
            "std_error": float(std_err),
            "m": int(len(freqs_sel)),
            "log_model": log_model,
            "log_periodogram": log_periodogram,
            "frequency": freqs_sel,
            "periodogram": psd_sel,
        }
        return self.results

    def _fgn_spectrum(self, freqs, hurst, scale=1.0):
        """Compute fGn power spectrum."""
        # fGn spectrum: S(f) = scale * |2*sin(π*f)|^(2H-2)
        return scale * np.abs(2 * np.sin(np.pi * freqs)) ** (2 * hurst - 2)

    def _local_whittle_estimate(self, freqs, psd):
        """Estimate using local Whittle likelihood."""

        def neg_log_likelihood(params):
            hurst, scale = params
            if hurst <= 0 or hurst >= 1 or scale <= 0:
                return np.inf

            model_spectrum = self._fgn_spectrum(freqs, hurst, scale)

            # Local Whittle likelihood
            log_lik = np.sum(np.log(model_spectrum) + psd / model_spectrum)
            return log_lik

        # Initial guess
        x0 = [0.5, np.mean(psd)]

        # Optimize
        result = optimize.minimize(
            neg_log_likelihood,
            x0,
            bounds=[(0.01, 0.99), (1e-6, None)],
            method="L-BFGS-B",
        )

        if result.success:
            hurst, scale = result.x
            log_lik = -result.fun
        else:
            # Fallback to simple regression
            hurst, scale, log_lik = self._fallback_estimate(freqs, psd)

        return hurst, scale, log_lik

    def _standard_whittle_estimate(self, freqs, psd):
        """Estimate using standard Whittle likelihood."""

        def neg_log_likelihood(params):
            hurst, scale = params
            if hurst <= 0 or hurst >= 1 or scale <= 0:
                return np.inf

            model_spectrum = self._fgn_spectrum(freqs, hurst, scale)

            # Standard Whittle likelihood
            log_lik = np.sum(np.log(model_spectrum) + psd / model_spectrum)
            return log_lik

        # Initial guess
        x0 = [0.5, np.mean(psd)]

        # Optimize
        result = optimize.minimize(
            neg_log_likelihood,
            x0,
            bounds=[(0.01, 0.99), (1e-6, None)],
            method="L-BFGS-B",
        )

        if result.success:
            hurst, scale = result.x
            log_lik = -result.fun
        else:
            # Fallback to simple regression
            hurst, scale, log_lik = self._fallback_estimate(freqs, psd)

        return hurst, scale, log_lik

    def _fallback_estimate(self, freqs, psd):
        """Fallback estimation using simple regression."""
        # Simple power law fit as fallback
        log_f = np.log(freqs)
        log_psd = np.log(psd)

        slope, intercept, _, _, _ = stats.linregress(log_f, log_psd)
        beta = -slope
        hurst = (beta + 1) / 2
        scale = np.exp(intercept)

        # Compute log-likelihood
        model_spectrum = self._fgn_spectrum(freqs, hurst, scale)
        log_lik = -np.sum(np.log(model_spectrum) + psd / model_spectrum)

        return hurst, scale, log_lik

    def plot_scaling(self, save_path=None):
        """Plot the scaling relationship and PSD."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        plt.figure(figsize=(15, 4))

        # Log-log scaling relationship
        plt.subplot(1, 3, 1)
        x = self.results["log_model"]
        y = self.results["log_periodogram"]

        plt.scatter(x, y, s=40, alpha=0.7, label="Data points")

        # Plot fitted line
        slope, intercept, _, _, _ = stats.linregress(x, y)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept
        plt.plot(x_fit, y_fit, "r--", label="Linear fit")

        plt.xlabel("log(model spectrum)")
        plt.ylabel("log(periodogram)")
        plt.title("Whittle Fit (log-log)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Log-log components
        plt.subplot(1, 3, 2)
        plt.scatter(np.exp(x), np.exp(y), s=30, alpha=0.7)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Model spectrum")
        plt.ylabel("Periodogram")
        plt.title("Whittle Components (log-log)")
        plt.grid(True, which="both", ls=":", alpha=0.3)

        # Plain PSD over frequency for additional context
        try:
            import numpy as _np

            n_points = len(y)
            # Create a pseudo-frequency axis for visualization
            freq_axis = _np.linspace(0, 0.5, n_points)
            plt.subplot(1, 3, 3)
            plt.plot(freq_axis, _np.exp(y), alpha=0.7)
            plt.xlabel("Frequency (proxy)")
            plt.ylabel("Periodogram")
            plt.title("PSD (linear scale, proxy)")
            plt.grid(True, alpha=0.3)
        except Exception:
            pass

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()
