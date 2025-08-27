"""
TBR (Time-Based Regression) Python Package - Professional Implementation

This module provides a comprehensive Python implementation of Time-Based
Regression analysis for measuring intervention effects in treatment/control
experiments across any domain. The methodology enables rigorous statistical
analysis of causal effects in time series data with proper uncertainty
quantification.

All functions implement mathematically rigorous TBR formulas and are designed
to be domain-agnostic, serving researchers and analysts across industries
including marketing, healthcare, economics, product development, and beyond.

Key Features
------------
- Domain-agnostic treatment effect analysis with simple time series input
- Rigorous statistical methodology with proper variance quantification
- Comprehensive credible interval construction using t-distribution
- Support for any time series treatment/control experiment
- Professional API following PyPI package standards
- Complete mathematical implementation of TBR methodology

Examples
--------
Basic TBR analysis workflow:

>>> import pandas as pd
>>> from tbr.functional.tbr_functions import perform_tbr_analysis
>>>
>>> # Simple time series with pre-aggregated control and test metrics
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=100),
...     'control': np.random.normal(1000, 50, 100),
...     'test': np.random.normal(1020, 55, 100)
... })
>>>
>>> # Run TBR analysis
>>> tbr_results, daily_summaries = perform_tbr_analysis(
...     data=data,
...     date_col='date',
...     control_col='control',
...     test_col='test',
...     pretest_start='2023-01-01',
...     test_start='2023-02-15',
...     test_end='2023-03-01',
...     level=0.80,
...     threshold=0.0,
...     model_name='experiment_analysis'
... )
>>>
>>> # Get treatment effect estimate
>>> effect = daily_summaries.iloc[-1]['estimate']
>>> print(f"Treatment Effect: {effect}")
"""

import datetime
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from tbr.utils.constants import DEFAULT_TBR_MODEL

# Export list for clean imports
__all__ = [
    "perform_tbr_analysis",
    "validate_required_columns",
    "safe_int_conversion",
    "validate_no_nulls",
    "parse_date_string",
    "validate_date_periods",
    "split_by_periods",
    "fit_tbr_regression_model",
    "calculate_model_variance",
    "calculate_prediction_variance",
    "generate_counterfactual_predictions",
    "calculate_cumulative_standard_deviation",
    "compute_interval_estimate_and_ci",
    "create_tbr_summary",
    "create_incremental_tbr_summaries",
]


def validate_required_columns(
    df: pd.DataFrame, required_cols: List[str], df_name: str
) -> None:
    """
    Validate that DataFrame contains all required columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    required_cols : List[str]
        List of required column names
    df_name : str
        Name of the DataFrame for error messages

    Raises
    ------
    ValueError
        If any required columns are missing

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'date': ['2023-01-01'], 'control': [100]})
    >>> validate_required_columns(df, ['date', 'control'], 'test_data')
    # No error - validation passes

    >>> validate_required_columns(df, ['date', 'control', 'test'], 'test_data')
    ValueError: Missing required columns in test_data: ['test']
    """
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in {df_name}: {missing_cols}")


def safe_int_conversion(value: float, param_name: str) -> int:
    """
    Safely convert float to int with validation for statistical parameters.

    Parameters
    ----------
    value : float
        Value to convert (should be very close to an integer)
    param_name : str
        Parameter name for error messages

    Returns
    -------
    int
        Rounded integer value

    Raises
    ------
    ValueError
        If value is not close to an integer (tolerance > 0.01)

    Examples
    --------
    >>> safe_int_conversion(43.0, "degrees_freedom")
    43
    >>> safe_int_conversion(43.999999999999, "degrees_freedom")
    44
    >>> safe_int_conversion(43.5, "degrees_freedom")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: degrees_freedom should be an integer...
    """
    rounded_value = round(value)

    # Validate that the original was actually close to an integer
    if abs(value - rounded_value) > 0.01:  # 1% tolerance
        raise ValueError(
            f"{param_name} should be an integer, got {value}. "
            f"This indicates a potential issue with the statistical calculation."
        )

    return rounded_value


def validate_no_nulls(df: pd.DataFrame, cols: List[str], df_name: str) -> None:
    """
    Validate that specified columns contain no null values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    cols : List[str]
        List of column names to check for nulls
    df_name : str
        Name of the DataFrame for error messages

    Raises
    ------
    ValueError
        If null values are found

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'date': ['2023-01-01'], 'control': [100]})
    >>> validate_no_nulls(df, ['date', 'control'], 'test_data')
    # No error - validation passes

    >>> df_with_nulls = pd.DataFrame({'date': [None], 'control': [100]})
    >>> validate_no_nulls(df_with_nulls, ['date', 'control'], 'test_data')
    ValueError: Null values found in test_data: {'date': 1}
    """
    null_counts = df[cols].isnull().sum()
    if null_counts.any():
        null_cols = null_counts[null_counts > 0].to_dict()
        raise ValueError(f"Null values found in {df_name}: {null_cols}")


