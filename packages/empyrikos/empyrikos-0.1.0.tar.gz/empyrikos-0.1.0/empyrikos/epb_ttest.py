"""
Empirical Partially Bayes t-test implementation.
"""

import numpy as np
from typing import Union

from .julia_helpers import _ensure_empirikos_loaded, _get_julia_main, get_solver_optimizer


class EPBTTestResult:
    """
    Results of empirical partially Bayes t-test.
    
    This object contains all results from the empirical partially Bayes testing procedure:
    
    Attributes
    ----------
    n_rejected : int
        Number of hypotheses rejected at the specified alpha level
    pvalues : np.ndarray
        Empirical partially Bayes p-values for each test  
    adj_pvalues : np.ndarray
        Multiple testing corrected p-values (e.g., FDR-adjusted)
    reject : np.ndarray
        Boolean array indicating which hypotheses were rejected
    threshold : float
        P-value threshold used for rejection (largest rejected p-value) 
    prior_fitted : object
        Fitted prior distribution object from Julia
    """
    
    def __init__(self, n_rejected: int, pvalues: np.ndarray, adj_pvalues: np.ndarray, 
                 reject: np.ndarray, threshold: float, prior_fitted: object):
        self.n_rejected = n_rejected
        self.pvalues = pvalues
        self.adj_pvalues = adj_pvalues
        self.reject = reject
        self.threshold = threshold
        self.prior_fitted = prior_fitted
    
    def pvalue_function(self, beta_hat: Union[np.ndarray, list, float], 
                       se_hat_squared: Union[np.ndarray, list, float], 
                       df: Union[np.ndarray, list, int, float]) -> Union[np.ndarray, float]:
        """
        Compute empirical partially Bayes p-values for new data using the fitted prior.
        
        Uses the fitted prior distribution from the original analysis to compute
        empirical partially Bayes p-values for new effect size estimates, variance estimates, and degrees of freedom.
        
        Parameters
        ----------
        beta_hat : array-like or float
            Effect size estimates (e.g., regression coefficients, mean differences).
        se_hat_squared : array-like or float  
            Variance estimates corresponding to beta_hat (i.e., independent estimates of $\\mathrm{Var}(\\hat{\\beta}_i)$).
        df : array-like or float
            Degrees of freedom for each test. Can be a single value or an array.
            
        Returns
        -------
        np.ndarray or float
            Empirical partially Bayes p-values for the input data.
            Returns a scalar if all inputs are scalars, otherwise returns an array.
            
        Examples
        --------
        >>> # Using fitted result to compute p-values for new data
        >>> new_pval = result.pvalue_function(beta_hat=1.5, se_hat_squared=0.25, df=10)
        >>> print(f"P-value: {new_pval}")
        """
        # Ensure Julia packages are loaded
        _ensure_empirikos_loaded()
        jl = _get_julia_main()
        
        # Convert inputs to numpy arrays
        beta_hat = np.asarray(beta_hat, dtype=float)
        se_hat_squared = np.asarray(se_hat_squared, dtype=float)
        
        # Handle df - can be scalar or array
        if np.isscalar(df):
            df = np.full_like(beta_hat, df, dtype=float)
        else:
            df = np.asarray(df, dtype=float)
        
        # Validate inputs
        if not (beta_hat.shape == se_hat_squared.shape == df.shape):
            raise ValueError("beta_hat, se_hat_squared, and df must have the same shape")
        
        if np.any(se_hat_squared <= 0):
            raise ValueError("All variance estimates must be positive")
            
        if np.any(df <= 0):
            raise ValueError("All degrees of freedom must be positive")
        
        # Convert to Julia 
        jl.beta_hat_new = beta_hat
        jl.se_hat_squared_new = se_hat_squared
        jl.df_new = df
        jl.fitted_prior = self.prior_fitted
        
        # Create ScaledChiSquareSample objects for the variance estimates
        jl.seval("Zs_new = Empirikos.ScaledChiSquareSample.(se_hat_squared_new, df_new)")
        
        # Compute p-values using limma_pvalue
        jl.seval("pvals_new = Empirikos.limma_pvalue.(beta_hat_new, Zs_new, fitted_prior)")
        
        # Extract results
        pvalues_new = np.array(jl.pvals_new)
        
        # Return scalar if input was scalar, otherwise return array
        if pvalues_new.shape == ():
            return float(pvalues_new)
        elif pvalues_new.shape == (1,):
            return float(pvalues_new[0])
        else:
            return pvalues_new
    
    def se_hat_squared_pdf(self, se_hat_squared: Union[np.ndarray, list, float], 
                          df: Union[np.ndarray, list, int, float]) -> Union[np.ndarray, float]:
        """
        Compute the marginal probability density function of the variance estimates.
        
        Uses the fitted prior distribution from the original analysis to compute
        the marginal PDF of variance estimates at the specified values.
        
        Parameters
        ----------
        se_hat_squared : array-like or float  
            Variance estimates (i.e., independent estimates of $\\mathrm{Var}(\\hat{\\beta}_i)$).
        df : array-like or float
            Degrees of freedom for each test. Can be a single value or an array.
            
        Returns
        -------
        np.ndarray or float
            Marginal probability density values at the input points.
            Returns a scalar if all inputs are scalars, otherwise returns an array.
            
        Examples
        --------
        >>> # Compute PDF at a single point
        >>> pdf_val = result.se_hat_squared_pdf(se_hat_squared=0.25, df=10)
        >>> print(f"PDF: {pdf_val}")
        
        >>> # Compute PDF at multiple points
        >>> pdf_vals = result.se_hat_squared_pdf(
        ...     se_hat_squared=[0.25, 0.30, 0.18], 
        ...     df=[10, 15, 12]
        ... )
        >>> print(f"PDF values: {pdf_vals}")
        """
        # Ensure Julia packages are loaded
        _ensure_empirikos_loaded()
        jl = _get_julia_main()
        
        # Convert inputs to numpy arrays
        se_hat_squared = np.asarray(se_hat_squared, dtype=float)
        
        # Handle df - can be scalar or array
        if np.isscalar(df):
            df = np.full_like(se_hat_squared, df, dtype=float)
        else:
            df = np.asarray(df, dtype=float)
        
        # Validate inputs
        if not (se_hat_squared.shape == df.shape):
            raise ValueError("se_hat_squared and df must have the same shape")
        
        if np.any(se_hat_squared <= 0):
            raise ValueError("All variance estimates must be positive")
            
        if np.any(df <= 0):
            raise ValueError("All degrees of freedom must be positive")
        
        # Convert to Julia 
        jl.se_hat_squared = se_hat_squared
        jl.df = df
        jl.fitted_prior = self.prior_fitted
        
        # Create ScaledChiSquareSample objects for the variance estimates
        jl.seval("Zs = Empirikos.ScaledChiSquareSample.(se_hat_squared, df)")
        
        # Compute PDF values using the fitted prior
        jl.seval("pdf_vals = Empirikos.pdf.(fitted_prior, Zs)")
        
        # Extract results
        pdf_values = np.array(jl.pdf_vals)
        
        # Return scalar if input was scalar, otherwise return array
        if pdf_values.shape == ():
            return float(pdf_values)
        elif pdf_values.shape == (1,):
            return float(pdf_values[0])
        else:
            return pdf_values


