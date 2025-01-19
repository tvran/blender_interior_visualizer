import bpy
from .geometry import create_plane
from .materials import add_color_material, add_material_from_image
from .panels import create_panels

def create_scene(output_path):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    size = 2
    wall_height = 3 / size
    wall_length = 5 / size
    panel_size = 1

    wall1 = create_plane("Wall1", size, wall_height, wall_length, 1, (0, wall_length / 2, wall_height / 2), (0, math.radians(90), 0))
    floor = create_plane("Floor", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, 0), (0, 0, 0))
    ceiling = create_plane("Ceiling", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, wall_height), (0, 0, 0))

    wall1 = add_material_from_image(wall1, "Wall1_Material", "assets/wall_texture.jpg")
    floor = add_material_from_image(floor, "Floor_Material", "assets/wood_texture.jpg")
    ceiling = add_color_material(ceiling, "WhiteMaterial", (1, 1, 1, 1))

    create_panels(size, wall_length, wall_height, panel_size, panel_size, "assets/wall_texture.jpg")

    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)