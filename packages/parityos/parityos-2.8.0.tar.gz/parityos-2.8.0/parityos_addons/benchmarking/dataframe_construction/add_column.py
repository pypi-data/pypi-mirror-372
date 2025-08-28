"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2024.
All rights reserved.
"""

from typing import Callable, Type

import numpy as np
import pandas as pd


def add_metric_column(
        statistics: pd.DataFrame,
        data_column: pd.Series,
        metric_column_name: str,
        metric_function: Callable,
        metric_function_expected_argument_type: Type,
):
    """
    Adds a metric column to a given statistics pd.DataFrame. The new column is obtained by
    applying a given metric function on the given data column.

    :param statistics: pd.DataFrame, where the metric column should be added.
    :param data_column: data column from which the metric should be calculated.
    :param metric_column_name: name of the metric column.
    :param metric_function: function that calculates the metric from entries of the data_column.
    :param metric_function_expected_argument_type: expected type of the data column. When the entry
                                                   of the data column is not instance of this class
                                                   np.nan will be added in the metric column.
    """
    statistics[metric_column_name] = data_column.apply(
        lambda data: metric_function(data)
        if isinstance(data, metric_function_expected_argument_type) else np.nan,
    )