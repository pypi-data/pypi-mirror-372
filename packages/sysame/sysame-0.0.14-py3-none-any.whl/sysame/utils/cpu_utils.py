"""
Module for all all CPU utility related functions and classes.
"""

##### IMPORTS #####

# Standard imports
import platform
import subprocess
import os
import json

# Third party imports

# Local imports

# Import Rules

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def get_cpu_specs():
    """
    Get CPU specs for the current system.
    This function retrieves the CPU specifications such as name, number of cores,
    number of logical processors, and maximum clock speed.

    Returns
    -------
    dict
        A dictionary containing the following keys:
        - 'Name': Name of the CPU
        - 'NumberOfCores': Number of cores in the CPU
        - 'NumberOfLogicalProcessors': Number of logical processors in the CPU
        - 'MaxClockSpeed': Maximum clock speed of the CPU
    """
    system = platform.system()
    cpu_info = {}

    try:
        if system == "Windows":
            # Use PowerShell to output CPU info in JSON
            ps_script = (
                "Get-CimInstance Win32_Processor | "
                "Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | "
                "ConvertTo-Json"
            )
            result = subprocess.check_output(
                ["powershell", "-Command", ps_script], text=True
            )
            cpu_data = json.loads(result)

            # Handle single or multiple CPUs
            if isinstance(cpu_data, list):
                cpu_info = cpu_data[0]  # Assume first processor if multiple
            else:
                cpu_info = cpu_data

        elif system == "Darwin":  # macOS

            def sysctl(name):
                return subprocess.check_output(
                    ["sysctl", "-n", name], text=True
                ).strip()

            cpu_info["Name"] = sysctl("machdep.cpu.brand_string")
            cpu_info["NumberOfCores"] = sysctl("hw.physicalcpu")
            cpu_info["NumberOfLogicalProcessors"] = sysctl("hw.logicalcpu")
            freq_hz = int(sysctl("hw.cpufrequency"))
            cpu_info["MaxClockSpeed"] = f"{freq_hz / 1_000_000:.2f} MHz"

        elif system == "Linux":
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                info = f.read()
            lines = info.split("\n")
            model_name = next(
                (line.split(":")[1].strip() for line in lines if "model name" in line),
                "Unknown",
            )
            cpu_info["Name"] = model_name

            cpu_info["NumberOfCores"] = os.cpu_count()
            logical_cores = subprocess.getoutput("nproc")
            cpu_info["NumberOfLogicalProcessors"] = logical_cores

            freq_output = subprocess.getoutput("lscpu | grep 'max MHz'")
            if freq_output:
                cpu_info["MaxClockSpeed"] = freq_output.split(":")[1].strip() + " MHz"
            else:
                cpu_info["MaxClockSpeed"] = "Unknown"

    except Exception as e:  # pylint: disable=broad-except
        cpu_info["Error"] = f"Failed to get CPU info: {e}"

    return cpu_info
