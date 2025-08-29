"""
Detrended Fluctuation Analysis (DFA) estimator implementation.

This module provides a class for estimating the Hurst parameter using
Detrended Fluctuation Analysis, which is robust to non-stationarities.
Based on Algorithm 10 from the research paper.
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

    Based on Algorithm 10 from the research paper.

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
        Estimate Hurst parameter using DFA following Algorithm 10.

        Parameters
        ----------
        data : np.ndarray
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing estimation results
        """
        # Algorithm 10: EstHurstDFA(X, w, flag)
        # Step 1: N ← GetLength(X)
        N = len(data)
        
        # Step 2: Nopt ← SearchOptSeqLen(N, w)
        # For simplicity, we use the full sequence length
        Nopt = N
        
        # Step 3: T ← GenSbpf(Nopt, w) - Generate sub-block partition factors
        T = self._generate_sub_block_partition_factors(Nopt, self.parameters["min_box_size"])
        
        # Step 4: n ← GetLength(T)
        n = len(T)
        
        # Step 5: S ← 0 ∈ Rⁿˣ¹ - For the statistics
        S = np.zeros(n)
        
        # Step 6: Z ← 0 ∈ Rᴺˣ¹ - global cumulative sequence
        Z = np.zeros(N)
        
        # Step 7: Xopt ← A¹:ᴺopt {Xᵢ} - global arithmetic average
        Xopt = np.mean(data[:Nopt])
        
        # Step 8-10: Calculate cumulative sequence
        for i in range(N):
            Z[i] = np.sum(data[:i+1] - Xopt)
        
        # Step 11-25: Main DFA loop
        for idx in range(n):
            # Step 12: m ← Tᵢdx
            m = T[idx]
            
            # Step 13: k ← Nopt/m
            k = Nopt // m
            
            # Step 14: sτ ← 0 ∈ Rᵏˣ¹ - vector of standard deviation
            s_tau = np.zeros(k)
            
            # Step 15: ετ ← 0 ∈ Rᵐˣ¹ - vector of regression residuals
            epsilon_tau = np.zeros(m)
            
            # Step 16: M ← [[1 1 ... 1]ᵀ; [1 2 ... m]ᵀ] - for linear regression
            M = np.vstack([np.ones(m), np.arange(1, m+1)]).T
            
            # Step 17: qτ ← 0 ∈ R²ˣ¹ - q = [α, β]ᵀ
            q_tau = np.zeros(2)
            
            # Step 18-23: Process each block
            for tau in range(k):
                # Step 19: Yτ ← [Z(τ-1)m+1, Z(τ-1)m+2, ..., Zτm]ᵀ
                start_idx = tau * m
                end_idx = start_idx + m
                Y_tau = Z[start_idx:end_idx]
                
                # Step 20: qτ ← LinearRegression(M, Yτ, m, flag)
                q_tau = self._linear_regression_solver(M, Y_tau, m)
                
                # Step 21: ετ ← Yτ - Mqτ
                epsilon_tau = Y_tau - M @ q_tau
                
                # Step 22: sτ ← S¹:ᵐ {εᵢ²}
                s_tau[tau] = np.sqrt(np.mean(epsilon_tau**2))
            
            # Step 24: Sᵢdx ← A¹:ᵏ {sτ}
            S[idx] = np.mean(s_tau)
        
        # Step 26: (A, b) ← FormatPowLawData(T, S, n)
        A, b = self._format_power_law_data(T, S, n)
        
        # Step 27: p ← LinearRegrSolver(A, b, n, flag)
        p = self._linear_regression_solver(A, b, n)
        
        # Step 28: βDFA ← p₂
        beta_DFA = p[1]
        
        # Step 29: H ← βDFA
        H = beta_DFA
        
        # Store results
        self.results = {
            "hurst_parameter": float(H),
            "intercept": float(p[0]),
            "slope": float(beta_DFA),
            "r_squared": self._calculate_r_squared(T, S, p),
            "p_value": self._calculate_p_value(T, S, p),
            "std_error": self._calculate_std_error(T, S, p),
            "box_sizes": T.tolist(),
            "fluctuations": S.tolist(),
            "log_sizes": np.log(T),
            "log_fluctuations": np.log(S),
            "n_points": n,
            "method": "DFA (Algorithm 10)"
        }

        return self.results

    def _generate_sub_block_partition_factors(self, N: int, min_size: int) -> np.ndarray:
        """
        Generate sub-block partition factors (box sizes).
        
        Parameters
        ----------
        N : int
            Sequence length
        min_size : int
            Minimum box size
            
        Returns
        -------
        np.ndarray
            Array of box sizes
        """
        max_size = min(N // 4, N // 2)
        
        # Generate box sizes with approximately equal spacing in log space
        box_sizes = np.unique(
            np.logspace(
                np.log10(min_size),
                np.log10(max_size),
                num=min(20, max_size - min_size + 1),
                dtype=int,
            )
        )
        
        return box_sizes

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
            Box sizes
        S : np.ndarray
            Fluctuations
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
            raise ValueError("Insufficient valid data points for DFA analysis")
        
        # Format for log-log regression: log(S) = α + β*log(T)
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
        ax.set_title("DFA Scaling Analysis (Algorithm 10)")
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
