bl_info = {
    "name": "LiDAR Converter",
    "author": "RavenStryker (Jake Handlovic)",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "Sidebar > Wreckfest",
    "description": "Convert LiDAR (.las/.laz) files into terrain meshes in Blender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export",
}

from .lidar_converter import *
