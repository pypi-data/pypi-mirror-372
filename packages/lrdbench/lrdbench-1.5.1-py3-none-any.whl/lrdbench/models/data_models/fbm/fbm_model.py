"""
Fractional Brownian Motion (fBm) model implementation.

This module provides a class for generating fractional Brownian motion,
a self-similar Gaussian process with long-range dependence.
"""

import numpy as np
from scipy import linalg
from typing import Optional, Dict, Any, Union
import sys
import os

# Add the parent directory to the path to import BaseModel
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.data_models.base_model import BaseModel


class FractionalBrownianMotion(BaseModel):
    """
    Fractional Brownian Motion (fBm) model.

    Fractional Brownian motion is a self-similar Gaussian process with
    stationary increments. It is characterized by the Hurst parameter H,
    where 0 < H < 1.

    Parameters
    ----------
    H : float
        Hurst parameter (0 < H < 1)
        - H = 0.5: Standard Brownian motion
        - H > 0.5: Persistent (long-range dependence)
        - H < 0.5: Anti-persistent
    sigma : float, optional
        Standard deviation of the process (default: 1.0)
    method : str, optional
        Method for generating fBm:
        - 'davies_harte': Davies-Harte method (default)
        - 'cholesky': Cholesky decomposition method
        - 'circulant': Circulant embedding method
    """

    def __init__(self, H: float, sigma: float = 1.0, method: str = "davies_harte"):
        """
        Initialize the Fractional Brownian Motion model.

        Parameters
        ----------
        H : float
            Hurst parameter (0 < H < 1)
        sigma : float, optional
            Standard deviation of the process (default: 1.0)
        method : str, optional
            Generation method (default: 'davies_harte')
        """
        super().__init__(H=H, sigma=sigma, method=method)

    def _validate_parameters(self) -> None:
        """Validate model parameters."""
        H = self.parameters["H"]
        sigma = self.parameters["sigma"]
        method = self.parameters["method"]

        if not 0 < H < 1:
            raise ValueError("Hurst parameter H must be in (0, 1)")

        if sigma <= 0:
            raise ValueError("Standard deviation sigma must be positive")

        valid_methods = ["davies_harte", "cholesky", "circulant"]
        if method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")

    def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate fractional Brownian motion.

        Parameters
        ----------
        n : int
            Length of the time series to generate
        seed : int, optional
            Random seed for reproducibility

        Returns
        -------
        np.ndarray
            Generated fBm time series of length n
        """
        if seed is not None:
            np.random.seed(seed)

        H = self.parameters["H"]
        sigma = self.parameters["sigma"]
        method = self.parameters["method"]

        if method == "davies_harte":
            return self._davies_harte_method(n, H, sigma)
        elif method == "cholesky":
            return self._cholesky_method(n, H, sigma)
        elif method == "circulant":
            return self._circulant_method(n, H, sigma)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _davies_harte_method(self, n: int, H: float, sigma: float) -> np.ndarray:
        """
        Generate fBm using the Davies-Harte method.

        This method uses the spectral representation of fBm and is
        computationally efficient for large sample sizes.
        """
        # Calculate the spectral density
        freqs = np.arange(1, n // 2 + 1)
        spectral_density = sigma**2 * (2 * np.sin(np.pi * freqs / n)) ** (1 - 2 * H)

        # Generate complex Gaussian random variables
        real_part = np.random.normal(0, 1, n // 2)
        imag_part = np.random.normal(0, 1, n // 2)
        complex_noise = (real_part + 1j * imag_part) / np.sqrt(2)

        # Apply spectral density
        filtered_noise = complex_noise * np.sqrt(spectral_density)

        # Construct the full spectrum (symmetric)
        full_spectrum = np.zeros(n, dtype=complex)
        full_spectrum[1 : n // 2 + 1] = filtered_noise

        # Fill the second half (symmetric part)
        # For even n: we need n//2 - 1 elements (excluding the middle element)
        # For odd n: we need n//2 elements
        if n % 2 == 0:  # even n
            full_spectrum[n // 2 + 1 :] = np.conj(filtered_noise)[:-1][::-1]
        else:  # odd n
            full_spectrum[n // 2 + 1 :] = np.conj(filtered_noise)[::-1]

        # Inverse FFT to get the time series
        fbm = np.real(np.fft.ifft(full_spectrum)) * np.sqrt(n)

        return fbm

    def _cholesky_method(self, n: int, H: float, sigma: float) -> np.ndarray:
        """
        Generate fBm using Cholesky decomposition.

        This method constructs the covariance matrix and uses Cholesky
        decomposition to generate correlated Gaussian variables.
        """
        # Construct covariance matrix
        cov_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                cov_matrix[i, j] = (
                    sigma**2
                    * 0.5
                    * (
                        abs(i + 1) ** (2 * H)
                        + abs(j + 1) ** (2 * H)
                        - abs(i - j) ** (2 * H)
                    )
                )

        # Cholesky decomposition
        try:
            L = linalg.cholesky(cov_matrix, lower=True)
        except linalg.LinAlgError:
            # Add small regularization if matrix is not positive definite
            cov_matrix += 1e-10 * np.eye(n)
            L = linalg.cholesky(cov_matrix, lower=True)

        # Generate uncorrelated Gaussian noise
        noise = np.random.normal(0, 1, n)

        # Transform to correlated variables
        fbm = L @ noise

        return fbm

    def _circulant_method(self, n: int, H: float, sigma: float) -> np.ndarray:
        """
        Generate fBm using circulant embedding.

        This method uses circulant embedding for efficient generation
        of stationary Gaussian processes.
        """
        # Calculate autocovariance function
        lags = np.arange(n)
        autocov = (
            sigma**2
            * 0.5
            * (
                (lags + 1) ** (2 * H)
                - 2 * lags ** (2 * H)
                + np.maximum(0, lags - 1) ** (2 * H)
            )
        )

        # Construct circulant matrix
        circulant_row = np.concatenate([autocov, autocov[1 : n - 1][::-1]])

        # Eigenvalue decomposition
        eigenvalues = np.fft.fft(circulant_row)

        # Ensure positive eigenvalues
        eigenvalues = np.maximum(eigenvalues, 0)

        # Generate complex Gaussian noise
        noise = np.random.normal(0, 1, len(eigenvalues)) + 1j * np.random.normal(
            0, 1, len(eigenvalues)
        )
        noise = noise / np.sqrt(2)

        # Apply spectral filter
        filtered_noise = noise * np.sqrt(eigenvalues)

        # Inverse FFT
        fbm = np.real(np.fft.ifft(filtered_noise))[:n]

        return fbm

    def get_theoretical_properties(self) -> Dict[str, Any]:
        """
        Get theoretical properties of fBm.

        Returns
        -------
        dict
            Dictionary containing theoretical properties
        """
        H = self.parameters["H"]
        sigma = self.parameters["sigma"]

        return {
            "hurst_parameter": H,
            "variance": sigma**2,
            "self_similarity_exponent": H,
            "long_range_dependence": H > 0.5,
            "stationary_increments": True,
            "gaussian": True,
        }

    def get_increments(self, fbm: np.ndarray) -> np.ndarray:
        """
        Get the increments of fBm (fractional Gaussian noise).

        Parameters
        ----------
        fbm : np.ndarray
            Fractional Brownian motion time series

        Returns
        -------
        np.ndarray
            Increments (fractional Gaussian noise)
        """
        return np.diff(fbm)

    def get_autocorrelation(
        self, lag: Union[int, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Get theoretical autocorrelation function of fBm.

        For fBm, the autocorrelation function is:
        ρ(t,s) = (1/2)(|t|^(2H) + |s|^(2H) - |t-s|^(2H))

        Parameters
        ----------
        lag : int or np.ndarray
            Lag(s) for autocorrelation calculation

        Returns
        -------
        float or np.ndarray
            Autocorrelation values at the specified lags
        """
        H = self.parameters["H"]
        sigma = self.parameters["sigma"]

        if isinstance(lag, (int, float)):
            lag = np.array([lag])

        # Convert to absolute values for calculation
        lag_abs = np.abs(lag)

        # Autocorrelation formula for fBm
        # For lag k, ρ(k) = (1/2)(|k+1|^(2H) - 2|k|^(2H) + |k-1|^(2H))
        autocorr = 0.5 * (
            np.power(np.maximum(0, lag_abs + 1), 2 * H)
            - 2 * np.power(lag_abs, 2 * H)
            + np.power(np.maximum(0, lag_abs - 1), 2 * H)
        )

        # Normalize by variance
        autocorr = autocorr / (sigma**2)

        # Handle single value return
        if len(autocorr) == 1:
            return float(autocorr[0])
        return autocorr

    def get_cumulative_variance(
        self, t: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Get cumulative variance at time t.

        For fBm, Var(B_H(t)) = σ²|t|^(2H)

        Parameters
        ----------
        t : float or np.ndarray
            Time point(s)

        Returns
        -------
        float or np.ndarray
            Cumulative variance at time t
        """
        H = self.parameters["H"]
        sigma = self.parameters["sigma"]

        if isinstance(t, (int, float)):
            t = np.array([t])

        # Variance formula: Var(B_H(t)) = σ²|t|^(2H)
        variance = sigma**2 * np.power(np.abs(t), 2 * H)

        # Handle single value return
        if len(variance) == 1:
            return float(variance[0])
        return variance

    def get_spectral_density(
        self, frequency: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Get theoretical power spectral density of fBm.

        For fBm, S(f) = σ²|f|^(-2H-1)

        Parameters
        ----------
        frequency : float or np.ndarray
            Frequency(ies)

        Returns
        -------
        float or np.ndarray
            Power spectral density values
        """
        H = self.parameters["H"]
        sigma = self.parameters["sigma"]

        if isinstance(frequency, (int, float)):
            frequency = np.array([frequency])

        # Avoid division by zero for f=0
        frequency = np.where(frequency == 0, 1e-10, frequency)

        # Power spectral density formula: S(f) = σ²|f|^(-2H-1)
        psd = sigma**2 * np.power(np.abs(frequency), -2 * H - 1)

        # Handle single value return
        if len(psd) == 1:
            return float(psd[0])
        return psd
