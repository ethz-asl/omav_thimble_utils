#!/home/luce/.venv/thimble/bin/python
import bpy
import bmesh
import math
from mathutils import Vector



def create_cylinder(name, radius, depth, location=(0, 0, 0), vertices=128, axis="Z"):
    rot = (0, 0, 0)
    if axis == "X":
        rot = (0, math.radians(90), 0)
    elif axis == "Y":
        rot = (math.radians(90), 0, 0)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=location, vertices=vertices, rotation=rot
    )
    obj = bpy.context.object
    obj.name = name
    return obj


def apply_boolean(target, cutter, op="DIFFERENCE", delete_cutter=True):
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[target]
    mod = bpy.context.scene.objects[target].modifiers.new(name="Boolean", type="BOOLEAN")
    mod.operation = op
    mod.use_self = False
    mod.object = bpy.context.scene.objects[cutter]
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if delete_cutter:
        bpy.data.objects.remove(bpy.context.scene.objects[cutter])


def add_caps(obj, outer_radius, inner_radius, min_y, max_y, thickness=1.0):
    """
    Adds flat caps at both ends (Y axis), flush with outer edges, with central hole.
    """
    # --- bottom cap ---
    cap_bottom = create_cylinder("cap_bottom", outer_radius, thickness, axis="Y")
    cap_bottom.location = [0, min_y - thickness / 2.0, 0]

    hole = create_cylinder("cap_bottom_hole", inner_radius, thickness * 2, axis="Y")
    hole.location = cap_bottom.location
    apply_boolean("cap_bottom", "cap_bottom_hole")

    # --- top cap ---
    cap_top = create_cylinder("cap_top", outer_radius, thickness, axis="Y")
    cap_top.location = [0, max_y + thickness / 2.0, 0]

    hole2 = create_cylinder("cap_top_hole", inner_radius, thickness * 2, axis="Y")
    hole2.location = cap_top.location
    apply_boolean("cap_top", "cap_top_hole")

    # --- fuse caps with main object ---
    apply_boolean(obj.name, "cap_bottom", op="UNION")
    apply_boolean(obj.name, "cap_top", op="UNION")


def triangulate_object(obj):
    """Force triangulation for 3D printing compatibility."""
    mod = obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)

def finalize_for_print(obj, export_path=None):
    """
    Clean up mesh so it's watertight and ready for slicing.
    - Removes doubles
    - Recalculates normals
    - Fills holes
    - Makes manifold (Blender 4.x+)
    - Triangulates all faces
    - Optionally exports STL

    Args:
        obj (bpy.types.Object): Mesh object to finalize
        export_path (str): Path to export STL (optional)
    """

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.mesh.remove_doubles(threshold=1e-5)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.fill_holes(sides=0)

    try:
        bpy.ops.mesh.make_manifold()
    except Exception:
        pass  # ignored if not available

    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

    bpy.ops.object.mode_set(mode='OBJECT')

    if export_path:
        bpy.ops.wm.stl_export(filepath=export_path)

if __name__ == "__main__":
    file_name = "boolean-simplified-thimble-no-magnets-0.04-8"
    obj_path = f"/home/luce/code/thimble/scripts/{file_name}.obj"
    output_path = f"thimble.obj"
    export_path = f"thimble.stl"

    # reset scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # import
    bpy.ops.wm.obj_import(filepath=obj_path)
    obj = bpy.context.view_layer.objects.active
    obj.name = "micro"

    # bounding box
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)

    outer_radius = (max_x - min_x) / 2.0
    inner_radius = outer_radius * 0.215  # or compute from actual hole if known

    # add top + bottom caps
    add_caps(obj, outer_radius, inner_radius, min_y, max_y, thickness=2.0)
    
    finalize_for_print(obj, export_path)
    # triangulate_object(obj)

    # export
    bpy.ops.wm.obj_export(filepath=output_path)
    print("Exported capped object to", output_path)
