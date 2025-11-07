#!/home/luce/.venv/thimble/bin/python

# create_pouch_fixed.py
import bpy
import math
from mathutils import Vector


def create_cylinder(
    name, radius, depth, location=(0, 0, 0), vertices=128, axis="Y"
):
    rot = (0, 0, 0)
    if axis == "X":
        rot = (0, math.radians(90), 0)
    elif axis == "Y":
        rot = (math.radians(90), 0, 0)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=location,
        vertices=vertices,
        rotation=rot
    )

    obj = bpy.context.object
    obj.name = name
    return obj


def apply_boolean(obj1_name, obj2_name, operation_type="DIFFERENCE"):
    # make sure objects are selected for operation
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[obj1_name]

    # add modifier to first object
    mod = bpy.context.scene.objects[obj1_name].modifiers.new(
        name="Boolean", type="BOOLEAN"
    )
    mod.operation = operation_type
    mod.use_self = False
    mod.object = bpy.context.scene.objects[obj2_name]

    # apply modifier
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # delete seconds obj
    bpy.data.objects.remove(bpy.context.scene.objects[obj2_name])


def create_pouch(
    magnet_diameter, magnet_thickness, center=[0, 0, 0], name="pouch", axis="Y"
):
    ref_magnet_thickness = 3.175
    ref_magnet_diameter = 9.525

    midXY = 5 * magnet_diameter / ref_magnet_diameter
    outerXY = midXY + 1
    midZ = 3 * magnet_thickness / ref_magnet_thickness
    outerZ = midZ + 2

    lidXY = 4 * magnet_diameter / ref_magnet_diameter
    lidZ = midZ + 1

    convex_hull = create_cylinder(
        name + "_convex",
        radius=outerXY * 0.99,
        depth=outerZ * 0.99,
        location=(0, 0, 0),
        axis=axis
    )
    pouch_obj = create_cylinder(
        name, radius=outerXY, depth=outerZ, location=(0, 0, 0), axis=axis
    )
    cylinder1 = create_cylinder(
        name + "_cylinder1", radius=midXY, depth=midZ, location=(0, 0, 0), axis=axis
    )
    cylinder3 = create_cylinder(
        name + "_cylinder3",
        radius=lidXY,
        depth=lidZ,
        location=(0, 0, 0),
        # location=(0, 0, 1.9 + midZ / 2.0),
        axis=axis
    )

    # perform the boolean difference operation
    apply_boolean(name, name + "_cylinder1", "DIFFERENCE")
    apply_boolean(name, name + "_cylinder3", "DIFFERENCE")

    if axis == "Z":
        loc = [
            center[0],
            center[1],
            center[2] + outerZ / 2.0,
        ]
    elif axis == "Y":
        loc = [
            center[0], center[1] + outerZ / 2.0, center[2]
        ]
    elif axis == "X":
        loc = [
            center[0] + outerZ / 2.0, center[1], center[2]
        ]
    
    bpy.context.scene.objects[name + "_convex"].location = loc
    bpy.context.scene.objects[name].location = loc

    return name + "_convex", name


def simplify_object(obj, file_name, target_faces=300000):
    simplified_path = f"simplified-{file_name}.obj"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="OBJECT")

    poly_count = len(obj.data.polygons)
    if poly_count <= target_faces:
        print(f"No simplification needed ({poly_count} faces).")
        return

    ratio = target_faces / poly_count
    print(
        f"Applying Decimate: {poly_count} → {target_faces} faces (ratio={ratio:.4f})"
    )

    mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
    mod.ratio = ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)

    # export simplified obj
    bpy.ops.wm.obj_export(filepath=simplified_path)

    return


