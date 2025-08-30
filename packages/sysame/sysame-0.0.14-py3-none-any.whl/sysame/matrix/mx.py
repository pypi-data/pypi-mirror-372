# -*- coding: utf-8 -*-
"""
Module for matrix operations.
"""

##### IMPORTS #####
# Standard imports
from pathlib import Path
import itertools
from typing import Optional, Any
import math

# Third party imports
import polars as pl  # type: ignore
import numpy as np
import openmatrix as omx  # type: ignore
from dbfread import DBF  # type: ignore

# Local imports
from sysame.cube import cube

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def read_dbf_to_polars(
    dbf_file_path: Path,
    columns: Optional[list[str]] = None,
) -> pl.DataFrame:
    """Read DBF file into a Polars DataFrame.

    Parameters
    ----------
    dbf_file_path : Path
        Path to the DBF file
    columns : Optional[list[str]], optional
        List of column names to extract. If None, all columns are extracted.

    Returns
    -------
    pl.DataFrame
        DataFrame containing the DBF data
    """
    # Load DBF file data
    dbf_table = DBF(dbf_file_path)

    if columns is None:
        # Extract all columns
        dbf_df = pl.DataFrame(list(dbf_table))
    else:
        # Extract only specified columns
        # First, get field names from the DBF table to validate columns exist
        available_fields = {field for field in dbf_table.field_names}

        # Validate that requested columns exist
        missing_cols = set(columns) - available_fields
        if missing_cols:
            raise ValueError(f"Column(s) not found in DBF file: {missing_cols}")

        # Extract only the specified columns efficiently
        selected_data = []
        for record in dbf_table:
            row_data = {col: record[col] for col in columns}
            selected_data.append(row_data)

        dbf_df = pl.DataFrame(selected_data)

    return dbf_df


def get_mat_stats(
    mat_file: Path,
    voyager_exe: Optional[Path] = None,
    precision: int = 5,
) -> pl.DataFrame:
    """Get stats from Cube .MAT or .OMX file.

    Parameters
    ----------
    mat_file : Path
        Path to Cube .MAT file or .OMX file
    voyager_exe : Optional[Path], optional
        Path to Cube Voyager executable, by default None
        Needed only if the file is .MAT
        and needs to be converted to .OMX
    precision : int, optional
        Number of decimal places to round the stats, by default 5

    Returns
    -------
    stats_df: pl.DataFrame
        Stats from Cube .MAT file with statistics as columns and tabs as rows

    Examples
    --------
    >>> voyager_exe = Path("path/to/voyager.exe")
    >>> mat_file = Path("path/to/matrix.MAT")
    >>> stats_df = get_mat_stats(mat_file, voyager_exe)
    """
    # Ensure mat_file is Path
    mat_file = Path(mat_file)
    # Check if the file might be a .MAT file and ensure voyager_exe is provided
    if mat_file.suffix.upper() == ".MAT" or (
        mat_file.suffix == "" and Path(f"{mat_file}.MAT").exists()
    ):
        if voyager_exe is None:
            raise ValueError("voyager_exe must be provided for .MAT files")
    # If file has no extension, check for both .MAT and .OMX extensions
    if mat_file.suffix == "":
        mat_file_with_mat = mat_file.with_suffix(".MAT")
        mat_file_with_omx = mat_file.with_suffix(".OMX")

        if mat_file_with_mat.exists():
            mat_file = mat_file_with_mat
            cube.mat_to_omx(
                voyager_exe=voyager_exe if voyager_exe is not None else Path(),
                mat_path=mat_file,
                omx_path=mat_file.with_suffix(".OMX"),
            )
        elif mat_file_with_omx.exists():
            mat_file = mat_file_with_omx
        else:
            raise ValueError(
                f"Neither .MAT nor .OMX file for {mat_file} exists. Please check the file path."
            )

    # Handle .MAT file
    elif mat_file.suffix.upper() == ".MAT":
        if not mat_file.exists():
            raise ValueError(
                f"MAT file {mat_file} does not exist. Please check the file path."
            )
        cube.mat_to_omx(
            voyager_exe=voyager_exe if voyager_exe is not None else Path(),
            mat_path=mat_file,
            omx_path=mat_file.with_suffix(".OMX"),
        )

    # Handle .OMX file
    elif mat_file.suffix.upper() == ".OMX":
        if not mat_file.exists():
            raise ValueError(
                f"OMX file {mat_file} does not exist. Please check the file path."
            )

    # Handle case where the file extension is not .MAT or .OMX
    else:
        raise ValueError(
            f"File {mat_file} is not a .MAT or .OMX file. Please check the file path."
        )

    # Read omx
    with omx.open_file(mat_file.with_suffix(".OMX")) as file:
        tabs = file.list_matrices()
        stats: dict[str, dict[str, Any]] = {}
        for tab in tabs:
            matrix = np.array(file[tab][:])
            stats[tab] = {}
            stats[tab]["Shape"] = matrix.shape
            stats[tab]["Total"] = round(matrix.sum(), precision)
            stats[tab]["Intras."] = round(np.sum(np.diag(matrix)), precision)
            stats[tab]["Min."] = round(matrix.min(), precision)
            stats[tab]["Mean"] = round(matrix.mean(), precision)
            stats[tab]["Max."] = round(matrix.max(), precision)
            stats[tab]["Std."] = round(matrix.std(), precision)

            # Handle Min > 0, Max > 0, and Std. when there are no positive values
            positive_values = matrix[matrix > 0]
            if positive_values.size > 0:
                stats[tab]["Min > 0"] = round(positive_values.min(), precision)
                stats[tab]["Mean > 0"] = round(positive_values.mean(), precision)
                stats[tab]["Max > 0"] = round(positive_values.max(), precision)
                stats[tab]["Std. > 0"] = round(positive_values.std(), precision)
            else:
                stats[tab]["Min > 0"] = 0
                stats[tab]["Mean > 0"] = 0
                stats[tab]["Max > 0"] = 0
                stats[tab]["Std. > 0"] = 0
    # Close omx
    file.close()

    # Create df
    # First, get all statistic names from the first tab
    stat_names = list(next(iter(stats.values())).keys())

    # Create a dictionary with statistics data
    df_data = {"tab": list(stats.keys())}
    for stat_name in stat_names:
        df_data[stat_name] = [stats[tab][stat_name] for tab in stats.keys()]

    # Create df with strict=False to allow mixed types
    stats_df = pl.DataFrame(df_data, strict=False)

    return stats_df