def epb_ttest(
    beta_hat: Union[np.ndarray, list],
    se_hat_squared: Union[np.ndarray, list], 
    df: Union[np.ndarray, list, int],
    alpha: float = 0.05,
    multiple_test: str = "benjamini_hochberg",
    solver: str = "hypatia"
) -> EPBTTestResult:
    """
    Empirical partially Bayes t-test for multiple testing.
    
    Performs multiple testing with empirical Bayes shrinkage on variance estimates,
    providing improved power compared to standard multiple testing procedures.
    
    Mathematical Model
    ------------------
    For each hypothesis i, we observe:
    
    $$
    (\\hat{\\beta}_i, \\hat{s}_i^2) \\sim \\mathrm{N}(\\beta_i, \\sigma_i^2) \\otimes \\frac{\\sigma_i^2}{\\nu_i} \\chi^2_{\\nu_i}
    $$
    
    where $\\hat{\\beta}_i$ (beta_hat) are effect size estimates, $\\hat{s}_i^2$ (se_hat_squared) are 
    independent estimates of $\\mathrm{Var}(\\hat{\\beta}_i)$ following a scaled chi-squared distribution, and $\\nu_i$ (df) 
    are the degrees of freedom. 
    
    The empirical Bayes procedure estimates a prior distribution for the unknown variances
    and computes moderated test statistics. We test $H_0: \\beta_i = 0$ vs $H_1: \\beta_i \\neq 0$.
    
    Parameters
    ----------
    beta_hat : array-like
        Effect size estimates (e.g., regression coefficients, mean differences).
    se_hat_squared : array-like  
        Variance estimates corresponding to beta_hat (i.e., independent estimates of $\\mathrm{Var}(\\hat{\\beta}_i)$).
    df : array-like or int
        Degrees of freedom for each test. Can be a single value (applied to all)
        or an array with one value per test.
    alpha : float, default=0.05
        Significance level for multiple testing correction.
    multiple_test : str, default="benjamini_hochberg"
        Multiple testing procedure. Currently supports "benjamini_hochberg".
    solver : str, default="hypatia"
        Optimization solver to use. Options: "hypatia", "mosek".
        
    Returns
    -------
    EPBTTestResult
        Results object containing empirical partially Bayes test results.
        
        Attributes:
            n_rejected (int): Number of hypotheses rejected at the specified alpha level.
            pvalues (numpy.ndarray): Empirical partially Bayes p-values for each test.
            adj_pvalues (numpy.ndarray): Multiple testing corrected p-values (e.g., FDR-adjusted).
            reject (numpy.ndarray): Boolean array indicating which hypotheses were rejected.
            threshold (float): P-value threshold used for rejection (largest rejected p-value).
            prior_fitted (object): Fitted prior distribution object from Julia.
        
    Examples
    --------
    >>> import numpy as np
    >>> import empirikos as eb
    >>> 
    >>> # Generate test data consistent with model assumptions
    >>> np.random.seed(42)
    >>> n_tests = 100
    >>> df = np.full(n_tests, 10)  # degrees of freedom
    >>> 
    >>> # True effect sizes: mix of nulls and non-nulls
    >>> true_beta = np.zeros(n_tests)
    >>> true_beta[50:] = np.random.normal(0, 1, 50)  # 50 nulls, 50 non-nulls
    >>> # True variances from inverse gamma (conjugate prior)
    >>> true_sigma_sq = 1.0 / np.random.gamma(2, 1/0.5, n_tests)
    >>> 
    >>> # Generate observed data according to model
    >>> beta_hat = np.random.normal(true_beta, np.sqrt(true_sigma_sq))
    >>> se_hat_squared = true_sigma_sq * np.random.chisquare(df) / df
    >>>
    >>> # Run empirical partially Bayes t-test
    >>> result = eb.epb_ttest(beta_hat, se_hat_squared, df, alpha=0.05)
    >>> print(f"Rejections: {result.n_rejected}")
    """
    
    # Ensure Julia packages are loaded
    _ensure_empirikos_loaded()
    jl = _get_julia_main()
    
    # Convert inputs to numpy arrays
    beta_hat = np.asarray(beta_hat, dtype=float)
    se_hat_squared = np.asarray(se_hat_squared, dtype=float) 
    
    # Handle df - can be scalar or array
    if np.isscalar(df):
        df = np.full_like(beta_hat, df, dtype=float)
    else:
        df = np.asarray(df, dtype=float)
    
    # Validate inputs
    if not (beta_hat.shape == se_hat_squared.shape == df.shape):
        raise ValueError("beta_hat, se_hat_squared, and df must have the same shape")
    
    if np.any(se_hat_squared <= 0):
        raise ValueError("All variance estimates must be positive")
        
    if np.any(df <= 0):
        raise ValueError("All degrees of freedom must be positive")
        
    if not (0 < alpha < 1):
        raise ValueError("alpha must be between 0 and 1")
    
    if multiple_test.lower() != "benjamini_hochberg":
        raise ValueError(f"Unsupported multiple testing method: {multiple_test}")
    
    # Get solver optimizer
    solver_optimizer = get_solver_optimizer(solver)
    
    # Convert to Julia and create NormalChiSquareSample objects
    jl.beta_hat_jl = beta_hat
    jl.se_hat_squared_jl = se_hat_squared
    jl.df_jl = df
    
    # Create samples in Julia using broadcasting
    jl.seval("Zs = Empirikos.NormalChiSquareSample.(beta_hat_jl, se_hat_squared_jl, df_jl)")
    
    # Create test object with solver
    jl.solver_opt = solver_optimizer
    jl.seval(f"test = Empirikos.EmpiricalPartiallyBayesTTest(α={alpha}, solver=solver_opt)")
    
    # Fit the model
    jl.seval("result = fit(test, Zs)")
    
    # Extract results
    total_rejections = int(jl.result.total_rejections)
    pvalues = np.array(jl.result.pvalue)
    adj_pvalues = np.array(jl.result.adjp)
    rejected = np.array(jl.result.rj_idx)
    cutoff = float(jl.result.cutoff)
    prior = jl.result.prior
    
    return EPBTTestResult(
        n_rejected=total_rejections,
        pvalues=pvalues,
        adj_pvalues=adj_pvalues,
        reject=rejected, 
        threshold=cutoff,
        prior_fitted=prior
    )