"""
TBR - Time-Based Regression Analysis Package

⚠️  **ALPHA RELEASE** ⚠️
This package is under active development. The API may change in future versions.
For production use, please wait for the stable 1.0.0 release.

A comprehensive, domain-agnostic Python package for Time-Based Regression (TBR)
analysis. Perform rigorous statistical analysis of treatment/control group time
series data across any industry.

Features
--------
- Domain-agnostic treatment/control analysis
- Rigorous statistical methodology with proper variance quantification
- Comprehensive credible interval construction using t-distribution
- Support for any time series treatment/control experiment
- Professional PyPI package with full type hints and documentation

Quick Start
-----------
>>> import pandas as pd
>>> from tbr.functional import perform_tbr_analysis
>>>
>>> # Your time series data with columns: date, control, test
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=100),
...     'control': np.random.normal(100, 10, 100),
...     'test': np.random.normal(105, 10, 100)
... })
>>>
>>> # Perform TBR analysis
>>> tbr_df, summary_df = perform_tbr_analysis(
...     data=data,
...     date_col='date',
...     control_col='control',
...     test_col='test',
...     pretest_start='2023-01-01',
...     test_start='2023-02-15',
...     test_end='2023-04-10'
... )

See Also
--------
- Documentation: https://tbr.readthedocs.io/
- Source Code: https://github.com/idohi/tbr
- Issues: https://github.com/idohi/tbr/issues
"""

__version__ = "0.1.0a1"
__author__ = "Ido Hirsh"
__license__ = "Apache-2.0"

# Import main functionality for easy access
from .functional import perform_tbr_analysis
from .utils import CONTROL_VAL, DEFAULT_TBR_MODEL, TEST_VAL

__all__ = [
    "perform_tbr_analysis",
    "CONTROL_VAL",
    "TEST_VAL",
    "DEFAULT_TBR_MODEL",
    "__version__",
    "__author__",
    "__license__",
]