def furness(
    matrix: np.ndarray,
    productions: np.ndarray,
    attractions: np.ndarray,
    max_iterations: int = 1_000,
    tolerance: float = 1e-15,
) -> tuple[np.ndarray, list[str]]:
    """
    Compute the Furness matrix using an iterative method.

    Parameters
    ----------
    matrix : np.ndarray
        The input matrix to be adjusted.
    productions : np.ndarray
        The production values for each row.
    attractions : np.ndarray
        The attraction values for each column.
    max_iterations : int, optional
        The maximum number of iterations to perform (default is 1,000).
    tolerance : float, optional
        The convergence tolerance (default is 1e-6).

    Returns
    -------
    matrix: np.ndarray
        The adjusted matrix.
    convergence_track: list[str]
        Track ov convergence stats per iteration

    Notes
    -----
    The Furness method is an iterative technique for adjusting a matrix to match
    given row and column totals.

    Examples
    --------
    >>> import numpy as np
    >>> matrix = np.array([[1, 2], [3, 4]])
    >>> productions = np.array([5, 7])
    >>> attractions = np.array([3, 9])
    >>> result = furness(matrix, productions, attractions)
    >>> np.allclose(result.sum(axis=0), attractions)
    True
    >>> np.allclose(result.sum(axis=1), productions)
    True

    """
    # Convergence track
    convergence_track: list[str] = []
    matrix = matrix.copy()
    # Ensure matrices are floats
    matrix = matrix.astype(float)
    productions = productions.astype(float)
    attractions = attractions.astype(float)
    for i in range(max_iterations):
        # Row adjustment
        row_sums = matrix.sum(axis=1, keepdims=True)  # Shape (n, 1)
        row_factors = productions[:, None] / row_sums  # Broadcasting (n, 1)
        matrix *= row_factors

        # Column adjustment
        col_sums = matrix.sum(axis=0, keepdims=True)  # Shape (1, m)
        col_factors = attractions[None, :] / col_sums  # Broadcasting (1, m)
        matrix *= col_factors

        # Check convergence
        row_error = np.abs(matrix.sum(axis=1) - productions).max()
        col_error = np.abs(matrix.sum(axis=0) - attractions).max()
        # Convergence track
        convergence_track.append(
            f"Its: {i}, Row error: {row_error}, Col error: {col_error}"
        )
        if row_error < tolerance and col_error < tolerance:
            break
    else:
        print("Furness method did not converge within the maximum iterations.")

    return matrix, convergence_track


