"""
Module for all plotting classes an functions.
"""

##### IMPORTS #####

# Standard imports
from pathlib import Path
from typing import Optional, Any, Union
from collections.abc import Iterable

# Third party imports
import numpy as np
import seaborn as sns  # type: ignore
from scipy import stats  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.colors import to_hex, ColorConverter
import matplotlib.patheffects as pe

# Local imports

# Import Rules

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def plot_scatter(
    x_data: Iterable[int | float],
    y_data: Union[Iterable[int | float], list[Iterable[int | float]]],
    y_labels: Optional[Union[str, list[str]]] = None,
    y_colors: Optional[Union[str, list[str]]] = None,
    groups: Optional[Iterable[Any]] = None,
    group_colors: Optional[dict[str, str]] = None,
    group_labels: Optional[dict[str, str]] = None,
    aggregation_data: Optional[Iterable[float]] = None,
    aggregation_label: str = "Aggregation",
    gridsize: int = 40,
    reduce_function: str = "sum",
    x_label: str = "X values",
    y_label: str = "Y values",
    title: str = "Scatter Plot with Regression",
    dot_size: int = 10,
    regression_line_width: float = 1.2,
    sort_by_count: bool = False,
    plot_save_path: Optional[Path] = None,
    show_regression: bool = True,
    show_identity: bool = True,
) -> None:
    """Generates a scatter plot with regression line with optional aggregation coloring,
    group coloring, and support for multiple y-series.

    Parameters
    ----------
    x_data : Iterable[float]
        X-axis data
    y_data : Union[Iterable[float], List[Iterable[float]]]
        Y-axis data - single array or list of arrays for multiple series
    y_labels : Optional[Union[str, List[str]]], optional
        Labels for y-series, by default None
    y_colors : Optional[Union[str, List[str]]], optional
        Colors for y-series, by default None
    groups : Optional[Iterable[Any]], optional
        Grouping data (only used with single y-series), by default None
    group_colors : Optional[dict[str, str]], optional
        Group colors, by default None
    group_labels : Optional[dict[str, str]], optional
        Dictionary mapping group values to custom display labels, by default None
    aggregation_data : Optional[Iterable[float]], optional
        Aggregation data (only used with single y-series), by default None
    aggregation_label : str, optional
        Aggregation label, by default "Aggregation"
    gridsize : int, optional
        Aggregation grid size, by default 40
    reduce_function : str, optional
        Function to apply when aggregating values in hexbin:
        - "sum": Sum the aggregation values within each hex (default)
        - "mean": Average the aggregation values within each hex
        - "count": Count the number of points within each hex (ignores aggregation values)
        - "max": Maximum aggregation value within each hex
        - "min": Minimum aggregation value within each hex
        By default "sum"
    x_label : str, optional
        X-axis label, by default "X values"
    y_label : str, optional
        Y-axis label, by default "Y values"
    title : str, optional
        Plot title, by default "Scatter Plot with Regression"
    dot_size : int, optional
        Dot size, by default 10
    regression_line_width : float, optional
        Regression line width, by default 1.2
    sort_by_count : bool, optional
        Sort groups by count, by default False
    plot_save_path : Optional[Path], optional
        Plot save path, by default None
    show_regression : bool, optional
        Show regression line(s), by default True
    show_identity : bool, optional
        Show identity line, by default True

    Raises
    ------
    ValueError
        If the input arrays do not have the same shape.
        If the groups array does not match the x and y data shape.
        If the aggregation array does not match the x and y data shape.
        If multiple y-series are provided with groups or aggregation data.
        If reduce_function is not valid.
    """
    # Map string parameter to numpy function
    reduce_func_map = {
        "sum": np.sum,
        "mean": np.mean,
        "count": len,  # For count, we just count the number of values
        "max": np.max,
        "min": np.min,
    }

    if reduce_function not in reduce_func_map:
        raise ValueError(
            f"reduce_function must be one of {list(reduce_func_map.keys())}"
        )

    reduce_func = reduce_func_map[reduce_function]

    # Convert x_data to numpy array
    x_array = np.asarray(x_data).flatten()

    # Determine if we have single or multiple y-series
    is_multiple_series = (
        isinstance(y_data, (list, tuple))
        and len(y_data) > 0
        and isinstance(y_data[0], (list, tuple, np.ndarray))
        and not isinstance(y_data[0], (str, bytes))
    )

    if is_multiple_series:
        # Multiple y-series case
        if groups is not None or aggregation_data is not None:
            raise ValueError(
                "Groups and aggregation data are not supported with multiple y-series."
            )

        y_arrays = [np.asarray(y).flatten() for y in y_data]
        n_series = len(y_arrays)

        # Validate all y arrays have same shape as x
        for i, y_arr in enumerate(y_arrays):
            if y_arr.shape != x_array.shape:
                raise ValueError(f"Y-series {i} must have the same shape as x data.")

        # Handle labels
        if y_labels is None:
            y_labels = [f"Series {i + 1}" for i in range(n_series)]
        elif isinstance(y_labels, str):
            y_labels = [y_labels]
        elif len(y_labels) != n_series:
            raise ValueError(
                f"Number of y_labels ({len(y_labels)}) must match number of y-series ({n_series})."
            )

        # Handle colors
        if y_colors is None:
            if n_series <= 10:
                palette = sns.color_palette("tab10", n_colors=n_series)
            else:
                palette = sns.color_palette("husl", n_colors=n_series)
            y_colors = [to_hex(palette[i]) for i in range(n_series)]
        elif isinstance(y_colors, str):
            y_colors = [y_colors]
        elif len(y_colors) != n_series:
            raise ValueError(
                f"Number of y_colors ({len(y_colors)}) must match number of y-series ({n_series})."
            )

    else:
        # Single y-series case
        y_arrays = [np.asarray(y_data).flatten()]
        n_series = 1

        if y_arrays[0].shape != x_array.shape:
            raise ValueError("Y data must have the same shape as x data.")

        y_labels = [y_labels] if y_labels else ["Data Points"]  # type: ignore
        y_colors = [y_colors] if y_colors else ["#5E8AB4"]  # type: ignore

        # Process groups if provided
        if groups is not None:
            groups_array = np.asarray(groups).flatten()
            if groups_array.shape != x_array.shape:
                raise ValueError(
                    "Groups array must have the same shape as x and y arrays."
                )
            groups_array_str = groups_array.astype(str)
            unique_groups = np.unique(groups_array_str)
        else:
            groups_array_str = None
            unique_groups = None

        # Process aggregation data if provided
        if aggregation_data is not None:
            aggregation_array = np.asarray(aggregation_data).flatten()
            if aggregation_array.shape != x_array.shape:
                raise ValueError(
                    "Aggregation array must have the same shape as x and y arrays."
                )
        else:
            aggregation_array = None

    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#3A3A3A",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D2D2D",
            "ytick.color": "#2D2D2D",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#3A3A3A",
            "legend.shadow": True,
        }
    )

    # Create figure layout
    fig, ax = plt.subplots(figsize=(10, 8))

    # Calculate overall data range for axis limits
    all_x = x_array
    all_y = np.concatenate(y_arrays)
    min_val = min(np.min(all_x), np.min(all_y))
    max_val = max(np.max(all_x), np.max(all_y))
    padding = 0.05 * (max_val - min_val)
    extent = (
        min_val - padding,
        max_val + padding,
        min_val - padding,
        max_val + padding,
    )

    # Plotting logic
    if not is_multiple_series and aggregation_array is not None:
        # Single series with aggregation coloring
        cmap = sns.cubehelix_palette(rot=-0.4, gamma=0.5, as_cmap=True)

        # Handle the special case of count
        if reduce_function == "count":
            # For count, we don't use the C parameter at all
            hb = ax.hexbin(
                x_array,
                y_arrays[0],
                gridsize=gridsize,
                cmap=cmap,
                extent=extent,
                mincnt=1,
                alpha=0.9,
            )
        else:
            # For all other functions, use the aggregation array
            hb = ax.hexbin(
                x_array,
                y_arrays[0],
                C=aggregation_array,
                gridsize=gridsize,
                cmap=cmap,
                extent=extent,
                mincnt=1,
                reduce_C_function=reduce_func,
                alpha=0.9,
            )

        # Add colorbar with appropriate label
        if reduce_function == "count":
            colorbar_label = f"Count of Points"
        else:
            colorbar_label = f"{reduce_function.title()} of {aggregation_label}"

        cbar = fig.colorbar(hb, ax=ax, label=colorbar_label, shrink=0.8)
        cbar.ax.tick_params(labelsize=10)
        cbar.outline.set_linewidth(0.7)
        cbar.outline.set_edgecolor("#4D5154")

    elif not is_multiple_series and groups_array_str is not None:
        # Single series with group coloring
        # Ensure keys are strings
        if group_colors is not None:
            group_colors = {str(k): v for k, v in group_colors.items()}

        # Ensure group_labels keys are strings if provided
        if group_labels is not None:
            group_labels = {str(k): v for k, v in group_labels.items()}

        # Create color mapping if not provided
        if group_colors is None:
            n_colors = len(unique_groups)
            if n_colors <= 12:
                base_palette = sns.color_palette("Set2", n_colors=n_colors)
            else:
                base_palette = sns.color_palette("Spectral", n_colors=n_colors)
            group_colors = {
                group: to_hex(base_palette[i % len(base_palette)])
                for i, group in enumerate(unique_groups)
            }

        group_counts = {
            group: np.sum(groups_array_str == group) for group in unique_groups
        }
        if sort_by_count:
            sorted_groups = sorted(
                unique_groups, key=lambda g: group_counts[g], reverse=True
            )
        else:
            sorted_groups = sorted(unique_groups)

        for i, group in enumerate(sorted_groups):
            mask = groups_array_str == group
            color = group_colors.get(str(group), sns.color_palette("colorblind")[i])

            # Get display label for the group
            display_label = (
                group_labels.get(str(group), str(group)) if group_labels else str(group)
            )

            ax.scatter(
                x_array[mask],
                y_arrays[0][mask],
                color=color,
                edgecolor="white",
                linewidth=0.5,
                alpha=0.85,
                s=dot_size,
                label=f"{display_label} (n={np.sum(mask):,})",
                zorder=i + 2,
            )
    else:
        # Multiple series or standard single series scatter plot
        for i, (y_arr, label, color) in enumerate(zip(y_arrays, y_labels, y_colors)):
            ax.scatter(
                x_array,
                y_arr,
                alpha=0.85,
                color=color,
                edgecolors="white",
                linewidth=0.5,
                s=dot_size,
                label=f"{label} (n={len(x_array):,})",
                zorder=i + 2,
            )

    # Identity line
    if show_identity:
        ax.plot(
            [min_val, max_val],
            [min_val, max_val],
            linestyle="--",
            color="#888888",
            linewidth=1.2,
            label="Identity line (y = x)",
            zorder=10,
        )

    # Regression lines
    if show_regression:
        reg_colors = [
            "#D7263D",
            "#FF6B35",
            "#F7931E",
            "#FFD23F",
            "#06D6A0",
            "#118AB2",
            "#073B4C",
        ]
        for i, y_arr in enumerate(y_arrays):
            slope, intercept, r_value, _, _ = stats.linregress(x_array, y_arr)
            r_squared = r_value**2
            reg_line = slope * x_array + intercept

            reg_color = (
                reg_colors[i % len(reg_colors)] if len(y_arrays) > 1 else "#D7263D"
            )

            # Sort for smooth line plotting
            sort_idx = np.argsort(x_array)
            x_sorted = x_array[sort_idx]
            reg_sorted = reg_line[sort_idx]

            series_suffix = f" ({y_labels[i]})" if len(y_arrays) > 1 else ""
            ax.plot(
                x_sorted,
                reg_sorted,
                linestyle="-",
                color=reg_color,
                linewidth=regression_line_width,
                alpha=0.6,
                label=f"$y = {slope:.2f}x {'+' if intercept >= 0 else '-'} "
                f"{abs(intercept):.2f}$, $R^2 = {r_squared:.3f}${series_suffix}",
                zorder=11 + i,
            )

    # Axis limits and labels
    ax.set_xlim(min_val - padding, max_val + padding)
    ax.set_ylim(min_val - padding, max_val + padding)
    ax.set_xlabel(x_label, fontsize=13, labelpad=10)
    ax.set_ylabel(y_label, fontsize=13, labelpad=10)
    ax.set_title(title, fontsize=16, fontweight="semibold", color="#2D3033", pad=15)
    ax.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", linewidth=0.8)
    ax.legend(loc="upper left", fontsize=10)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.1f}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.1f}"))
    ax.tick_params(axis="both", which="major", labelsize=10)

    plt.tight_layout()

    # Save or show the plot
    if plot_save_path:
        plt.savefig(plot_save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()


def plot_scatter_subplots(
    x_data_list: list[Iterable[int | float]],
    y_data_list: list[Iterable[int | float]],
    titles: Optional[list[str]] = None,
    x_labels: Optional[list[str]] = None,
    y_labels: Optional[list[str]] = None,
    groups_list: Optional[list[Optional[Iterable[Any]]]] = None,
    group_colors: Optional[dict[str, str]] = None,
    group_labels: Optional[dict[str, str]] = None,
    aggregation_data_list: Optional[list[Optional[Iterable[float]]]] = None,
    aggregation_labels: Optional[list[str]] = None,
    gridsize: int = 40,
    reduce_function: str = "sum",
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    figsize: Optional[tuple[int, int]] = None,
    main_title: Optional[str] = None,
    main_title_subplots_top: float = 0.9,  # NEW: fraction of figure height usable by subplots if main_title provided
    dot_size: int = 10,
    show_regression: bool = True,
    show_identity: bool = True,
    sort_by_count: bool = False,
    share_x_axis_limits: Optional[str] = None,
    share_y_axis_limits: Optional[str] = None,
    check_for_single_ref: bool = False,
    plot_save_path: Optional[Path] = None,
) -> None:
    """Creates a subplot figure with multiple scatter plots.

    Parameters
    ----------
    x_data_list : list[Iterable[int | float]]
        List of x-axis data arrays for each subplot
    y_data_list : list[Iterable[int | float]]
        List of y-axis data arrays for each subplot
    titles : Optional[list[str]], optional
        List of titles for each subplot
    x_labels : Optional[list[str]], optional
        List of x-axis labels for each subplot, by default None
    y_labels : Optional[list[str]], optional
        List of y-axis labels for each subplot, by default None
    groups_list : Optional[list[Optional[Iterable[Any]]]], optional
        List of group arrays for each subplot (None for no grouping), by default None
    group_colors : Optional[dict[str, str]], optional
        Dictionary mapping group names to colors, by default None
    group_labels : Optional[dict[str, str]], optional
        Dictionary mapping group values to custom display labels, by default None
    aggregation_data_list : Optional[list[Optional[Iterable[float]]]], optional
        List of aggregation arrays for each subplot (None for no aggregation), by default None
    aggregation_labels : Optional[list[str]], optional
        List of aggregation labels for colorbars, by default None
    gridsize : int, optional
        Grid size for hexbin aggregation plots, by default 40
    reduce_function : str, optional
        Function to apply when aggregating values in hexbin:
        - "sum": Sum the aggregation values within each hex (default)
        - "mean": Average the aggregation values within each hex
        - "count": Count the number of points within each hex (ignores aggregation values)
        - "max": Maximum aggregation value within each hex
        - "min": Minimum aggregation value within each hex
        By default "sum"
    rows : Optional[int], optional
        Number of rows for subplots. If None, will be calculated automatically.
    cols : Optional[int], optional
        Number of columns for subplots. If None, will be calculated automatically.
    figsize : Optional[tuple[int, int]], optional
        Figure size (width, height). If None, will be calculated based on subplots.
    main_title : Optional[str], optional
        Main title for the entire figure, by default None
    main_title_subplots_top : float
        Top (0–1) of rectangle reserved for subplots when main_title is used.
        Decrease (e.g. 0.88) to create more clearance under the main title.
        Ignored if main_title is None. Default 0.90.
    dot_size : int, optional
        Size of scatter plot dots, by default 10
    show_regression : bool, optional
        Show regression lines, by default True
    show_identity : bool, optional
        Show identity lines, by default True
    sort_by_count : bool, optional
        Sort groups by count in legend, by default False
    share_x_axis_limits : Optional[str], optional
        How to share x-axis limits:
        - None or "none": No sharing (default)
        - "all": Share x-axis limits across all subplots
        - "row": Share x-axis limits within each row
        - "col": Share x-axis limits within each column
        By default None
    share_y_axis_limits : Optional[str], optional
        How to share y-axis limits:
        - None or "none": No sharing (default)
        - "all": Share y-axis limits across all subplots
        - "row": Share y-axis limits within each row
        - "col": Share y-axis limits within each column
        By default None
    check_for_single_ref : bool, optional
        If True, check for a single value in the reference data and add it to the ref label, by default False
    plot_save_path : Optional[Path], optional
        Path to save the combined plot, by default None

    Raises
    ------
    ValueError
        If the input lists don't have the same length or are empty.
        If groups_list provided but doesn't match the length of other lists.
        If aggregation_data_list provided but doesn't match the length of other lists.
        If group arrays don't match the shape of corresponding x/y data.
        If aggregation arrays don't match the shape of corresponding x/y data.
        If both groups and aggregation data are provided for the same subplot.
        If reduce_function is not valid.
        If share_x_axis_limits or share_y_axis_limits values are not valid.
    """
    # Validate inputs
    if not x_data_list or not y_data_list:
        raise ValueError("All input lists must be non-empty.")
    if titles is None:
        titles = [""] * len(x_data_list)
    if not (len(x_data_list) == len(y_data_list) == len(titles)):
        raise ValueError(
            "x_data_list, y_data_list, and titles must have the same length."
        )

    if groups_list is not None and len(groups_list) != len(x_data_list):
        raise ValueError("groups_list must have the same length as other input lists.")

    if aggregation_data_list is not None and len(aggregation_data_list) != len(
        x_data_list
    ):
        raise ValueError(
            "aggregation_data_list must have the same length as other input lists."
        )

    if x_labels is not None and len(x_labels) != len(x_data_list):
        raise ValueError("x_labels must have the same length as x_data_list.")
    if y_labels is not None and len(y_labels) != len(y_data_list):
        raise ValueError("y_labels must have the same length as y_data_list.")

    if x_labels is None:
        x_labels = [""] * len(x_data_list)
    if y_labels is None:
        y_labels = [""] * len(y_data_list)

    if aggregation_labels is None:
        aggregation_labels = ["Aggregation"] * len(x_data_list)
    elif len(aggregation_labels) != len(x_data_list):
        aggregation_labels = aggregation_labels + ["Aggregation"] * (
            len(x_data_list) - len(aggregation_labels)
        )

    # Validate axis sharing parameters
    valid_share_options = [None, "none", "all", "row", "col"]
    if share_x_axis_limits not in valid_share_options:
        raise ValueError(
            f"share_x_axis_limits must be one of {valid_share_options}, got {share_x_axis_limits}"
        )
    if share_y_axis_limits not in valid_share_options:
        raise ValueError(
            f"share_y_axis_limits must be one of {valid_share_options}, got {share_y_axis_limits}"
        )

    # Ensure group_labels keys are strings if provided
    if group_labels is not None:
        group_labels = {str(k): v for k, v in group_labels.items()}

    # Map string parameter to numpy function
    reduce_func_map = {
        "sum": np.sum,
        "mean": np.mean,
        "count": len,
        "max": np.max,
        "min": np.min,
    }

    if reduce_function not in reduce_func_map:
        raise ValueError(
            f"reduce_function must be one of {list(reduce_func_map.keys())}"
        )

    reduce_func = reduce_func_map[reduce_function]

    n_plots = len(x_data_list)

    # Calculate grid dimensions if not provided
    if rows is None and cols is None:
        cols = int(np.ceil(np.sqrt(n_plots)))
        rows = int(np.ceil(n_plots / cols))
    elif rows is None:
        rows = int(np.ceil(n_plots / cols))
    elif cols is None:
        cols = int(np.ceil(n_plots / rows))

    # Calculate figure size if not provided
    if figsize is None:
        figsize = (cols * 8, rows * 6)

    # Convert all data to numpy arrays for easier processing
    x_arrays = [np.asarray(x_data).flatten() for x_data in x_data_list]
    y_arrays = [np.asarray(y_data).flatten() for y_data in y_data_list]

    # Validate that x and y arrays have the same shape
    for i, (x_array, y_array) in enumerate(zip(x_arrays, y_arrays)):
        if x_array.shape != y_array.shape:
            raise ValueError(
                f"x_data and y_data for subplot {i} must have the same shape."
            )

    # Process aggregation data if provided
    if aggregation_data_list is not None:
        aggregation_arrays: list[Optional[np.ndarray]] = []
        for i, agg in enumerate(aggregation_data_list):
            if agg is not None:
                arr = np.asarray(agg).flatten()
                if arr.shape != x_arrays[i].shape:
                    raise ValueError(
                        f"Aggregation array for subplot {i} must match x/y shapes."
                    )
                aggregation_arrays.append(arr)
            else:
                aggregation_arrays.append(None)
    else:
        aggregation_arrays = [None] * n_plots

    # Validate that groups and aggregation are not both provided for same subplot
    if groups_list is not None and aggregation_data_list is not None:
        for i in range(n_plots):
            if groups_list[i] is not None and aggregation_arrays[i] is not None:
                raise ValueError(
                    f"Cannot use both groups and aggregation data for subplot {i}. "
                    "Choose one coloring method per subplot."
                )

    # Calculate axis limits based on sharing options
    def calculate_limits_with_padding(
        data_arrays: list[np.ndarray],
    ) -> tuple[float, float]:
        """Calculate the limits of the data arrays with padding.

        Parameters
        ----------
        data_arrays : list[np.ndarray]
            List of data arrays to calculate limits from.

        Returns
        -------
        tuple[float, float]
            The lower and upper limits for the data arrays.
        """
        if not data_arrays:
            return 0, 1  # fallback

        all_values = np.concatenate([a for a in data_arrays if len(a) > 0])
        if len(all_values) == 0:
            return 0, 1  # fallback

        min_val = float(np.min(all_values))
        max_val = float(np.max(all_values))
        pad = 0.05 * (max_val - min_val) if max_val != min_val else 0.05
        return min_val - pad, max_val + pad

    # Initialize limits dictionaries
    x_limits: dict[str, tuple[float, float]] = {}
    y_limits: dict[str, tuple[float, float]] = {}

    # Calculate x-axis limits
    if share_x_axis_limits == "all":
        # Share across all subplots
        x_limits["all"] = calculate_limits_with_padding(x_arrays)
    elif share_x_axis_limits == "row":
        # Share within each row
        for row in range(rows):
            idxs = [
                row * cols + col for col in range(cols) if row * cols + col < n_plots
            ]
            x_limits[f"row_{row}"] = calculate_limits_with_padding(
                [x_arrays[i] for i in idxs]
            )
    elif share_x_axis_limits == "col":
        # Share within each column
        for col in range(cols):
            idxs = [
                row * cols + col for row in range(rows) if row * cols + col < n_plots
            ]
            x_limits[f"col_{col}"] = calculate_limits_with_padding(
                [x_arrays[i] for i in idxs]
            )
    else:
        for i in range(n_plots):
            x_limits[f"plot_{i}"] = calculate_limits_with_padding([x_arrays[i]])

    # Calculate y-axis limits
    if share_y_axis_limits == "all":
        # Share across all subplots
        y_limits["all"] = calculate_limits_with_padding(y_arrays)
    elif share_y_axis_limits == "row":
        # Share within each row
        for row in range(rows):
            idxs = [
                row * cols + col for col in range(cols) if row * cols + col < n_plots
            ]
            y_limits[f"row_{row}"] = calculate_limits_with_padding(
                [y_arrays[i] for i in idxs]
            )
    elif share_y_axis_limits == "col":
        # Share within each column
        for col in range(cols):
            idxs = [
                row * cols + col for row in range(rows) if row * cols + col < n_plots
            ]
            y_limits[f"col_{col}"] = calculate_limits_with_padding(
                [y_arrays[i] for i in idxs]
            )
    else:  # None or "none" - individual limits
        for i in range(n_plots):
            y_limits[f"plot_{i}"] = calculate_limits_with_padding([y_arrays[i]])

    def get_subplot_limits(idx: int) -> tuple[tuple[float, float], tuple[float, float]]:
        """Get the limits for the specified subplot.

        Parameters
        ----------
        idx : int
            The index of the subplot.

        Returns
        -------
        tuple[tuple[float, float], tuple[float, float]]
            The x and y limits for the subplot.
        """
        row = idx // cols
        col = idx % cols
        if share_x_axis_limits == "all":
            xlim = x_limits["all"]
        elif share_x_axis_limits == "row":
            xlim = x_limits[f"row_{row}"]
        elif share_x_axis_limits == "col":
            xlim = x_limits[f"col_{col}"]
        else:
            xlim = x_limits[f"plot_{idx}"]

        if share_y_axis_limits == "all":
            ylim = y_limits["all"]
        elif share_y_axis_limits == "row":
            ylim = y_limits[f"row_{row}"]
        elif share_y_axis_limits == "col":
            ylim = y_limits[f"col_{col}"]
        else:
            ylim = y_limits[f"plot_{idx}"]
        return xlim, ylim

    # Apply Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#3A3A3A",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D2D2D",
            "ytick.color": "#2D2D2D",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#3A3A3A",
            "legend.shadow": True,
        }
    )

    # Create subplots
    fig, axes = plt.subplots(rows, cols, figsize=figsize)

    # Ensure axes is always a numpy array for consistent indexing
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    elif rows == 1 or cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()

    # Create each subplot
    for i in range(n_plots):
        ax = axes[i]

        # Get pre-processed arrays
        x_array = x_arrays[i]
        y_array = y_arrays[i]
        aggregation_array = aggregation_arrays[i]

        # Process groups if provided for this subplot
        groups_array_str = None
        unique_groups = None
        if groups_list is not None and groups_list[i] is not None:
            groups_array = np.asarray(groups_list[i]).flatten()
            if groups_array.shape != x_array.shape:
                raise ValueError(
                    f"Groups array for subplot {i} must have the same shape as x and y arrays."
                )
            groups_array_str = groups_array.astype(str)
            unique_groups = np.unique(groups_array_str)

        # Get axis limits for this subplot
        xlim, ylim = get_subplot_limits(i)

        # Calculate extent for hexbin (using the broader range for proper coverage)
        extent = (xlim[0], xlim[1], ylim[0], ylim[1])

        # For identity and regression lines, use the broader range
        min_val = min(xlim[0], ylim[0])
        max_val = max(xlim[1], ylim[1])

        # Create scatter plot - aggregation, grouped, or standard
        if aggregation_array is not None:
            # Aggregation coloring using hexbin
            cmap = sns.cubehelix_palette(rot=-0.4, gamma=0.5, as_cmap=True)

            # Handle the special case of count
            if reduce_function == "count":
                # For count, we don't use the C parameter at all
                hb = ax.hexbin(
                    x_array,
                    y_array,
                    gridsize=gridsize,
                    cmap=cmap,
                    extent=extent,
                    mincnt=1,
                    alpha=0.9,
                )
            else:
                # For all other functions, use the aggregation array
                hb = ax.hexbin(
                    x_array,
                    y_array,
                    C=aggregation_array,
                    gridsize=gridsize,
                    cmap=cmap,
                    extent=extent,
                    mincnt=1,
                    reduce_C_function=reduce_func,
                    alpha=0.9,
                )

            # Add colorbar with appropriate label
            if reduce_function == "count":
                colorbar_label = f"Count of Points"
            else:
                colorbar_label = f"{reduce_function.title()} of {aggregation_labels[i]}"

            cbar = fig.colorbar(hb, ax=ax, label=colorbar_label, shrink=0.8)
            cbar.ax.tick_params(labelsize=10)
            cbar.outline.set_linewidth(0.7)
            cbar.outline.set_edgecolor("#4D5154")

        elif groups_array_str is not None:
            # Group coloring
            # Ensure keys are strings for group_colors
            if group_colors is not None:
                group_colors_str = {str(k): v for k, v in group_colors.items()}
            else:
                group_colors_str = None

            # Create color mapping if not provided
            if group_colors_str is None:
                n_colors = len(unique_groups)
                if n_colors <= 12:
                    palette = sns.color_palette("Set2", n_colors=n_colors)
                else:
                    palette = sns.color_palette("Spectral", n_colors=n_colors)
                group_colors_str = {
                    g: to_hex(palette[j % len(palette)])
                    for j, g in enumerate(unique_groups)
                }
            counts = {g: np.sum(groups_array_str == g) for g in unique_groups}
            if sort_by_count:
                ordered = sorted(unique_groups, key=lambda g: counts[g], reverse=True)
            else:
                ordered = sorted(unique_groups)
            for j, g in enumerate(ordered):
                mask = groups_array_str == g
                color = group_colors_str.get(str(g), sns.color_palette("colorblind")[j])
                display_label = (
                    group_labels.get(str(g), str(g)) if group_labels else str(g)
                )
                ax.scatter(
                    x_array[mask],
                    y_array[mask],
                    color=color,
                    edgecolor="white",
                    linewidth=0.5,
                    alpha=0.85,
                    s=dot_size,
                    label=f"{display_label} (n={np.sum(mask):,})",
                    zorder=j + 2,
                )
        else:
            # Standard scatter plot
            ax.scatter(
                x_array,
                y_array,
                alpha=0.85,
                color="#5E8AB4",
                edgecolors="white",
                linewidth=0.5,
                s=dot_size,
                label=f"Data Points (n={len(x_array):,})",
                zorder=2,
            )

        # Identity line
        if show_identity:
            ax.plot(
                [min_val, max_val],
                [min_val, max_val],
                linestyle="--",
                color="#888888",
                linewidth=1.2,
                label="Identity line (y = x)",
                zorder=10,
            )

        # Regression line
        if show_regression and len(np.unique(x_array)) > 1 and np.std(x_array) > 1e-10:
            # Check if x values have sufficient variation for regression
            if len(np.unique(x_array)) > 1 and np.std(x_array) > 1e-10:
                slope, intercept, r_value, _, _ = stats.linregress(x_array, y_array)
                r_squared = r_value**2
                reg_line = slope * x_array + intercept

                # Sort for smooth line plotting
                sort_idx = np.argsort(x_array)
                x_sorted = x_array[sort_idx]
                reg_sorted = reg_line[sort_idx]

                ax.plot(
                    x_sorted,
                    reg_sorted,
                    linestyle="-",
                    color="#D7263D",
                    linewidth=1.2,
                    alpha=0.5,
                    label=f"$y = {slope:.2f}x {'+' if intercept >= 0 else '-'} "
                    f"{abs(intercept):.2f}$, $R^2 = {r_squared:.3f}$",
                    zorder=11,
                )

        # X label
        if check_for_single_ref and np.all(np.equal(x_array, x_array.flat[0])):
            x_labels[i] = x_labels[i] + f" - ({x_array.flat[0]:.2f})"

        # Formatting
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel(x_labels[i], fontsize=13, labelpad=10)
        ax.set_ylabel(y_labels[i], fontsize=13, labelpad=10)
        ax.set_title(
            titles[i], fontsize=14, fontweight="semibold", color="#2D3033", pad=15
        )
        ax.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", linewidth=0.8)

        # Always show legend (regression and identity lines should always be visible)
        ax.legend(loc="upper left", fontsize=10)

        ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.2f}"))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.2f}"))
        ax.tick_params(axis="both", which="major", labelsize=10)

    # Hide unused subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)

    # Layout and main title (prevent overlap)
    if main_title:
        # Reserve vertical space for suptitle
        fig.tight_layout(rect=[0, 0, 1, main_title_subplots_top])
        fig.suptitle(
            main_title,
            fontsize=18,
            fontweight="bold",
            color="#2D3033",
            y=0.995,
        )
    else:
        fig.tight_layout()

    if plot_save_path:
        plt.savefig(plot_save_path, dpi=300, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_differences(
    x_data: Iterable[float],
    y_data: Iterable[float],
    groups: Optional[Iterable[Any]] = None,
    group_colors: Optional[dict[str, str]] = None,
    x_label: str = "X values",
    y_label: str = "Y values",
    data_label: str = "Data",
    dot_size: int = 32,
    regression_line_width: float = 1.2,
    sort_by_count: bool = False,
    save_path: Path | None = None,
):
    """Plots of differences between two datasets with optional grouping.

    Parameters
    ----------
    x_data : Iterable[float]
        X-axis Data
    y_data : Iterable[float]
        Y-axis Data
    groups : Iterable[Any], optional
        Grouping array for coloring the scatter points, by default None
    group_colors : Dict[str, str], optional
        Dictionary mapping unique group values to specific colors, by default None
    x_label : str, optional
        Label for the x-axis, by default "X values"
    y_label : str, optional
        Label for the y-axis, by default "Y values"
    data_label : str, optional
        Name of the data/attribute being analyzed, by default "Data"
    dot_size : int, optional
        Size of the scatter points, by default 32
    regression_line_width : float, optional
        Width of the regression line, by default 1.2
    sort_by_count : bool, optional
        Whether to sort groups by their counts, by default False
    save_path : Path | None, optional
        Path to save the figure, by default None

    Raises
    ------
    ValueError
        If the input arrays do not have the same shape.
        If the groups array does not match the x and y data shape.
        If the group colors do not match the number of unique groups.
    """
    # Convert to numpy arrays
    x_array = np.asarray(x_data)
    y_array = np.asarray(y_data)

    # Check they are the same dimensions
    if x_array.shape != y_array.shape:
        raise ValueError("All input arrays must have the same shape.")

    # Flatten arrays
    x_array_flatten = x_array.flatten()
    y_array_flatten = y_array.flatten()

    # Process groups if provided
    if groups is not None:
        groups_array = np.asarray(groups).flatten()
        if groups_array.shape != x_array_flatten.shape:
            raise ValueError("Groups array must have the same shape as x and y arrays.")
        groups_array_str = groups_array.astype(str)
        unique_groups = np.unique(groups_array_str)
        group_counts = {
            group: np.sum(groups_array_str == group) for group in unique_groups
        }
        if sort_by_count:
            sorted_groups = sorted(
                unique_groups, key=lambda g: group_counts[g], reverse=True
            )
        else:
            sorted_groups = sorted(unique_groups)
    else:
        groups_array_str = None
        unique_groups = None
        sorted_groups = None

    # Ensure keys are strings
    if group_colors is not None:
        group_colors = {str(k): v for k, v in group_colors.items()}
    # Create color mapping if not provided
    if group_colors is None and unique_groups is not None:
        n_colors = len(unique_groups)
        if n_colors <= 12:
            base_palette = sns.color_palette("Set2", n_colors=n_colors)
        else:
            base_palette = sns.color_palette("Spectral", n_colors=n_colors)
        group_colors = {
            group: to_hex(base_palette[i % len(base_palette)])
            for i, group in enumerate(unique_groups)
        }

    # Basic statistics
    diff = y_array_flatten - x_array_flatten

    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#4D5154",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D3033",
            "ytick.color": "#2D3033",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#4D5154",
            "legend.shadow": True,
        }
    )

    # Create figure layout
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle(
        f"{x_label} vs. {y_label} Analysis of {data_label}",
        fontsize=20,
        fontweight="bold",
        color="#2D3033",
    )

    # Tick formatter
    formatter = FuncFormatter(lambda x, _: f"{x:,.1f}")

    # Title style for subplots
    title_font = {"fontsize": 15, "fontweight": "semibold", "color": "#2D3033"}

    # Default Colors
    default_scatter_color = "#5E8AB4"
    default_residual_color = "#5E8AB4"
    default_hist_color = "#5E8AB4"
    default_bland_altman_color = "#5E8AB4"

    # Colors for statistical elements
    regression_line_color = "#DC267F"
    identity_line_color = "#444444"
    mean_diff_line_color = "#000000"
    loa_line_color = "#555555"

    # Store group handles and labels for the shared legend
    group_handles: list[plt.Artist] = []
    group_labels: list[str] = []

    # 1. Scatter plot with regression
    ax1 = axes[0, 0]
    # Calculate regression
    slope, intercept, r_value, _, _ = stats.linregress(x_array_flatten, y_array_flatten)
    r_squared = r_value**2
    reg_line = slope * x_array_flatten + intercept

    # Plot scatter points
    if groups_array_str is not None:
        # Plot each group separately
        for i, group in enumerate(sorted_groups):  # type: ignore
            mask = groups_array_str == group
            group_x = x_array_flatten[mask]
            group_y = y_array_flatten[mask]
            color = group_colors.get(str(group), sns.color_palette("colorblind")[i])  # type: ignore
            scatter = ax1.scatter(
                group_x,
                group_y,
                alpha=0.8,
                color=color,
                edgecolors="white",
                linewidth=0.5,
                s=dot_size,
                label=f"{group} (n={np.sum(mask):,})",
                zorder=i + 2,
            )

            # Store handle and label only on the first subplot
            if i == 0 or len(group_handles) < len(sorted_groups):  # type: ignore
                group_handles.append(scatter)
                group_labels.append(f"{group} (n={len(group_x):,})")
    else:
        # Plot all points with the same color
        ax1.scatter(
            x_array_flatten,
            y_array_flatten,
            alpha=0.8,
            color=default_scatter_color,
            edgecolors="white",
            linewidth=0.5,
            s=dot_size,
        )

    # Identity line
    min_val = min(np.min(x_array_flatten), np.min(y_array_flatten))
    max_val = max(np.max(x_array_flatten), np.max(y_array_flatten))
    identity_line = ax1.plot(
        [min_val, max_val],
        [min_val, max_val],
        "--",
        color=identity_line_color,
        linewidth=1.2,
        label="Identity line (y = x)",
    )[0]

    # Regression line with equation and R-squared
    regression_line = ax1.plot(
        x_array_flatten,
        reg_line,
        color=regression_line_color,
        linewidth=regression_line_width,
        linestyle="-",
        alpha=0.6,
        zorder=100,
        label=f"$y = {slope:.2f}x {'+' if intercept >= 0 else '-'} "
        f"{abs(intercept):.2f}$\n$R^2 = {r_squared:.3f}$",
    )[0]

    # Labels and title
    ax1.set_xlabel(f"{x_label} {data_label}", fontsize=13)
    ax1.set_ylabel(f"{y_label} {data_label}", fontsize=13)
    ax1.set_title("Pre vs. Post Scatter Plot", fontdict=title_font)

    # Add subplot-specific legend (no group info)
    ax1.legend(
        handles=[identity_line, regression_line],
        loc="upper left",
        fontsize=10,
        shadow=True,
    )

    ax1.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC")
    ax1.tick_params(axis="both", which="major", labelsize=10)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.yaxis.set_major_formatter(formatter)

    # 2. Residual plot
    ax2 = axes[0, 1]
    # Plot residuals with grouping if provided
    if groups_array_str is not None:
        # Plot each group separately
        for i, group in enumerate(sorted_groups):  # type: ignore
            mask = groups_array_str == group
            group_x = x_array_flatten[mask]
            group_diff = diff[mask]
            color = group_colors.get(str(group), sns.color_palette("colorblind")[i])  # type: ignore
            ax2.scatter(
                group_x,
                group_diff,
                alpha=0.8,
                color=color,
                edgecolors="white",
                linewidth=0.5,
                s=dot_size,
                zorder=i + 2,
            )
    else:
        # Plot all points with the same color
        ax2.scatter(
            x_array_flatten,
            diff,
            alpha=0.8,
            color=default_residual_color,
            s=dot_size,
            edgecolors="white",
            linewidth=0.5,
        )

    zero_line = ax2.axhline(
        y=0,
        color=identity_line_color,
        linestyle="--",
        alpha=0.8,
        linewidth=1.2,
        label="Zero difference",
    )
    ax2.set_xlabel(f"{x_label} {data_label}", fontsize=13)
    ax2.set_ylabel(f"Residuals ({y_label} - {x_label})  {data_label}", fontsize=13)
    ax2.set_title("Residual Plot", fontdict=title_font)
    ax2.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC")
    ax2.tick_params(axis="both", which="major", labelsize=10)
    ax2.xaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_formatter(formatter)

    # Add legend for zero line only
    ax2.legend(handles=[zero_line], loc="best", fontsize=10, shadow=True)

    # 3. Histogram of differences
    ax3 = axes[1, 0]
    if groups_array_str is not None:
        bin_edges = np.histogram_bin_edges(diff, bins=30)
        width = (bin_edges[1] - bin_edges[0]) / len(
            sorted_groups  # type: ignore
        )  # Calculate bar width
        all_percentages: list[
            float
        ] = []  # Track all percentages to set appropriate y-axis limits

        # Calculate the total count of all data points for overall percentage calculation
        total_count = len(diff)

        for i, group in enumerate(sorted_groups):  # type: ignore
            mask = groups_array_str == group
            group_diff = diff[mask]
            color = group_colors.get(str(group), sns.color_palette("colorblind")[i])  # type: ignore
            # Calculate histogram data for the current group
            hist, _ = np.histogram(group_diff, bins=bin_edges)  # density=False here

            # Calculate percentages relative to the total dataset
            percentages = (hist / total_count) * 100
            all_percentages.extend(percentages)

            # Calculate the x positions for the bars of the current group
            x_positions = bin_edges[:-1] + i * width
            ax3.bar(
                x_positions,
                percentages,
                width=width,
                alpha=0.6,
                color=color,
                edgecolor="#555555",
                linewidth=0.5,
            )
        # Adjust y-axis scale for grouped data too
        max_percentage = max(all_percentages) if all_percentages else 5
        # Add 20% padding above the maximum percentage
        ax3.set_ylim(0, max_percentage * 1.2)
    else:
        # In the non-grouped case, this is already showing percentages of the total
        n, _, patches = ax3.hist(
            diff,
            bins=30,
            alpha=0.6,
            color=default_hist_color,
            edgecolor="#555555",
            linewidth=0.5,
        )
        # Calculate percentages for each bin
        percentages = (n / len(diff)) * 100
        # Override the bar heights with percentages
        for patch, percentage in zip(patches, percentages):
            patch.set_height(percentage)
            patch.set_y(0)  # Ensure bars start from y=0
        # Adjust y-axis scale to better fit the data distribution
        max_percentage = max(percentages) if len(percentages) > 0 else 5  # type: ignore
        # Add 20% padding above the maximum percentage
        ax3.set_ylim(0, max_percentage * 1.2)

    zero_line_hist = ax3.axvline(
        x=0,
        color=identity_line_color,
        linestyle="--",
        alpha=0.8,
        linewidth=1.2,
        label="Zero difference",
    )
    ax3.set_xlabel(f"Difference ({y_label} - {x_label}) {data_label}", fontsize=13)
    ax3.set_ylabel("Frequency (%)", fontsize=13)
    ax3.set_title("Distribution of Differences", fontdict=title_font)
    ax3.grid(axis="y", linestyle="--", alpha=0.4, color="#CCCCCC")
    ax3.tick_params(axis="both", which="major", labelsize=10)
    ax3.xaxis.set_major_formatter(formatter)
    ax3.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.1f}%"))

    # Add legend for zero line only
    ax3.legend(handles=[zero_line_hist], loc="best", fontsize=10, shadow=True)

    # 4. Bland-Altman plot
    ax4 = axes[1, 1]
    mean = (x_array_flatten + y_array_flatten) / 2
    # Calculate Bland-Altman statistics for all data
    mean_diff = np.mean(diff)
    std_diff = np.std(diff)
    limit_of_agreement = 1.96 * std_diff

    # Plot scatter points with grouping if provided
    if groups_array_str is not None:
        # Plot each group separately
        for i, group in enumerate(sorted_groups):  # type: ignore
            mask = groups_array_str == group
            group_mean = mean[mask]
            group_diff = diff[mask]
            color = group_colors.get(str(group), sns.color_palette("colorblind")[i])  # type: ignore
            ax4.scatter(
                group_mean,
                group_diff,
                alpha=0.8,
                color=color,
                edgecolors="white",
                linewidth=0.5,
                s=dot_size,
                zorder=i + 2,
            )
    else:
        # Plot all points with the same color
        ax4.scatter(
            mean,
            diff,
            alpha=0.8,
            color=default_bland_altman_color,
            s=dot_size,
            edgecolors="white",
            linewidth=0.5,
        )

    # Draw reference lines (based on all data)
    mean_line = ax4.axhline(
        y=mean_diff,
        color=mean_diff_line_color,
        linestyle="-",
        alpha=0.8,
        linewidth=2.0,
        label=f"Mean diff: {mean_diff:.3f}",
    )
    upper_loa = ax4.axhline(
        y=mean_diff + limit_of_agreement,
        color=loa_line_color,
        linestyle="--",
        alpha=0.8,
        linewidth=1.5,
        label=f"LoA (+1.96 SD): {mean_diff + limit_of_agreement:.3f}",
    )
    lower_loa = ax4.axhline(
        y=mean_diff - limit_of_agreement,
        color=loa_line_color,
        linestyle="--",
        alpha=0.8,
        linewidth=1.5,
        label=f"LoA (-1.96 SD): {mean_diff - limit_of_agreement:.3f}",
    )
    ax4.set_xlabel(f"Mean of {x_label} and {y_label} {data_label}", fontsize=13)
    ax4.set_ylabel(f"Difference ({y_label} - {x_label}) {data_label}", fontsize=13)
    ax4.set_title("Bland-Altman Plot", fontdict=title_font)

    # Create a legend for the statistics lines only
    ax4.legend(
        handles=[mean_line, upper_loa, lower_loa],
        fontsize=10,
        shadow=True,
        loc="best",
    )

    ax4.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC")
    ax4.tick_params(axis="both", which="major", labelsize=10)
    ax4.xaxis.set_major_formatter(formatter)
    ax4.yaxis.set_major_formatter(formatter)

    plt.tight_layout()

    # Create a shared legend for groups at the figure level
    if groups_array_str is not None and group_handles and group_labels:
        # Calculate position for legend
        # Position below the subplots but above the bottom of the figure
        fig.legend(
            handles=group_handles,
            labels=group_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.01),
            ncol=min(
                len(group_handles), 4
            ),  # Adjust number of columns based on group count
            fontsize=10,
            title="Groups",
            title_fontsize=12,
            shadow=True,
            frameon=True,
            facecolor="#FFFFFF",
            edgecolor="#4D5154",
        )
        # Adjust bottom margin to make room for the legend
        plt.subplots_adjust(bottom=0.1)  # Adjust this value as needed

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()


