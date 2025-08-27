# Empyrikos Python Package

Python interface to [Empirikos.jl](https://github.com/nignatiadis/Empirikos.jl) for empirical Bayes methods.

## Installation

```bash
pip install git+https://github.com/nignatiadis/empyrikos.git
```

## Requirements

- Python 3.10+
- Julia 1.10+ (will be automatically installed via JuliaCall if not present)

## Quick Start

```python
import empyrikos as eb
import numpy as np

# Example: Empirical partially Bayes t-test
# Generate test data consistent with model assumptions
np.random.seed(42)
n_tests = 100
df = np.full(n_tests, 10)  # degrees of freedom

# True effect sizes: mix of nulls and non-nulls  
true_beta = np.zeros(n_tests)
true_beta[50:] = np.random.normal(0, 1, 50)  # 50 nulls, 50 non-nulls
# True variances from inverse gamma (conjugate prior)
true_sigma_sq = 1.0 / np.random.gamma(2, 1/0.5, n_tests)

# Generate observed data according to model
beta_hat = np.random.normal(true_beta, np.sqrt(true_sigma_sq))
se_hat_squared = true_sigma_sq * np.random.chisquare(df) / df

# Run empirical partially Bayes t-test
result = eb.epb_ttest(
    beta_hat=beta_hat,
    se_hat_squared=se_hat_squared, 
    df=df,
    alpha=0.05
)

print(f"Number of rejections: {result.n_rejected}")
print(f"Adjusted p-values: {result.adj_pvalues[:5]}...")  # first 5
```

### Additional Methods on Results

After running `epb_ttest()`, the returned `EPBTTestResult` object provides additional methods:

#### `pvalue_function(beta_hat, se_hat_squared, df)`

Compute empirical partially Bayes p-values for new data using the fitted prior from the original analysis.

```python
# Using fitted result to compute p-values for new data
new_pval = result.pvalue_function(beta_hat=1.5, se_hat_squared=0.25, df=10)
print(f"P-value: {new_pval}")

# Multiple new observations
new_pvals = result.pvalue_function(
    beta_hat=[1.5, -0.8, 2.1], 
    se_hat_squared=[0.25, 0.30, 0.18], 
    df=[10, 15, 12]
)
print(f"P-values: {new_pvals}")
```

#### `se_hat_squared_pdf(se_hat_squared, df)`

Compute the marginal probability density function of the variance estimates using the fitted prior.

```python
# Compute PDF at a single point
pdf_val = result.se_hat_squared_pdf(se_hat_squared=0.25, df=10)
print(f"PDF: {pdf_val}")

# Compute PDF at multiple points
pdf_vals = result.se_hat_squared_pdf(
    se_hat_squared=[0.25, 0.30, 0.18], 
    df=[10, 15, 12]
)
print(f"PDF values: {pdf_vals}")
```

## Documentation

For detailed documentation and examples, see [the documentation](docs/).

## License

MIT License - see LICENSE file for details.