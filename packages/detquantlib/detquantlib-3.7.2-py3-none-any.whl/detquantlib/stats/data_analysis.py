import numpy as np
import pandas as pd
import plotly.graph_objects as go

from detquantlib.figures.plotly_figures import set_standard_layout


def filter_outliers(
    df: pd.DataFrame,
    column: str,
    stats_radius: int,
    std_dev_excl_factor: int = 3,
    max_iter: int = 10,
    plot_series_at_every_iter: bool = False,
) -> pd.DataFrame:
    """
    Filters out outliers from a given time series.

    Args:
        df: Times series dataframe
        column: Name of the column containing outliers to be filtered out
        stats_radius: For an observation at a given time t, the mean and the standard deviation
            will be computed over the interval [t - stats_radius, t + stats_radius]
        std_dev_excl_factor: An observation at a given time t will be flagged as an outlier if it
            is outside the interval
                [mean(t) - std(t) * std_dev_excl_factor, mean(t) + std(t) * std_dev_excl_factor]
        max_iter: Outliers affect the mean and standard deviation of neighbouring observations,
            such that smaller neighbouring outliers may go undetected if we perform the filtering
            process only once. Hence, the operation needs to be repeated multiple times. Parameter
            'max_iter' determines the maximum number of iterations of the filtering processes.
        plot_series_at_every_iter: If plot_series=True, the time series will be plotted at
            every iteration. This parameter can be used to assess the effectiveness of the
            other input parameters in the outliers filtering process.

    Returns:
        df: Time series dataframe with outliers removed
    """
    # Initialize number of outliers found in time series (filtering will stop when this reaches 0)
    nr_outliers = 1

    # Iteratively remove outliers
    for count in range(max_iter):
        if nr_outliers > 0:
            # Count number of rows in df
            nr_rows = df.shape[0]

            # Calculate rolling mean and standard deviation per observation
            for i, loc in enumerate(df.index):
                # Determine time interval
                min_i = max(i - stats_radius, 0)
                max_i = min(i + stats_radius, nr_rows)

                # Calculate mean and standard deviation around current observation
                idx = df.index[min_i:max_i]
                df.loc[loc, "mean"] = np.mean(df.loc[idx, column])
                df.loc[loc, "std_dev"] = np.std(df.loc[idx, column], ddof=1)

            # Identify lower and upper bounds
            lower_bound = df["mean"] - df["std_dev"] * std_dev_excl_factor
            upper_bound = df["mean"] + df["std_dev"] * std_dev_excl_factor

            # Plot time series
            if plot_series_at_every_iter:
                create_outliers_iteration_plot(
                    x_values=df.index,
                    data=df[column],
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    y_label=column,
                    title=f"Outliers Filtering (Iteration {count+1}/{max_iter})",
                )

            # Exclude outliers, i.e. observations outside std dev boundaries
            idx_keep = (df[column] >= lower_bound) & (df[column] <= upper_bound)
            df = df.loc[idx_keep, :]

            # Count number of outliers found in time series
            nr_outliers = np.sum(np.invert(idx_keep))

            if nr_outliers == 0:
                print(f"No (more) outliers detected (iteration {count+1} out of max {max_iter}).")
            else:
                print(
                    f"Outliers filtering excluded {nr_outliers}/{idx_keep.shape[0]}"
                    f" observations (iteration {count+1} out of max {max_iter})."
                )

    # Plot time series
    if plot_series_at_every_iter:
        create_outliers_iteration_plot(
            x_values=df.index,
            data=df[column],
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            y_label=column,
            title="Outliers Filtering (Final Data)",
        )

    # Dataframe post-processing
    df.reset_index(drop=True, inplace=True)
    df.drop(["mean", "std_dev"], axis=1, inplace=True)

    return df


def create_outliers_iteration_plot(
    x_values: pd.Series,
    data: pd.Series,
    lower_bound: pd.Series,
    upper_bound: pd.Series,
    y_label: str,
    title: str,
):
    """
    Short utility function used in the 'filter_outliers()' function to plot outliers at every
    iteration.

    Args:
        x_values: X-axis values
        data: Time series data
        lower_bound: Time series lower bound to identify outliers
        upper_bound: Time series upper bound to identify outliers
        y_label: Y-axis label
        title: Plot title
    """
    # Define plot line colors
    data_color = "blue"
    data_line = dict(color=data_color)
    bounds_color = "#ED595C"
    bounds_line = dict(color=bounds_color)

    # Create plot
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x_values, y=upper_bound, mode="lines", name="Upper bound", line=bounds_line)
    )
    fig.add_trace(go.Scatter(x=x_values, y=data, mode="lines", name="Data", line=data_line))
    fig.add_trace(
        go.Scatter(x=x_values, y=lower_bound, mode="lines", name="Lower bound", line=bounds_line)
    )
    fig.update_layout(yaxis_title=y_label, title=title)
    fig = set_standard_layout(fig)
    fig.show()