def plot_line(
    x_data: Iterable[Any],
    y_data: Union[Iterable[int | float], list[Iterable[int | float]]],
    group_labels: Optional[list[str]] = None,
    group_colors: Optional[dict[str, str]] = None,
    group_linestyles: Optional[dict[str, str]] = None,
    x_label: str = "X values",
    y_label: str = "Y values",
    title: str = "Line Chart",
    precision: int = 1,
    sort_data: bool = True,
    plot_save_path: Optional[Path] = None,
) -> None:
    """
    Generates a line chart with optional multiple Y-axis data series.

    Parameters
    ----------
    x_data : Iterable[Any]
        X-axis values.
    y_data : Union[Iterable[int | float], list[Iterable[int | float]]]
        Y-axis data series or a list of Y-axis data series.
    group_labels : Optional[list[str]], optional
        Labels for each line, inferred from list index if not provided.
    group_colors : Optional[dict[str, str]], optional
        Custom color mapping, by default None.
    group_linestyles : Optional[dict[str, str]], optional
        Custom line style mapping for each line, by default None.
        Example: {'Series 1': '-', 'Series 2': '--', 'Series 3': '-.'}
        Common styles: '-' (solid), '--' (dashed), '-.' (dashdot),
        ':' (dotted)
    x_label : str, optional
        X-axis label, by default "X values".
    y_label : str, optional
        Y-axis label, by default "Y values".
    title : str, optional
        Plot title, by default "Line Chart".
    precision : int, optional
        Decimal precision for Y-axis values, by default 1.
    sort_data : bool, optional
        Whether to sort the data by X values before plotting, by default True.
    plot_save_path : Optional[Path], optional
        Path to save plot image, by default None.

    Raises
    ------
    ValueError
        If group_labels length does not match y_data_list length.
        If any Y series does not match the shape of X data.
    """
    # Convert input data to numpy arrays
    x_array = np.asarray(x_data).flatten()
    is_multiple_series = (
        isinstance(y_data, (list, tuple))
        and len(y_data) > 0
        and isinstance(y_data[0], (list, tuple, np.ndarray))
        and not isinstance(y_data[0], (str, bytes))
    )
    if is_multiple_series:
        y_series = [np.asarray(ys).flatten() for ys in y_data]
    else:
        y_series = [np.asarray(y_data).flatten()]
    # Check if all Y series match the shape of X data
    if any(ys.shape != x_array.shape for ys in y_series):
        raise ValueError("All Y series must match the shape of X data.")
    if sort_data:
        sort_idx = np.argsort(x_array)
        x_array = x_array[sort_idx]
        for i, ys in enumerate(y_series):
            y_series[i] = ys[sort_idx]

    num_series = len(y_series)

    # Default group labels if none provided
    if group_labels is None:
        group_labels = [f"Series {i + 1}" for i in range(num_series)]

    if len(group_labels) != num_series:
        raise ValueError("group_labels length must match y_data_list length.")

    # Create color mapping if not provided
    if group_colors is None:
        palette = sns.color_palette("Set2", num_series)
        group_colors = {
            label: to_hex(palette[i % len(palette)])
            for i, label in enumerate(group_labels)
        }

    # Create line style mapping if not provided
    if group_linestyles is None:
        default_linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]
        group_linestyles = {
            label: default_linestyles[i % len(default_linestyles)]
            for i, label in enumerate(group_labels)
        }

    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#3A3A3A",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D2D2D",
            "ytick.color": "#2D2D2D",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#3A3A3A",
            "legend.shadow": True,
        }
    )

    # Create figure layout
    _, ax = plt.subplots(figsize=(10, 8))

    # Plot each series
    for i, (y_data, label) in enumerate(zip(y_series, group_labels)):
        ax.plot(
            x_array,
            y_data,
            label=label,
            linewidth=2,
            color=group_colors.get(label, sns.color_palette("colorblind")[i]),
            linestyle=group_linestyles.get(label, "-"),
            alpha=0.9,
        )

    # Set axis labels and title
    ax.set_xlabel(x_label, fontsize=13, labelpad=10)
    ax.set_ylabel(y_label, fontsize=13, labelpad=10)
    ax.set_title(title, fontsize=16, fontweight="semibold", color="#2D3033", pad=15)

    # Configure grid and legend
    ax.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", linewidth=0.8)
    ax.legend(loc="best", fontsize=10)

    # Check if x_data is numeric (int or float)
    if np.issubdtype(x_array.dtype, np.number):
        x_has_floats = not np.allclose(x_array, np.round(x_array))

        if x_has_floats:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.1f}"))
        else:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{int(val):,}"))
    else:
        # For string (categorical) x-axis, set ticks to the category labels
        ax.set_xticks(np.arange(len(x_array)))
        ax.set_xticklabels(x_array)

    # Configure Y-axis formatting
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.{precision}f}"))
    ax.tick_params(axis="both", which="major", labelsize=10)

    # Adjust layout
    plt.tight_layout()

    # Save or show the plot
    if plot_save_path:
        plt.savefig(plot_save_path, dpi=100, bbox_inches="tight")
    else:
        plt.show()


