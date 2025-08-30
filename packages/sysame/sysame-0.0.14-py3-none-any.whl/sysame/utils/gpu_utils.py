"""
Module for all all GPU utility related functions and classes.
"""

##### IMPORTS #####

# Standard imports
import platform
import subprocess
import re
import json
from typing import Any, Union, Optional, Match

# Third party imports

# Local imports

# Import Rules

##### CONSTANTS #####

##### CLASSES #####


##### FUNCTIONS #####
def get_gpu_specs() -> dict[str, Union[list[dict[str, Any]], int, str]]:
    """
    Retrieve GPU specifications across Windows, macOS, and Linux platforms.

    This function detects the current operating system and calls the appropriate
    platform-specific function to gather GPU information.

    Returns
    -------
    dict[str, Union[list[dict[str, Any]], int, str]]
        Dictionary containing GPU information with the following possible keys:
        - 'gpus': List of dictionaries, each containing information about a GPU
        - 'count': Number of GPUs detected
        - 'error': Error message if GPU information could not be retrieved

    Notes
    -----
    The specific information available will vary by operating system and GPU type.
    """
    system: str = platform.system().lower()

    if system == "windows":
        return _get_gpu_specs_windows()
    elif system == "darwin":
        return _get_gpu_specs_macos()
    elif system == "linux":
        return _get_gpu_specs_linux()
    else:
        return {"error": f"Unsupported operating system: {system}"}


