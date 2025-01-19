import bpy

def create_plane(name, size, size_x, size_y, size_z, location, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD', location=location)
    plane = bpy.context.object
    plane.name = name
    modifier = plane.modifiers.new(name="Solidify", type='SOLIDIFY')
    modifier.thickness = 0.05
    plane.rotation_euler = rotation
    plane.scale = (size_x / 2, size_y / 2, 1)
    return plane