def parse_date_string(
    date_str: Union[str, pd.Timestamp], param_name: str, make_exclusive: bool = False
) -> pd.Timestamp:
    """
    Parse date string or timezone-aware datetime to a UTC datetime object.

    Parameters
    ----------
    date_str : Union[str, pd.Timestamp]
        Date as string (YYYY-MM-DD format) or timezone-aware datetime object
    param_name : str
        Parameter name for error messages
    make_exclusive : bool, default False
        If True, adds 1 day to make the date exclusive (useful for end dates).
        If False, keeps the date as-is (useful for start dates).

    Returns
    -------
    pd.Timestamp
        Parsed date object with UTC timezone. If make_exclusive=True,
        the date is shifted to the next day at 00:00:00 UTC.

    Raises
    ------
    ValueError
        If date format is invalid or timezone is not specified

    Examples
    --------
    >>> parse_date_string('2023-01-01', 'start_date')
    Timestamp('2023-01-01 00:00:00+0000', tz='UTC')

    >>> parse_date_string('2023-01-01', 'end_date', make_exclusive=True)
    Timestamp('2023-01-02 00:00:00+0000', tz='UTC')
    """
    if isinstance(date_str, pd.Timestamp):
        if date_str.tzinfo is None:
            raise ValueError(f"{param_name} must be timezone-aware, got naive datetime")
        parsed_date = date_str.tz_convert("UTC")
    elif isinstance(date_str, str):
        try:
            parsed_date = pd.to_datetime(date_str).tz_localize("UTC")
        except ValueError as e:
            raise ValueError(
                f"{param_name} must be in YYYY-MM-DD format, got: {date_str}"
            ) from e
    else:
        raise ValueError(
            f"{param_name} must be string or timezone-aware datetime, got: {type(date_str)}"
        )

    # Add 1 day for exclusive end dates
    if make_exclusive:
        parsed_date = parsed_date + pd.Timedelta(days=1)

    return parsed_date


def validate_date_periods(
    pretest_start: Union[str, datetime.date],
    test_start: Union[str, datetime.date],
    test_end: Union[str, datetime.date],
) -> Tuple[datetime.date, datetime.date, datetime.date]:
    """
    Validate and parse date parameters for TBR analysis.

    Parameters
    ----------
    pretest_start : Union[str, datetime.date]
        Start date of pretest period
    test_start : Union[str, datetime.date]
        Start date of test period
    test_end : Union[str, datetime.date]
        End date of test period

    Returns
    -------
    Tuple[datetime.date, datetime.date, datetime.date]
        Parsed and validated dates (pretest_start, test_start, test_end)

    Raises
    ------
    ValueError
        If dates are invalid or in wrong order

    Examples
    --------
    >>> validate_date_periods('2023-01-01', '2023-02-01', '2023-02-15')
    (Timestamp('2023-01-01 00:00:00+0000', tz='UTC'),
     Timestamp('2023-02-01 00:00:00+0000', tz='UTC'),
     Timestamp('2023-02-16 00:00:00+0000', tz='UTC'))
    """
    # Parse dates
    pretest_start_date = parse_date_string(
        pretest_start, "pretest_start", make_exclusive=False
    )
    test_start_date = parse_date_string(test_start, "test_start", make_exclusive=False)
    test_end_date = parse_date_string(test_end, "test_end", make_exclusive=True)

    # Validate date order
    if not (pretest_start_date < test_start_date < test_end_date):
        raise ValueError(
            f"Dates must be in order: pretest_start < test_start < test_end, "
            f"got: {pretest_start_date} < {test_start_date} < {test_end_date} "
            f"(Note: test_end shown as next day due to exclusive boundary handling)"
        )

    return pretest_start_date, test_start_date, test_end_date


