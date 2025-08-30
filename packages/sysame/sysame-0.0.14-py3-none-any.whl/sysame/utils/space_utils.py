"""
Module for all all Space (RAM/Storage) utility related functions and classes.
"""

##### IMPORTS #####

# Standard imports
import platform
import subprocess
import json
from typing import TypedDict

# Third party imports

# Local imports

# Import Rules

##### CONSTANTS #####


##### CLASSES #####
class RAMInfo(TypedDict):
    """Dictionary containing RAM information.

    Attributes
    ----------
    Total : str
        Total RAM capacity.
    """

    Total: str


class StorageInfo(TypedDict, total=False):
    """Dictionary containing storage device information.

    Attributes
    ----------
    Drive : str
        Drive letter or device name.
    Total : str
        Total storage capacity.
    Used : str
        Used storage capacity.
    Free : str
        Free storage capacity.
    Mount : str
        Mount point (only for macOS/Linux).
    """

    Drive: str
    Total: str
    Used: str
    Free: str
    Mount: str


class SystemSpaceInfo(TypedDict, total=False):
    """Dictionary representing system information including RAM and storage.

    Attributes
    ----------
    RAM : RAMInfo
        RAM details.
    Storage : list of StorageInfo
        List of storage device details.
    Error : str
        Error message, if any occurred during system information gathering.
    """

    RAM: RAMInfo
    Storage: list[StorageInfo]
    Error: str


##### FUNCTIONS #####
def get_space_specs() -> SystemSpaceInfo:
    """Retrieve RAM and storage specifications of the system.

    Returns
    -------
    SystemInfo
        Dictionary containing information about total RAM and storage devices.
    """
    system = platform.system()
    info: SystemSpaceInfo = {"RAM": {"Total": ""}, "Storage": []}

    try:
        if system == "Windows":
            # RAM
            ram_script = (
                "Get-CimInstance Win32_PhysicalMemory | "
                "Select-Object Capacity | ConvertTo-Json"
            )
            ram_output = subprocess.check_output(
                ["powershell", "-Command", ram_script],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            ram_data = json.loads(ram_output)
            total_ram_bytes = 0
            if isinstance(ram_data, list):
                total_ram_bytes = sum(
                    int(stick["Capacity"]) for stick in ram_data if "Capacity" in stick
                )
            elif isinstance(ram_data, dict) and "Capacity" in ram_data:
                total_ram_bytes = int(ram_data["Capacity"])
            info["RAM"]["Total"] = f"{total_ram_bytes / (1024**3):.2f} GB"

            # Storage
            storage_script = (
                "Get-CimInstance Win32_LogicalDisk | "
                "Where-Object { $_.DriveType -eq 3 } | "
                "Select-Object DeviceID, Size, FreeSpace | ConvertTo-Json"
            )
            storage_output = subprocess.check_output(
                ["powershell", "-Command", storage_script],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            storage_data = json.loads(storage_output)
            if isinstance(storage_data, dict):
                storage_data = [storage_data]

            for disk in storage_data:
                total = int(disk.get("Size", 0) or 0)
                free = int(disk.get("FreeSpace", 0) or 0)
                used = total - free
                info["Storage"].append(
                    {
                        "Drive": str(disk.get("DeviceID", "")),
                        "Total": f"{total / (1024**3):.2f} GB",
                        "Used": f"{used / (1024**3):.2f} GB",
                        "Free": f"{free / (1024**3):.2f} GB",
                    }
                )

        elif system == "Darwin":
            # RAM
            ram_bytes = int(
                subprocess.check_output(
                    ["sysctl", "-n", "hw.memsize"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            )
            info["RAM"]["Total"] = f"{ram_bytes / (1024**3):.2f} GB"

            # Storage
            df_output = subprocess.check_output(
                ["df", "-H", "/"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).splitlines()
            if len(df_output) >= 2:
                parts = df_output[1].split()
                info["Storage"].append(
                    {
                        "Drive": parts[0],
                        "Total": parts[1],
                        "Used": parts[2],
                        "Free": parts[3],
                        "Mount": parts[5],
                    }
                )

        elif system == "Linux":
            # RAM
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                lines = f.readlines()
            mem_total_kb = int(
                next(
                    (
                        line.split(":")[1].strip().split()[0]
                        for line in lines
                        if "MemTotal" in line
                    ),
                    "0",
                )
            )
            info["RAM"]["Total"] = f"{mem_total_kb / 1024:.2f} MB"

            # Storage
            df_output = subprocess.check_output(
                ["df", "-h", "/"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).splitlines()
            if len(df_output) >= 2:
                parts = df_output[1].split()
                info["Storage"].append(
                    {
                        "Drive": parts[0],
                        "Total": parts[1],
                        "Used": parts[2],
                        "Free": parts[3],
                        "Mount": parts[5],
                    }
                )

    except Exception as e:  # pylint: disable=broad-except
        info["Error"] = f"Failed to get info: {e}"

    return info