def expand_matrix(
    mx_df: pl.DataFrame,
    zones_no: int,
) -> pl.DataFrame:
    """Expand matrix to all possible movements (zones x zones).

    Parameters
    ----------
    mx_df : pl.DataFrame
        matrix
    zones_no: int
        number of model zones

    Returns
    -------
    expanded_mx : pl.DataFrame
        expanded matrix

    Examples
    --------
    >>> import polars as pl
    >>> import itertools
    >>> mx_df = pl.DataFrame({"origin": [1, 2], "destination": [3, 4], "value": [5, 6]})
    >>> expanded_mx.shape
    shape: (2, 3)
    >>> zones_no = 5
    >>> expanded_mx = expand_matrix(mx_df, zones_no)
    >>> expanded_mx.shape
    shape: (25, 3)
    """
    # generate all combination
    zone_combination = list(itertools.product(range(1, zones_no + 1), repeat=2))
    # create expanded dataframe
    expanded_mx = pl.DataFrame(
        {
            mx_df.columns[0]: [x[0] for x in zone_combination],
            mx_df.columns[1]: [x[1] for x in zone_combination],
        }
    )
    # normalize datatypes
    d_type_mapping = {
        mx_df.columns[0]: pl.Int32,
        mx_df.columns[1]: pl.Int32,
    }

    # Convert columns to the specified data types
    for col, d_type in d_type_mapping.items():
        expanded_mx = expanded_mx.with_columns(expanded_mx[col].cast(d_type))
        mx_df = mx_df.with_columns(mx_df[col].cast(d_type))
    # remove nans
    mx_df = mx_df.filter(mx_df[mx_df.columns[0]].is_not_null())
    mx_df = mx_df.filter(mx_df[mx_df.columns[1]].is_not_null())
    # merge with the original matrix and fillna with 0
    expanded_mx = expanded_mx.join(
        mx_df, on=[mx_df.columns[0], mx_df.columns[1]], how="full"
    ).fill_null(strategy="zero")
    expanded_mx = expanded_mx.drop(
        f"{mx_df.columns[0]}_right", f"{mx_df.columns[1]}_right"
    )
    # Sort
    expanded_mx = expanded_mx.sort([expanded_mx.columns[0], expanded_mx.columns[1]])

    return expanded_mx


def long_mx_2_wide_mx(
    mx_df: pl.DataFrame,
    zones_no: int,
) -> np.ndarray[Any, Any]:
    """Convert polars long matrix to numpy wide matrix.

    Assumes that the long matrix is in the format of [origin, destination, value].

    Parameters
    ----------
    mx_df : pl.DataFrame
        polars long matrix dataframe to convert
    zones_no: int
        number of model zones

    Returns
    -------
    np_mx : np.ndarray
        numpy wide matrix

    Examples
    --------
    >>> import polars as pl
    >>> import itertools
    >>> mx_df = pl.DataFrame({"origin": [1, 2], "destination": [3, 4], "value": [5, 6]})
    >>> zones_no = 5
    >>> np_mx = long_mx_2_wide_mx(mx_df, zones_no)
    >>> np_mx.shape
    (5, 5)
    """
    # expand matrix
    mx_df = expand_matrix(mx_df, zones_no)
    # reshape to wide polars matrix
    wide_mx = mx_df.pivot(
        index=mx_df.columns[0],
        columns=mx_df.columns[1],
        values=mx_df.columns[2],
        aggregate_function="sum",
    )  # type: ignore
    np_mx = wide_mx.drop(mx_df.columns[0]).to_numpy()

    return np_mx