if __name__ == "__main__":
    file_name = "simplified-thimble-no-magnets-0.04-8"
    obj_path = f"/home/luce/code/thimble/cad/{file_name}.obj"
    input_path = f"/home/luce/code/thimble/cad/{file_name}.stl"
    output_path = f"boolean-{file_name}.obj"

    # clear scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # import STL
    bpy.ops.wm.obj_import(filepath=obj_path)
    obj = bpy.context.view_layer.objects.active
    if obj is None:
        raise RuntimeError(
            "No active object after import — check import path and that an object was created."
        )
    obj.name = "micro"

    # simplify object
    simplify_object(obj, file_name)

    # bounding box to get dimensions
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)

    outer_radius = (
        (max_x - min_x) / 2.0
        # 50  # approximate outer (assumes centered at 0)
    )
    inner_radius = (
        outer_radius * 0.3
        # 10.5
    )
    mid_radius = 0.5 * (outer_radius + inner_radius)

    print(f"out: {outer_radius}, in: {inner_radius}, mid: {mid_radius}")   
    center_y = 0.5 * (max_y + min_y)
    center_z = 0.5 * (max_z + min_z)
    print(f"center: ({center_y}, {center_z})")

    # # four centers on the mid-circle
    # pouch_centers = [
    #     [mid_radius, center_y, center_z],  # east
    #     [-mid_radius, center_y, center_z],  # west
    #     [0, center_y + mid_radius, center_z],  # north
    #     [0, center_y - mid_radius, center_z],  # south
    # ]
    # four centers in the X–Z cross-section plane (since axis is Y)
    pouch_centers = [
        [ mid_radius, center_y, center_z],  # east (X+)
        [-mid_radius, center_y, center_z],  # west (X-)
        [0, center_y, center_z + mid_radius],  # up (Z+)
        [0, center_y, center_z - mid_radius],  # down (Z-)
    ]

    # magnet size:  mm x  mm
    magnet_diameter = 9.0
    magnet_thickness = 3.0
    for i, c in enumerate(pouch_centers):
        convex, pouch = create_pouch(magnet_diameter, magnet_thickness, c, f"pouch{i}", axis="Y")
        apply_boolean("micro", convex, "DIFFERENCE")
        apply_boolean("micro", pouch, "UNION")

    # export result
    bpy.ops.wm.obj_export(filepath=output_path)
    print("Exported with pouches to", output_path)

    # # (diameter, thickness, [x,y,z]) in a 0..(extent) coordinate system.
    # list_of_magnets = [
    #     [5.0, 2.0, [15.0, 15.0, 15.0]],
    #     [5.0, 2.0, [35.0, 15.0, 15.0]],
    #     [5.0, 2.0, [15.0, 35.0, 15.0]],
    #     [5.0, 2.0, [35.0, 35.0, 15.0]],
    # ]

    # # clear scene
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete()

    # # import OBJ (use import_scene)
    # # bpy.ops.import_mesh.stl(filepath=input_path)
    # bpy.ops.wm.obj_import(filepath=obj_path)
    # # bpy.ops.preferences.addon_enable(module="io_scene_obj")
    # # bpy.ops.import_scene.obj(filepath=input_path)

    # # assume the imported object is the active objectstl
    # imported_object = bpy.context.view_layer.objects.active
    # if imported_object is None:
    #     raise RuntimeError("No active object after import — check import path and that an object was created.")
    # imported_object.name = "micro"

    # # compute world bounding-box corners
    # bbox_world = [imported_object.matrix_world @ Vector(corner) for corner in imported_object.bound_box]
    # min_x = min(v.x for v in bbox_world)
    # min_y = min(v.y for v in bbox_world)
    # min_z = min(v.z for v in bbox_world)
    # bbox_min = Vector((min_x, min_y, min_z))
    # max_x = max(v.x for v in bbox_world)
    # max_y = max(v.y for v in bbox_world)
    # max_z = max(v.z for v in bbox_world)
    # bbox_max = Vector((max_x, max_y, max_z))

    # print("bbox_min:", bbox_min)
    # print("bbox_max:", bbox_max)
    # print("bbox_extents:", bbox_max - bbox_min)

    # # convert your magnet centers (which are in a 0..extent space) to world coordinates by adding bbox_min
    # for index, magnet in enumerate(list_of_magnets):
    #     diam, thick, center_local = magnet
    #     world_center = bbox_min + Vector(center_local)
    #     print(f"magnet {index} world center: {world_center}, diam: {diam}, thick: {thick}")

    #     convex_hull_name, pouch_name = create_pouch(diam, thick, world_center, "pouch" + str(index))
    #     # subtract convex hull from micro, then union pouch back to micro (as in your original flow)
    #     boolean("micro", convex_hull_name, "DIFFERENCE")
    #     boolean("micro", pouch_name, "UNION")

    # # export result
    # # bpy.ops.export_scene.obj(filepath=output_path)
    # export_mesh(filepath=output_path)
    # print("Exported to", output_path)
