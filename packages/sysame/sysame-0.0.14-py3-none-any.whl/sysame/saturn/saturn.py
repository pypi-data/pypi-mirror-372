# -*- coding: utf-8 -*-
"""
Module for creating and calling Saturn native process scripts.
"""

##### IMPORTS #####
# Standard imports
from pathlib import Path
import subprocess

# Third party imports

# Local imports

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def unstack_ufm(
    saturn_mx: Path,
    ufm_path: Path,
) -> None:
    """Unstack Saturn/UFM matrix.

    Parameters
    ----------
    saturn_mx : Path
        Path to Saturn MX executable
    ufm_path : Path
        Path to UFM file to unstack

    Raises
    ------
    RuntimeError
        When Saturn fails
    """
    # Create key file
    key_script_path = Path(ufm_path.parent.resolve() / "Key_Unstack.Key")
    vdu_script_path = Path(ufm_path.parent.resolve() / "VDU_Unstack.VDU")
    with open(key_script_path, "wt", encoding="utf-8") as key_file:
        key_file.write(
            "\n".join(
                [
                    "15",
                    "1",
                    "1",
                    "0",
                    "0",
                    "0",
                ]
            )
        )
    with open(vdu_script_path, "wt", encoding="utf-8") as _:
        pass
    args = (
        f"{saturn_mx.resolve()} "
        f"{ufm_path.resolve()} KEY {key_script_path.with_suffix('')} "
        f"VDU {vdu_script_path.with_suffix('')}"
    )
    process_results = subprocess.run(args, capture_output=True, check=False)
    if process_results.returncode == 2:
        print(f" ERROR: Unstacking {ufm_path} Failed")
        raise RuntimeError
    # clean up key and vdu files
    key_script_path.unlink(missing_ok=True)
    vdu_script_path.unlink(missing_ok=True)


def run_satpig(
    saturn_satpig: Path,
    ufs_path: Path,
    ufm_path: Path,
    mode_id: int | str,
) -> None:
    """Run SatPig to produce Saturn Routes.

    Parameters
    ----------
    saturn_satpig : Path
        Path to Saturn SatPig executable
    ufs_path: Path
        Path to UFS file to unstack
    ufm_path : Path
        Path to UFM file to unstack
    mode_id: int | sr
        Userclass/Mode ID

    Raises
    ------
    RuntimeError
        When Saturn fails
    """
    # Create key file
    control_file_path = Path(ufs_path.parent.resolve() / f"UC{mode_id}_CF.DAT")
    with open(control_file_path, "wt", encoding="utf-8") as ct_file:
        ct_file.write(
            "\n".join(
                [
                    "&PARAM",
                    "TRPFOR = F",
                    "CSVFOR = T",
                    "NAMES = F",
                    "ALLOD = F",
                    "FPHMIN = 0.02",
                    f"NOMAD = {mode_id}",
                    "&END",
                ]
            )
        )
    args = (
        f"{saturn_satpig.resolve()} "
        f"{ufs_path.with_suffix('')} {ufm_path.with_suffix('')} "
        f"KR {control_file_path.with_suffix('')}"
    )
    process_results = subprocess.run(args, capture_output=True, check=False)
    if process_results.returncode == 2:
        print(f" ERROR: SatPig for UFS:{ufs_path} & UFM:{ufm_path} has Failed")
        raise RuntimeError
    # Cleanup
    control_file_path.unlink(missing_ok=True)


def ufm_to_omx(
    saturn_mx: Path,
    ufm_path: Path,
) -> None:
    """Convert UFM to OMX.

    Parameters
    ----------
    saturn_mx : Path
        Path to Saturn MX executable
    ufm_path : Path
        Path to UFM file to convert

    Raises
    ------
    RuntimeError
        When Converting UFM to OMX fails
    """
    args = f"{saturn_mx.resolve()} {ufm_path.with_suffix('')} /DUMPO"
    process_results = subprocess.run(args, capture_output=True, check=False)
    if process_results.returncode == 2:
        print(f" ERROR: Converting {ufm_path} to OMX Failed")
        raise RuntimeError