def wide_mx_2_long_mx(
    mx_array: np.ndarray,
    o_col: str = "o",
    d_col: str = "d",
    v_col: str = "v",
) -> pl.DataFrame:
    """Convert numpy wide matrix to polars long matrix.

    Parameters
    ----------
    mx_array : np.array
        wide numpy matrix array
    o_col : str, optional
        name of origin/production column, by default "o"
    d_col : str, optional
        name of destination/attraction column, by default "d"
    v_col : str, optional
        name of values column, by default "v"

    Returns
    -------
    mx_df : pl.DataFrame
        polars long matrix

    Examples
    --------
    >>> import numpy as np
    >>> mx_array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> mx_df = wide_mx_2_long_mx(mx_array)
    >>> mx_df.shape
    shape: (3, 3)
    """
    # Get the shape of the matrix
    num_rows, num_cols = mx_array.shape

    # Reshape the matrix into a 1D array
    values = mx_array.flatten()

    # Create row and column indices for the long DataFrame
    rows = np.repeat(np.arange(num_rows), num_cols)
    cols = np.tile(np.arange(num_cols), num_rows)

    # Create a polars DataFrame
    mx_df = pl.DataFrame({o_col: rows, d_col: cols, v_col: values})

    # adjust zone numbers
    mx_df = mx_df.with_columns(mx_df[o_col] + 1)
    mx_df = mx_df.with_columns(mx_df[d_col] + 1)

    # cast IDs to int32
    mx_df = mx_df.with_columns(mx_df[o_col].cast(pl.Int32))
    mx_df = mx_df.with_columns(mx_df[d_col].cast(pl.Int32))

    return mx_df


def read_omx_to_polars(
    omx_file_path: Path,
    o_col: str = "o",
    d_col: str = "d",
    limited_tabs: Optional[list[str]] = None,
    stack: bool = False,
    clean_omx: bool = False,
) -> pl.DataFrame:
    """Read OMX file to polars dataframe.

    Parameters
    ----------
    omx_file_path : Path
        full path to the .OMX file
    o_col : str, optional
        name of origin/production vector header, by default "o"
    d_col : str, optional
        name of destination/attraction vector header, by default "d"
    limited_tabs : list[str], optional
        if only specific tabs are needed from the omx
    stack : bool, optional
        if stack then the matrices will be stacked in one vector with
        an additional vector referring to each mx tab
    clean_omx : bool, optional
        whether or not to remove the omx after being read

    Returns
    -------
    matrix_df : pl.DataFrame
        matrix as polars dataframe
    """
    # Create an empty list if limited_tabs is None
    tab_list: list[str] = [] if limited_tabs is None else limited_tabs

    matrix_df = pl.DataFrame()
    # open omx
    omx_mat = omx.open_file(omx_file_path)
    # get matrices
    omx_tabs = omx_mat.list_matrices()

    if len(tab_list) == 0:
        for i, mat_lvl in enumerate(omx_tabs):
            # get matrix level into a polars df
            mx_lvl_df = wide_mx_2_long_mx(
                np.array(omx_mat[mat_lvl]),
                o_col,
                d_col,
                mat_lvl,
            )
            if stack:
                mx_lvl_df = mx_lvl_df.with_columns(pl.lit(mat_lvl).alias("mx"))
                mx_lvl_df = mx_lvl_df.rename({mat_lvl: "value"})
                mx_lvl_df = mx_lvl_df.select([o_col, d_col, "mx", "value"])
                matrix_df = pl.concat([matrix_df, mx_lvl_df])
            else:
                if i == 0:
                    matrix_df = pl.concat([matrix_df, mx_lvl_df])
                else:
                    matrix_df = matrix_df.join(mx_lvl_df, on=[o_col, d_col], how="full")
                    matrix_df = matrix_df.drop(f"{o_col}_right", f"{d_col}_right")

    else:
        counter = 0
        for i, mat_lvl in enumerate(omx_mat.list_matrices()):
            if mat_lvl in tab_list:
                # get matrix level into a polars df
                mx_lvl_df = wide_mx_2_long_mx(
                    np.array(omx_mat[mat_lvl]),
                    o_col,
                    d_col,
                    mat_lvl,
                )
                if stack:
                    mx_lvl_df = mx_lvl_df.with_columns(pl.lit(mat_lvl).alias("mx"))
                    mx_lvl_df = mx_lvl_df.rename({mat_lvl: "value"})
                    mx_lvl_df = mx_lvl_df.select([o_col, d_col, "mx", "value"])
                    matrix_df = pl.concat([matrix_df, mx_lvl_df])
                else:
                    if counter == 0:
                        matrix_df = pl.concat([matrix_df, mx_lvl_df])
                    else:
                        matrix_df = matrix_df.join(
                            mx_lvl_df, on=[o_col, d_col], how="full"
                        )
                        matrix_df = matrix_df.drop(f"{o_col}_right", f"{d_col}_right")
                counter = counter + 1
    omx_mat.close()
    # if removing the omx is needed
    if clean_omx:
        omx_file_path.unlink()

    return matrix_df