def _get_gpu_specs_windows() -> dict[str, Union[list[dict[str, Any]], int, str]]:
    """
    Get GPU specifications on Windows using PowerShell and WMI.

    Uses Windows Management Instrumentation (WMI) to query for graphics hardware
    information. For NVIDIA GPUs, also attempts to use nvidia-smi for additional
    details.

    Returns
    -------
    dict[str, Union[list[dict[str, Any]], int, str]]
        Dictionary containing GPU information with the following keys:
        - 'gpus': List of dictionaries, each containing information about a GPU
          including name, VRAM, driver version, etc.
        - 'count': Number of GPUs detected
        - 'error': Error message if GPU information could not be retrieved

    Notes
    -----
    For NVIDIA GPUs, additional information like clock speeds, temperature,
    and utilization may be available if nvidia-smi is installed.
    """
    try:
        # Run PowerShell command to get GPU info
        cmd: str = "Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, CurrentRefreshRate, DriverVersion, VideoModeDescription | ConvertTo-Json"
        result: subprocess.CompletedProcess = subprocess.run(
            ["powershell", "-Command", cmd], capture_output=True, text=True, check=True
        )

        if not result.stdout.strip():
            return {"error": "No GPU information found"}

        # Parse the JSON output
        gpu_data: Union[list[dict[str, Any]], dict[str, Any]] = json.loads(
            result.stdout
        )
        # Handle case of single GPU (not in a list)
        if not isinstance(gpu_data, list):
            gpu_data = [gpu_data]

        gpus: list[dict[str, Any]] = []
        for gpu in gpu_data:
            # Get additional details for each GPU
            try:
                # Try to get more detailed info
                details_cmd: str = f"""
                (Get-WmiObject Win32_VideoController | Where-Object {{ $_.Name -eq '{gpu["Name"]}' }} | 
                ForEach-Object {{
                    $props = @{{
                        'Name' = $_.Name;
                        'AdapterRAM' = $_.AdapterRAM;
                        'DriverVersion' = $_.DriverVersion;
                        'VideoProcessor' = $_.VideoProcessor;
                        'VideoArchitecture' = $_.VideoArchitecture;
                        'VideoMemoryType' = $_.VideoMemoryType;
                    }}
                    New-Object PSObject -Property $props
                }}) | ConvertTo-Json
                """
                details_result: subprocess.CompletedProcess = subprocess.run(
                    ["powershell", "-Command", details_cmd],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if details_result.returncode == 0 and details_result.stdout.strip():
                    details: dict[str, Any] = json.loads(details_result.stdout)
                    gpu_info: dict[str, Any] = details
                else:
                    gpu_info = gpu
            except Exception:  # pylint: disable=broad-except
                gpu_info = gpu

            # Calculate VRAM in a readable format if available
            if gpu_info.get("AdapterRAM"):
                try:
                    vram_bytes: int = int(gpu_info["AdapterRAM"])
                    vram_gb: float = vram_bytes / (1024**3)
                    gpu_info["VRAM"] = f"{vram_gb:.2f} GB"
                except (ValueError, TypeError):
                    pass

            gpus.append(gpu_info)

        # Try to get NVIDIA-specific info if available
        try:
            nvidia_cmd: str = "nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu,clocks.current.sm,clocks.current.memory --format=csv,noheader"
            nvidia_result: subprocess.CompletedProcess = subprocess.run(
                nvidia_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )

            if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                for i, line in enumerate(nvidia_result.stdout.strip().split("\n")):
                    if i < len(gpus):
                        parts: list[str] = [part.strip() for part in line.split(",")]
                        if len(parts) >= 8:
                            gpus[i]["Core_Clock"] = parts[6]
                            gpus[i]["Memory_Clock"] = parts[7]
                            gpus[i]["GPU_Temperature"] = parts[4]
                            gpus[i]["GPU_Utilization"] = parts[5]
        except Exception:  # pylint: disable=broad-except
            pass

        return {"gpus": gpus, "count": len(gpus)}

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get GPU information: {str(e)}"}
    except Exception as e:  # pylint: disable=broad-except
        return {"error": f"Unexpected error retrieving GPU information: {str(e)}"}


def _get_gpu_specs_macos() -> dict[str, Union[list[dict[str, Any]], int, str]]:
    """
    Get GPU specifications on macOS using system_profiler.

    Uses system_profiler and osascript to gather detailed information about
    graphics hardware on macOS systems, including integrated and discrete GPUs.

    Returns
    -------
    dict[str, Union[list[dict[str, Any]], int, str]]
        Dictionary containing GPU information with the following keys:
        - 'gpus': List of dictionaries, each containing information about a GPU
          including name, VRAM, metal support, etc.
        - 'count': Number of GPUs detected
        - 'error': Error message if GPU information could not be retrieved

    Notes
    -----
    For Apple Silicon (M1/M2) GPUs, additional information like compute units
    and clock speeds may be available.
    """
    try:
        # Use system_profiler to get graphics/displays info
        cmd: list[str] = ["system_profiler", "SPDisplaysDataType", "-json"]
        result: subprocess.CompletedProcess = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )

        data: dict[str, Any] = json.loads(result.stdout)
        graphics_cards: list[dict[str, Any]] = []
        gpu_info: dict[str, Any] = {}

        # Navigate through the nested structure
        if "SPDisplaysDataType" in data:
            for item in data["SPDisplaysDataType"]:
                if (
                    "spdisplays_mtlgpufamilyname" in item
                    or "spdisplays_device-type" in item
                ):
                    # Extract basic information
                    for key, value in item.items():
                        if key.startswith("spdisplays_"):
                            clean_key: str = key.replace("spdisplays_", "")
                            gpu_info[clean_key] = value

                    # Try to get more detailed info about metal GPU
                    if "spdisplays_metal" in item and item["spdisplays_metal"] == "Yes":
                        try:
                            # Get Metal device info
                            metal_cmd: str = """
                            osascript -e '
                            tell application "System Information"
                                open
                                delay 1
                                set hardwareContents to text of UI element 1 of scroll area 1 of window 1
                                quit
                            end tell'
                            """
                            metal_result: subprocess.CompletedProcess = subprocess.run(
                                metal_cmd,
                                shell=True,
                                capture_output=True,
                                text=True,
                                check=False,
                            )

                            if metal_result.returncode == 0:
                                gpu_section: bool = False
                                for line in metal_result.stdout.split("\n"):
                                    if "Graphics/Displays:" in line:
                                        gpu_section = True
                                    elif (
                                        gpu_section
                                        and item.get("spdisplays_device-id", "") in line
                                    ):
                                        next_lines: list[str] = (
                                            metal_result.stdout.split("\n")[
                                                metal_result.stdout.split("\n").index(
                                                    line
                                                ) :
                                            ]
                                        )
                                        for next_line in next_lines[
                                            :20
                                        ]:  # Look at next 20 lines max
                                            if "VRAM" in next_line:
                                                vram_match: Optional[Match[str]] = (
                                                    re.search(
                                                        r"VRAM.*?(\d+)\s*(MB|GB)",
                                                        next_line,
                                                    )
                                                )
                                                if vram_match:
                                                    gpu_info["VRAM"] = (
                                                        f"{vram_match.group(1)} {vram_match.group(2)}"
                                                    )
                                            if "Device ID" in next_line:
                                                continue  # Already have this
                                            if (
                                                "Compute Units" in next_line
                                                or "Cores" in next_line
                                            ):
                                                cores_match: Optional[Match[str]] = (
                                                    re.search(
                                                        r"(Compute Units|Cores).*?(\d+)",
                                                        next_line,
                                                    )
                                                )
                                                if cores_match:
                                                    gpu_info["Compute_Units"] = (
                                                        cores_match.group(2)
                                                    )
                                            if "Clock" in next_line:
                                                clock_match: Optional[Match[str]] = (
                                                    re.search(
                                                        r"Clock.*?(\d+(?:\.\d+)?)\s*(MHz|GHz)",
                                                        next_line,
                                                    )
                                                )
                                                if clock_match:
                                                    gpu_info["Clock"] = (
                                                        f"{clock_match.group(1)} {clock_match.group(2)}"
                                                    )
                                        break
                        except Exception:  # pylint: disable=broad-except
                            pass  # Fallback to basic info if osascript fails

                    graphics_cards.append(gpu_info)

        # If no structured data found, try parsing text output
        if not graphics_cards:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                check=False,
            )
            current_gpu: Optional[str] = None

            for line in result.stdout.split("\n"):
                line = line.strip()

                # Check if this is a new GPU entry
                if re.match(r"^\w+\s*:", line) and not line.startswith("    "):
                    if gpu_info and current_gpu:
                        graphics_cards.append(gpu_info)
                        gpu_info = {}
                    current_gpu = line.split(":")[0].strip()

                # Extract information
                if ":" in line:
                    key, value = [x.strip() for x in line.split(":", 1)]
                    if key == "Chipset Model":
                        gpu_info["Name"] = value
                    elif key == "VRAM" or key == "Total VRAM":
                        gpu_info["VRAM"] = value
                    elif key == "Device ID":
                        gpu_info["Device_ID"] = value
                    elif key == "Metal Support" or key == "Metal":
                        gpu_info["Metal_Support"] = value
                    elif "Compute Units" in key or "Cores" in key:
                        match_obj: Optional[Match[str]] = re.search(r"(\d+)", value)
                        gpu_info["Compute_Units"] = (
                            match_obj.group(1) if match_obj else value
                        )
                    elif "Clock" in key:
                        gpu_info["Clock"] = value

            # Add the last GPU if it exists
            if gpu_info and current_gpu:
                graphics_cards.append(gpu_info)

        return {"gpus": graphics_cards, "count": len(graphics_cards)}

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get GPU information: {str(e)}"}
    except Exception as e:  # pylint: disable=broad-except
        return {"error": f"Unexpected error retrieving GPU information: {str(e)}"}