def split_by_periods(
    aggregated_data: pd.DataFrame,
    date_col: str,
    control_col: str,
    test_col: str,
    pretest_start: Union[str, datetime.date],
    test_start: Union[str, datetime.date],
    test_end: Union[str, datetime.date],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split aggregated time series data into pretest, test and cooldown periods.

    Parameters
    ----------
    aggregated_data : pd.DataFrame
        Time series data with columns for date, control, and test metrics
    date_col : str
        Name of the date column
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column
    pretest_start : Union[str, datetime.date]
        Start date of pretest period
    test_start : Union[str, datetime.date]
        Start date of test period
    test_end : Union[str, datetime.date]
        End date of test period

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (baseline_data, pretest_data, test_data, cooldown_data) - DataFrames for each period

    Raises
    ------
    ValueError
        If date validation fails or no data found in periods

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=90),
    ...     'control': range(90),
    ...     'test': range(100, 190)
    ... })
    >>> baseline, pretest, test, cooldown = split_by_periods(
    ...     data, 'date', 'control', 'test',
    ...     '2023-01-15', '2023-02-15', '2023-03-01'
    ... )
    """
    # Validate dates
    pretest_start_date, test_start_date, test_end_date = validate_date_periods(
        pretest_start, test_start, test_end
    )

    # Validate input data
    validate_required_columns(
        aggregated_data, [date_col, control_col, test_col], "aggregated_data"
    )

    # Convert date column to datetime if it's string
    data_copy = aggregated_data.copy()
    if data_copy[date_col].dtype == "object":
        data_copy[date_col] = pd.to_datetime(data_copy[date_col]).dt.tz_localize("UTC")

    # Split into periods - pandas handles datetime vs date comparison well
    baseline_mask = data_copy[date_col] < pd.to_datetime(pretest_start_date)
    pretest_mask = (data_copy[date_col] >= pd.to_datetime(pretest_start_date)) & (
        data_copy[date_col] < pd.to_datetime(test_start_date)
    )
    test_mask = (data_copy[date_col] >= pd.to_datetime(test_start_date)) & (
        data_copy[date_col] < pd.to_datetime(test_end_date)
    )  # Exclusive end date
    cooldown_mask = data_copy[date_col] >= pd.to_datetime(
        test_end_date
    )  # Exclusive end date

    baseline_data = data_copy[baseline_mask].copy()
    pretest_data = data_copy[pretest_mask].copy()
    test_data = data_copy[test_mask].copy()
    cooldown_data = data_copy[cooldown_mask].copy()

    return baseline_data, pretest_data, test_data, cooldown_data


def fit_tbr_regression_model(
    time_series_data: pd.DataFrame,
    date_col: str,
    control_col: str,
    test_col: str,
    pretest_start: Union[str, datetime.date],
    test_start: Union[str, datetime.date],
) -> Dict[str, float]:
    """
    Fit TBR regression model using statsmodels OLS on pretest period.

    This function fits a linear regression model of the form:
    test = α + β * control + ε

    The model is trained exclusively on the pretest period to avoid
    contamination from treatment effects.

    Parameters
    ----------
    time_series_data : pd.DataFrame
        Time series data with date, control, and test columns
    date_col : str
        Name of the date column
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column
    pretest_start : Union[str, datetime.date]
        Start date for pretest period
    test_start : Union[str, datetime.date]
        Start date for test period (end of pretest)

    Returns
    -------
    Dict[str, float]
        Dictionary containing regression parameters:
        - 'alpha': Intercept (α)
        - 'beta': Slope coefficient (β)
        - 'sigma': Residual standard deviation (σ)
        - 'var_alpha': Variance of intercept estimate
        - 'var_beta': Variance of slope estimate
        - 'cov_alpha_beta': Covariance between α and β estimates
        - 'degrees_freedom': Residual degrees of freedom
        - 'n_pretest': Number of pretest observations
        - 'x_mean': Mean of control values (x̄)

    Raises
    ------
    ValueError
        If insufficient data, constant control values, or invalid regression results

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=60),
    ...     'control': np.random.normal(1000, 50, 60),
    ...     'test': np.random.normal(1020, 55, 60)
    ... })
    >>> model = fit_tbr_regression_model(
    ...     data, 'date', 'control', 'test',
    ...     '2023-01-01', '2023-02-15'
    ... )
    >>> print(f"Beta coefficient: {model['beta']:.3f}")
    """
    # Input validation
    if time_series_data.empty:
        raise ValueError("Input DataFrame is empty")

    required_cols = [date_col, control_col, test_col]
    validate_required_columns(time_series_data, required_cols, "time_series_data")

    # Convert dates to datetime if they aren't already
    df = time_series_data.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col]).dt.tz_localize("UTC")

    start_pretest = pd.to_datetime(pretest_start).tz_localize("UTC")
    start_test = pd.to_datetime(test_start).tz_localize("UTC")

    # Filter to pretest period only
    pretest_df = df[
        (df[date_col] >= start_pretest) & (df[date_col] < start_test)
    ].copy()

    if len(pretest_df) < 3:
        raise ValueError(
            f"Insufficient pretest data: {len(pretest_df)} observations. Need at least 3."
        )

    # Check for missing or invalid values
    if pretest_df[[control_col, test_col]].isnull().any().any():
        raise ValueError("Pretest data contains null values")

    if not np.isfinite(pretest_df[[control_col, test_col]]).all().all():
        raise ValueError("Pretest data contains infinite or NaN values")

    # Extract x (control) and y (test) for regression
    x = pretest_df[control_col].values
    y = pretest_df[test_col].values
    n = len(x)

    # Check for constant control values
    if np.var(x) == 0:
        raise ValueError(
            "Control group values are constant in pretest period - cannot fit regression"
        )

    # Prepare data for statsmodels (add constant for intercept)
    X = sm.add_constant(x)

    # Fit OLS regression using statsmodels
    model = sm.OLS(y, X).fit()

    # Extract all parameters directly from statsmodels
    alpha = model.params[0]  # Intercept
    beta = model.params[1]  # Slope

    # Extract variances from standard errors
    var_alpha = model.bse[0] ** 2  # Variance of intercept
    var_beta = model.bse[1] ** 2  # Variance of slope

    # Extract covariance from covariance matrix
    cov_matrix = model.cov_params()
    cov_alpha_beta = cov_matrix[0, 1]  # Covariance between intercept and slope

    # Extract other statistics
    sigma = np.sqrt(model.scale)  # Residual standard deviation
    degrees_freedom = int(model.df_resid)  # Degrees of freedom

    # Compute additional statistics needed for TBR
    x_mean = np.mean(x)

    # Validation of computed statistics
    if not np.isfinite([alpha, beta, sigma, var_alpha, var_beta, cov_alpha_beta]).all():
        raise ValueError("Computed regression parameters contain invalid values")

    if sigma <= 0:
        raise ValueError(f"Invalid residual standard deviation: {sigma}")

    if var_alpha <= 0 or var_beta <= 0:
        raise ValueError("Computed coefficient variances are non-positive")

    # Return all parameters as a simple dictionary
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "sigma": float(sigma),
        "var_alpha": float(var_alpha),
        "var_beta": float(var_beta),
        "cov_alpha_beta": float(cov_alpha_beta),
        "degrees_freedom": int(degrees_freedom),
        "n_pretest": int(n),
        "x_mean": float(x_mean),
    }


def calculate_model_variance(
    x_values: np.ndarray,
    x_mean: float,
    sigma: float,
    n_pretest: int,
    sum_x_squared_deviations: Optional[float] = None,
    var_beta: Optional[float] = None,
) -> np.ndarray:
    """
    Calculate model variance for fitted values using TBR formula.

    Implements the TBR model variance formula for MODEL UNCERTAINTY ONLY:
    V[ŷ*] = σ² · (1/n + (x* - x̄)²/Σ(xi - x̄)²)

    This captures only the uncertainty in the fitted model, not the residual noise.
    For prediction variance which includes residual noise, use calculate_prediction_variance().

    Parameters
    ----------
    x_values : np.ndarray
        Control values for which to calculate model variance
    x_mean : float
        Mean of control values from pretest period (x̄)
    sigma : float
        Residual standard deviation (σ)
    n_pretest : int
        Number of pretest observations
    sum_x_squared_deviations : Optional[float], optional
        Σ(xi - x̄)². If not provided, calculated from var_beta and sigma
    var_beta : Optional[float], optional
        Variance of slope coefficient. Used to calculate sum_x_squared_deviations if not provided

    Returns
    -------
    np.ndarray
        Model variances for each x value (model uncertainty only)

    Raises
    ------
    ValueError
        If parameters are invalid or insufficient information provided

    Notes
    -----
    Either sum_x_squared_deviations OR var_beta must be provided.
    If both are provided, sum_x_squared_deviations takes precedence.

    Examples
    --------
    >>> import numpy as np
    >>> x_vals = np.array([100, 110, 120])
    >>> variances = calculate_model_variance(
    ...     x_vals, x_mean=105, sigma=10, n_pretest=30, var_beta=0.001
    ... )
    >>> print(f"Model variances: {variances}")
    """
    # Input validation
    if len(x_values) == 0:
        raise ValueError("x_values cannot be empty")

    if sigma <= 0:
        raise ValueError("sigma must be positive")

    if n_pretest < 3:
        raise ValueError("n_pretest must be at least 3")

    # Calculate sum_x_squared_deviations if not provided
    if sum_x_squared_deviations is None:
        if var_beta is None:
            raise ValueError(
                "Either sum_x_squared_deviations or var_beta must be provided"
            )
        if var_beta <= 0:
            raise ValueError("var_beta must be positive")
        sum_x_squared_deviations = sigma**2 / var_beta

    if sum_x_squared_deviations <= 0:
        raise ValueError("sum_x_squared_deviations must be positive")

    # Apply TBR model variance formula (MODEL UNCERTAINTY ONLY)
    # V[ŷ*] = σ² · (1/n + (x* - x̄)²/Σ(xi - x̄)²)
    x_deviations_squared = (x_values - x_mean) ** 2

    model_variances = sigma**2 * (
        1.0 / n_pretest + x_deviations_squared / sum_x_squared_deviations
    )

    return model_variances


def calculate_prediction_variance(
    x_values: np.ndarray,
    x_mean: float,
    sigma: float,
    n_pretest: int,
    sum_x_squared_deviations: Optional[float] = None,
    var_beta: Optional[float] = None,
) -> np.ndarray:
    """
    Calculate prediction variance including both model uncertainty and residual noise.

    Implements the TBR prediction variance formula:
    V[y*] = σ² + V[ŷ*] = σ² + σ² · (1/n + (x* - x̄)²/Σ(xi - x̄)²)

    This can be simplified to:
    V[y*] = σ² · (1 + 1/n + (x* - x̄)²/Σ(xi - x̄)²)

    Parameters
    ----------
    x_values : np.ndarray
        Control values for which to calculate prediction variance
    x_mean : float
        Mean of control values from pretest period (x̄)
    sigma : float
        Residual standard deviation (σ)
    n_pretest : int
        Number of pretest observations
    sum_x_squared_deviations : Optional[float], optional
        Σ(xi - x̄)². If not provided, calculated from var_beta and sigma
    var_beta : Optional[float], optional
        Variance of slope coefficient. Used to calculate sum_x_squared_deviations if not provided

    Returns
    -------
    np.ndarray
        Prediction variances for each x value (model uncertainty + residual noise)

    Notes
    -----
    Either sum_x_squared_deviations OR var_beta must be provided.
    If both are provided, sum_x_squared_deviations takes precedence.

    Examples
    --------
    >>> import numpy as np
    >>> x_vals = np.array([100, 110, 120])
    >>> variances = calculate_prediction_variance(
    ...     x_vals, x_mean=105, sigma=10, n_pretest=30, var_beta=0.001
    ... )
    >>> print(f"Prediction variances: {variances}")
    """
    # Calculate model uncertainty component
    model_variances = calculate_model_variance(
        x_values=x_values,
        x_mean=x_mean,
        sigma=sigma,
        n_pretest=n_pretest,
        sum_x_squared_deviations=sum_x_squared_deviations,
        var_beta=var_beta,
    )

    # Add residual variance: V[y*] = σ² + V[ŷ*]
    prediction_variances = sigma**2 + model_variances

    return prediction_variances


def generate_counterfactual_predictions(
    alpha: float,
    beta: float,
    sigma: float,
    x_mean: float,
    n_pretest: int,
    var_beta: float,
    test_period_data: pd.DataFrame,
    control_col: str,
) -> pd.DataFrame:
    """
    Generate counterfactual predictions and their standard deviations for test period.

    Parameters
    ----------
    alpha : float
        Regression intercept coefficient
    beta : float
        Regression slope coefficient
    sigma : float
        Residual standard deviation from regression model
    x_mean : float
        Mean of control values during pretest period
    n_pretest : int
        Number of observations in pretest period
    var_beta : float
        Variance of the slope coefficient estimate
    test_period_data : pd.DataFrame
        Data for test period with control values
    control_col : str
        Name of control column

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: date, control, pred, predsd
        - pred: counterfactual predictions (ŷ*)
        - predsd: prediction standard deviations (V[ŷ*]^0.5)

    Examples
    --------
    >>> import pandas as pd
    >>> test_data = pd.DataFrame({
    ...     'date': pd.date_range('2023-02-15', periods=14),
    ...     'control': np.random.normal(1000, 50, 14)
    ... })
    >>> predictions = generate_counterfactual_predictions(
    ...     alpha=50, beta=0.95, sigma=25, x_mean=1000, n_pretest=45,
    ...     var_beta=0.001, test_period_data=test_data, control_col='control'
    ... )
    """
    # Input validation
    if test_period_data.empty:
        raise ValueError("test_period_data cannot be empty")

    if control_col not in test_period_data.columns:
        raise ValueError(f"Column '{control_col}' not found in test_period_data")

    # Get control values for test period
    x_test = test_period_data[control_col].values

    # Calculate counterfactual predictions: ŷ* = α + β * x*
    predictions = alpha + beta * x_test

    # Calculate prediction variances
    prediction_variances = calculate_prediction_variance(
        x_values=x_test,
        x_mean=x_mean,
        sigma=sigma,
        n_pretest=int(n_pretest),
        var_beta=var_beta,
    )

    # Calculate prediction standard deviations
    prediction_std_devs = np.sqrt(prediction_variances)

    # Create result DataFrame
    result_df = test_period_data[["date", control_col]].copy()
    result_df["pred"] = predictions
    result_df["predsd"] = prediction_std_devs

    return result_df


def calculate_cumulative_standard_deviation(
    test_x_values: np.ndarray,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
) -> np.ndarray:
    """
    Calculate standard deviation of cumulative causal effect for TBR test period.

    This function implements the TBR formula for cumulative variance:
    V[Δr(T)] = T · σ² + T² · v
    where v = Var(α̂) + 2·x̄_T·Cov(α̂,β̂) + x̄_T²·Var(β̂)

    Parameters
    ----------
    test_x_values : np.ndarray
        Array of control group values during test period
    sigma : float
        Residual standard deviation from regression model
    var_alpha : float
        Variance of intercept estimate
    var_beta : float
        Variance of slope estimate
    cov_alpha_beta : float
        Covariance between intercept and slope estimates

    Returns
    -------
    np.ndarray
        Array of cumulative standard deviations for each time point

    Examples
    --------
    >>> import numpy as np
    >>> x_vals = np.array([1000, 1020, 1010, 1030])
    >>> cumsd = calculate_cumulative_standard_deviation(
    ...     x_vals, sigma=25, var_alpha=100, var_beta=0.001,
    ...     cov_alpha_beta=-0.05
    ... )
    >>> print(f"Cumulative std devs: {cumsd}")
    """
    n = len(test_x_values)
    T_values = np.arange(1, n + 1)  # [1, 2, 3, ..., n]

    # Calculate cumulative means efficiently using vectorized operations
    cumsum_x = np.cumsum(test_x_values)
    x_mean_cumulative = cumsum_x / T_values

    # Vectorized calculation of v for all time points
    v_values = (
        var_alpha
        + 2 * x_mean_cumulative * cov_alpha_beta
        + (x_mean_cumulative**2) * var_beta
    )

    # Vectorized calculation of cumulative variance
    cum_variance = T_values * (sigma**2) + (T_values**2) * v_values

    # Vectorized square root
    return np.sqrt(cum_variance)


def compute_interval_estimate_and_ci(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    start_day: int,
    end_day: int,
    ci_level: float,
) -> Dict[str, float]:
    """
    Compute cumulative effect estimate and credible interval for a subinterval.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR daily output with columns 'y', 'pred', 'period', 'estsd'
    tbr_summary : pd.DataFrame
        TBR summary with 'sigma' and 't_dist_df'
    start_day : int
        Start day of subinterval (1-indexed within test period)
    end_day : int
        End day of subinterval (inclusive)
    ci_level : float
        Credible interval level (default 0.80)

    Returns
    -------
    Dict[str, float]
        Dictionary with keys: 'estimate', 'precision', 'lower', 'upper'

    Examples
    --------
    >>> result = compute_interval_estimate_and_ci(
    ...     tbr_results, daily_summaries, start_day=5, end_day=10, ci_level=0.80
    ... )
    >>> print(f"Effect estimate: {result['estimate']:.2f}")
    >>> print(f"80% CI: [{result['lower']:.2f}, {result['upper']:.2f}]")
    """
    # Filter for test period
    test_df = tbr_df[tbr_df["period"] == 1].reset_index(drop=True)

    # Slice the subinterval (remember start_day is 1-indexed)
    interval_df = test_df.iloc[start_day - 1 : end_day]

    # Estimate of cumulative effect (sum of differences)
    estimate = (interval_df["y"] - interval_df["pred"]).sum()

    # Posterior variance = sum of estsd^2 + n * sigma^2
    sum_estsd_sq = np.sum(interval_df["estsd"] ** 2)
    n_days = end_day - start_day + 1
    sigma = float(tbr_summary.iloc[-1]["sigma"])
    dof = int(tbr_summary.iloc[-1]["t_dist_df"])

    posterior_variance = sum_estsd_sq + n_days * sigma**2
    se = np.sqrt(posterior_variance)

    # t-multiplier
    alpha = 1 - ci_level
    t_mult = stats.t.ppf(1 - alpha / 2, dof)

    # Precision (half-width)
    precision = t_mult * se

    return {
        "estimate": estimate,
        "precision": precision,
        "lower": estimate - precision,
        "upper": estimate + precision,
    }


def create_tbr_summary(
    tbr_dataframe: pd.DataFrame,
    alpha: float,
    beta: float,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
    degrees_freedom: int,
    level: float,
    threshold: float,
    model_name: str = DEFAULT_TBR_MODEL,
) -> pd.DataFrame:
    """
    Create TBR summary statistics DataFrame with credible intervals and probabilities.

    This function generates a single-row summary DataFrame containing all key
    statistics for the TBR analysis, including the cumulative effect estimate,
    credible intervals, and model parameters.

    Parameters
    ----------
    tbr_dataframe : pd.DataFrame
        Complete TBR dataframe with all periods and statistics
    alpha : float
        Regression intercept coefficient
    beta : float
        Regression slope coefficient
    sigma : float
        Residual standard deviation from regression model
    var_alpha : float
        Variance of intercept estimate
    var_beta : float
        Variance of slope estimate
    cov_alpha_beta : float
        Covariance between intercept and slope estimates
    degrees_freedom : int
        Residual degrees of freedom from regression
    level : float
        Credibility level for confidence intervals
    threshold : float
        Threshold for probability calculation
    model_name : str
        Name of the TBR model

    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with TBR summary statistics

    Raises
    ------
    ValueError
        If input validation fails or required data is missing

    Examples
    --------
    >>> summary = create_tbr_summary(
    ...     tbr_results, alpha=50, beta=0.95, sigma=25,
    ...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0,
    ...     model_name='experiment_analysis'
    ... )
    >>> print(f"Effect estimate: {summary['estimate'].iloc[0]:.2f}")
    """
    # Input validation
    if tbr_dataframe.empty:
        raise ValueError("TBR dataframe cannot be empty")

    required_cols = ["period", "cumdif", "cumsd"]
    missing_cols = [col for col in required_cols if col not in tbr_dataframe.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in TBR dataframe: {missing_cols}")

    if not (0 <= level <= 1):
        raise ValueError(f"Level must be between 0 and 1, got: {level}")

    if degrees_freedom <= 0:
        raise ValueError(f"Degrees of freedom must be positive, got: {degrees_freedom}")

    if sigma <= 0:
        raise ValueError(f"Sigma must be positive, got: {sigma}")

    # Extract test period data (period == 1)
    test_period_data = tbr_dataframe[tbr_dataframe["period"] == 1].copy()

    if test_period_data.empty:
        raise ValueError("No test period data found (period == 1)")

    # Calculate core summary statistics
    # estimate: Final cumulative effect from test period
    estimate = test_period_data["cumdif"].iloc[-1]

    # se: Final cumulative standard deviation from test period
    se = test_period_data["cumsd"].iloc[-1]

    # Calculate credible interval using t-distribution
    alpha_level = 1 - level  # Probability outside interval
    t_critical = stats.t.ppf(1 - alpha_level / 2, df=degrees_freedom)

    # Credible interval bounds
    margin_of_error = t_critical * se
    lower = estimate - margin_of_error
    upper = estimate + margin_of_error

    # precision: Half-width of credible interval
    precision = margin_of_error

    # prob: Posterior probability that true cumulative effect exceeds threshold
    t_stat = (threshold - estimate) / se if se > 0 else 0
    prob = 1 - stats.t.cdf(t_stat, df=degrees_freedom)

    # Ensure probability is between 0 and 1
    prob = max(0.0, min(1.0, prob))

    # Create summary dictionary
    summary_data = {
        "estimate": float(estimate),
        "precision": float(precision),
        "lower": float(lower),
        "upper": float(upper),
        "se": float(se),
        "level": float(level),
        "thres": float(threshold),
        "prob": float(prob),
        "model": str(model_name),
        "alpha": float(alpha),
        "beta": float(beta),
        "alpha_beta_cov": float(cov_alpha_beta),
        "var_alpha": float(var_alpha),
        "var_beta": float(var_beta),
        "sigma": float(sigma),
        "t_dist_df": float(degrees_freedom),
    }

    # Create single-row DataFrame with specified dtypes
    summary_df = pd.DataFrame([summary_data])

    # Ensure correct dtypes
    dtype_mapping = {
        "estimate": "float64",
        "precision": "float64",
        "lower": "float64",
        "upper": "float64",
        "se": "float64",
        "level": "float64",
        "thres": "float64",
        "prob": "float64",
        "model": "object",
        "alpha": "float64",
        "beta": "float64",
        "alpha_beta_cov": "float64",
        "var_alpha": "float64",
        "var_beta": "float64",
        "sigma": "float64",
        "t_dist_df": "float64",
    }

    summary_df = summary_df.astype(dtype_mapping)

    return summary_df


def create_incremental_tbr_summaries(
    tbr_dataframe: pd.DataFrame,
    alpha: float,
    beta: float,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
    degrees_freedom: int,
    level: float,
    threshold: float,
    model_name: str = DEFAULT_TBR_MODEL,
) -> pd.DataFrame:
    """
    Create incremental TBR summary statistics for each test period day.

    This function generates summary statistics for incremental test periods:
    - Day 1: Summary for first day only
    - Day 2: Summary for first two days (cumulative)
    - Day 3: Summary for first three days (cumulative)
    - ...and so on

    Parameters
    ----------
    tbr_dataframe : pd.DataFrame
        Complete TBR dataframe with all periods and statistics
    alpha : float
        Regression intercept coefficient
    beta : float
        Regression slope coefficient
    sigma : float
        Residual standard deviation from regression model
    var_alpha : float
        Variance of intercept estimate
    var_beta : float
        Variance of slope estimate
    cov_alpha_beta : float
        Covariance between intercept and slope estimates
    degrees_freedom : int
        Residual degrees of freedom from regression
    level : float
        Credibility level for confidence intervals
    threshold : float
        Threshold for probability calculation
    model_name : str
        Name of the TBR model

    Returns
    -------
    pd.DataFrame
        Multi-row DataFrame with incremental TBR summary statistics.
        Each row represents cumulative statistics up to that test day.
        Includes an additional 'test_day' column indicating the incremental period.

    Raises
    ------
    ValueError
        If input validation fails or no test period data is found

    Examples
    --------
    >>> incremental_summaries = create_incremental_tbr_summaries(
    ...     tbr_results, alpha=50, beta=0.95, sigma=25,
    ...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0,
    ...     model_name='experiment_analysis'
    ... )
    >>> print(f"Day 1 effect: {incremental_summaries.iloc[0]['estimate']:.2f}")
    """
    # Input validation
    if tbr_dataframe.empty:
        raise ValueError("TBR dataframe cannot be empty")

    required_cols = ["period", "cumdif", "cumsd"]
    missing_cols = [col for col in required_cols if col not in tbr_dataframe.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in TBR dataframe: {missing_cols}")

    if not (0 <= level <= 1):
        raise ValueError(f"Level must be between 0 and 1, got: {level}")

    if degrees_freedom <= 0:
        raise ValueError(f"Degrees of freedom must be positive, got: {degrees_freedom}")

    if sigma <= 0:
        raise ValueError(f"Sigma must be positive, got: {sigma}")

    # Extract test period data (period == 1)
    test_period_data = tbr_dataframe[tbr_dataframe["period"] == 1].copy()

    if test_period_data.empty:
        raise ValueError("No test period data found (period == 1)")

    # Get pretest data for combining with incremental test periods
    pretest_data = tbr_dataframe[tbr_dataframe["period"] == 0].copy()

    num_test_days = len(test_period_data)
    incremental_summaries = []

    # Generate summary for each incremental test period
    for day_idx in range(num_test_days):
        # Create subset of test data up to current day (inclusive)
        test_subset = test_period_data.iloc[: day_idx + 1].copy()

        # Combine pretest data with current test subset
        incremental_df = pd.concat([pretest_data, test_subset], ignore_index=True)

        # Generate summary for this incremental period
        summary = create_tbr_summary(
            tbr_dataframe=incremental_df,
            alpha=alpha,
            beta=beta,
            sigma=sigma,
            var_alpha=var_alpha,
            var_beta=var_beta,
            cov_alpha_beta=cov_alpha_beta,
            degrees_freedom=degrees_freedom,
            level=level,
            threshold=threshold,
            model_name=DEFAULT_TBR_MODEL,
        )

        # Add test day identifier
        summary["test_day"] = day_idx + 1

        incremental_summaries.append(summary)

    # Combine all incremental summaries
    result_df = pd.concat(incremental_summaries, ignore_index=True)

    # Reorder columns to put test_day first for clarity
    cols = ["test_day"] + [col for col in result_df.columns if col != "test_day"]
    result_df = result_df[cols]

    return result_df


def perform_tbr_analysis(
    data: pd.DataFrame,
    date_col: str,
    control_col: str,
    test_col: str,
    pretest_start: Union[str, pd.Timestamp],
    test_start: Union[str, pd.Timestamp],
    test_end: Union[str, pd.Timestamp],
    level: float = 0.80,
    threshold: float = 0.0,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Execute complete TBR analysis pipeline for domain-agnostic time series data.

    This is the main function that orchestrates the entire TBR analysis process
    for any treatment/control time series experiment. The input should be
    pre-aggregated time series data with control and test group metrics.

    Parameters
    ----------
    data : pd.DataFrame
        Time series data with date, control, and test columns.
        Should contain pre-aggregated metrics for control and test groups.
    date_col : str
        Name of the date column
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column
    pretest_start : Union[str, pd.Timestamp]
        Start date of pretest period
    test_start : Union[str, pd.Timestamp]
        Start date of test period
    test_end : Union[str, pd.Timestamp]
        End date of test period
    level : float, default 0.80
        Credibility level for confidence intervals (0.80 = 80%)
    threshold : float, default 0.0
        Threshold for probability calculation (usually 0 for positive effect testing)

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        - tbr_dataframe: Complete time series with predictions, effects, and uncertainties
        - daily_summaries: Day-by-day progression of cumulative effects with statistics

    Raises
    ------
    ValueError
        If input validation fails or insufficient data for analysis

    Examples
    --------
    Basic usage with marketing campaign data:

    >>> import pandas as pd
    >>> import numpy as np
    >>>
    >>> # Create sample time series data
    >>> dates = pd.date_range('2023-01-01', periods=90)
    >>> data = pd.DataFrame({
    ...     'date': dates,
    ...     'control': np.random.normal(1000, 50, 90),
    ...     'test': np.random.normal(1020, 55, 90)
    ... })
    >>>
    >>> # Run TBR analysis
    >>> tbr_results, daily_summaries = perform_tbr_analysis(
    ...     data=data,
    ...     date_col='date',
    ...     control_col='control',
    ...     test_col='test',
    ...     pretest_start='2023-01-01',
    ...     test_start='2023-02-15',
    ...     test_end='2023-03-01',
    ...     level=0.80,
    ...     threshold=0.0
    ... )
    >>>
    >>> # Get final treatment effect
    >>> final_effect = daily_summaries.iloc[-1]['estimate']
    >>> print(f"Treatment Effect: {final_effect:.2f}")
    >>>
    >>> # Check significance
    >>> is_significant = daily_summaries.iloc[-1]['lower'] > 0
    >>> print(f"Significant Positive Effect: {is_significant}")

    Medical trial example:

    >>> # Medical trial data
    >>> medical_data = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=120),
    ...     'control_recovery_rate': np.random.normal(0.75, 0.05, 120),
    ...     'treatment_recovery_rate': np.random.normal(0.82, 0.06, 120)
    ... })
    >>>
    >>> tbr_results, summaries = perform_tbr_analysis(
    ...     data=medical_data,
    ...     date_col='date',
    ...     control_col='control_recovery_rate',
    ...     test_col='treatment_recovery_rate',
    ...     pretest_start='2023-01-01',
    ...     test_start='2023-03-01',
    ...     test_end='2023-04-01',
    ...     level=0.95,
    ...     threshold=0.05  # 5% improvement threshold
    ... )
    """
    # Input validation
    if data.empty:
        raise ValueError("Input data cannot be empty")

    required_cols = [date_col, control_col, test_col]
    validate_required_columns(data, required_cols, "data")
    validate_no_nulls(data, required_cols, "data")

    # Validate metric columns are numeric
    if not pd.api.types.is_numeric_dtype(data[control_col]):
        raise ValueError(f"Control column '{control_col}' must be numeric")

    if not pd.api.types.is_numeric_dtype(data[test_col]):
        raise ValueError(f"Test column '{test_col}' must be numeric")

    # Step 1: Split data by periods
    baseline_data, pretest_data, test_data, cooldown_data = split_by_periods(
        aggregated_data=data,
        date_col=date_col,
        control_col=control_col,
        test_col=test_col,
        pretest_start=pretest_start,
        test_start=test_start,
        test_end=test_end,
    )

    if pretest_data.empty:
        raise ValueError("No pretest data found - check pretest period dates")

    if test_data.empty:
        raise ValueError("No test data found - check test period dates")

    # Step 2: Fit the TBR regression model on pretest data
    model_params = fit_tbr_regression_model(
        time_series_data=data,
        date_col=date_col,
        control_col=control_col,
        test_col=test_col,
        pretest_start=pretest_start,
        test_start=test_start,
    )

    # Step 3: Create TBR dataframe with all periods and calculations
    # First, prepare test data with period indicators
    test_data_with_period = test_data.copy()
    test_data_with_period["period"] = 1

    if not cooldown_data.empty:
        cooldown_data_with_period = cooldown_data.copy()
        cooldown_data_with_period["period"] = 3

        # Combine test and cooldown data
        test_data_extended = (
            pd.concat(
                [test_data_with_period, cooldown_data_with_period], ignore_index=True
            )
            .sort_values(date_col)
            .reset_index(drop=True)
        )
    else:
        test_data_extended = test_data_with_period

    # Create comprehensive TBR dataframe
    tbr_dataframe = _create_tbr_dataframe(
        baseline_data=baseline_data,
        pretest_data=pretest_data,
        test_data=test_data_extended,
        date_col=date_col,
        control_col=control_col,
        test_col=test_col,
        model_params=model_params,
    )

    # Step 4: Create incremental daily summaries
    daily_summaries = create_incremental_tbr_summaries(
        tbr_dataframe=tbr_dataframe,
        alpha=model_params["alpha"],
        beta=model_params["beta"],
        sigma=model_params["sigma"],
        var_alpha=model_params["var_alpha"],
        var_beta=model_params["var_beta"],
        cov_alpha_beta=model_params["cov_alpha_beta"],
        degrees_freedom=safe_int_conversion(
            model_params["degrees_freedom"], "degrees_freedom"
        ),
        level=level,
        threshold=threshold,
        model_name=DEFAULT_TBR_MODEL,
    )

    return tbr_dataframe, daily_summaries


