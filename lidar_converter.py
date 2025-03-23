import bpy
import laspy
import numpy as np
import open3d as o3d
import os
from bpy.props import StringProperty, IntProperty, FloatProperty
from bpy_extras.io_utils import ImportHelper

class LIDAR_OT_ImportFile(bpy.types.Operator, ImportHelper):
    """Select a LiDAR .las/.laz file"""
    bl_idname = "lidar.import_file"
    bl_label = "Select LiDAR File"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".las;.laz"
    filter_glob: StringProperty(default="*.las;*.laz", options={'HIDDEN'})

    def execute(self, context):
        context.scene.lidar_laz_file = self.filepath  # Store file path
        return {'FINISHED'}

class LIDAR_OT_SetSaveDirectory(bpy.types.Operator, ImportHelper):
    """Select a directory to save the .blend file"""
    bl_idname = "lidar.set_save_directory"
    bl_label = "Select Save Directory"
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        context.scene.lidar_save_directory = self.directory  # Store directory path
        return {'FINISHED'}

class LIDAR_OT_Convert(bpy.types.Operator):
    """Convert LiDAR .las/.laz to Blender Mesh"""
    bl_idname = "lidar.convert"
    bl_label = "Convert LiDAR to Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        laz_file_path = scene.lidar_laz_file
        save_directory = scene.lidar_save_directory
        psr_depth = scene.lidar_psr_depth
        vertex_count = scene.lidar_vertex_count
        scale = scene.lidar_scale

        # ===== ENSURE A .LAS/.LAZ FILE IS SELECTED =====
        if not laz_file_path:
            self.report({'ERROR'}, "No .las/.laz file selected.")
            return {'CANCELLED'}

        # ===== ENSURE SAVE DIRECTORY IS SELECTED =====
        if not save_directory:
            self.report({'ERROR'}, "No save directory selected.")
            return {'CANCELLED'}

        output_blend_path = os.path.join(save_directory, "lidar_conversion.blend")

        # ===== LOAD LIDAR DATA =====
        self.report({'INFO'}, "Loading LiDAR data...")
        las = laspy.read(laz_file_path)
        points = np.vstack((las.x, las.y, las.z)).T

        # ===== REMOVE OUTLIERS =====
        z_mean, z_std = np.mean(points[:, 2]), np.std(points[:, 2])
        z_min, z_max = z_mean - 3 * z_std, z_mean + 3 * z_std
        points = points[(points[:, 2] >= z_min) & (points[:, 2] <= z_max)]
        self.report({'INFO'}, f"Filtered outliers, remaining points: {len(points)}")

        # ===== NORMALIZE COORDINATES =====
        min_vals = np.min(points, axis=0)
        max_vals = np.max(points, axis=0)
        center = (max_vals + min_vals) / 2
        scale_factor = np.max(max_vals - min_vals) or 1.0
        points = (points - center) / scale_factor

        # ===== CREATE POINT CLOUD =====
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        # ===== ADAPTIVE DOWNSAMPLING =====
        if len(points) > vertex_count:
            voxel_size = (np.ptp(points[:, 0]) + np.ptp(points[:, 1])) / 2048
            self.report({'INFO'}, f"Downsampling from {len(points)} → {vertex_count} points using voxel size {voxel_size:.4f}")
            pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

        self.report({'INFO'}, f"Final Point Cloud Size: {len(pcd.points)}")

        # ===== ESTIMATE NORMALS =====
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=5, max_nn=50))

        # ===== POISSON SURFACE RECONSTRUCTION =====
        self.report({'INFO'}, "Performing Poisson Surface Reconstruction...")
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=psr_depth)
        self.report({'INFO'}, f"Generated Mesh: {len(mesh.vertices)} vertices, {len(mesh.triangles)} faces")

        # ===== CONVERT TO POLYGON MESH =====
        blender_mesh = bpy.data.meshes.new(name="TerrainMesh")
        blender_obj = bpy.data.objects.new("Terrain", blender_mesh)
        bpy.context.collection.objects.link(blender_obj)

        vertices = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.triangles)

        blender_mesh.from_pydata(vertices.tolist(), [], [tuple(f) for f in faces])
        blender_mesh.update()

        # ===== CONVERT TRIS TO QUADS =====
        bpy.context.view_layer.objects.active = blender_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.object.mode_set(mode='OBJECT')

        # ===== SCALE & SAVE =====
        blender_obj.scale = (scale, scale, scale)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.wm.save_as_mainfile(filepath=output_blend_path)

        self.report({'INFO'}, f"Blender file saved: {output_blend_path}")
        return {'FINISHED'}

# SIDEBAR PANEL
class LIDAR_PT_Panel(bpy.types.Panel):
    """Sidebar UI for LiDAR Converter"""
    bl_label = "LiDAR Converter"
    bl_idname = "LIDAR_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Wreckfest'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = False
        layout.use_property_decorate = False

        # ===== LIDAR FILE SELECTION =====
        layout.label(text="LiDAR File:")
        row = layout.row(align=True)
        row.prop(scene, "lidar_laz_file", text="")
        row.operator("lidar.import_file", text="", icon="FILE_FOLDER")

        layout.separator()

        # ===== SAVE DIRECTORY SELECTION =====
        layout.label(text="Save Directory:")
        row = layout.row(align=True)
        row.prop(scene, "lidar_save_directory", text="")

        layout.separator()

        # ===== CONVERSION SETTINGS =====
        layout.prop(scene, "lidar_psr_depth")
        layout.prop(scene, "lidar_vertex_count", text="Vertex Count")
        layout.prop(scene, "lidar_scale")

        layout.separator()

        # ===== CONVERT BUTTON =====
        row = layout.row()
        row.scale_x = 1.6
        row.operator("lidar.convert", text="Convert LiDAR to Mesh", icon="MESH_GRID")

# REGISTRATION
def register():
    bpy.utils.register_class(LIDAR_OT_ImportFile)
    bpy.utils.register_class(LIDAR_OT_SetSaveDirectory)
    bpy.utils.register_class(LIDAR_OT_Convert)
    bpy.utils.register_class(LIDAR_PT_Panel)

    bpy.types.Scene.lidar_laz_file = StringProperty(name="LiDAR File", default="")
    bpy.types.Scene.lidar_save_directory = StringProperty(name="Save Directory", subtype="DIR_PATH")
    bpy.types.Scene.lidar_psr_depth = IntProperty(name="PSR Depth", default=14, min=8, max=18)
    bpy.types.Scene.lidar_vertex_count = IntProperty(
        name="Vertex Count",
        description="Maximum number of vertices after downsampling",
        default=1000000,
        min=100000,
        max=5000000
    )
    bpy.types.Scene.lidar_scale = FloatProperty(name="Scale", default=10.0, min=0.1, max=100.0)

def unregister():
    bpy.utils.unregister_class(LIDAR_OT_ImportFile)
    bpy.utils.unregister_class(LIDAR_OT_SetSaveDirectory)
    bpy.utils.unregister_class(LIDAR_OT_Convert)
    bpy.utils.unregister_class(LIDAR_PT_Panel)

    del bpy.types.Scene.lidar_laz_file
    del bpy.types.Scene.lidar_save_directory
    del bpy.types.Scene.lidar_psr_depth
    del bpy.types.Scene.lidar_vertex_count
    del bpy.types.Scene.lidar_scale

if __name__ == "__main__":
    register()