def _get_gpu_specs_linux() -> dict[str, Union[list[dict[str, Any]], int, str]]:
    """
    Get GPU specifications on Linux using various system tools.

    Uses a combination of lspci, lshw, nvidia-smi (for NVIDIA GPUs),
    and rocm-smi (for AMD GPUs) to gather comprehensive information
    about graphics hardware on Linux systems.

    Returns
    -------
    dict[str, Union[list[dict[str, Any]], int, str]]
        Dictionary containing GPU information with the following keys:
        - 'gpus': List of dictionaries, each containing information about a GPU
          including name, device ID, driver, vendor, etc.
        - 'count': Number of GPUs detected
        - 'error': Error message if GPU information could not be retrieved

    Notes
    -----
    For NVIDIA GPUs, detailed information like VRAM, clocks, and compute
    capability will be available if nvidia-smi is installed.
    For AMD GPUs, additional information will be available if rocm-smi
    is installed.
    """
    try:
        # First identify the GPUs with lspci
        gpu_list: list[dict[str, Any]] = []
        lspci_cmd: list[str] = ["lspci", "-nnk"]
        lspci_result: subprocess.CompletedProcess = subprocess.run(
            lspci_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        vendor: str

        if lspci_result.returncode == 0:
            gpu_sections: list[str] = []
            current_section: str = ""
            is_gpu: bool = False

            # Identify GPU sections in lspci output
            for line in lspci_result.stdout.split("\n"):
                if re.search(r"VGA|3D|Display|Graphics", line, re.IGNORECASE):
                    if current_section and is_gpu:
                        gpu_sections.append(current_section)
                    current_section = line + "\n"
                    is_gpu = True
                elif (
                    line.startswith("\t") and is_gpu
                ):  # Continuation of current section
                    current_section += line + "\n"
                elif line and is_gpu:  # New section
                    gpu_sections.append(current_section)
                    current_section = line + "\n"
                    is_gpu = (
                        re.search(r"VGA|3D|Display|Graphics", line, re.IGNORECASE)
                        is not None
                    )
                elif line:
                    current_section = line + "\n"
                    is_gpu = False

            # Add last section if it's a GPU
            if current_section and is_gpu:
                gpu_sections.append(current_section)

            # Parse the GPU sections
            for section in gpu_sections:
                gpu_info: dict[str, Any] = {}

                # Extract name/model
                name_match: Optional[Match[str]] = re.search(
                    r"VGA.*?:\s*(.*?)(?:\[|$)", section
                ) or re.search(r"3D.*?:\s*(.*?)(?:\[|$)", section)
                if name_match:
                    gpu_info["Name"] = name_match.group(1).strip()

                # Extract device ID
                device_id_match: Optional[Match[str]] = re.search(
                    r"\[(\w+:\w+)\]", section
                )
                if device_id_match:
                    gpu_info["Device_ID"] = device_id_match.group(1)

                # Extract kernel driver
                driver_match: Optional[Match[str]] = re.search(
                    r"Kernel driver in use:\s*(.*)", section
                )
                if driver_match:
                    gpu_info["Driver"] = driver_match.group(1).strip()

                # Identify GPU vendor
                vendor = "unknown"
                if "nvidia" in section.lower():
                    vendor = "nvidia"
                elif (
                    "amd" in section.lower()
                    or "radeon" in section.lower()
                    or "ati" in section.lower()
                ):
                    vendor = "amd"
                elif "intel" in section.lower():
                    vendor = "intel"

                gpu_info["Vendor"] = vendor
                gpu_list.append(gpu_info)

        # Try to get more detailed information using vendor-specific tools
        for i, gpu in enumerate(gpu_list):
            vendor = gpu.get("Vendor", "").lower()

            # Try NVIDIA-specific info
            if vendor == "nvidia":
                try:
                    nvidia_cmd: list[str] = [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,clocks.sm,clocks.mem",
                        "--format=csv,noheader",
                    ]
                    nvidia_result: subprocess.CompletedProcess = subprocess.run(
                        nvidia_cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                        lines: list[str] = [
                            lin.strip()
                            for lin in nvidia_result.stdout.strip().split("\n")
                        ]
                        if i < len(lines):
                            parts: list[str] = [p.strip() for p in lines[i].split(",")]
                            if len(parts) >= 7:
                                gpu["Name"] = parts[0]
                                gpu["VRAM"] = parts[1]
                                gpu["Memory_Used"] = parts[2]
                                gpu["Memory_Free"] = parts[3]
                                gpu["GPU_Utilization"] = parts[4]
                                gpu["Core_Clock"] = parts[5]
                                gpu["Memory_Clock"] = parts[6]

                                # Try to get compute capability and CUDA cores
                                try:
                                    nvidia_smi_query: list[str] = [
                                        "nvidia-smi",
                                        "--query-gpu=compute_cap",
                                        "--format=csv,noheader",
                                    ]
                                    cap_result: subprocess.CompletedProcess = (
                                        subprocess.run(
                                            nvidia_smi_query,
                                            capture_output=True,
                                            text=True,
                                            check=False,
                                        )
                                    )
                                    if (
                                        cap_result.returncode == 0
                                        and cap_result.stdout.strip()
                                    ):
                                        lines_cap: list[str] = [
                                            lin.strip()
                                            for lin in cap_result.stdout.strip().split(
                                                "\n"
                                            )
                                        ]
                                        if i < len(lines_cap):
                                            gpu["Compute_Capability"] = lines_cap[i]
                                except Exception:  # pylint: disable=broad-except
                                    pass

                except Exception:  # pylint: disable=broad-except
                    pass

            # Try AMD-specific info
            elif vendor == "amd":
                try:
                    # Try rocm-smi if available
                    rocm_cmd: list[str] = [
                        "rocm-smi",
                        "--showproductname",
                        "--showmeminfo",
                        "vram",
                        "--showclocks",
                    ]
                    rocm_result: subprocess.CompletedProcess = subprocess.run(
                        rocm_cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if rocm_result.returncode == 0:
                        for line in rocm_result.stdout.split("\n"):
                            if gpu.get("Name", "").lower() in line.lower() or (
                                gpu.get("Device_ID", "")
                                and gpu.get("Device_ID", "") in line
                            ):
                                gpu_index: int = -1
                                try:
                                    # Try to find the GPU index
                                    for match in re.finditer(
                                        r"GPU\[(\d+)\]", rocm_result.stdout
                                    ):
                                        if match.start() < rocm_result.stdout.find(
                                            line
                                        ) and match.end() > rocm_result.stdout.rfind(
                                            line
                                        ):
                                            gpu_index = int(match.group(1))
                                            break

                                    if gpu_index >= 0:
                                        # Extract memory info
                                        mem_pattern: str = (
                                            r"GPU\["
                                            + str(gpu_index)
                                            + r"\].*?vram\s+total.*?(\d+)\s*MB"
                                        )
                                        mem_match: Optional[Match[str]] = re.search(
                                            mem_pattern, rocm_result.stdout, re.DOTALL
                                        )
                                        if mem_match:
                                            gpu["VRAM"] = f"{mem_match.group(1)} MB"

                                        # Extract clock speeds
                                        clock_pattern: str = (
                                            r"GPU\["
                                            + str(gpu_index)
                                            + r"\].*?(\d+)\s*MHz.*?sclk"
                                        )
                                        clock_match: Optional[Match[str]] = re.search(
                                            clock_pattern, rocm_result.stdout, re.DOTALL
                                        )
                                        if clock_match:
                                            gpu["Core_Clock"] = (
                                                f"{clock_match.group(1)} MHz"
                                            )

                                        mem_clock_pattern: str = (
                                            r"GPU\["
                                            + str(gpu_index)
                                            + r"\].*?(\d+)\s*MHz.*?mclk"
                                        )
                                        mem_clock_match: Optional[Match[str]] = (
                                            re.search(
                                                mem_clock_pattern,
                                                rocm_result.stdout,
                                                re.DOTALL,
                                            )
                                        )
                                        if mem_clock_match:
                                            gpu["Memory_Clock"] = (
                                                f"{mem_clock_match.group(1)} MHz"
                                            )
                                except Exception:  # pylint: disable=broad-except
                                    pass
                except Exception:  # pylint: disable=broad-except
                    # Fallback to lshw for AMD
                    pass

            # Try lshw for additional details regardless of vendor
            try:
                lshw_cmd: list[str] = ["lshw", "-C", "display", "-json"]
                lshw_result: subprocess.CompletedProcess = subprocess.run(
                    lshw_cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if lshw_result.returncode == 0 and lshw_result.stdout.strip():
                    try:
                        lshw_data: Union[list[dict[str, Any]], dict[str, Any]] = (
                            json.loads(lshw_result.stdout)
                        )
                        # Handle case where it's not a list
                        if not isinstance(lshw_data, list):
                            lshw_data = [lshw_data]

                        # Find matching GPU
                        for lshw_gpu in lshw_data:
                            # Match by product name or device ID
                            if gpu.get("Name", "").lower() in lshw_gpu.get(
                                "product", ""
                            ).lower() or gpu.get("Device_ID", "") in lshw_gpu.get(
                                "businfo", ""
                            ):
                                # Extract clock if available
                                if "clock" in lshw_gpu:
                                    gpu["Clock"] = f"{lshw_gpu['clock'] / 1000000} MHz"

                                # Extract capabilities
                                if "capabilities" in lshw_gpu:
                                    gpu["Capabilities"] = lshw_gpu["capabilities"]

                                # Extract configuration
                                if "configuration" in lshw_gpu:
                                    config: dict[str, Any] = lshw_gpu["configuration"]
                                    if "driver" in config:
                                        gpu["Driver"] = config["driver"]
                                    if "latency" in config:
                                        gpu["Latency"] = config["latency"]
                    except json.JSONDecodeError:
                        # Try to parse text output
                        pass
            except Exception:  # pylint: disable=broad-except
                pass

        # Try glxinfo for additional OpenGL details
        try:
            glx_cmd: list[str] = ["glxinfo"]
            glx_result: subprocess.CompletedProcess = subprocess.run(
                glx_cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if glx_result.returncode == 0:
                for gpu in gpu_list:
                    # Look for matching GPU in glxinfo output
                    if gpu.get("Name", "") and gpu.get("Name", "") in glx_result.stdout:
                        # Extract OpenGL version
                        gl_version: Optional[Match[str]] = re.search(
                            r"OpenGL version string: (.*)", glx_result.stdout
                        )
                        if gl_version:
                            gpu["OpenGL_Version"] = gl_version.group(1)

                        # Extract OpenGL renderer
                        gl_renderer: Optional[Match[str]] = re.search(
                            r"OpenGL renderer string: (.*)", glx_result.stdout
                        )
                        if gl_renderer:
                            gpu["OpenGL_Renderer"] = gl_renderer.group(1)
        except Exception:  # pylint: disable=broad-except
            pass

        return {"gpus": gpu_list, "count": len(gpu_list)}

    except Exception as e:  # pylint: disable=broad-except
        return {"error": f"Unexpected error retrieving GPU information: {str(e)}"}