def _create_tbr_dataframe(
    baseline_data: pd.DataFrame,
    pretest_data: pd.DataFrame,
    test_data: pd.DataFrame,
    date_col: str,
    control_col: str,
    test_col: str,
    model_params: Dict[str, float],
) -> pd.DataFrame:
    """
    Internal function to create the comprehensive TBR dataframe.

    This function creates the main TBR output with all required columns
    for different periods (baseline, pretest, test, cooldown).
    """
    # Process baseline period (if exists)
    if not baseline_data.empty:
        baseline_df = baseline_data.copy()
        baseline_df["period"] = -1
        baseline_df["y"] = baseline_df[test_col]
        baseline_df["x"] = baseline_df[control_col]
        baseline_df["pred"] = np.nan
        baseline_df["predsd"] = np.nan
        baseline_df["dif"] = np.nan
        baseline_df["cumdif"] = np.nan
        baseline_df["cumsd"] = np.nan
        baseline_df["estsd"] = np.nan
    else:
        baseline_df = pd.DataFrame()

    # Process pretest period
    pretest_df = pretest_data.copy()
    pretest_df["period"] = 0
    pretest_df["y"] = pretest_df[test_col]
    pretest_df["x"] = pretest_df[control_col]

    # Calculate fitted values for pretest
    pretest_df["pred"] = model_params["alpha"] + model_params["beta"] * pretest_df["x"]

    # Calculate fitted value standard deviations for pretest
    fitted_variances = calculate_model_variance(
        x_values=pretest_df["x"].values,
        x_mean=model_params["x_mean"],
        sigma=model_params["sigma"],
        n_pretest=safe_int_conversion(model_params["n_pretest"], "n_pretest"),
        var_beta=model_params["var_beta"],
    )
    pretest_df["estsd"] = np.sqrt(fitted_variances)
    pretest_df["predsd"] = 0.0

    # Calculate residuals
    pretest_df["dif"] = pretest_df["y"] - pretest_df["pred"]
    pretest_df["cumdif"] = np.nan
    pretest_df["cumsd"] = 0.0

    # Process test period (includes test and cooldown if present)
    test_df = test_data.copy()
    test_df["y"] = test_df[test_col]
    test_df["x"] = test_df[control_col]

    # Generate counterfactual predictions
    test_predictions = generate_counterfactual_predictions(
        alpha=model_params["alpha"],
        beta=model_params["beta"],
        sigma=model_params["sigma"],
        x_mean=model_params["x_mean"],
        n_pretest=safe_int_conversion(model_params["n_pretest"], "n_pretest"),
        var_beta=model_params["var_beta"],
        test_period_data=test_df,
        control_col=control_col,
    )

    test_df["pred"] = test_predictions["pred"]
    test_df["predsd"] = test_predictions["predsd"]

    # Calculate effects
    test_df["dif"] = test_df["y"] - test_df["pred"]
    test_df["cumdif"] = test_df["dif"].cumsum()

    # Calculate cumulative standard deviations
    cumsd_values = calculate_cumulative_standard_deviation(
        test_df["x"].values,
        model_params["sigma"],
        model_params["var_alpha"],
        model_params["var_beta"],
        model_params["cov_alpha_beta"],
    )
    test_df["cumsd"] = cumsd_values
    test_df["estsd"] = np.nan

    # Combine all periods
    dataframes_to_combine = [
        df for df in [baseline_df, pretest_df, test_df] if not df.empty
    ]
    tbr_df = pd.concat(dataframes_to_combine, ignore_index=True)

    # Order columns consistently
    output_cols = [
        date_col,
        "period",
        "y",
        "x",
        "pred",
        "predsd",
        "dif",
        "cumdif",
        "cumsd",
        "estsd",
    ]
    tbr_df = tbr_df[output_cols]

    return tbr_df
