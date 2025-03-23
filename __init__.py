bl_info = {
    "name": "LiDAR Converter",
    "author": "RavenStryker (Jake Handlovic)",
    "version": (1, 1),
    "blender": (4, 2, 0),
    "location": "Sidebar > Wreckfest",
    "description": "Convert LiDAR (.las/.laz) files into terrain meshes in Blender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export",
}

import bpy
import os
import subprocess
import sys

# Automatically detect Blender's Python environment
BLENDER_PYTHON = sys.executable

# List of required dependencies
REQUIRED_PACKAGES = ["laspy[lazrs]", "numpy", "open3d"]

def ensure_dependencies():
    """Check and install missing dependencies in Blender's Python environment."""
    missing_packages = []

    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Installing missing dependencies: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([BLENDER_PYTHON, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call([BLENDER_PYTHON, "-m", "pip", "install"] + missing_packages)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")

# Ensure all dependencies are installed upon enabling the add-on
ensure_dependencies()

# Import the main LiDAR conversion script
from .lidar_converter import *

def register():
    """Register the LiDAR Converter add-on."""
    print("LiDAR Converter Add-on Registered")
    lidar_converter.register()

def unregister():
    """Unregister the LiDAR Converter add-on."""
    print("LiDAR Converter Add-on Unregistered")
    lidar_converter.unregister()
