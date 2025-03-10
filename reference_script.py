reference_script = """
# user asked: Design a 7x7m room with 3m ceiling. 
# I want the ceiling to be covered in beige color. 
# The first wall should be filled in 1x1m panels with 
# wall-textures-1000x1000 texture, the second wall should 
# be filled in 1x0.5m panels with abstract-background texture. 
# The floor must be covered with 1x1m wood_texture panels.

import os
import bpy
import math
from enum import Enum

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

def create_interior_light(name, location, energy=30):
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
        exit()

    links.new(image_texture.outputs['Color'], principled_bsdf.inputs['Base Color'])
    links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])
    plane = assign_material(plane, material)
    return plane

class WallOrientation(Enum):
    FLOOR = 'floor'     
    WALL_X = 'wall_x'   
    WALL_Y = 'wall_y'   

def create_panels(size, plane_length, plane_width, panel_length, panel_width, 
                 image_path, location=(0,0,0), rotation=(0,0,0), gap=0.001,
                 orientation=WallOrientation.FLOOR):
    effective_panel_length = panel_length + gap
    effective_panel_width = panel_width + gap

    num_panels_x = math.ceil(plane_length / effective_panel_length)
    num_panels_y = math.ceil(plane_width / effective_panel_width)

    panels = []

    for i in range(num_panels_x):
        for j in range(num_panels_y):
            current_panel_length = panel_length
            current_panel_width = panel_width

            if i == num_panels_x - 1:
                current_panel_length = plane_length - ((num_panels_x - 1) * effective_panel_length) - gap
            if j == num_panels_y - 1:
                current_panel_width = plane_width - ((num_panels_y - 1) * effective_panel_width) - gap

            if current_panel_length <= 0.001 or current_panel_width <= 0.001:
                continue

            offset_primary = effective_panel_length * i + current_panel_length / 2
            offset_secondary = effective_panel_width * j + current_panel_width / 2

            if orientation == WallOrientation.FLOOR:
                panel_location = (location[0] + offset_primary, location[1] + offset_secondary, location[2])
                panel_rotation = rotation

            elif orientation == WallOrientation.WALL_X:
                panel_location = (location[0], location[1] + offset_primary, location[2] + offset_secondary)
                panel_rotation = (rotation[0], rotation[1] + math.pi/2, rotation[2])

            else:
                panel_location = (location[0] + offset_primary, location[1], location[2] + offset_secondary)
                panel_rotation = (rotation[0] + math.pi/2, rotation[1], rotation[2])

            panel_name = f"Panel_{i+1}_{j+1}"

            try:
                panel = create_plane(
                    panel_name,
                    size,
                    current_panel_length,
                    current_panel_width,
                    1,
                    panel_location,
                    rotation=panel_rotation
                )
                add_material_from_image(panel, f"{panel_name}_material", image_path)
                panels.append(panel)

            except Exception as e:
                print(f"Error creating panel {panel_name}: {str(e)}")
                continue

    return panels

def create_scene(output_path):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    size = 2
    wall_height = 3 / size
    wall_length = 7 / size
    panel_size1 = 0.5 / size
    panel_size2 = 1 / size
    floor_panel_size = 1 / size

    # Create Plane 
    ceiling = create_plane("Ceiling", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, wall_height), (0, 0, 0))

    # Add Materials
    ceiling = add_color_material(ceiling, "BeigeMaterial", (222/255, 210/255, 197/255, 1))
    
    # Wall1 panels
    wall1_panels = create_panels(size, wall_length, wall_height, panel_size1, panel_size1, 
                                  "/content/wall-textures-1000x1000.jpg", 
                                  location=(0, 0, 0),
                                  gap=0.0,
                                  orientation=WallOrientation.WALL_X)

    # Wall2 panels
    wall2_panels = create_panels(size, wall_length, wall_height, panel_size1, panel_size2, 
                                  "/content/abstract-background-wall-concept-with-copy-space.jpg", 
                                  location=(0, 0, 0),
                                  gap=0.0,
                                  orientation=WallOrientation.WALL_Y)
    
    # Floor panels
    floor_panels = create_panels(size, wall_length, wall_length, floor_panel_size, floor_panel_size, 
                                  "/content/wood_texture.jpeg", 
                                  location=(0, 0, 0),
                                  gap=0.0,
                                  orientation=WallOrientation.FLOOR)

    # Add interior lights
    light1 = create_interior_light("InteriorLight1", (wall_length/4, wall_length/4, wall_height/2), energy=30)
    light2 = create_interior_light("InteriorLight2", (wall_length*3/4, wall_length*3/4, wall_height/2), energy=30)

    # --- Camera Setup ---
    camera_location = (wall_length / 2, wall_length / 2, wall_height / size)
    camera_target = (0, 0, 0)

    bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=camera_location, rotation=(math.radians(90), 0, math.radians(135)), scale=(1, 1, 1))
    camera = bpy.context.object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    camera.data.lens = 35  

    # --- Set World Background to White ---
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (1, 1, 1, 1)  # White
    bg.inputs[1].default_value = 1.0  

    # --- Render Settings ---
    bpy.context.scene.render.resolution_x = 900  
    bpy.context.scene.render.resolution_y = 900  
    bpy.context.scene.render.resolution_percentage = 50  
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.cycles.use_adaptive_sampling = True

    # --- Render the Image ---
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    print(f"Image rendered to: {output_path}")
    display(Image(filename=output_path))

output_directory = "/home/turannurgozhin/blender_interior_visualizer"
output_path = os.path.join(output_directory, "rendered_room.png")
os.makedirs(output_directory, exist_ok=True)
create_scene(output_path)
"""
