"""
Rescaled Range (R/S) Analysis estimator.

This module provides the RSEstimator class for estimating the Hurst parameter
using the classic R/S (Rescaled Range) method.
Based on Algorithm 11 from the research paper.
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
    Based on Algorithm 11 from the research paper.

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
        Estimate the Hurst parameter using R/S analysis following Algorithm 11.

        Parameters
        ----------
        data : np.ndarray
            Time series data

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        # Algorithm 11: EstHurstRS(X, w, flag)
        # Step 1: N ← GetLength(X)
        N = len(data)
        
        # Step 2: Nopt ← SearchOptSeqLen(N, w)
        # For simplicity, we use the full sequence length
        Nopt = N
        
        # Step 3: T ← GenSbpf(Nopt, w) - Generate sub-block partition factors
        T = self._generate_sub_block_partition_factors(Nopt, self.parameters["min_window_size"])
        
        # Step 4: n ← GetLength(T)
        n = len(T)
        
        # Step 5: S ← 0 ∈ Rⁿˣ¹ - For the statistics
        S = np.zeros(n)
        
        # Step 6-25: Main R/S loop
        for idx in range(n):
            # Step 7: m ← T_idx
            m = T[idx]
            
            # Step 8: k ← Nopt/m
            k = Nopt // m
            
            # Step 9: L ← 0 ∈ Rᵏˣ¹ - For the rescaled range
            L = np.zeros(k)
            
            # Step 10-24: Process each block
            for tau in range(k):
                # Step 11: E_τ ← A_1^m {X_((τ-1)m+i)} - Calculate mean
                start_idx = tau * m
                end_idx = start_idx + m
                block_data = data[start_idx:end_idx]
                E_tau = np.mean(block_data)
                
                # Step 12: B_τ ← 0 ∈ Rᵐˣ¹
                B_tau = np.zeros(m)
                
                # Step 13-15: Calculate deviations from mean
                for j in range(m):
                    B_tau[j] = block_data[j] - E_tau
                
                # Step 16: Y_τ ← 0 ∈ Rᵐˣ¹
                Y_tau = np.zeros(m)
                
                # Step 17-19: Calculate cumulative sum of deviations
                for i in range(m):
                    Y_tau[i] = np.sum(B_tau[:i+1])
                
                # Step 20: r_τ(m) ← max_{1≤i≤m} Y_τ^i - min_{1≤i≤m} Y_τ^i
                r_tau = np.max(Y_tau) - np.min(Y_tau)
                
                # Step 21: s_τ(m) ← S_1^m {B_τ^j} - Calculate standard deviation
                s_tau = np.std(B_tau, ddof=1)
                
                # Step 22: L_τ ← r_τ(m) / s_τ(m) - Calculate rescaled range
                if s_tau > 0:
                    L[tau] = r_tau / s_tau
                else:
                    L[tau] = 0.0
            
            # Step 25: S_idx ← A_1^k {L_τ} - Average rescaled range
            S[idx] = np.mean(L)
        
        # Step 26: (A, b) ← FormatPowLawData(T, S, n)
        A, b = self._format_power_law_data(T, S, n)
        
        # Step 27: p ← LinearRegrSolver(A, b, n, flag)
        p = self._linear_regression_solver(A, b, n)
        
        # Step 28: β_RS ← p_2
        beta_RS = p[1]
        
        # Step 29: H ← β_RS
        H = beta_RS
        
        # Store results
        self.results = {
            "hurst_parameter": float(H),
            "intercept": float(p[0]),
            "slope": float(beta_RS),
            "r_squared": self._calculate_r_squared(T, S, p),
            "p_value": self._calculate_p_value(T, S, p),
            "std_error": self._calculate_std_error(T, S, p),
            "window_sizes": T.tolist(),
            "rs_values": S.tolist(),
            "log_sizes": np.log(T),
            "log_rs": np.log(S),
            "n_points": n,
            "method": "R/S (Algorithm 11)"
        }

        return self.results

    def _generate_sub_block_partition_factors(self, N: int, min_size: int) -> np.ndarray:
        """
        Generate sub-block partition factors (window sizes).
        
        Parameters
        ----------
        N : int
            Sequence length
        min_size : int
            Minimum window size
            
        Returns
        -------
        np.ndarray
            Array of window sizes
        """
        max_size = min(N // 4, N // 2)
        
        # Generate window sizes with approximately equal spacing in log space
        window_sizes = np.unique(
            np.logspace(
                np.log10(min_size),
                np.log10(max_size),
                num=min(20, max_size - min_size + 1),
                dtype=int,
            )
        )
        
        return window_sizes

    def _linear_regression_solver(self, A: np.ndarray, b: np.ndarray, n: int) -> np.ndarray:
        """
        Solve linear regression problem.
        
        Parameters
        ----------
        A : np.ndarray
            Design matrix
        b : np.ndarray
            Response vector
        n : int
            Number of data points
            
        Returns
        -------
        np.ndarray
            Regression coefficients
        """
        # Use least squares solver
        p, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
        return p

    def _format_power_law_data(self, T: np.ndarray, S: np.ndarray, n: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Format data for power law fitting.
        
        Parameters
        ----------
        T : np.ndarray
            Window sizes
        S : np.ndarray
            R/S values
        n : int
            Number of points
            
        Returns
        -------
        tuple
            (A, b) for linear regression
        """
        # Filter out invalid points
        valid_mask = (S > 0) & np.isfinite(S)
        T_valid = T[valid_mask]
        S_valid = S[valid_mask]
        
        if len(T_valid) < 3:
            raise ValueError("Insufficient valid data points for R/S analysis")
        
        # Format for log-log regression: log(R/S) = α + β*log(T)
        log_T = np.log(T_valid)
        log_S = np.log(S_valid)
        
        # Design matrix: [1, log(T)]
        A = np.vstack([np.ones(len(log_T)), log_T]).T
        b = log_S
        
        return A, b

    def _calculate_r_squared(self, T: np.ndarray, S: np.ndarray, p: np.ndarray) -> float:
        """Calculate R-squared value."""
        A, b = self._format_power_law_data(T, S, len(T))
        y_pred = A @ p
        ss_res = np.sum((b - y_pred) ** 2)
        ss_tot = np.sum((b - np.mean(b)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    def _calculate_p_value(self, T: np.ndarray, S: np.ndarray, p: np.ndarray) -> float:
        """Calculate p-value for the regression."""
        A, b = self._format_power_law_data(T, S, len(T))
        y_pred = A @ p
        residuals = b - y_pred
        
        # Calculate F-statistic
        ss_res = np.sum(residuals ** 2)
        ss_reg = np.sum((y_pred - np.mean(b)) ** 2)
        
        if ss_res == 0:
            return 0.0
            
        n = len(b)
        k = 2  # number of parameters (intercept + slope)
        
        f_stat = (ss_reg / (k - 1)) / (ss_res / (n - k))
        p_value = 1 - stats.f.cdf(f_stat, k - 1, n - k)
        
        return p_value

    def _calculate_std_error(self, T: np.ndarray, S: np.ndarray, p: np.ndarray) -> float:
        """Calculate standard error of the slope."""
        A, b = self._format_power_law_data(T, S, len(T))
        y_pred = A @ p
        residuals = b - y_pred
        
        n = len(b)
        mse = np.sum(residuals ** 2) / (n - 2)
        
        # Standard error of slope (second parameter)
        x_centered = A[:, 1] - np.mean(A[:, 1])
        std_err = np.sqrt(mse / np.sum(x_centered ** 2))
        
        return std_err

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

        return {
            "r_squared": self.results["r_squared"],
            "std_error": self.results["std_error"],
            "p_value": self.results["p_value"],
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
            ax.set_title("R/S Scaling Analysis (Algorithm 11)")
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
            self.results["window_sizes"],
            self.results["rs_values"],
            "bo-",
            label="R/S values",
            markersize=6,
        )

        # Plot fitted line
        log_scales = self.results["log_sizes"]
        log_rs_fitted = (
            self.results["intercept"] + self.results["hurst_parameter"] * log_scales
        )
        rs_fitted = np.exp(log_rs_fitted)
        ax1.loglog(
            self.results["window_sizes"],
            rs_fitted,
            "r--",
            label=f'Fitted line (H={self.results["hurst_parameter"]:.3f})',
        )

        ax1.set_xlabel("Scale")
        ax1.set_ylabel("R/S")
        ax1.set_title("R/S Analysis (Algorithm 11)")
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
            "method": "R/S Analysis (Algorithm 11)",
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
