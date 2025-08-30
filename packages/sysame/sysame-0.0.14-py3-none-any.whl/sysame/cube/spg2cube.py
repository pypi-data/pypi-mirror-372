# -*- coding: utf-8 -*-
"""
Module for Converting SPG linefiles to Cube linefiles.
"""

##### IMPORTS #####
# Standard imports
import shlex
import datetime
import math
from pathlib import Path
from typing import Any
from collections import OrderedDict

# Third party imports
import pandas as pd  # type: ignore
import networkx as nx  # type: ignore

# Local imports

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def create_log(
    text: str,
    log_file: Path,
) -> None:
    """Create a log file and write the text to it.

    Parameters
    ----------
    text : str
        Text to be written to the log file.
    log_file : Path
        Path to the log file.
    """
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(text)


def append_log(
    text: str,
    log_file: Path,
) -> None:
    """Append text to the log file.

    Parameters
    ----------
    text : str
        Text to be appended to the log file.
    log_file : Path
        Path to the log file.
    """
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text)


def process_network_data(
    nodes_file: Path,
    links_file: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Process network data from CSV files and convert to WKT format.

    Parameters
    ----------
    nodes_file : Path
        Path to the nodes file.
    links_file : Path
        Path to the links file.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Tuple containing the nodes and links DataFrames.
    """
    _nodes_df = pd.read_csv(nodes_file, dtype={"X": str, "Y": str})
    _nodes_df["GEOM"] = (
        "" + "POINT (" + _nodes_df["X"] + " " + _nodes_df["Y"] + ")" + ""
    )
    _nodes_df.to_csv(
        path_or_buf=f"{nodes_file.stem}.wkt",
        index=False,
        sep=",",
        header=True,
    )

    _links_df = pd.read_csv(
        links_file,
        dtype={"AX": str, "AY": str, "BX": str, "BY": str},
    )
    _links_df["GEOM"] = (
        ""
        + "LINESTRING ("
        + _links_df["AX"]
        + " "
        + _links_df["AY"]
        + ", "
        + _links_df["BX"]
        + " "
        + _links_df["BY"]
        + ")"
        + ""
    )
    _links_df.to_csv(
        path_or_buf=f"{links_file.stem}.wkt",
        index=False,
        sep=",",
        header=True,
    )

    return _nodes_df, _links_df


def parse_stn_hierarchy(input_file: Path, log_file: Path) -> dict[str, int]:
    """Parse the station hierarchy file and return a dictionary of station codes and their ranks.

    Parameters
    ----------
    input_file : Path
        Path to the station hierarchy file.
    log_file : Path
        Path to the log file.

    Returns
    -------
    dict[str, int]
        Dictionary of station codes and their ranks.
    """
    stn_hierarchy_dct: dict[str, int] = OrderedDict()

    with open(input_file, "r", encoding="utf-8") as f:
        text_lines = f.readlines()
        for line in text_lines:
            try:
                tokens = line.split(",")
                stn_hierarchy_dct[tokens[0]] = int(tokens[1])
            except Exception as e:  # pylint: disable=broad-except
                print(e)
                # This try/except is here to catch bad formatting of file (blank lines etc.)

    # stn_hierarchy_dct = dict(sorted(stn_hierarchy_dct.items(), key=operator.itemgetter(1)))

    append_log(text="!- Station hierarchy ([station] - [rank]):\n\n", log_file=log_file)
    append_log(
        text="".join(
            [
                x + " - " + str(stn_hierarchy_dct[x]) + "\n"
                for x in stn_hierarchy_dct.keys()
            ]
        )
        + "\n",
        log_file=log_file,
    )

    return stn_hierarchy_dct


def parse_system_file(
    system_file: Path,
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Parse the system file and return dictionaries of operators and vehicle types.

    Parameters
    ----------
    system_file : Path
        Path to the system file.

    Returns
    -------
    tuple[dict[str, dict], dict[str, dict]]
        Tuple containing dictionaries of operators and vehicle types.
    """

    _operator_dct: dict[str, dict[str, str]] = {}
    _veh_type_dct: dict[str, dict[str, str]] = {}

    def process_system_line(line):
        tokens = shlex.split(line)
        tokens = [t for t in tokens if "=" in t]
        temp_dct = {t.split("=")[0]: t.split("=")[1] for t in tokens}
        return temp_dct

    with open(system_file, "r", encoding="utf-8") as f:
        text_lines = f.readlines()
        for line in text_lines:
            if line.startswith("OPERATOR"):
                temp_dct = process_system_line(line)
                _operator_dct[temp_dct["NAME"]] = temp_dct

            if line.startswith("VEHICLETYPE"):
                temp_dct = process_system_line(line)
                _veh_type_dct[temp_dct["LONGNAME"]] = temp_dct

    return _operator_dct, _veh_type_dct


def expand_veh_type_dct(
    in_veh_type_dct: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Expand the vehicle type dictionary to try and mitigate some of the irregular stock-type nomenclature.

    Parameters
    ----------
    in_veh_type_dct : dict[str, dict[str, str]]
        Input vehicle type dictionary.

    Returns
    -------
    dict[str, dict[str, str]]
        Expanded vehicle type dictionary.
    """
    out_veh_type_dct = {}

    def try_new_key(key, item):
        try:
            out_veh_type_dct[key] = item
        except:
            pass

    for v_key in in_veh_type_dct.keys():
        v_item = in_veh_type_dct[v_key]
        out_veh_type_dct[v_key] = v_item
        if "/" in v_key:
            try_new_key(v_key.replace("/", "x"), v_item)
        if "x" in v_key:
            try_new_key(v_key.replace("x", "/"), v_item)
        if "(" in v_key and ")" in v_key:
            try_new_key(v_key.replace("(", "x").replace(")", ""), v_item)
            try_new_key(v_key.replace("(", "/").replace(")", ""), v_item)
        try_new_key("--" + v_key, v_item)

    return out_veh_type_dct


def get_hhmm_from_mpm(
    mpm: int | str,
) -> str:
    """Convert minutes past midnight (MPM) to hours and minutes (HH:MM) format.

    Parameters
    ----------
    mpm : int | str
        Minutes past midnight.

    Returns
    -------
    str
        Time in HH:MM format.
    """
    mpm = int(mpm)
    if mpm >= 1440:
        mpm = mpm - 1440
    mpm = str(mpm).rjust(4, "0")
    return (
        str(math.trunc(int(mpm) / 60)).rjust(2, "0")
        + ":"
        + str(int(mpm) % 60).rjust(2, "0")
    )


def process_spg_data(
    spg_folder: Path,
    log_file: Path,
) -> dict[str, dict]:
    """Parse the SPG files return a dictionary of services.

    Parameters
    ----------
    spg_folder : Path
        Path to the folder containing SPG files.
    log_file : Path
        Path to the log file.

    Returns
    -------
    dict[str, dict]
        Dictionary of services with service ID as keys and service details as values.
    """
    toc_index_in_filename = 0  # TODO: rethink this
    spg_list = [
        f.stem
        for f in [f for f in spg_folder.iterdir() if f.is_file()]
        if f.suffix == ".spg"
    ]
    append_log(text="!- .SPG files loaded:\n\n", log_file=log_file)
    append_log(text="".join([x + ".spg\n" for x in spg_list]) + "\n", log_file=log_file)

    service_dct = {}
    for file_name in spg_list:
        # Test files have operator specified in file name as 4th component - need to ensure something similar enforced in new files
        if toc_index_in_filename > -1:
            operator = file_name.split("_")[toc_index_in_filename]
        # operator = shlex.split(file_name)[3]
        # Looks like operator is going to be lumped in with stock type, so a plan might be to split by "_", take first token (say "XC") as operator, .....
        # then replace("XC_", "") in the stock type to take it back to standard generic type, should cover multiple instances in stock type.

        with open(file_name + ".spg", "r", encoding="utf-8") as f:
            next(f)  # Skip header
            services = f.read().strip()
            services = services[:-1].split("T\n")  # [:-1] to remove trailing 'T'
            # Process a single service

            for service in services:
                points = service.strip().split("\n")
                point_no = 0
                points_dct = {}

                # operator=''

                for point in points:
                    point_dct = {}
                    point_dct["stn_code"] = point[1:4]
                    point_dct["js_ind"] = point[4:6]
                    point_dct["arr_time_mpm"] = point[6:10].strip().rjust(4, "0")
                    point_dct["dep_time_mpm"] = point[10:14].strip().rjust(4, "0")
                    point_dct["stop_type"] = point[14:15]
                    point_dct["route_code"] = point[15:19]

                    if toc_index_in_filename > -1:
                        stock_type = point[19:]  # operator_stock_type = point[19:]
                    else:
                        operator_stock_type = point[19:]
                        operator = operator_stock_type.split("--")[0]
                        # stock_type = operator_stock_type.replace(operator + '--', '')
                        stock_type = operator_stock_type

                    point_dct["stock_type"] = stock_type.strip()

                    point_dct["arr_time_hhmm"] = get_hhmm_from_mpm(
                        point_dct["arr_time_mpm"]
                    )
                    point_dct["dep_time_hhmm"] = get_hhmm_from_mpm(
                        point_dct["dep_time_mpm"]
                    )

                    points_dct[point_no] = point_dct
                    point_no += 1

                temp_dct = {}

                # Given that ultimately all services should only have one stock type (split/joins removed etc.), store initial type for use in final conversion.
                temp_dct["initial_stock_type"] = points_dct[0]["stock_type"]

                temp_dct["dep_time_mpm_service_start"] = points_dct[0]["dep_time_mpm"]
                temp_dct["arr_time_mpm_service_end"] = points_dct[
                    max(points_dct.keys())
                ]["arr_time_mpm"]
                temp_dct["operator"] = operator
                temp_dct["points"] = points_dct
                temp_dct["spg_txt"] = service.strip()

                # Analyse points to form service signature

                temp_dct["line_id_output"] = "".join(
                    [
                        points_dct[0]["dep_time_hhmm"],
                        " ",
                        points_dct[0]["stn_code"],
                        "-",
                        points_dct[point_no - 1]["stn_code"],
                        " ",
                        points_dct[point_no - 1]["arr_time_hhmm"],
                    ]
                )
                service_id = "".join(
                    [
                        operator,
                        " ",
                        points_dct[0]["dep_time_mpm"],
                        " ",
                        points_dct[0]["stn_code"],
                        "-",
                        points_dct[point_no - 1]["stn_code"],
                        " ",
                        points_dct[point_no - 1]["arr_time_mpm"],
                    ]
                )

                # service_id = ''.join([points_dct[0]['dep_time_hhmm'],' ',points_dct[0]['stn_code'],'-',points_dct[point_no-1]['stn_code'],' ', points_dct[point_no-1]['arr_time_hhmm']])
                service_dct[service_id] = temp_dct
                # print(service_id)

    append_log(
        text="Total number of services read in = "
        + str(len([x for x in service_dct.keys()]))
        + ".\n",
        log_file=log_file,
    )

    return service_dct


def log_section_divider() -> str:
    """Section divider for log files.

    Returns
    -------
    str
        Section divider string.
    """
    return "\n               ///////////////////////////////////////////////////\n"


def log_subsection_divider() -> str:
    """ ""Subsection divider for log files.

    Returns
    -------
    str
        Subsection divider string.
    """
    return "\n                                 ///////////\n\n"


def remodel_raw_service_dct(
    raw_service_dct: dict[str, dict],
    stn_hierarchy_dct: dict[str, int],
    operator_dct: dict[str, dict],
    log_file: Path,
) -> dict[str, dict]:
    """Remodel the raw service dictionary to remove services that are not in the system file and those with split/join markers.

    Parameters
    ----------
    raw_service_dct : dict[str, dict]
        Raw service dictionary to be remodeled.
    stn_hierarchy_dct : dict[str, int]
        Station hierarchy dictionary.
    operator_dct : dict[str, dict]
        Operator dictionary.
    log_file : Path
        Path to the log file.

    Returns
    -------
    dict[str, dict]
        Remodeled raw service dictionary.
    """
    append_log(
        text=log_section_divider()
        + "                          /// SERVICE LEVEL ANALYSIS ///\n\n",
        log_file=log_file,
    )

    ######################################################
    append_log(
        text="!- Remove services where TOC not in system file.\n\n",
        log_file=log_file,
    )

    in_service_dct = raw_service_dct
    out_service_dct = {}

    change_count = 0

    for s_key in in_service_dct.keys():
        operator = in_service_dct[s_key]["operator"]
        if operator in operator_dct.keys():
            out_service_dct[s_key] = in_service_dct[s_key]
        else:
            append_log(
                text="Service: " + s_key + " Operator: " + " " + operator + "\n",
                log_file=log_file,
            )
            change_count += 1
    if change_count == 0:
        append_log(text="No instances found.\n", log_file=log_file)

    append_log(text=log_subsection_divider(), log_file=log_file)

    ######################################################
    append_log(
        text="!- Remove services that have a split/join marker - for manual treatment.\n\n",
        log_file=log_file,
    )

    in_service_dct = out_service_dct
    out_service_dct = {}

    change_count = 0

    for s_key, s_values in in_service_dct.items():
        #####18012021 update#####
        # Get needed service info
        points_dct = s_values["points"]
        operatorStr = s_values["operator"]
        spgTxt = s_values["spg_txt"]
        # get unique js_ind
        unique_js_inds = list(set([points_dct[x]["js_ind"] for x in points_dct.keys()]))
        # to capture first record errors in the services input records
        if "M0" not in unique_js_inds:
            continue
        # remove standard service (M0)
        unique_js_inds.remove("M0")
        # if serrvice has a split/join (J1, V1)
        if len(unique_js_inds) > 0:
            # if 'V1' in unique_js_inds or 'J1' in unique_js_inds:
            # append_log('Service: ' + s_key + ' - Join/Split Indicators: ' + ' '.join(unique_js_inds) + '\n')
            # get unique js_ind (again cause it's been cleaned from M0 above)
            unique_js_inds = list(
                set([points_dct[x]["js_ind"] for x in points_dct.keys()])
            )
            # empty dict
            serviceParts = {}
            # empty list
            all_stations = []
            # loop over js_ind to split the service parts
            for ind in unique_js_inds:
                serviceSplit = {
                    k: v for k, v in points_dct.items() if v["js_ind"] == ind
                }
                # re-key dectionary
                serviceSplit = {i: v for i, v in enumerate(serviceSplit.values())}
                # rename service to include service part (J1, V1, M0)
                serviceParts[s_key + " (" + ind + ")"] = serviceSplit
                # get dict length
                dct_len = len(serviceSplit)
                # empty list
                part_unique_stns = []
                # loop over dict keys and append station to stations list
                for i in range(0, dct_len):
                    part_unique_stns.append(serviceSplit[i]["stn_code"])
                # combine all parts' stations
                all_stations.extend(part_unique_stns)
            # remove standard M0 from list
            unique_js_inds.remove("M0")
            # check if it's a J (Join) or V (Split) service
            # if Join
            if "J" in unique_js_inds[0]:
                # prepare to count stations occurancies
                unique_stns = []
                unique_stns = pd.DataFrame(all_stations, columns=["Station"])
                unique_stns["occ"] = 0
                # count stns occurancies
                for i, row in unique_stns.iterrows():
                    stn = unique_stns.at[i, "Station"]
                    occs = unique_stns.at[i, "occ"]
                    occurances = all_stations.count(stn)
                    unique_stns.at[i, "occ"] = occs + occurances
                # keep those that appear more than once as it's where the join/split is happening
                join_split_points = unique_stns.loc[unique_stns["occ"] > 1].reset_index(
                    drop=True
                )
                # if more than one then if join then keep the last, if split then keep the first
                if len(join_split_points) > 1:
                    join_split_points = join_split_points.iloc[[-1]]
                    join_split_points = join_split_points.reset_index(drop=True)
                stn = join_split_points.at[0, "Station"]
                stops_dct = {}
                # get  the location of the split/join station for each part
                for part in serviceParts:
                    stop_dct = {
                        k: v
                        for k, v in serviceParts[part].items()
                        if v["stn_code"] == stn
                    }
                    for key in stop_dct:
                        stop = key
                    stops_dct[part] = stop
                # get separate dicts for the main route and the split/join route
                service_to_fill = {
                    k: v for (k, v) in serviceParts.items() if "M0" not in k
                }
                service_to_fill_from = {
                    k: v for (k, v) in serviceParts.items() if "M0" in k
                }
                # get key of the service to fill (split/join route)
                service_to_fill_k = list(service_to_fill.keys())[0]
                # get key of the service to fill from (main route)
                service_to_fill_from_k = list(service_to_fill_from.keys())[0]
                # Update stock type for each part of the service
                partLength = len(service_to_fill[service_to_fill_k])
                mainLength = len(service_to_fill_from[service_to_fill_from_k])
                part_stock = service_to_fill[service_to_fill_k][0]["stock_type"]
                main_stock = service_to_fill_from[service_to_fill_from_k][0][
                    "stock_type"
                ]
                for stop_key in service_to_fill[service_to_fill_k]:
                    service_to_fill[service_to_fill_k][stop_key]["stock_type"] = (
                        part_stock
                    )
                for stop_key in service_to_fill_from[service_to_fill_from_k]:
                    service_to_fill_from[service_to_fill_from_k][stop_key][
                        "stock_type"
                    ] = main_stock
                # get the location of the stop for the main route
                service_to_fill_from_stop = stops_dct[service_to_fill_from_k]
                # get the partial route from the main route (if split then anything beyond the common stn, if join then anything before it)
                route_filling = {
                    k: v
                    for (k, v) in service_to_fill_from[service_to_fill_from_k].items()
                    if k > service_to_fill_from_stop
                }
                # update stocktype
                for stop_key in route_filling:
                    route_filling[stop_key]["stock_type"] = part_stock
                # update route
                service_to_fill[service_to_fill_k].update(route_filling)
                # get the updated service
                service_to_fill = service_to_fill[service_to_fill_k]
                # re-key dict
                service_to_fill = {i: v for i, v in enumerate(service_to_fill.values())}
                # get the main service
                service_to_fill_from = service_to_fill_from[service_to_fill_from_k]
                # re-key dict
                service_to_fill_from = {
                    i: v for i, v in enumerate(service_to_fill_from.values())
                }
                # get a list of the new service
                to_fill_keys_list = list(service_to_fill)
                # get first stn
                to_fill_first_stop = to_fill_keys_list[0]
                # get last stn
                to_fill_last_stop = to_fill_keys_list[-1]
                # get a list of the main service
                to_fill_from_keys_list = list(service_to_fill_from)
                # get first stn
                to_fill_from_first_stop = to_fill_from_keys_list[0]
                # get last stn
                to_fill_from_last_stop = to_fill_from_keys_list[-1]
                # new dectionary for the new service
                out_service_to_fill = {}
                # add related info
                out_service_to_fill["arr_time_mpm_service_end"] = service_to_fill[
                    max(service_to_fill.keys())
                ]["arr_time_mpm"]
                out_service_to_fill["dep_time_mpm_service_start"] = service_to_fill[0][
                    "dep_time_mpm"
                ]
                out_service_to_fill["initial_stock_type"] = part_stock
                out_service_to_fill["line_id_output"] = (
                    "".join(
                        [
                            service_to_fill[to_fill_first_stop]["dep_time_hhmm"],
                            " ",
                            service_to_fill[to_fill_first_stop]["stn_code"],
                            "-",
                            service_to_fill[to_fill_last_stop]["stn_code"],
                            " ",
                            service_to_fill[to_fill_last_stop]["arr_time_hhmm"],
                        ]
                    )
                    + " ("
                    + service_to_fill_k[-3:]
                )
                out_service_to_fill["operator"] = operatorStr
                out_service_to_fill["points"] = service_to_fill
                out_service_to_fill["spg_txt"] = spgTxt
                stops_lngth = len(out_service_to_fill["points"])
                for i in range(0, stops_lngth):
                    out_service_to_fill["points"][i]["stock_type"] = part_stock
                # new dectionary for the main service
                out_service_to_fill_from = {}
                # add related info
                out_service_to_fill_from["arr_time_mpm_service_end"] = (
                    service_to_fill_from[max(service_to_fill_from.keys())][
                        "arr_time_mpm"
                    ]
                )
                out_service_to_fill_from["dep_time_mpm_service_start"] = (
                    service_to_fill_from[0]["dep_time_mpm"]
                )
                out_service_to_fill_from["initial_stock_type"] = main_stock
                out_service_to_fill_from["line_id_output"] = (
                    "".join(
                        [
                            service_to_fill_from[to_fill_from_first_stop][
                                "dep_time_hhmm"
                            ],
                            " ",
                            service_to_fill_from[to_fill_from_first_stop]["stn_code"],
                            "-",
                            service_to_fill_from[to_fill_from_last_stop]["stn_code"],
                            " ",
                            service_to_fill_from[to_fill_from_last_stop][
                                "arr_time_hhmm"
                            ],
                        ]
                    )
                    + " ("
                    + service_to_fill_from_k[-3:]
                )
                out_service_to_fill_from["operator"] = operatorStr
                out_service_to_fill_from["points"] = service_to_fill_from
                out_service_to_fill_from["spg_txt"] = spgTxt
                stops_lngth = len(out_service_to_fill_from["points"])
                for i in range(0, stops_lngth):
                    out_service_to_fill_from["points"][i]["stock_type"] = part_stock

                append_log(
                    text="Service: "
                    + s_key
                    + " - Join/Split Indicators: "
                    + " ".join(unique_js_inds)
                    + " treated to "
                    + service_to_fill_k
                    + " - AND - "
                    + service_to_fill_from_k
                    + "\n",
                    log_file=log_file,
                )

            # check if it's a J (Join) or V (Split) service
            # if Split
            elif "V" in unique_js_inds[0]:
                # prepare to count stations occurancies
                unique_stns = []
                unique_stns = pd.DataFrame(all_stations, columns=["Station"])
                unique_stns["occ"] = 0
                # count stns occurancies
                for i, row in unique_stns.iterrows():
                    stn = unique_stns.at[i, "Station"]
                    occs = unique_stns.at[i, "occ"]
                    occurances = all_stations.count(stn)
                    unique_stns.at[i, "occ"] = occs + occurances
                # keep those that appear more than once as it's where the join/split is happening
                join_split_points = unique_stns.loc[unique_stns["occ"] > 1].reset_index(
                    drop=True
                )
                # if more than one then if join then keep the last, if split then keep the first
                if len(join_split_points) > 1:
                    join_split_points = join_split_points.iloc[[0]]
                    join_split_points = join_split_points.reset_index(drop=True)
                stn = join_split_points.at[0, "Station"]
                stops_dct = {}
                # get  the location of the split/join station for each part
                for part in serviceParts:
                    stop_dct = {
                        k: v
                        for k, v in serviceParts[part].items()
                        if v["stn_code"] == stn
                    }
                    for key in stop_dct:
                        stop = key
                    stops_dct[part] = stop
                # get separate dicts for the main route and the split/join route
                service_to_fill = {
                    k: v for (k, v) in serviceParts.items() if "M0" not in k
                }
                service_to_fill_from = {
                    k: v for (k, v) in serviceParts.items() if "M0" in k
                }
                # get key of the service to fill (split/join route)
                service_to_fill_k = list(service_to_fill.keys())[0]
                # get key of the service to fill from (main route)
                service_to_fill_from_k = list(service_to_fill_from.keys())[0]
                # Update stock type for each part of the service
                partLength = len(service_to_fill[service_to_fill_k])
                mainLength = len(service_to_fill_from[service_to_fill_from_k])
                part_stock = service_to_fill[service_to_fill_k][partLength - 1][
                    "stock_type"
                ]
                main_stock = service_to_fill_from[service_to_fill_from_k][
                    mainLength - 1
                ]["stock_type"]
                for stop_key in service_to_fill[service_to_fill_k]:
                    service_to_fill[service_to_fill_k][stop_key]["stock_type"] = (
                        part_stock
                    )
                for stop_key in service_to_fill_from[service_to_fill_from_k]:
                    service_to_fill_from[service_to_fill_from_k][stop_key][
                        "stock_type"
                    ] = main_stock
                # get the location of the stop for the main route
                service_to_fill_from_stop = stops_dct[service_to_fill_from_k]
                # get the partial route from the main route (if split then anything beyond the common stn, if join then anything before it)
                route_filling = {
                    k: v
                    for (k, v) in service_to_fill_from[service_to_fill_from_k].items()
                    if k < service_to_fill_from_stop
                }
                # update stocktype
                for stop_key in route_filling:
                    route_filling[stop_key]["stock_type"] = part_stock
                # update route
                second_fill_dct = service_to_fill[service_to_fill_k]
                # tmp dict
                tmp_dct = {}
                # start count at 0
                count_fill = 0
                # add from the foute filling and the split part in the correct order
                for i in route_filling:
                    tmp_dct[i] = route_filling[i]
                    count_fill += 1
                for i in second_fill_dct:
                    tmp_dct[count_fill] = second_fill_dct[i]
                    count_fill += 1
                # update new service dict
                service_to_fill[service_to_fill_k] = tmp_dct
                service_to_fill = service_to_fill[service_to_fill_k]
                # re-key dict
                service_to_fill = {i: v for i, v in enumerate(service_to_fill.values())}
                # update main service dict
                service_to_fill_from = service_to_fill_from[service_to_fill_from_k]
                # re-key dict
                service_to_fill_from = {
                    i: v for i, v in enumerate(service_to_fill_from.values())
                }
                # update stocktype
                for stop_key in service_to_fill_from:
                    service_to_fill_from[stop_key]["stock_type"] = main_stock
                # get a list of the new service
                to_fill_keys_list = list(service_to_fill)
                # get first stn
                to_fill_first_stop = to_fill_keys_list[0]
                # get last stn
                to_fill_last_stop = to_fill_keys_list[-1]
                # get a list of the main service
                to_fill_from_keys_list = list(service_to_fill_from)
                # get first stn
                to_fill_from_first_stop = to_fill_from_keys_list[0]
                # get last stn
                to_fill_from_last_stop = to_fill_from_keys_list[-1]
                # new dectionary for the new service
                out_service_to_fill = {}
                # add related info
                out_service_to_fill["arr_time_mpm_service_end"] = service_to_fill[
                    max(service_to_fill.keys())
                ]["arr_time_mpm"]
                out_service_to_fill["dep_time_mpm_service_start"] = service_to_fill[0][
                    "dep_time_mpm"
                ]
                out_service_to_fill["initial_stock_type"] = part_stock
                out_service_to_fill["line_id_output"] = (
                    "".join(
                        [
                            service_to_fill[to_fill_first_stop]["dep_time_hhmm"],
                            " ",
                            service_to_fill[to_fill_first_stop]["stn_code"],
                            "-",
                            service_to_fill[to_fill_last_stop]["stn_code"],
                            " ",
                            service_to_fill[to_fill_last_stop]["arr_time_hhmm"],
                        ]
                    )
                    + " ("
                    + service_to_fill_k[-3:]
                )
                out_service_to_fill["operator"] = operatorStr
                out_service_to_fill["points"] = service_to_fill
                out_service_to_fill["spg_txt"] = spgTxt
                stops_lngth = len(out_service_to_fill["points"])
                for i in range(0, stops_lngth):
                    out_service_to_fill["points"][i]["stock_type"] = part_stock
                # new dectionary for the main service
                out_service_to_fill_from = {}
                # add related info
                out_service_to_fill_from["arr_time_mpm_service_end"] = (
                    service_to_fill_from[max(service_to_fill_from.keys())][
                        "arr_time_mpm"
                    ]
                )
                out_service_to_fill_from["dep_time_mpm_service_start"] = (
                    service_to_fill_from[0]["dep_time_mpm"]
                )
                out_service_to_fill_from["initial_stock_type"] = main_stock
                out_service_to_fill_from["line_id_output"] = (
                    "".join(
                        [
                            service_to_fill_from[to_fill_from_first_stop][
                                "dep_time_hhmm"
                            ],
                            " ",
                            service_to_fill_from[to_fill_from_first_stop]["stn_code"],
                            "-",
                            service_to_fill_from[to_fill_from_last_stop]["stn_code"],
                            " ",
                            service_to_fill_from[to_fill_from_last_stop][
                                "arr_time_hhmm"
                            ],
                        ]
                    )
                    + " ("
                    + service_to_fill_from_k[-3:]
                )
                out_service_to_fill_from["operator"] = operatorStr
                out_service_to_fill_from["points"] = service_to_fill_from
                out_service_to_fill_from["spg_txt"] = spgTxt
                stops_lngth = len(out_service_to_fill_from["points"])
                for i in range(0, stops_lngth):
                    out_service_to_fill_from["points"][i]["stock_type"] = part_stock

                append_log(
                    text="Service: "
                    + s_key
                    + " - Join/Split Indicators: "
                    + " ".join(unique_js_inds)
                    + " treated to "
                    + service_to_fill_k
                    + " - AND - "
                    + service_to_fill_from_k
                    + "\n",
                    log_file=log_file,
                )

            # add to ouput services dict
            out_service_dct[service_to_fill_k] = out_service_to_fill
            out_service_dct[service_to_fill_from_k] = out_service_to_fill_from

            #####18012021 update#####
            change_count += 1
        else:
            out_service_dct[s_key] = in_service_dct[s_key]

    if change_count == 0:
        append_log(text="No instances found.\n", log_file=log_file)

    append_log(text=log_subsection_divider(), log_file=log_file)

    append_log(
        text="!- Remove services that have > 1 type of rolling stock specified, without a split/join marker (removed above).\n\n",
        log_file=log_file,
    )

    in_service_dct = out_service_dct
    out_service_dct = {}

    change_count = 0

    for s_key, s_value in in_service_dct.items():
        points_dct = s_value["points"]
        # unique_js_inds = list(set([points_dct[x]['js_ind'] for x in points_dct.keys()]))
        unique_stock_types = list(
            set([points_dct[x]["stock_type"] for x in points_dct.keys()])
        )

        if len(unique_stock_types) > 1:  # > len(unique_js_inds):
            append_log(
                text="Service: "
                + s_key
                + " - Stock Types: "
                + " ".join(unique_stock_types)
                + "\n",
                log_file=log_file,
            )  # + ' - Join/Split Indicators: ' + ' '.join(unique_js_inds) + '\n')
            change_count += 1
        else:
            out_service_dct[s_key] = in_service_dct[s_key]

    if change_count == 0:
        append_log(text="No instances found.\n", log_file=log_file)

    append_log(text=log_subsection_divider(), log_file=log_file)

    append_log(
        text="!- Remove services where stock type not in expanded system file list of stock types.\n\n",
        log_file=log_file,
    )

    in_service_dct = out_service_dct
    out_service_dct = {}

    change_count = 0

    for s_key, s_value in in_service_dct.items():
        points_dct = s_value["points"]
        # By this point, in theory should only be one stock type per service, but anyway....
        unique_stock_types = list(
            set([points_dct[x]["stock_type"] for x in points_dct.keys()])
        )
        st_ok = True
        for st in unique_stock_types:
            if st not in veh_type_dct.keys():
                st_ok = False
                break

        if st_ok:
            out_service_dct[s_key] = in_service_dct[s_key]
        else:
            append_log(
                text="Service: "
                + s_key
                + " - Stock Types: "
                + " ".join(unique_stock_types)
                + "\n",
                log_file=log_file,
            )
            change_count += 1

    if change_count == 0:
        append_log("No instances found.\n")

    append_log(log_subsection_divider())

    append_log(
        "!- Remove services where < 2 service points intersect with model network.\n\n"
    )

    in_service_dct = out_service_dct
    out_service_dct = {}

    stns_in_network = list(nodes_df[nodes_df["STATIONCODE"].notnull()]["STATIONCODE"])

    change_count = 0

    for s_key, s_value in in_service_dct.items():
        points_dct = s_value["points"]
        stns_in_service = [points_dct[x]["stn_code"] for x in points_dct.keys()]
        if len(list(set(stns_in_service).intersection(stns_in_network))) >= 2:
            out_service_dct[s_key] = in_service_dct[s_key]
        else:
            append_log(
                "Service: " + s_key + " Points: " + " ".join(stns_in_service) + "\n"
            )
            change_count += 1
    if change_count == 0:
        append_log("No instances found.\n")

    append_log(log_subsection_divider())

    append_log(
        "Total number of services remaining, following service level modifications = "
        + str(len([x for x in out_service_dct.keys()]))
        + ".\n"
    )

    append_log(
        log_section_divider()
        + "                          /// POINT LEVEL ANALYSIS ///\n\n"
    )

    append_log(
        "!- Remove service points where the corresponding station is not in the model network.\n\n"
    )

    # Run with the same service dct from here, no more service level changes, only points.
    service_dct = out_service_dct
    out_service_dct = {}

    change_count = 0

    for s_key, s_value in service_dct.items():
        points_in_dct = s_value["points"]
        i = 0
        points_out_dct = {}
        change_flag = False
        change_points = []
        for l_key in points_in_dct.keys():
            if points_in_dct[l_key]["stn_code"] in stns_in_network:
                points_out_dct[i] = points_in_dct[l_key]
                i += 1
            else:
                change_points.append(points_in_dct[l_key]["stn_code"])
                change_flag = True
        if change_flag == True:
            append_log(s_key + " has " + str(len(change_points)) + " changes.\n")
            append_log("Changes: " + "".join([s + " " for s in change_points]) + "\n")
            append_log(
                "Old pattern: "
                + "".join(
                    [points_in_dct[x]["stn_code"] + " " for x in points_in_dct.keys()]
                )
                + "\n"
            )
            append_log(
                "New pattern: "
                + "".join(
                    [points_out_dct[x]["stn_code"] + " " for x in points_out_dct.keys()]
                )
                + "\n\n"
            )
            change_count += 1
        service_dct[s_key]["points"] = points_out_dct

    if change_count == 0:
        append_log("No instances found.\n")

    append_log(log_subsection_divider())
    append_log("!- Force stopping at service extremes where truncated.\n\n")

    change_count = 0

    for s_key, s_value in service_dct.items():
        points_out_dct = s_value["points"]
        if points_out_dct[0]["stop_type"] != "N":
            points_out_dct[0]["stop_type"] = "N"
            append_log(
                "Service: "
                + s_key
                + " - First stop type changed for station: "
                + points_out_dct[0]["stop_type"]
                + "\n"
            )
            change_count += 1
        if points_out_dct[max(points_out_dct.keys())]["stop_type"] != "N":
            points_out_dct[max(points_out_dct.keys())]["stop_type"] = "N"
            append_log(
                "Service: "
                + s_key
                + " - Last stop type changed for station: "
                + points_out_dct[max(points_out_dct.keys())]["stop_type"]
                + "\n"
            )
            change_count += 1
        service_dct[s_key]["points"] = points_out_dct

    if change_count == 0:
        append_log("No instances found.\n")

    append_log(log_subsection_divider())
    append_log(
        "!- Suppress DWELL at service extremes, and list offsets (minutes) for truncated services.\n\n"
    )

    change_count = 0

    # Added later to suppress dwells at the start and/or end of all services (originally just truncated services).
    for s_key, s_value in service_dct.items():
        service_origin_stn = s_value["line_id_output"].split(" ")[1].split("-")[0]
        service_destination_stn = s_value["line_id_output"].split("-")[1].split(" ")[0]

        service_has_offset = False

        points_out_dct = service_dct[s_key]["points"]

        points_out_dct[0]["arr_time_hhmm"] = points_out_dct[0]["dep_time_hhmm"]
        points_out_dct[0]["arr_time_mpm"] = points_out_dct[0]["dep_time_mpm"]

        if points_out_dct[0]["stn_code"] != service_origin_stn:
            service_has_offset = True
            o_offset_mpm = get_time_2_minus_1(
                service_dct[s_key]["dep_time_mpm_service_start"],
                points_out_dct[0]["dep_time_mpm"],
            )
            o_offset_stn = points_out_dct[0]["stn_code"]
        else:
            o_offset_mpm = 0
            o_offset_stn = service_origin_stn

        points_out_dct[max(points_out_dct.keys())]["dep_time_hhmm"] = points_out_dct[
            max(points_out_dct.keys())
        ]["arr_time_hhmm"]
        points_out_dct[max(points_out_dct.keys())]["dep_time_mpm"] = points_out_dct[
            max(points_out_dct.keys())
        ]["arr_time_mpm"]

        if (
            points_out_dct[max(points_out_dct.keys())]["stn_code"]
            != service_destination_stn
        ):
            service_has_offset = True
            d_offset_mpm = get_time_2_minus_1(
                points_out_dct[max(points_out_dct.keys())]["dep_time_mpm"],
                service_dct[s_key]["arr_time_mpm_service_end"],
            )
            d_offset_stn = points_out_dct[max(points_out_dct.keys())]["stn_code"]
        else:
            d_offset_mpm = 0
            d_offset_stn = service_destination_stn

        if service_has_offset == True:
            change_count += 1
            service_dct[s_key]["offset"] = (
                str(o_offset_mpm)
                + " "
                + o_offset_stn
                + "-"
                + d_offset_stn
                + " "
                + str(d_offset_mpm)
            )
            append_log(
                "Service: "
                + s_key
                + " | Offset: "
                + service_dct[s_key]["offset"]
                + "\n"
            )
        else:
            service_dct[s_key]["offset"] = ""

        service_dct[s_key]["points"] = points_out_dct

    if change_count == 0:
        append_log("No instances found.\n")

    append_log(log_subsection_divider())
    append_log(
        log_section_divider()
        + "                          /// TIME PERIOD ANALYSIS ///\n\n"
    )

    stn_hierarchy_stns_only = stn_hierarchy_dct.keys()

    for s_key, s_value in service_dct.items():
        points_dct = s_value["points"]

        def allocate_mpm_to_tp(mpm):
            mpm = int(mpm)
            if mpm >= 1440:
                mpm = mpm - 1440
            if mpm >= 420 and mpm < 600:
                tp = "AM"
            elif mpm >= 600 and mpm < 960:
                tp = "IP"
            elif mpm >= 960 and mpm < 1140:
                tp = "PM"
            else:
                tp = "OP"

            return tp

        ###
        # Allocate time period based on service start time.
        service_start = s_value["dep_time_mpm_service_start"]
        time_period = allocate_mpm_to_tp(service_start)
        s_value["tp_service_start"] = time_period

        ###
        # Allocate time period based on time first on network.
        service_dct[s_key]["stn_code_first_on_nw"] = points_dct[0]["stn_code"]
        service_dct[s_key]["dep_time_mpm_first_on_nw"] = points_dct[0]["dep_time_mpm"]
        service_dct[s_key]["dep_time_hhmm_first_on_nw"] = points_dct[0]["dep_time_hhmm"]

        first_on_network = s_value["dep_time_mpm_first_on_nw"]
        time_period = allocate_mpm_to_tp(first_on_network)
        service_dct[s_key]["tp_first_on_nw"] = time_period

        ###
        # Allocate time period based on station hierarchy (might as well build timed stopping pattern at the same time).
        key_stn_dep_dct = {}
        timed_stopping_pattern = []
        for point_no in points_dct.keys():
            point = points_dct[point_no]
            if point["stop_type"] != "P":
                timed_stopping_pattern.append(
                    point["stn_code"]
                    + " "
                    + point["dep_time_hhmm"]
                    + " ("
                    + point["stop_type"]
                    + ") "
                )
                if point["stn_code"] in stn_hierarchy_stns_only:
                    key_stn_dep_dct[point["stn_code"]] = point["dep_time_mpm"]

        # Analyse key station dictionary to assess hierarchy
        if key_stn_dep_dct:
            stn_code = ""
            stn_rank = 10000
            for key in key_stn_dep_dct.keys():
                if stn_hierarchy_dct[key] < stn_rank:
                    stn_code, stn_rank = key, stn_hierarchy_dct[key]

            dep_time_mpm = key_stn_dep_dct[stn_code]
            service_dct[s_key]["tp_stn_hierarchy"] = allocate_mpm_to_tp(dep_time_mpm)
            service_dct[s_key]["tp_stn_hierarchy_stn"] = (
                stn_code
                + " (rank="
                + str(stn_rank)
                + ") - "
                + get_hhmm_from_mpm(dep_time_mpm)
            )
        else:
            service_dct[s_key]["tp_stn_hierarchy"] = s_value["tp_first_on_nw"]
            service_dct[s_key]["tp_stn_hierarchy_stn"] = "N/A"

        service_dct[s_key]["stopping_pattern"] = " - ".join(timed_stopping_pattern)

    append_log("!- Allocate time periods to services based on different methods.\n\n")

    def n_services(tp, measure):
        return (
            tp
            + ": "
            + str(
                len(
                    [
                        service_dct[s_key][measure]
                        for s_key, s_value in service_dct.items()
                        if s_value[measure] == tp
                    ]
                )
            )
        )

    append_log(
        text="!- Method 1 - Service start time.\n",
        log_file=log_file,
    )
    measure = "tp_service_start"
    append_log(
        test="Services by TP :- "
        + " | ".join(
            [
                n_services("AM", measure),
                n_services("IP", measure),
                n_services("PM", measure),
                n_services("OP", measure),
            ]
        )
        + "\n\n",
        log_file=log_file,
    )

    append_log(
        test="!- Method 2 - Service first appears on network.\n",
        log_file=log_file,
    )
    measure = "tp_first_on_nw"
    append_log(
        text="Services by TP :- "
        + " | ".join(
            [
                n_services("AM", measure),
                n_services("IP", measure),
                n_services("PM", measure),
                n_services("OP", measure),
            ]
        )
        + "\n\n",
        log_file=log_file,
    )

    append_log(
        text="!- Method 3 - Station hierarchy (& first appearance on network where no intersection with ranked station).\n",
        log_file=log_file,
    )
    measure = "tp_stn_hierarchy"
    append_log(
        text="Services by TP :- "
        + " | ".join(
            [
                n_services("AM", measure),
                n_services("IP", measure),
                n_services("PM", measure),
                n_services("OP", measure),
            ]
        )
        + "\n",
        log_file=log_file,
    )

    append_log(
        text=log_subsection_divider(),
        log_file=log_file,
    )

    return service_dct


def compile_shortest_paths(
    service_dct: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Compile shortest paths.

    Parameters
    ----------
    service_dct : dict[str, dict[str, Any]]
        Service dictionary containing service information.

    Returns
    -------
    dict[str, dict[str, Any]]
        Dictionary containing shortest path information for each service.
    """
    stn_to_stn_list: list = []
    for s_key in service_dct.keys():
        points_dct = service_dct[s_key]["points"]
        i = 0
        for i in range(len(points_dct.keys()) - 1):
            stn_to_stn_list.append(
                points_dct[i]["stn_code"] + "-" + points_dct[i + 1]["stn_code"]
            )

    stn_to_stn_list = list(set(stn_to_stn_list))

    edges = links_df[["A", "B", "DISTANCE"]].itertuples(index=False, name=None)
    graph = nx.DiGraph()

    for edge in edges:
        graph.add_edge(edge[0], edge[1], weight=edge[2])

    sp_dct = {}
    for stn_to_stn in stn_to_stn_list:
        temp_dct = {}
        temp_dct["From_Stn"] = stn_to_stn.split("-")[0]
        temp_dct["From_Node"] = node_stn_dct[temp_dct["From_Stn"]]["N"]

        temp_dct["To_Stn"] = stn_to_stn.split("-")[1]
        temp_dct["To_Node"] = node_stn_dct[temp_dct["To_Stn"]]["N"]

        temp_dct["Path"] = nx.dijkstra_path(
            graph, temp_dct["From_Node"], temp_dct["To_Node"]
        )
        temp_dct["Path"] = [int(n) for n in temp_dct["Path"]]
        sp_dct[stn_to_stn] = temp_dct

    return sp_dct


def get_time_2_minus_1(
    str_time_1: str,
    str_time_2: str,
) -> int:
    """Calculate the difference in minutes between two time strings.

    Parameters
    ----------
    str_time_1 : str
        First time string in HHMM format.
    str_time_2 : str
        Second time string in HHMM format.

    Returns
    -------
    int
        Difference in minutes between the two time strings.
    """
    signed_mins = int(str_time_2) - int(str_time_1)

    if signed_mins < 0:
        unsigned_mins = 1440 + signed_mins
    else:
        unsigned_mins = signed_mins

    return unsigned_mins


def cubeify_service_dct(
    moira_service_dct: dict[str, dict[str, Any]],
    sp_dct: dict[str, dict[str, Any]],
    operator_dct: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Convert service dictionary to Cube format.

    Parameters
    ----------
    moira_service_dct : dict[str, dict[str, Any]]
        Moira service dictionary containing service information.
    sp_dct : dict[str, dict[str, Any]]
        Dictionary containing shortest path information for each service.
    operator_dct : dict[str, dict[str, Any]]
        Dictionary containing operator information.

    Returns
    -------
    dict[str, dict[str, Any]]
        Cube formatted services.
    """
    all_nodes_xy_dct = nodes_df[["N", "X", "Y"]].set_index("N")
    all_nodes_xy_dct = all_nodes_xy_dct.to_dict("index")

    def process_stop(point, last_dep_time, end_stn):
        body_elements.extend([str(node_stn_dct[point["stn_code"]]["N"])])

        nntime = get_time_2_minus_1(last_dep_time, point["arr_time_mpm"])
        dwell = get_time_2_minus_1(point["arr_time_mpm"], point["dep_time_mpm"])

        body_elements.extend(["NNTIME=" + str(nntime)])
        if dwell > 0:
            body_elements.extend(["DWELL=" + str(dwell)])

        if points_dct[i]["stop_type"] == "U":
            body_elements.extend(["ACCESS=1"])
        elif points_dct[i]["stop_type"] == "D":
            body_elements.extend(["ACCESS=2"])

        if end_stn == False:
            # sp[1]='N=' + sp[1]
            body_elements.extend(sp[1:-1])

        return point["dep_time_mpm"]

    cube_service_dct = {}

    for s_key in moira_service_dct.keys():
        temp_service_dct = {}

        s_dct = moira_service_dct[s_key]

        head_elements = []
        # head_elements.append('LINE NAME=' + '"' + s_key + '"')
        head_elements.append("LINE NAME=" + '"' + s_dct["line_id_output"] + '"')
        head_elements.append("MODE=1")
        head_elements.append(
            "OPERATOR=" + operator_dct[s_dct["operator"]]["NUMBER"]
        )  # Sort when file naming convention agreed.
        head_elements.append(
            "COLOR=" + operator_dct[s_dct["operator"]]["NUMBER"]
        )  # Same as OPERATOR.
        head_elements.append("ONEWAY=T")
        head_elements.append(
            "HEADWAY[1]=TBC"
        )  # This is dealt with at the end when services are allocated to time periods by method.

        # << Wait for split/join method to be decided before dealing with rolling stock>>.
        vehicle_type = veh_type_dct[s_dct["initial_stock_type"]]["NUMBER"]
        head_elements.append("VEHICLETYPE=" + str(vehicle_type))  # RS work.
        # head_elements.append('VEHICLETYPE=??') # RS work.
        if s_dct["offset"] != "":
            head_elements.append("USERA2=" + '"' + "OFFSET " + s_dct["offset"] + '"')

        points_dct = s_dct["points"]
        body_elements = []
        last_dep_time = 0
        start_stn = True

        for i in range(len(points_dct.keys()) - 1):
            sp = sp_dct[
                points_dct[i]["stn_code"] + "-" + points_dct[i + 1]["stn_code"]
            ]["Path"]
            sp = [str(-1 * s) for s in sp]

            if start_stn == True:
                body_elements.extend([sp[0]])
                # body_elements[0]='N=' + str(-1*int(body_elements[0]))
                body_elements[0] = str(-1 * int(body_elements[0]))

                dwell = get_time_2_minus_1(
                    points_dct[i]["arr_time_mpm"], points_dct[i]["dep_time_mpm"]
                )
                if dwell > 0:
                    body_elements.extend(["DWELL=" + str(dwell)])

                if points_dct[i]["stop_type"] == "U":
                    body_elements.extend(["ACCESS=1"])
                elif points_dct[i]["stop_type"] == "D":
                    body_elements.extend(["ACCESS=2"])

                body_elements.extend(sp[1:-1])

                start_stn = False
                last_dep_time = points_dct[i]["dep_time_mpm"]

            else:
                if points_dct[i]["stop_type"] == "P":
                    body_elements.extend(sp[:-1])
                else:
                    last_dep_time = process_stop(points_dct[i], last_dep_time, False)

        process_stop(points_dct[i + 1], last_dep_time, True)

        # Prepend 'N=' to first body element, and any node following a time/dwell/access etc.
        element_no = 0
        prev_element_not_numeric = True
        for e in body_elements:
            try:
                int(e)
                if prev_element_not_numeric == True:
                    e = "N=" + e
                    prev_element_not_numeric = False
            except:
                prev_element_not_numeric = True

            body_elements[element_no] = e
            element_no += 1

        cube_text = ", ".join(head_elements[:4]) + ", \n"
        cube_text += ", ".join(head_elements[4:]) + ", \n"

        body_chunks = [
            body_elements[i : i + 8] for i in range(0, len(body_elements), 8)
        ]

        for i in range(len(body_chunks)):
            if i < len(body_chunks) - 1:
                cube_text += ", ".join(body_chunks[i]) + ", \n"
            else:
                cube_text += ", ".join(body_chunks[i])

        # Collate service data and add to dictionary.

        temp_service_dct["cube_txt"] = cube_text

        service_nodes = [
            str(e).replace("N=", "").replace("-", "") for e in body_elements
        ]
        service_nodes = [int(n) for n in service_nodes if n.isnumeric()]
        service_wkt = (
            ""
            + "LINESTRING ("
            + ", ".join(
                [
                    all_nodes_xy_dct[n]["X"] + " " + all_nodes_xy_dct[n]["Y"]
                    for n in service_nodes
                ]
            )
            + ")"
            + ""
        )

        temp_service_dct["geom"] = service_wkt

        cube_service_dct[s_key] = temp_service_dct

    # Top up the CUBE service dictionary with bits of info from the corresponding MOIRA service dictionary.
    for s_key in cube_service_dct:
        cube_service_dct[s_key]["operator"] = moira_service_dct[s_key]["operator"]
        cube_service_dct[s_key]["stopping_pattern"] = moira_service_dct[s_key][
            "stopping_pattern"
        ]
        cube_service_dct[s_key]["tp_first_on_nw"] = moira_service_dct[s_key][
            "tp_first_on_nw"
        ]
        cube_service_dct[s_key]["tp_service_start"] = moira_service_dct[s_key][
            "tp_service_start"
        ]
        cube_service_dct[s_key]["tp_stn_hierarchy"] = moira_service_dct[s_key][
            "tp_stn_hierarchy"
        ]
        cube_service_dct[s_key]["tp_stn_hierarchy_stn"] = moira_service_dct[s_key][
            "tp_stn_hierarchy_stn"
        ]
        cube_service_dct[s_key]["spg_txt"] = moira_service_dct[s_key]["spg_txt"]

        # cube_service_dct[s_key]['operator'] = cube_service_dct[s_key]['operator']

    return cube_service_dct


def output_cube_services(
    cube_service_dct: dict[str, dict[str, Any]],
    output_folder: Path,
) -> None:
    """Output Cube services to files.

    Parameters
    ----------
    cube_service_dct : dict[str, dict[str, Any]]
        Dictionary of Cube services keyed by service ID.
    output_folder : Path
        Path to output folder.
    """

    headway_dct = {"AM": "180", "IP": "360", "PM": "180", "OP": "720"}

    # Dump line files for first on network time period slicing.
    def write_lines_files(tp_choice, export_folder):
        unique_tp = list(
            set([cube_service_dct[s][tp_choice] for s in cube_service_dct.keys()])
        )
        for tp in unique_tp:
            tp_lst = [";;<<PT>><<LINE>>;;"]
            tp_lst.extend(
                [
                    cube_service_dct[s]["cube_txt"]
                    for s in cube_service_dct.keys()
                    if cube_service_dct[s][tp_choice] == tp
                ]
            )
            tp_lst.sort()  # File header survives this sort.
            tp_text = (
                "\n\n".join(tp_lst)
                .strip()
                .replace("HEADWAY[1]=TBC", "HEADWAY[1]=" + headway_dct[tp])
            )
            with open(output_folder / f"output_{tp}.lin", "w", encoding="utf-8") as f:
                f.write(tp_text)

    write_lines_files("tp_service_start", "service_lin_ss")
    write_lines_files("tp_first_on_nw", "service_lin_fon")
    write_lines_files("tp_stn_hierarchy", "service_lin_sh")

    # Summary of all services and GIS representation.
    cube_service_df = pd.DataFrame.from_dict(
        cube_service_dct, orient="index"
    ).reset_index()

    col_rename_dct = {"index": "service"}
    cube_service_df = cube_service_df.rename(columns=col_rename_dct)
    cube_service_df = cube_service_df[
        [
            "service",
            "operator",
            "stopping_pattern",
            "tp_service_start",
            "tp_first_on_nw",
            "tp_stn_hierarchy",
            "tp_stn_hierarchy_stn",
            "cube_txt",
            "spg_txt",
            "geom",
        ]
    ]
    cube_service_df.to_csv(
        path_or_buf="Cube_Service_Long_List.csv",
        index=False,
        sep=",",
        header=True,
    )


def spg_to_cube(
    spg_folder: Path,
    system_file: Path,
    nodes_file: Path,
    links_file: Path,
    stn_hierarchy_file: Path,
    output_folder: Path,
) -> None:
    """Convert SPG data to Cube format.

    Parameters
    ----------
    spg_folder : Path
        Path to the folder containing SPG files.
    system_file : Path
        Path to the system file.
    nodes_file : Path
        Path to the nodes file.
    links_file : Path
        Path to the links file.
    stn_hierarchy_file : Path
        Path to the station hierarchy file.
    output_folder : Path
        Path to the output folder.
    """
    start_time = datetime.datetime.now()

    create_log(
        "!- MOIRA-CUBE Processing Log - "
        + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        + "\n"
    )

    append_log(
        log_section_divider()
        + "                          /// INPUT INFORMATION ///\n\n"
    )

    nodes_df, links_df = process_network_data(nodes_file, links_file)
    node_stn_dct = nodes_df[~nodes_df["STATIONCODE"].isnull()][
        ["N", "STATIONCODE", "X", "Y"]
    ].set_index("STATIONCODE")
    node_stn_dct = node_stn_dct.to_dict("index")

    stn_hierarchy_dict = parse_stn_hierarchy(
        stn_hierarchy_file, output_folder / "ProcessLog.LOG"
    )

    operator_dict, veh_type_dct = parse_system_file(system_file)

    veh_type_dct = expand_veh_type_dct(veh_type_dct)

    raw_service_dct = process_spg_data(spg_folder, output_folder / "ProcessLog.LOG")
    moira_service_dct = remodel_raw_service_dct(
        raw_service_dct=raw_service_dct,
        stn_hierarchy_dct=stn_hierarchy_dict,
        operator_dct=operator_dict,
        log_file=output_folder / "ProcessLog.LOG",
    )

    sp_dct = compile_shortest_paths(moira_service_dct)

    cube_service_dct = cubeify_service_dct(
        moira_service_dct=moira_service_dct, sp_dct=sp_dct, operator_dct=operator_dict
    )
    output_cube_services(
        cube_service_dct=cube_service_dct,
        output_folder=output_folder,
    )

    end_time = datetime.datetime.now()
    delta = end_time - start_time
    delta_seconds = int(delta.total_seconds())

    append_log(
        text="Processing complete, time taken: " + str(delta_seconds) + " seconds.",
        log_file=output_folder / "ProcessLog.LOG",
    )