def skims_hw_time(
    satlook_exe: Path,
    ufs_path: Path,
) -> None:
    """Skim HW Time from UFS.

    Parameters
    ----------
    satlook_exe : Path
        Path to Saturn SatLook executable
    ufs_path : Path
        Path to UFS file to skim

    Raises
    ------
    RuntimeError
        When Skimming time off the UFS fails
    """
    args = (
        f'"{satlook_exe.resolve()}" "{ufs_path}" M 28 '
        f'"{ufs_path.with_suffix("")}_TimeSkim" /TIMESKIM'
    )
    process_results = subprocess.run(args, capture_output=True, check=False)
    if process_results.returncode == 2:
        print(f" ERROR: Skimming time from {ufs_path} has Failed")
        raise RuntimeError


def extract_network_data(
    satdb_path: Path,
    network_ufs_file: Path,
) -> None:
    """Export Saturn network data.

    Parameters
    ----------
    satdb_path : Path
        Path to SatDB executable
    network_ufs_file : Path
        Path to UFS file to unstack

    Raises
    ------
    RuntimeError
        When Exporting Nodes or Links fails using SatDB.
    """
    # Create key & VDU files
    nodes_key_file = Path(network_ufs_file.parent.resolve() / "Nodes_Key.Key")
    nodes_vdu_file = Path(network_ufs_file.parent.resolve() / "Nodes_VDU.VDU")
    links_key_file = Path(network_ufs_file.parent.resolve() / "Links_Key.Key")
    links_vdu_file = Path(network_ufs_file.parent.resolve() / "Links_VDU.VDU")
    # create key files
    with open(nodes_key_file, "wt", encoding="utf-8") as ct_file:
        ct_file.write(
            "\n".join(
                [
                    "2",
                    "6",
                    "2",
                    "3",
                    "5",
                    "0",
                    "0",
                    "6",
                    "6",
                    "0",
                    "13",
                    "1",
                    "0",
                    f"{network_ufs_file.parent.resolve()}/Nodes.CSV",
                    "Y",
                    "0",
                    "Y",
                ]
            )
        )
        with open(links_key_file, "wt", encoding="utf-8") as ct_file:
            ct_file.write(
                "\n".join(
                    [
                        "2",
                        "6",
                        "2",
                        "3",
                        "5",
                        "0",
                        "0",
                        "4",
                        "1893",
                        "1803",
                        "4003",
                        "4053",
                        "1863",
                        "4513",
                        "0",
                        "13 ",
                        "1",
                        "0",
                        f"{network_ufs_file.parent.resolve()}/Links.CSV",
                        "0",
                        "y",
                    ]
                )
            )
        with open(nodes_vdu_file, "wt", encoding="utf-8") as _:
            pass
        with open(links_vdu_file, "wt", encoding="utf-8") as _:
            pass
    args = (
        f"{satdb_path.resolve()} "
        f"{network_ufs_file.with_suffix('')} KEY {nodes_key_file.with_suffix('')} "
        f"VDU {nodes_vdu_file.with_suffix('')}"
    )
    process_results = subprocess.run(args, capture_output=True, check=False)
    if process_results.returncode == 2:
        print(f" ERROR: SatDB Failed exporting nodes from {network_ufs_file}")
        raise RuntimeError
    args = (
        f"{satdb_path.resolve()} "
        f"{network_ufs_file.with_suffix('')} KEY {links_key_file.with_suffix('')} "
        f"VDU {links_vdu_file.with_suffix('')}"
    )
    process_results = subprocess.run(args, capture_output=True, check=False)
    if process_results.returncode == 2:
        print(f" ERROR: SatDB Failed exporting links from {network_ufs_file}")
        raise RuntimeError
    # clean up key and vdu files
    nodes_key_file.unlink(missing_ok=True)
    nodes_vdu_file.unlink(missing_ok=True)
    links_key_file.unlink(missing_ok=True)
    links_vdu_file.unlink(missing_ok=True)