def plot_bar(
    categories: Iterable[Any],
    values: list[Iterable[float]],
    group_labels: Optional[list[str]] = None,
    group_colors: Optional[dict[str, str]] = None,
    x_label: str = "Categories",
    y_label: str = "Values",
    title: str = "Bar Chart",
    sort_by_value: bool = False,
    horizontal: bool = False,
    plot_save_path: Optional[Path] = None,
    plot_lines: bool = False,
) -> None:
    """
    Generates a grouped bar chart with optional group coloring, orientation,
    and an option to plot lines trend.

    Parameters
    ----------
    categories : Iterable[Any]
        Bar categories.
    values : list[Iterable[float]]
        List of value sequences (each for one group).
    group_labels : Optional[list[str]], optional
        Group names, inferred from list index if not provided.
    group_colors : Optional[dict[str, str]], optional
        Custom color mapping, by default None.
    x_label : str, optional
        X-axis label, by default "Categories".
    y_label : str, optional
        Y-axis label, by default "Values".
    title : str, optional
        Plot title, by default "Bar Chart".
    sort_by_value : bool, optional
        Sort bars by value of first group, by default False.
    horizontal : bool, optional
        Plot horizontal bars instead of vertical, by default False.
    plot_save_path : Optional[Path], optional
        Path to save plot image, by default None.
    plot_lines : bool, optional
        If True, plots a line connecting the maximum value of each bar within a group,
        by default False.

    Raises
    ------
    ValueError
        If any value series does not match the shape of categories.
        If group_labels length does not match values_list length.
    """
    # Convert input data to numpy arrays
    cats = np.asarray(categories)
    values_series = [np.asarray(vs) for vs in values]
    # Check if all value series match the shape of categories
    if any(vs.shape != cats.shape for vs in values_series):
        raise ValueError("All value series must match shape of categories.")

    num_series = len(values_series)
    if group_labels is None:
        group_labels = [f"Group {i + 1}" for i in range(num_series)]

    if len(group_labels) != num_series:
        raise ValueError("group_labels length must match values_list length.")
    # Create color mapping if not provided
    if group_colors is None:
        palette = sns.color_palette("Set2", num_series)
        group_colors = {
            label: to_hex(palette[i % len(palette)])
            for i, label in enumerate(group_labels)
        }
    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#3A3A3A",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D2D2D",
            "ytick.color": "#2D2D2D",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#3A3A3A",
            "legend.shadow": True,
        }
    )
    # Create figure layout
    _, ax = plt.subplots(figsize=(10, 8))

    index = np.arange(len(cats))
    total_width = 0.8
    bar_width = total_width / num_series
    offsets = np.linspace(
        -total_width / 2 + bar_width / 2, total_width / 2 - bar_width / 2, num_series
    )
    # Sort categories and values if required
    if sort_by_value:
        sort_idx = np.argsort(values_series[0])[::-1]
        cats = cats[sort_idx]
        values_series = [vs[sort_idx] for vs in values_series]
        index = np.arange(len(cats))
    # Plot each group
    for i, (values, label) in enumerate(zip(values_series, group_labels)):
        bar_color = group_colors.get(label, sns.color_palette("tab20")[i])

        # Derive a darker shade for the line color
        converter = ColorConverter()
        rgb_color = converter.to_rgb(bar_color)
        line_color = to_hex([c * 0.7 for c in rgb_color])  # Darken by 30%

        if horizontal:
            ax.barh(
                index + offsets[i],
                values,
                height=bar_width,
                color=bar_color,
                edgecolor="white",
                linewidth=0.8,
                alpha=0.9,
                label=label,
            )
            if plot_lines:
                ax.plot(
                    values,  # X-coordinates are the values
                    index + offsets[i],  # Y-coordinates are the bar positions
                    color=line_color,  # Use the derived line color
                    linestyle="--",
                    linewidth=1.5,
                    label=f"{label} Trend",
                )
        else:
            ax.bar(
                index + offsets[i],
                values,
                width=bar_width,
                color=bar_color,
                edgecolor="white",
                linewidth=0.8,
                alpha=0.9,
                label=label,
            )
            if plot_lines:
                ax.plot(
                    index + offsets[i],  # X-coordinates are the bar positions
                    values,  # Y-coordinates are the values
                    color=line_color,  # Use the derived line color
                    linestyle="--",
                    linewidth=1.5,
                    label=f"{label} Trend",
                )
    # Set axis formatting
    if horizontal:
        ax.set_yticks(index)
        ax.set_yticklabels(cats)
        ax.set_xlabel(y_label, fontsize=13, labelpad=10)
        ax.set_ylabel(x_label, fontsize=13, labelpad=10)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.1f}"))
    else:
        ax.set_xticks(index)
        ax.set_xticklabels(cats)
        ax.set_xlabel(x_label, fontsize=13, labelpad=10)
        ax.set_ylabel(y_label, fontsize=13, labelpad=10)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.1f}"))

    ax.set_title(title, fontsize=16, fontweight="semibold", color="#2D3033", pad=15)
    ax.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", linewidth=0.8)
    ax.legend(loc="best", fontsize=10)
    ax.tick_params(axis="both", which="major", labelsize=10)
    # Adjust layout
    plt.tight_layout()
    # Save or show the plot
    if plot_save_path:
        plt.savefig(plot_save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()


def plot_pie(
    labels: Iterable[Any],
    values: Iterable[float],
    title: str = "Distribution",  # Changed default title to be more generic
    colors: Optional[Iterable[str]] = None,
    explode: Optional[Iterable[float]] = None,
    display_percent: bool = True,
    start_angle: int = 90,
    donut: bool = True,
    plot_save_path: Optional[Path] = None,
) -> None:
    """
    Generates a pie chart with optional donut style, custom colors, and percentage display.

    Parameters
    ----------
    labels : Iterable[Any]
        Labels for pie slices.
    values : Iterable[float]
        Values corresponding to each label.
    title : str, optional
        Plot title, by default "Distribution".
    colors : Optional[Iterable[str]], optional
        List of hex or named colors for each slice. If None, a curated palette is used.
    explode : Optional[Iterable[float]], optional
        Explode values per slice, by default 0.03 for all, creating a subtle separation.
    display_percent : bool, optional
        Whether to display percentages on slices, by default True.
    start_angle : int, optional
        Starting angle, by default 90 (12 o'clock).
    donut : bool, optional
        Whether to display as donut chart (adds white circle), by default True.
    plot_save_path : Optional[Path], optional
        Path to save the figure. If None, the plot is displayed.

    Raises
    ------
    ValueError
        If labels and values have different lengths.
        If any value is negative.
        If explode values are negative.
    """
    # Convert inputs to numpy arrays for consistency
    labels = np.array(labels)
    values = np.array(values)
    # Validate inputs
    if len(labels) != len(values):
        raise ValueError("Labels and values must have the same length.")
    # Ensure values are non-negative
    if np.any(values < 0):
        raise ValueError("Values must be non-negative.")
    # Handle explode parameter
    if explode is None:
        explode = [0.01] * len(values)  # Subtle separation for all slices
    else:
        explode = np.asarray(explode, dtype=float)
        # Ensure values are non-negative
        if np.any(explode < 0):
            raise ValueError("Explode values must be non-negative.")
    # Normalize values to sum to 1 for percentage display
    values = np.asarray(values, dtype=float) / values.sum()
    if colors is None:
        # Use seaborn palette
        palette = sns.color_palette("pastel", len(values))
        colors = [to_hex(c) for c in palette]

    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#F8F9FA",
            "text.color": "#333333",
            "axes.edgecolor": "#D0D0D0",
            "axes.labelcolor": "#333333",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        }
    )
    # Create figure layout
    fig, ax = plt.subplots(figsize=(9, 9))

    # Set the title
    ax.set_title(title, fontsize=18, fontweight="bold", color="#2C3E50", pad=25)
    # Create chart
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        explode=explode,
        colors=colors,
        startangle=start_angle,
        autopct="%1.1f%%" if display_percent else None,
        pctdistance=0.75,
        labeldistance=1.1,
        textprops={"fontsize": 12, "color": "#4A4A4A"},
        wedgeprops={"linewidth": 1.5, "edgecolor": "#FFFFFF"},
        frame=False,
    )

    # Donut styling
    if donut:
        centre_circle = plt.Circle((0, 0), 0.60, fc="#F8F9FA", zorder=10)
        ax.add_artist(centre_circle)

    # Auto-text Styling
    for autotext in autotexts:
        autotext.set_color("#FFFFFF")
        autotext.set_fontsize(12)
        autotext.set_weight("bold")
        autotext.set_path_effects(
            [pe.Stroke(linewidth=1.5, foreground="black"), pe.Normal()]
        )

    # Label styling
    for text in texts:
        text.set_color("#333333")
        text.set_fontsize(12)
        text.set_weight("semibold")

    ax.axis("equal")

    # Adjust layout
    plt.tight_layout()
    # Save or show the plot
    if plot_save_path:
        plt.savefig(
            plot_save_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor()
        )
    else:
        plt.show()


