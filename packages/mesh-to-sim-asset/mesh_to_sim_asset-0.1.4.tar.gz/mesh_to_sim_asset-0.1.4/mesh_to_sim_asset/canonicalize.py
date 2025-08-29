import os
import subprocess
import tempfile


def canonicalize_gltf(
    input_gltf_path: str,
    output_gltf_path: str,
    canonical_orientation: dict,
    scale: float = 1.0,
    placement_options: dict | None = None,
) -> None:
    """
    Canonicalize a GLTF mesh using Blender.
    This applies the canonical orientation transform in Blender's coordinate system,
    which matches the LLM's analysis coordinate system.

    Args:
        input_gltf_path: The path to the input GLTF file.
        output_gltf_path: The path to the output GLTF file.
        canonical_orientation: The canonical orientation of the mesh from the LLM in
            format {"up_axis": "z", "front_axis": "x"}, where the up_axis is the axis
            that is aligned with the world Z axis and the front_axis is the axis that
            is aligned with the world Y axis.
        scale: The scale of the mesh in range (0, 1].
        placement_options: Placement options dict, e.g. {"on_ceiling": false, ...}.
    """
    if placement_options is None:
        placement_options = {"on_object": True}

    # Create a temporary Blender script.
    blender_script = f"""
import bpy
import bmesh
import mathutils
import numpy as np

# Clear scene.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import GLTF.
bpy.ops.import_scene.gltf(filepath='{input_gltf_path}')

# Find root object(s) (usually an EMPTY that contains all meshes).
top_level_objects = [obj for obj in bpy.context.scene.objects if obj.parent is None]
if not top_level_objects:
    raise RuntimeError("No top-level objects found")

# Use first root object as the scene root (can extend if needed).
root_obj = next(obj for obj in top_level_objects if obj.children)

# Make it active.
bpy.context.view_layer.objects.active = root_obj

# Apply transforms (reset first to avoid cumulative transforms).
bpy.ops.object.select_all(action='DESELECT')
root_obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Apply scaling.
scale_factor = {scale}
root_obj.scale = (scale_factor, scale_factor, scale_factor)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Parse canonical orientation.
up_axis = "{canonical_orientation['up_axis']}"
front_axis = "{canonical_orientation['front_axis']}"

placement_options = {placement_options}

# Axis conversion helper.
def axis_to_vector(axis_str):
    sign = -1 if axis_str.startswith('-') else 1
    base = axis_str.lstrip('-')
    if base == 'x':
        return mathutils.Vector((sign, 0, 0))
    elif base == 'y':
        return mathutils.Vector((0, sign, 0))
    elif base == 'z':
        return mathutils.Vector((0, 0, sign))

up = axis_to_vector(up_axis)
front = axis_to_vector(front_axis)

# Ensure perpendicularity: recompute front to be orthogonal to up.
right = front.cross(up)

if right.length < 1e-6:
    # up and front are nearly parallel — pick arbitrary orthogonal right.
    if abs(up.x) < 0.99:
        right = up.cross(mathutils.Vector((1,0,0)))
    else:
        right = up.cross(mathutils.Vector((0,1,0)))

right.normalize()
front = up.cross(right)
front.normalize()

# Build rotation matrix to align object to canonical orientation.
current_up = mathutils.Vector((0, 0, 1))
current_front = mathutils.Vector((0, 1, 0))
current_right = mathutils.Vector((1, 0, 0))

target_matrix = mathutils.Matrix((
    right,
    front,
    up
)).transposed()

current_matrix = mathutils.Matrix((
    current_right,
    current_front,
    current_up
)).transposed()

rotation_matrix = target_matrix @ current_matrix.inverted()
rotation_matrix = rotation_matrix.to_4x4()

# Apply rotation.
root_obj.matrix_world = rotation_matrix @ root_obj.matrix_world
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Compute bounding box in world coordinates (from all mesh children).
all_mesh_verts_world = []
for obj in root_obj.children_recursive:
    if obj.type == 'MESH':
        all_mesh_verts_world.extend([obj.matrix_world @ v.co for v in obj.data.vertices])

if not all_mesh_verts_world:
    raise RuntimeError("No mesh vertices found for bounding box computation.")

xs = [v.x for v in all_mesh_verts_world]
ys = [v.y for v in all_mesh_verts_world]
zs = [v.z for v in all_mesh_verts_world]

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
min_z, max_z = min(zs), max(zs)

# Placement logic.
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2

if placement_options.get("on_ceiling", False):
    # Center x/y, top at z=0 (object just below ground).
    loc_x = -center_x
    loc_y = -center_y
    loc_z = -max_z
elif placement_options.get("on_wall", False):
    # Center x/z, min_y at y=0 (object just touches x-z plane).
    loc_x = -center_x
    loc_y = -min_y
    loc_z = -center_z
else:  # on_object or on_floor
    # Center x/y, bottom at z=0 (object just above ground).
    loc_x = -center_x
    loc_y = -center_y
    loc_z = -min_z

root_obj.location = mathutils.Vector((loc_x, loc_y, loc_z))
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

# Export.
bpy.ops.export_scene.gltf(
    filepath='{output_gltf_path}',
    export_format='GLTF_SEPARATE',
    use_selection=False
)
"""

    # Write script to temporary file.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(blender_script)
        script_path = f.name
    try:
        # Run Blender.
        cmd = [
            "env",
            "-u",
            "LD_LIBRARY_PATH",
            "blender",
            "--background",
            "--python",
            script_path,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Blender canonicalization failed:\\n{result.stderr}\\n{result.stdout}"
            )
    finally:
        # Clean up script file.
        os.unlink(script_path)
