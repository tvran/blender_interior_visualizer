import bpy

def assign_material(plane, material):
    if plane.data.materials:
        plane.data.materials[0] = material
    else:
        plane.data.materials.append(material)
    return plane

def add_color_material(plane, material_name, color=(0, 0, 0, 1)):
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    bsdf_color = material.node_tree.nodes.get("Principled BSDF")
    bsdf_color.inputs['Base Color'].default_value = color
    return assign_material(plane, material)

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
    return assign_material(plane, material)