def read_cube_mat_to_polars(
    voyager_exe: Path,
    mat_file: Path,
    o_col: str = "o",
    d_col: str = "d",
    limited_tabs: Optional[list[Any]] = None,
    stack: bool = False,
    clean_omx: bool = True,
) -> pl.DataFrame:
    """Read Cube .MAT file into polars dataframe.

    Conversion is done through OMX

    Parameters
    ----------
    voyager_exe : Path
        path to voyager executable
    mat_file : Path
        path to Cube matrix file
    o_col : str, optional
        name of origin/production vector header, by default "o"
    d_col : str, optional
        name of destination/attraction vector header, by default "d"
    limited_tabs : list, optional
        if only specific tabs are needed from the omx
    stack : bool, optional
        if stack then the matrices will be stacked in one vector with
        an additional vector referring to each mx tab
    clean_omx : bool, optional
        whether or not to remove the omx after being read, by default True

    Returns
    -------
    matrix_df : pl.DataFrame
        matrix polars dataframe
    """
    # Create an empty list if limited_tabs is None
    tab_list = [] if limited_tabs is None else limited_tabs

    # convert mat to omx
    cube.mat_to_omx(
        voyager_exe,
        mat_file,
        mat_file.parent / f"{mat_file.stem}.omx",
    )

    matrix_df = read_omx_to_polars(
        omx_file_path=mat_file.parent / f"{mat_file.stem}.omx",
        o_col=o_col,
        d_col=d_col,
        limited_tabs=tab_list,
        stack=stack,
        clean_omx=clean_omx,
    )

    d_type_mapping = {
        o_col: pl.Int32,
        d_col: pl.Int32,
    }

    # Convert columns to the specified data types using the apply function
    for col, d_type in d_type_mapping.items():
        matrix_df = matrix_df.with_columns(matrix_df[col].cast(d_type))

    return matrix_df


def read_mat_to_array(
    voyager_exe: Path,
    mat_file: Path,
    limited_tabs: Optional[list] = None,
    clean_omx: bool = True,
) -> dict[Any, np.ndarray]:
    """Read .MAT into a dictionary of arrays

    Parameters
    ----------
    mat_file : Path
        matrix path
    cube_path : Path
        path to cube voyager executable
    limited_tabs : list[str], optional
        if only specific tabs are needed from the omx, by default None
        matrix tabs to read in
    clean_omx : bool, optional
       whether or not to remove the omx after being read, by default True

    Returns
    -------
    array_dict: dict[Any : np.ndarray]
        dictionary of matrices in array format
    """
    if limited_tabs is None:
        limited_tabs = []  # Create a new list if it's None
    # convert mat to omx
    cube.mat_to_omx(
        voyager_exe,
        mat_file,
        mat_file.parent / f"{mat_file.stem}.omx",
    )
    # create an empty dictionary
    array_dict: dict[Any, np.ndarray] = {}
    # open omx
    omx_path = mat_file.parent / f"{mat_file.stem}.omx"
    omx_mat = omx.open_file(omx_path)
    # get matrices
    if limited_tabs is None or len(limited_tabs) == 0:
        tab_list = omx_mat.list_matrices()
    else:
        tab_list = limited_tabs

    for tab in tab_list:
        # get matrix level into a polars df
        array_dict[tab] = np.array(omx_mat[tab])

    omx_mat.close()
    # if removing the omx is needed
    if clean_omx:
        omx_path.unlink()

    return array_dict


def split_dataframe_into_chunks(
    pl_df: pl.DataFrame,
    chunk_size: int,
) -> list[pl.DataFrame]:
    """Function splits a dataframe to equal size dataframes.

    Parameters
    ----------
    df : pl.DataFrame
        given dataframe to split
    chunk_size : int
        size of each chunk

    Returns
    -------
    chunks : list[pl.DataFrame]
        list of chunk dataframes
    """
    # round up to avoid floats
    chunk_size = math.ceil(chunk_size)
    # split dataframe to equal sizes (= chunk_size)
    chunks = [
        pl_df[i : i + round(chunk_size)]
        for i in range(0, pl_df.shape[0], round(chunk_size))
    ]

    return chunks
