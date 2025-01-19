import math
from .geometry import create_plane
from .materials import add_material_from_image

def create_panels(size, plane_length, plane_width, panel_length, panel_width, image_path, location=(0, 0, 0), rotation=(0, 0, 0)):
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
            panel = create_plane(panel_name, size, current_panel_length, current_panel_width, 1, panel_location, rotation)
            add_material_from_image(panel, f"{panel_name}_material", image_path)