def plot_boxplot(
    data_arrays: Union[Iterable[int | float], list[Iterable[int | float]]],
    labels=None,
    title="Box Plot",
    xlabel="",
    ylabel="Values",
    figsize=(10, 8),
    showfliers=True,
    fliers_color: str = "#4859F1",
    patch_artist=True,
    colors=None,
    show_mean=True,
    mean_line_color: str = "#DD2941",
    mean_line_style="-",
    plot_save_path=None,
) -> None:
    """Generates a box plot with optional mean line and custom styling.

    Parameters:
    -----------
    data_arrays : Union[Iterable[int | float], list[Iterable[int | float]]]
        Data for each box. Can be a single array or a list of arrays.
    labels : list of str, optional
        Labels for each box. If None, uses default numbering.
    title : str, default "Box Plot"
        Title of the plot.
    xlabel : str, default ""
        X-axis label.
    ylabel : str, default "Values"
        Y-axis label.
    figsize : tuple, default (10, 8)
        Figure size (width, height).
    showfliers : bool, default True
        Whether to show outliers.
    fliers_color : str, default "#4859F1"
        Color for outliers if showfliers is True.
    patch_artist : bool, default True
        Whether to fill boxes with color.
    colors : list, optional
        Colors for each box. If None, uses professional color palette.
    show_mean : bool, default True
        Whether to show mean line for each box.
    mean_line_color : str, default "#DD2941"
        Color for mean line.
    mean_line_style : str, default '-'
        Line style for mean line.
    plot_save_path : Path, optional
        Path to save the plot. If None, displays the plot.

    """
    # Determine if we have single or multiple y-series
    is_multiple_series = (
        isinstance(data_arrays, (list, tuple))
        and len(data_arrays) > 0
        and isinstance(data_arrays[0], (list, tuple, np.ndarray))
        and not isinstance(data_arrays[0], (str, bytes))
    )
    if is_multiple_series:
        data_arrays = [np.asarray(y).flatten() for y in data_arrays]

    n_boxes = len(data_arrays)

    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#3A3A3A",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D2D2D",
            "ytick.color": "#2D2D2D",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#3A3A3A",
            "legend.shadow": True,
        }
    )

    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)

    # Color palette
    if colors is None:
        if n_boxes <= 8:
            palette = sns.color_palette("tab20c", n_colors=n_boxes)
        elif n_boxes <= 12:
            palette = sns.color_palette("tab20", n_colors=n_boxes)
        else:
            palette = sns.color_palette("husl", n_colors=n_boxes)
        colors = [to_hex(palette[i]) for i in range(n_boxes)]
    elif len(colors) < n_boxes:
        # Extend colors if not enough provided
        colors = colors * (n_boxes // len(colors) + 1)
        colors = colors[:n_boxes]

    # Create box plot
    bp = ax.boxplot(
        data_arrays,
        tick_labels=labels,
        showfliers=showfliers,
        patch_artist=patch_artist,
        boxprops=dict(linewidth=1, alpha=0.8),
        whiskerprops=dict(linewidth=1, color="#4D5154"),
        capprops=dict(linewidth=1.2, color="#4D5154"),
        medianprops=dict(linewidth=2, color="#2D3033", alpha=0.9),
        flierprops=dict(
            marker="o",
            markerfacecolor=fliers_color,
            markersize=3,
            markeredgewidth=0.5,
            alpha=0.7,
        ),
    )

    # Color the boxes
    if patch_artist and colors:
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_edgecolor("#4D5154")
            patch.set_linewidth(1.2)

    # Add mean line
    if show_mean:
        for i, dataset in enumerate(data_arrays):
            x_pos = i + 1  # Box plot positions start at 1

            if show_mean:
                mean_val = np.mean(dataset)
                ax.plot(
                    [x_pos - 0.15, x_pos + 0.15],
                    [mean_val, mean_val],
                    color=mean_line_color,
                    linestyle=mean_line_style,
                    linewidth=2.5,
                    alpha=0.5,
                    label="Mean" if i == 0 else "",
                    zorder=10,
                )

    # Grid styling
    ax.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", linewidth=0.8)
    ax.set_axisbelow(True)

    # Labels and title
    ax.set_xlabel(xlabel, fontsize=13, labelpad=10, color="#2D3033")
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10, color="#2D3033")
    ax.set_title(title, fontsize=16, fontweight="semibold", color="#2D3033", pad=15)

    # Format tick labels
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.1f}"))
    ax.tick_params(axis="both", which="major", labelsize=10, colors="#2D2D2D")

    # Add legend if mean is shown
    if show_mean:
        legend = ax.legend(loc="best", fontsize=11, framealpha=0.95)
        legend.get_frame().set_facecolor("#FFFFFF")
        legend.get_frame().set_edgecolor("#3A3A3A")
        legend.get_frame().set_linewidth(0.8)

    plt.tight_layout()

    # Save or show the plot
    if plot_save_path:
        plt.savefig(
            plot_save_path,
            dpi=300,
            bbox_inches="tight",
            facecolor="#F8F9FA",
            edgecolor="none",
        )
    else:
        plt.show()


