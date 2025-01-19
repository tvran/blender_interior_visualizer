reference_script = """
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
    # Scaling: Blender's default plane is 2x2 units, so scale by half the desired size
    plane.scale = (size_x / 2, size_y / 2, 1)
    return plane

def create_interior_light(name, location, energy=1000):
    # Create a point light
    light_data = bpy.data.lights.new(name=name, type='POINT')
    light_data.energy = energy  # Increased energy for better visibility
    light_data.shadow_soft_size = 2  # Larger size for softer shadows
    
    # Create the light object
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)
    
    # Set the light's location
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
    bsdf_color.inputs['Base Color'].default_value = color  # Set color
    plane = assign_material(plane, material)
    return plane

def add_material_from_image(plane, material_name, image_path):
    material_name = material_name
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    while nodes:
        nodes.remove(nodes[0])

    # Create nodes
    principled_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    principled_bsdf.location = (200, 0)
    material_output = nodes.new('ShaderNodeOutputMaterial')
    material_output.location = (400, 0)
    image_texture = nodes.new('ShaderNodeTexImage')
    image_texture.location = (0, 0)

    # Load image
    try:
        image_texture.image = bpy.data.images.load(image_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        print(f"Make sure the image exists at: {image_path}")
        print("If using a relative path, ensure the image is in the same directory as the .blend file")
        exit()

    # Create links
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
    num_panels_x = math.floor(plane_length / panel_length)  # Number of panels along X
    num_panels_y = math.floor(plane_width / panel_width)  # Number of panels along Y

    remaining_length = plane_length - (num_panels_x * panel_length)
    remaining_height = plane_width - (num_panels_y * panel_width)

    for i in range(num_panels_x + 1):
        for j in range(num_panels_y + 1):

            current_panel_length = panel_length if i < num_panels_x else remaining_length
            current_panel_width = panel_width if j < num_panels_y else remaining_height

            # Skip if there's no space left for the last panels
            if current_panel_length <= 0 or current_panel_width <= 0:
                continue

            # Calculate position for each panel
            x = location[0] + (current_panel_length / 2) + i * panel_length
            y = location[1]  # Plane depth (adjust for walls or floors)
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

            add_material_from_image(panel, "{panel_name}_material", image_path)
    return

def create_scene(output_path):
    # --- Clear Existing Objects ---
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # --- Define Dimensions ---
    size = 2
    wall_height = 3 / size
    wall_length = 5  / size
    panel_size = 1  # meters (both length and height, assuming square panels)

    # --- Create Planes ---
    # Wall1 is at x=0, extends along y from 0 to 5, z from 0 to 3
    wall1 = create_plane("Wall1", size, wall_height, wall_length, 1, (0, wall_length / 2, wall_height / 2), (0, math.radians(90), 0))
    # Wall2 is at y=0, extends along x from 0 to 5, z from 0 to 3
    #wall2 = create_plane("Wall2", size, wall_length, wall_height, 1, (wall_length / 2, 0, wall_height / 2), (math.radians(90), 0, 0))
    # --- Create Floor ---
    # Floor extends along x and y from 0 to 5, located at z=0
    floor = create_plane("Floor", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, 0), (0, 0, 0))
    # --- Create Ceiling ---
    # Ceiling extends along x and y from 0 to 5, located at z=3
    ceiling = create_plane("Ceiling", size, wall_length, wall_length, 1, (wall_length / 2, wall_length / 2, wall_height), (0, 0, 0))

    # --- Add Materials with Assigned Textures ---
    # Black Material for Wall 1
    wall1 = add_material_from_image(wall1, "Wall1_Material", "/content/Untitled.jpg")
    # Floor Material
    floor = add_material_from_image(floor, "Floor_Material", "/content/wood_texture.jpeg")
    # White Material for Ceiling
    ceiling = add_color_material(ceiling, "WhiteMaterial", (8/255, 45/255, 23/255, 1))
    # Panels for Wall 2
    wall2 = create_panels(
        size,
        wall_length,
        wall_height,
        panel_size,
        panel_size,
        "/content/Untitled.jpg",
        location=(0,0,0),
        rotation=((math.radians(90)),0,0)
    )

    
     # Add interior lights
    light1 = create_interior_light("InteriorLight1", (wall_length/4, wall_length/4, wall_height/2), energy=30)
    light2 = create_interior_light("InteriorLight2", (wall_length*3/4, wall_length*3/4, wall_height/2), energy=30)

    # --- Camera Setup ---
    # Define camera location and target
    camera_location = (5, 5, 0.9)
    camera_target = (0, 0, 0)

    # Add Camera
    bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=camera_location, rotation=(math.radians(90), 0, math.radians(135)), scale=(1, 1, 1))
    camera = bpy.context.object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    camera.data.lens = 35  # Focal length

    # --- Set World Background to White ---
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.5, 0.5, 0.5, 0)  # White
    bg.inputs[1].default_value = 1.0  # Strength

    # --- Render Settings ---
    bpy.context.scene.render.resolution_x = 1024  # Width in pixels
    bpy.context.scene.render.resolution_y = 1024  # Height in pixels
    bpy.context.scene.render.resolution_percentage = 50  # Scale resolution
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

    # --- Render the Image ---
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    print(f"Image rendered to: {output_path}")
    display(Image(filename=output_path))

# --- Specify the Output Path ---
output_path = "/content/rendered_scene.png"  # Replace with your desired path
create_scene(output_path)
"""