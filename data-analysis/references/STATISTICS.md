# Statistical Reference Guide

## Descriptive Statistics

### Central Tendency

**Mean (Average)**
```
μ = (Σx) / n
```
- Sum of all values divided by count
- Sensitive to outliers
- Use when data is normally distributed

**Median**
```
Middle value when sorted
```
- 50th percentile
- Robust to outliers
- Use when data has outliers or is skewed

**Mode**
```
Most frequently occurring value
```
- Can have multiple modes
- Use for categorical data

### Dispersion

**Variance**
```
σ² = Σ(x - μ)² / n
```
- Average squared deviation from mean
- In squared units

**Standard Deviation**
```
σ = √(σ²)
```
- Square root of variance
- In same units as data
- ~68% of data within 1σ, ~95% within 2σ (normal distribution)

**Range**
```
Range = max - min
```
- Simple but sensitive to outliers

**Interquartile Range (IQR)**
```
IQR = Q3 - Q1
```
- Range of middle 50% of data
- Robust to outliers

**Coefficient of Variation**
```
CV = (σ / μ) × 100%
```
- Relative measure of dispersion
- Useful for comparing variability across different scales

### Distribution Shape

**Skewness**
```
Skewness = Σ((x - μ) / σ)³ / n
```
- Negative: left-skewed (tail on left)
- Zero: symmetric
- Positive: right-skewed (tail on right)

**Kurtosis**
```
Kurtosis = Σ((x - μ) / σ)⁴ / n - 3
```
- Negative: flatter than normal (platykurtic)
- Zero: normal distribution (mesokurtic)
- Positive: more peaked than normal (leptokurtic)

## Inferential Statistics

### Correlation

**Pearson Correlation (r)**
```
r = Σ((x - x̄)(y - ȳ)) / √(Σ(x - x̄)² × Σ(y - ȳ)²)
```
- Range: -1 to +1
- Measures linear relationship
- Assumes normal distribution

**Interpretation:**
- r = 1: Perfect positive correlation
- r = 0: No correlation
- r = -1: Perfect negative correlation
- |r| > 0.7: Strong correlation
- 0.3 < |r| < 0.7: Moderate correlation
- |r| < 0.3: Weak correlation

**Spearman Correlation (ρ)**
- Rank-based correlation
- Use for non-normal or ordinal data

### Hypothesis Testing

**Null Hypothesis (H₀)**
- Assumes no effect or relationship
- What we try to reject

**Alternative Hypothesis (H₁)**
- What we want to prove
- Opposite of null hypothesis

**P-value**
- Probability of observing results if H₀ is true
- p < 0.05: Statistically significant (common threshold)
- p < 0.01: Highly significant
- p < 0.001: Very highly significant

**Confidence Interval**
```
CI = μ ± (z × σ/√n)
```
- 95% CI: z = 1.96
- 99% CI: z = 2.58

### Common Tests

**T-Test**
```
t = (x̄₁ - x̄₂) / √(s²(1/n₁ + 1/n₂))
```
- Compare means of two groups
- Assumes normal distribution
- Use when n < 30 or σ unknown

**Types:**
- Independent samples: Compare two separate groups
- Paired samples: Compare before/after in same group
- One-sample: Compare sample mean to known value

**ANOVA (Analysis of Variance)**
```
F = (Between-group variability) / (Within-group variability)
```
- Compare means of 3+ groups
- If significant, use post-hoc tests to find which groups differ

**Chi-Square Test**
```
χ² = Σ((Observed - Expected)² / Expected)
```
- Test relationship between categorical variables
- Test if distribution matches expected distribution

**Degrees of Freedom:**
```
df = (rows - 1) × (columns - 1)
```

## Regression Analysis

**Simple Linear Regression**
```
y = β₀ + β₁x + ε
```
- β₀: Intercept
- β₁: Slope (change in y per unit change in x)
- ε: Error term

**Coefficient of Determination (R²)**
```
R² = 1 - (SS_res / SS_tot)
```
- Range: 0 to 1
- Proportion of variance explained by model
- R² = 0.7: Model explains 70% of variance

**Interpretation:**
- R² > 0.7: Strong model
- 0.4 < R² < 0.7: Moderate model
- R² < 0.4: Weak model

## Probability Distributions

### Normal Distribution
```
f(x) = (1 / (σ√(2π))) × e^(-(x-μ)²/(2σ²))
```
- Bell curve
- Symmetric around mean
- 68-95-99.7 rule

### Standard Normal Distribution
```
Z = (x - μ) / σ
```
- Mean = 0, Standard Deviation = 1
- Use Z-tables for probabilities

## Sample Size Calculations

**Minimum Sample Size (Mean)**
```
n = (Z × σ / E)²
```
- Z: Z-score for confidence level
- σ: Standard deviation
- E: Margin of error

**Example (95% confidence, E=0.5, σ=2):**
```
n = (1.96 × 2 / 0.5)² = 61.47 ≈ 62
```

## Effect Size

**Cohen's d**
```
d = (μ₁ - μ₂) / σ_pooled
```
- Small: d = 0.2
- Medium: d = 0.5
- Large: d = 0.8

## Common Mistakes to Avoid

1. **Correlation ≠ Causation**
   - Correlation shows relationship, not cause

2. **P-hacking**
   - Testing multiple hypotheses increases false positives
   - Use Bonferroni correction: α_adjusted = α / number_of_tests

3. **Ignoring Assumptions**
   - Check normality before using parametric tests
   - Check equal variances for t-tests
   - Check independence of observations

4. **Sample Size Issues**
   - Too small: Low statistical power
   - Too large: May find statistically significant but practically meaningless differences

5. **Outlier Mishandling**
   - Don't remove outliers without justification
   - Use robust statistics or non-parametric tests

## Quick Reference Table

| Analysis Goal | Test to Use | Assumptions |
|--------------|-------------|-------------|
| Compare 2 means | Independent t-test | Normal distribution, equal variance |
| Compare 2 means (same subjects) | Paired t-test | Normal distribution of differences |
| Compare 3+ means | ANOVA | Normal distribution, equal variance |
| Relationship between 2 continuous | Pearson correlation | Linear relationship, normal distribution |
| Relationship between 2 ordinal | Spearman correlation | Monotonic relationship |
| Association between 2 categorical | Chi-square test | Expected frequency ≥ 5 |
| Predict continuous from continuous | Linear regression | Linear relationship, normal residuals |
| Compare distributions | Kolmogorov-Smirnov | - |
| Non-normal data, 2 groups | Mann-Whitney U | - |
| Non-normal data, 3+ groups | Kruskal-Wallis | - |

## Statistical Significance vs. Practical Significance

**Statistical Significance (p < 0.05)**
- Result unlikely due to chance
- Doesn't mean the effect is important

**Practical Significance**
- Effect size matters in real world
- Consider context and domain knowledge

Example:
- p = 0.001 (highly significant)
- But difference is only 0.1% improvement
- May not be practically meaningful
