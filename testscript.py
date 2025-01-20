import os
import bpy
import math
from IPython.display import Image, display

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_plane(name, size, size_x, size_y, size_z, location, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD', location=location)
    plane = bpy.context.selected_objects[-1]
    plane.name = name
    modifier = plane.modifiers.new(name="Solidify", type='SOLIDIFY')
    modifier.thickness = 0.05
    plane.rotation_euler = rotation
    plane.scale = (size_x / 2, size_y / 2, 1)
    return plane

def create_interior_light(name, location, energy=30):  # Set max energy to 30
    light_data = bpy.data.lights.new(name=name, type='POINT')
    light_data.energy = energy
    light_data.shadow_soft_size = 2

    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)

    light_object.location = location

    return light_object

def assign_material(plane, material):
    if plane.data.materials:
        plane.data.materials[0] = material
    else:
        plane.data.materials.append(material)
    return plane

def add_color_material(plane, material_name, color=(0,0,0,0)):
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    bsdf_color = material.node_tree.nodes.get("Principled BSDF")
    bsdf_color.inputs['Base Color'].default_value = color
    plane = assign_material(plane, material)
    return plane

def add_material_from_image(plane, material_name, image_path):
    material_name = material_name
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    while nodes:
        nodes.remove(nodes[0])

    principled_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    principled_bsdf.location = (200, 0)
    material_output = nodes.new('ShaderNodeOutputMaterial')
    material_output.location = (400, 0)
    image_texture = nodes.new('ShaderNodeTexImage')
    image_texture.location = (0, 0)

    try:
        image_texture.image = bpy.data.images.load(image_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        print(f"Make sure the image exists at: {image_path}")
        print("If using a relative path, ensure the image is in the same directory as the .blend file")
        exit()

    links.new(image_texture.outputs['Color'], principled_bsdf.inputs['Base Color'])
    links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])
    plane = assign_material(plane, material)
    return plane

def create_panels(
        size,
        plane_length,
        plane_width,
        panel_length,
        panel_width,
        image_path,
        location=(0,0,0),
        rotation=(0,0,0)
    ):
    num_panels_x = math.floor(plane_length / panel_length)
    num_panels_y = math.floor(plane_width / panel_width)

    remaining_length = plane_length - (num_panels_x * panel_length)
    remaining_height = plane_width - (num_panels_y * panel_width)

    for i in range(num_panels_x + 1):
        for j in range(num_panels_y + 1):

            current_panel_length = panel_length if i < num_panels_x else remaining_length
            current_panel_width = panel_width if j < num_panels_y else remaining_height

            if current_panel_length <= 0 or current_panel_width <= 0:
                continue

            x = location[0] + (current_panel_length / 2) + i * panel_length
            y = location[1]
            z = location[2] + (current_panel_width / 2) + j * panel_width

            panel_location = (x, y, z)
            panel_name = f"Panel_{i+1}_{j+1}"
            panel = create_plane(
                panel_name,
                size,
                current_panel_length,
                current_panel_width,
                1,
                panel_location,
                rotation=rotation
            )

            add_material_from_image(panel, f"{panel_name}_material", image_path)
    return

def create_scene(output_path):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    size = 2
    wall_height = 4 / size  # 4m ceiling
    wall_length = 10 / size  # 10m walls
    panel_size = 1  # meters

    wall1 = create_plane("Wall1", size, wall_height, wall_length, 1, (0, wall_length / 2, wall_height / 2), (0, math.radians(90), 0))
    wall2 = create_plane("Wall2", size, wall_length, wall_height, 1, (wall_length / 2, 0, wall_height / 2), (math.radians(90), 0, 0))
    floor = create_plane("Floor", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, 0), (0, 0, 0))
    ceiling = create_plane("Ceiling", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, wall_height), (0, 0, 0))

    wall1 = add_material_from_image(wall1, "Wall1_Material", "uploaded_assets/Untitled.jpg")
    wall2 = add_material_from_image(wall2, "Wall2_Material", "uploaded_assets/Untitled.jpg")
    floor = add_material_from_image(floor, "Floor_Material", "uploaded_assets/wood_texture.jpeg")
    ceiling = add_material_from_image(ceiling, "Ceiling_Material", "uploaded_assets/wood_texture.jpeg")

    light1 = create_interior_light("InteriorLight1", (5, 5, 2), energy=30)
    light2 = create_interior_light("InteriorLight2", (5, 5, 2.5), energy=30)

    camera_location = (10, 10, 2)  # Adjusted to view the room
    camera_target = (0, 0, 2)  # Looking towards the opposite corner

    bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=camera_location, rotation=(math.radians(90), 0, math.radians(135)), scale=(1, 1, 1))
    camera = bpy.context.object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    camera.data.lens = 35

    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (1, 1, 1, 1)  # White
    bg.inputs[1].default_value = 1.0  # Strength

    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.render.resolution_percentage = 50
    bpy.context.scene.render.engine = 'CYCLES'

    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    print(f"Image rendered to: {output_path}")
    display(Image(filename=output_path))
output_directory = "/home/turannurgozhin/blender_interior_visualizer"
output_path = os.path.join(output_directory, "rendered_scene.png")

# Create the directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True) 
create_scene(output_path)