def plot_cs_cv_ev(
    x_data: Iterable[Any],
    y_data: Union[Iterable[int | float], list[Iterable[int | float]]],
    group_labels: Optional[list[str]] = None,
    group_colors: Optional[dict[str, str]] = None,
    group_linestyles: Optional[dict[str, str]] = None,
    x_label: str = "X values",
    y_label: str = "Y values",
    title: str = "Line Chart",
    precision: int = 1,
    sort_data: bool = True,
    plot_save_path: Optional[Path] = None,
    axes_start_zero: bool = False,
    reference_x: Optional[list[float]] = None,
    reference_y: Optional[list[float]] = None,
    reference_x_labels: Optional[list[str]] = None,
    reference_y_labels: Optional[list[str]] = None,
    highlight_areas: bool = False,
) -> None:
    """Plot Consumer Surplus, Competitive Variation, and Equivalent Variation.

    Parameters
    ----------
    x_data : Iterable[Any]
        Iterable containing the x-axis data.
    y_data : Union[Iterable[int  |  float], list[Iterable[int  |  float]]]
        Iterable containing the y-axis data.
    group_labels : Optional[list[str]], optional
        List of labels for each group, by default None
    group_colors : Optional[dict[str, str]], optional
        Dictionary mapping group labels to colors, by default None
    group_linestyles : Optional[dict[str, str]], optional
        Dictionary mapping group labels to line styles, by default None
    x_label : str, optional
        Label for the x-axis, by default "X values"
    y_label : str, optional
        Label for the y-axis, by default "Y values"
    title : str, optional
        Title of the plot, by default "Line Chart"
    precision : int, optional
        Number of decimal places for y-axis ticks, by default 1
    sort_data : bool, optional
        Whether to sort the data before plotting, by default True
    plot_save_path : Optional[Path], optional
        Path to save the plot image, by default None
    axes_start_zero : bool, optional
        Whether to force the y-axis to start at zero, by default False
    reference_x : Optional[list[float]], optional
        X values for reference lines, by default None
    reference_y : Optional[list[float]], optional
        Y values for reference lines, by default None
    reference_x_labels : Optional[list[str]], optional
        Labels for the X reference lines, by default None
    reference_y_labels : Optional[list[str]], optional
        Labels for the Y reference lines, by default None
    highlight_areas : bool, optional
        Whether to highlight specific areas on the plot, by default False

    Raises
    ------
    ValueError
        If the input data is not valid.
        If the x-axis data is not valid.
        If the y-axis data is not valid.
    """
    # Handle multiple x_data series
    if isinstance(x_data[0], (list, tuple, np.ndarray)) and not isinstance(
        x_data[0], (str, bytes)
    ):
        x_series = [np.asarray(xs).flatten() for xs in x_data]
    else:
        x_array = np.asarray(x_data).flatten()
        x_series = [x_array]

    # Handle y_data
    is_multiple_series = (
        isinstance(y_data, (list, tuple))
        and len(y_data) > 0
        and isinstance(y_data[0], (list, tuple, np.ndarray))
        and not isinstance(y_data[0], (str, bytes))
    )
    if is_multiple_series:
        y_series = [np.asarray(ys).flatten() for ys in y_data]
    else:
        y_series = [np.asarray(y_data).flatten()]

    # Ensure we have matching x_series for each y_series
    if len(x_series) == 1 and len(y_series) > 1:
        x_series = x_series * len(y_series)
    elif len(x_series) != len(y_series):
        raise ValueError("Number of x_series must match y_series or be 1.")

    # Check if all Y series match the shape of corresponding X data
    for i, (xs, ys) in enumerate(zip(x_series, y_series)):
        if ys.shape != xs.shape:
            raise ValueError(
                f"Y series {i} must match the shape of corresponding X data."
            )

    if sort_data:
        for i in range(len(x_series)):
            sort_idx = np.argsort(x_series[i])
            x_series[i] = x_series[i][sort_idx]
            y_series[i] = y_series[i][sort_idx]

    num_series = len(y_series)

    # Default group labels if none provided
    if group_labels is None:
        group_labels = [f"Series {i + 1}" for i in range(num_series)]

    if len(group_labels) != num_series:
        raise ValueError("group_labels length must match y_data_list length.")

    # Create color mapping if not provided
    if group_colors is None:
        colors = ["blue", "green", "red", "orange", "purple", "brown"]
        group_colors = {
            label: colors[i % len(colors)] for i, label in enumerate(group_labels)
        }

    # Create line style mapping if not provided
    if group_linestyles is None:
        default_linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":"]
        group_linestyles = {
            label: default_linestyles[i % len(default_linestyles)]
            for i, label in enumerate(group_labels)
        }

    # Styling
    sns.set_theme(style="whitegrid", font_scale=1.2)
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F9FA",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#3A3A3A",
            "axes.linewidth": 1.0,
            "xtick.color": "#2D2D2D",
            "ytick.color": "#2D2D2D",
            "legend.frameon": True,
            "legend.facecolor": "#FFFFFF",
            "legend.edgecolor": "#3A3A3A",
            "legend.shadow": True,
        }
    )

    # Create figure layout
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot each series
    for i, (x_data, y_data, label) in enumerate(zip(x_series, y_series, group_labels)):
        ax.plot(
            x_data,
            y_data,
            linewidth=1.5,
            color=group_colors.get(label, "black"),
            linestyle=group_linestyles.get(label, "-"),
            alpha=0.8,
            zorder=10,
            label=label,
        )

    # Calculate intersection points for reference lines and areas
    intersection_points = []

    if highlight_areas and len(y_series) >= 1 and (reference_x or reference_y):
        # Use the first series (CS curve) for intersection calculations
        cs_x, cs_y = x_series[0], y_series[0]

        from scipy.interpolate import interp1d

        cs_interp = interp1d(
            cs_x, cs_y, kind="linear", bounds_error=False, fill_value="extrapolate"
        )

        if reference_x:
            # Given x-coordinates, find corresponding y-coordinates on the curve
            for ref_x in reference_x:
                ref_y = cs_interp(ref_x)
                intersection_points.append((ref_x, ref_y))
                # Draw vertical line from x-axis to curve intersection
                ax.plot(
                    [ref_x, ref_x],
                    [0, ref_y],
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=5,
                )
                # Draw horizontal line from y-axis to curve intersection
                ax.plot(
                    [0, ref_x],
                    [ref_y, ref_y],
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=5,
                )

        if reference_y:
            # Given y-coordinates, find corresponding x-coordinates on the curve
            for ref_y in reference_y:
                if cs_y[0] > cs_y[-1]:  # Decreasing function
                    ref_x = np.interp(ref_y, cs_y[::-1], cs_x[::-1])
                else:  # Increasing function
                    ref_x = np.interp(ref_y, cs_y, cs_x)
                intersection_points.append((ref_x, ref_y))
                # Draw horizontal line from y-axis to curve intersection
                ax.plot(
                    [0, ref_x],
                    [ref_y, ref_y],
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=5,
                )
                # Draw vertical line from x-axis to curve intersection
                ax.plot(
                    [ref_x, ref_x],
                    [0, ref_y],
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=5,
                )
    else:
        # If not highlighting areas, draw standard reference lines
        if reference_x:
            for ref_x in reference_x:
                ax.axvline(
                    x=ref_x,
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=5,
                )

        if reference_y:
            for ref_y in reference_y:
                ax.axhline(
                    y=ref_y,
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    zorder=5,
                )

    # The Hicksian curves are the second and third series in y_series
    # Find the x-values for y=0.08 on each Hicksian curve
    try:
        # Use np.interp
        x_hicksian1 = np.interp(0.08, y_series[1][::-1], x_series[1][::-1])
        x_hicksian2 = np.interp(0.08, y_series[2][::-1], x_series[2][::-1])

        ax.plot(
            [x_hicksian1, x_hicksian2],
            [0.08, 0.08],
            color="gray",
            linestyle=":",
            linewidth=2.0,
            alpha=0.8,
            zorder=12,  # Ensure it's on top of other elements
        )

        # Add a label to the new line
        ax.text(
            x_hicksian1 + (x_hicksian2 - x_hicksian1) / 2,
            0.08,
            s="",
            ha="center",
            va="bottom",
            fontsize=12,
            path_effects=[pe.withStroke(linewidth=2, foreground="white")],
        )
    except IndexError:
        print(
            "Could not add line between Hicksian curves. Ensure there are at least 3 data series."
        )

    # Highlight Consumer Surplus area if requested
    if highlight_areas and len(intersection_points) >= 2:
        # Sort intersection points by x-coordinate
        intersection_points.sort(key=lambda p: p[0])

        # Define bounds from intersection points
        x_min_bound = min(p[0] for p in intersection_points)
        x_max_bound = max(p[0] for p in intersection_points)
        y_min_bound = min(
            p[1] for p in intersection_points
        )  # Lower price (market price)
        y_max_bound = max(p[1] for p in intersection_points)  # Upper price bound

        # Use the first series (CS curve) for area calculation
        cs_x, cs_y = x_series[0], y_series[0]
        from scipy.interpolate import interp1d

        cs_interp = interp1d(
            cs_x, cs_y, kind="linear", bounds_error=False, fill_value="extrapolate"
        )

        # Create x values from 0 to the maximum x intersection point
        x_cs = np.linspace(0, x_max_bound, 200)
        y_cs = cs_interp(x_cs)

        # Clip the curve at the upper price bound
        y_cs_clipped = np.minimum(y_cs, y_max_bound)

        # Consumer Surplus: area under demand curve, above market price, within bounds
        ax.fill_between(
            x_cs,
            y_cs_clipped,
            y_min_bound,
            where=(y_cs_clipped >= y_min_bound),
            color="white",
            alpha=1.0,
            label="Consumer Surplus (CS)",
            hatch="\\\\\\",
            edgecolor="green",
            linewidth=0.5,
            zorder=1,
        )

    # Set axis labels and title
    ax.set_xlabel(x_label, fontsize=13, labelpad=10)
    ax.set_ylabel(y_label, fontsize=13, labelpad=10)
    if title is not None:
        ax.set_title(title, fontsize=16, fontweight="semibold", color="#2D3033", pad=15)

    # Force axes to start at zero if requested
    if axes_start_zero:
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

    # Configure grid and legend
    ax.grid(True, linestyle="--", alpha=0.4, color="#CCCCCC", linewidth=0.8)
    ax.legend(loc="best", fontsize=10, framealpha=0.9)

    # Configure axis formatting (formatter is used to display numbers, not for tick labels)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.0f}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:,.{precision}f}"))
    ax.tick_params(axis="both", which="major", labelsize=10)

    # Add text labels at the start of dashed lines on axes
    if reference_y:
        # Use custom labels if provided and the number matches, otherwise use formatted numbers
        labels = (
            reference_y_labels
            if reference_y_labels and len(reference_y_labels) == len(reference_y)
            else [f"${ref_y:.2f}$" for ref_y in reference_y]
        )

        for ref_y, label in zip(reference_y, labels):
            ax.text(
                x=-0.02,
                y=ref_y,
                s=label,
                ha="right",
                va="center",
                fontsize=12,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

    # Add text labels at the start of dashed lines on axes for X
    # It will also work when only y-references are given because intersection_points holds the calculated x-values
    if highlight_areas and intersection_points:
        intersection_points.sort(key=lambda p: p[0])
        # Use custom labels if provided and the number matches, otherwise use formatted numbers
        labels = (
            reference_x_labels
            if reference_x_labels
            and len(reference_x_labels) == len(intersection_points)
            else [f"${p[0]:,.0f}$" for p in intersection_points]
        )

        for p, label in zip(intersection_points, labels):
            ax.text(
                x=p[0],
                y=-0.0015,
                s=label,
                ha="center",
                va="top",
                fontsize=12,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )
    elif reference_x:  # If highlight_areas is False, use standard reference_x
        labels = (
            reference_x_labels
            if reference_x_labels and len(reference_x_labels) == len(reference_x)
            else [f"${ref_x:,.0f}$" for ref_x in reference_x]
        )
        for ref_x, label in zip(reference_x, labels):
            ax.text(
                x=ref_x,
                y=-0.015,
                s=label,
                ha="center",
                va="top",
                fontsize=12,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

    # Remove ticks from the axes
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Adjust layout
    plt.tight_layout()

    # Save or show the plot
    if plot_save_path:
        plt.savefig(plot_save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()
