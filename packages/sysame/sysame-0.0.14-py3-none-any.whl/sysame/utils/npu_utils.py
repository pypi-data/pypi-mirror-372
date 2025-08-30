"""
Module for all all NPU utility related functions and classes.
"""

##### IMPORTS #####

# Standard imports
import platform
import subprocess

# Third party imports

# Local imports

# Import Rules

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def get_npu_specs():
    """Check for NPU (Neural Processing Unit) on the system.
    This function checks for the presence of an NPU on the system and retrieves its specifications.

    Returns
    -------
    dict
        A dictionary containing the following keys:
        - 'found': A boolean indicating whether an NPU was found.
        - 'details': A string containing additional details about the NPU.

    Raises
    ------
    Exception
        If there is an error while checking for the NPU or if the platform is unsupported.
        The function may raise an exception if the system is not Windows, macOS, or Linux,
        or if there is an error while checking for the NPU.
    """
    system = platform.system()
    npu_info = {"found": False, "details": "No NPU detected or unsupported platform"}

    try:
        if system == "Windows":
            # Use Windows ML diagnostic tools (requires Windows ML and compatible NPU)
            output = subprocess.check_output(
                [
                    "powershell",
                    "-Command",
                    "Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -like '*NPU*' }",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if output.strip():
                npu_info["found"] = True
                npu_info["details"] = output.strip()

        elif system == "Darwin":
            # Use Apple Neural Engine check (indirect, via system profiler)
            output = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if "Neural Engine" in output:
                npu_info["found"] = True
                npu_info["details"] = "\n".join(
                    [
                        line.strip()
                        for line in output.splitlines()
                        if "Neural Engine" in line
                    ]
                )

        elif system == "Linux":
            # Look for NPU-related devices or drivers
            output = subprocess.check_output(
                ["lshw", "-C", "processor"], stderr=subprocess.DEVNULL, text=True
            )
            if "npu" in output.lower():
                npu_info["found"] = True
                npu_info["details"] = "\n".join(
                    [
                        line.strip()
                        for line in output.splitlines()
                        if "npu" in line.lower()
                    ]
                )
            else:
                # Some NPUs show up under /dev or lsusb
                dev_output = subprocess.getoutput("ls /dev | grep npu")
                if dev_output:
                    npu_info["found"] = True
                    npu_info["details"] = f"Device nodes: {dev_output.strip()}"

    except Exception as e:  # pylint: disable=broad-except
        npu_info["details"] = f"Error while checking NPU: {str(e)}"

    return npu_info
