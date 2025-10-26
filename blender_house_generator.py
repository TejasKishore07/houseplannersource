#!/usr/bin/env python3
"""
Ultra-Realistic House Architecture Generator
Usage: blender -b -P blender_house_generator.py -- --land 7 --orientation North --house_type 3BHK --output test_house.glb --furniture "beds,sofa,dining_table,kitchen_counter"
"""

import bpy
import sys
import json
import math
import bmesh

# Get custom arguments after '--'
argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

# Parse arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--land', type=int, required=True)
parser.add_argument('--orientation', type=str, required=True)
parser.add_argument('--house_type', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--format', type=str, choices=['glb', 'obj', 'fbx'], default='glb')
parser.add_argument('--kitchen_size', type=str, default='medium')
parser.add_argument('--living_room', type=str, default='medium')
parser.add_argument('--bathrooms', type=str, default='1')
parser.add_argument('--balcony', type=str, default='no')
parser.add_argument('--parking', type=str, default='no')
parser.add_argument('--garden', type=str, default='no')
parser.add_argument('--study_room', type=str, default='no')
parser.add_argument('--furniture', type=str, default='')

args = parser.parse_args(argv)

# Parse furniture list
furniture_list = []
if args.furniture:
    furniture_list = [item.strip() for item in args.furniture.split(',')]

print("🏗️ Ultra-Realistic House Architecture Generator")
print("=" * 60)
print(f"📏 Land Area: {args.land} cents")
print(f"🏠 House Type: {args.house_type}")
print(f" Orientation: {args.orientation}")
print(f" Kitchen: {args.kitchen_size}")
print(f"🛋️ Living Room: {args.living_room}")
print(f" Bathrooms: {args.bathrooms}")
print(f" Balcony: {args.balcony}")
print(f"🚗 Parking: {args.parking}")
print(f"🌱 Garden: {args.garden}")
print(f"📚 Study Room: {args.study_room}")
print(f"🪑 Furniture: {furniture_list}")

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_realistic_material(name, base_color, roughness=0.5, metallic=0.0):
    """Create a realistic material with proper PBR properties"""
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = base_color  # Base Color
    principled.inputs[7].default_value = roughness  # Roughness
    principled.inputs[6].default_value = metallic  # Metallic
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_wall_material():
    """Create realistic wall material with texture"""
    material = bpy.data.materials.new(name="WallMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = (0.95, 0.93, 0.88, 1)  # Warm white
    principled.inputs[7].default_value = 0.8  # Roughness
    principled.inputs[6].default_value = 0.0  # Metallic
    
    # Create Noise Texture for wall variation
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    noise_tex.location = (-300, 100)
    noise_tex.inputs[2].default_value = 50.0  # Scale
    noise_tex.inputs[3].default_value = 0.5  # Detail
    
    # Create Color Ramp to control noise effect
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-100, 100)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[1].position = 0.6
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(noise_tex.outputs[0], ramp.inputs[0])
    links.new(ramp.outputs[0], principled.inputs[19])  # Normal map
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_floor_material():
    """Create realistic wooden floor material"""
    material = bpy.data.materials.new(name="FloorMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = (0.35, 0.22, 0.12, 1)  # Rich wood color
    principled.inputs[7].default_value = 0.2  # Roughness
    principled.inputs[6].default_value = 0.0  # Metallic
    
    # Create Wood Texture
    wood_tex = nodes.new(type='ShaderNodeTexNoise')
    wood_tex.location = (-300, 100)
    wood_tex.inputs[2].default_value = 100.0  # Scale
    wood_tex.inputs[3].default_value = 8.0  # Detail
    
    # Create Color Ramp for wood grain
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-100, 100)
    ramp.color_ramp.elements[0].color = (0.25, 0.15, 0.08, 1)
    ramp.color_ramp.elements[1].color = (0.45, 0.28, 0.15, 1)
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(wood_tex.outputs[0], ramp.inputs[0])
    links.new(ramp.outputs[0], principled.inputs[0])  # Base Color
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_roof_material():
    """Create realistic roof material"""
    material = bpy.data.materials.new(name="RoofMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = (0.15, 0.12, 0.10, 1)  # Dark slate
    principled.inputs[7].default_value = 0.9  # Roughness
    principled.inputs[6].default_value = 0.0  # Metallic
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_door_material():
    """Create realistic door material"""
    material = bpy.data.materials.new(name="DoorMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = (0.25, 0.15, 0.08, 1)  # Dark wood
    principled.inputs[7].default_value = 0.3  # Roughness
    principled.inputs[6].default_value = 0.0  # Metallic
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_window_material():
    """Create realistic glass material"""
    material = bpy.data.materials.new(name="WindowMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = (0.9, 0.95, 1.0, 1)  # Slight blue tint
    principled.inputs[7].default_value = 0.0  # Roughness (smooth)
    principled.inputs[6].default_value = 0.0  # Metallic
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_furniture_material(color, roughness=0.6):
    """Create furniture material"""
    material = bpy.data.materials.new(name=f"FurnitureMaterial_{color[0]:.2f}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    nodes.clear()
    
    # Create Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs[0].default_value = color
    principled.inputs[7].default_value = roughness  # Roughness
    principled.inputs[6].default_value = 0.0  # Metallic
    
    # Create Material Output
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)
    
    # Link nodes
    links.new(principled.outputs[0], material_output.inputs[0])
    
    return material

def create_realistic_wall(start, end, height, material, thickness=0.2):
    """Create a realistic wall with proper thickness"""
    # Calculate wall dimensions
    length = ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    
    # Create wall mesh with thickness
    bpy.ops.mesh.primitive_cube_add(size=1)
    wall = bpy.context.active_object
    wall.name = "Wall"
    
    # Position and scale
    wall.location = ((start[0] + end[0])/2, (start[1] + end[1])/2, height/2)
    wall.scale = (length, thickness, height)
    wall.rotation_euler[2] = angle
    
    # Apply material
    if wall.data.materials:
        wall.data.materials[0] = material
    else:
        wall.data.materials.append(material)
    
    return wall

def create_realistic_room(room_data, wall_material, floor_material):
    """Create a realistic room with proper walls and floor"""
    x, y, width, height = room_data['x'], room_data['y'], room_data['width'], room_data['height']
    wall_height = 3.0
    wall_thickness = 0.2
    
    walls = []
    
    # Create four walls with thickness
    # Wall 1: Bottom
    walls.append(create_realistic_wall((x, y), (x + width, y), wall_height, wall_material, wall_thickness))
    
    # Wall 2: Right
    walls.append(create_realistic_wall((x + width, y), (x + width, y + height), wall_height, wall_material, wall_thickness))
    
    # Wall 3: Top
    walls.append(create_realistic_wall((x + width, y + height), (x, y + height), wall_height, wall_material, wall_thickness))
    
    # Wall 4: Left
    walls.append(create_realistic_wall((x, y + height), (x, y), wall_height, wall_material, wall_thickness))
    
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=1)
    floor = bpy.context.active_object
    floor.name = "Floor"
    
    floor.location = (x + width/2, y + height/2, 0)
    floor.scale = (width/2, height/2, 1)
    
    if floor.data.materials:
        floor.data.materials[0] = floor_material
    else:
        floor.data.materials.append(floor_material)
    
    return walls, floor

def create_realistic_door(position, width=1.0, height=2.1):
    """Create a realistic door with frame"""
    # Door frame
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.name = "DoorFrame"
    
    frame.location = position
    frame.scale = (width/2 + 0.1, 0.15, height/2 + 0.1)
    
    frame_material = create_furniture_material((0.8, 0.8, 0.8, 1))  # White frame
    if frame.data.materials:
        frame.data.materials[0] = frame_material
    else:
        frame.data.materials.append(frame_material)
    
    # Door panel
    bpy.ops.mesh.primitive_cube_add(size=1)
    door = bpy.context.active_object
    door.name = "Door"
    
    door.location = position
    door.scale = (width/2, 0.05, height/2)
    
    door_material = create_door_material()
    if door.data.materials:
        door.data.materials[0] = door_material
    else:
        door.data.materials.append(door_material)
    
    return [frame, door]

def create_realistic_window(position, width=1.2, height=1.2):
    """Create a realistic window with frame"""
    # Window frame
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame = bpy.context.active_object
    frame.name = "WindowFrame"
    
    frame.location = position
    frame.scale = (width/2 + 0.1, 0.15, height/2 + 0.1)
    
    frame_material = create_furniture_material((0.9, 0.9, 0.9, 1))  # White frame
    if frame.data.materials:
        frame.data.materials[0] = frame_material
    else:
        frame.data.materials.append(frame_material)
    
    # Glass panel
    bpy.ops.mesh.primitive_cube_add(size=1)
    glass = bpy.context.active_object
    glass.name = "WindowGlass"
    
    glass.location = position
    glass.scale = (width/2, 0.02, height/2)
    
    glass_material = create_window_material()
    if glass.data.materials:
        glass.data.materials[0] = glass_material
    else:
        glass.data.materials.append(glass_material)
    
    return [frame, glass]

def create_realistic_bed(position, size="double"):
    """Create a realistic bed with headboard and mattress"""
    if size == "single":
        bed_width, bed_length = 0.9, 2.0
    else:  # double
        bed_width, bed_length = 1.6, 2.0
    
    # Bed frame
    bpy.ops.mesh.primitive_cube_add(size=1)
    bed_frame = bpy.context.active_object
    bed_frame.name = "BedFrame"
    
    bed_frame.location = position
    bed_frame.scale = (bed_width/2, bed_length/2, 0.3)
    
    bed_material = create_furniture_material((0.6, 0.4, 0.2, 1))  # Wooden
    if bed_frame.data.materials:
        bed_frame.data.materials[0] = bed_material
    else:
        bed_frame.data.materials.append(bed_material)
    
    # Mattress
    bpy.ops.mesh.primitive_cube_add(size=1)
    mattress = bpy.context.active_object
    mattress.name = "Mattress"
    
    mattress.location = (position[0], position[1], position[2] + 0.15)
    mattress.scale = (bed_width/2 - 0.05, bed_length/2 - 0.05, 0.15)
    
    mattress_material = create_furniture_material((0.2, 0.3, 0.8, 1))  # Blue
    if mattress.data.materials:
        mattress.data.materials[0] = mattress_material
    else:
        mattress.data.materials.append(mattress_material)
    
    # Headboard
    bpy.ops.mesh.primitive_cube_add(size=1)
    headboard = bpy.context.active_object
    headboard.name = "Headboard"
    
    headboard.location = (position[0], position[1] + bed_length/2 - 0.1, position[2] + 0.5)
    headboard.scale = (bed_width/2, 0.1, 0.5)
    
    headboard_material = create_furniture_material((0.4, 0.25, 0.15, 1))  # Dark wood
    if headboard.data.materials:
        headboard.data.materials[0] = headboard_material
    else:
        headboard.data.materials.append(headboard_material)
    
    return [bed_frame, mattress, headboard]

def create_realistic_sofa(position):
    """Create a realistic sofa with cushions"""
    # Sofa base
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_base = bpy.context.active_object
    sofa_base.name = "SofaBase"
    
    sofa_base.location = position
    sofa_base.scale = (2.0/2, 0.8/2, 0.4)
    
    sofa_material = create_furniture_material((0.6, 0.4, 0.2, 1))  # Brown
    if sofa_base.data.materials:
        sofa_base.data.materials[0] = sofa_material
    else:
        sofa_base.data.materials.append(sofa_material)
    
    # Sofa back
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_back = bpy.context.active_object
    sofa_back.name = "SofaBack"
    
    sofa_back.location = (position[0], position[1] - 0.3, position[2] + 0.6)
    sofa_back.scale = (2.0/2, 0.1, 0.6)
    
    if sofa_back.data.materials:
        sofa_back.data.materials[0] = sofa_material
    else:
        sofa_back.data.materials.append(sofa_material)
    
    # Cushions
    cushions = []
    cushion_positions = [
        (position[0] - 0.6, position[1], position[2] + 0.2),
        (position[0] + 0.6, position[1], position[2] + 0.2),
    ]
    
    for i, cushion_pos in enumerate(cushion_positions):
        bpy.ops.mesh.primitive_cube_add(size=1)
        cushion = bpy.context.active_object
        cushion.name = f"SofaCushion_{i}"
        
        cushion.location = cushion_pos
        cushion.scale = (0.4, 0.6, 0.1)
        
        cushion_material = create_furniture_material((0.8, 0.7, 0.6, 1))  # Beige
        if cushion.data.materials:
            cushion.data.materials[0] = cushion_material
        else:
            cushion.data.materials.append(cushion_material)
        
        cushions.append(cushion)
    
    return [sofa_base, sofa_back] + cushions

def create_realistic_dining_table(position):
    """Create a realistic dining table with chairs"""
    # Table top
    bpy.ops.mesh.primitive_cube_add(size=1)
    table = bpy.context.active_object
    table.name = "DiningTable"
    
    table.location = position
    table.scale = (1.2/2, 0.8/2, 0.05)
    
    table_material = create_furniture_material((0.4, 0.25, 0.15, 1))  # Dark wood
    if table.data.materials:
        table.data.materials[0] = table_material
    else:
        table.data.materials.append(table_material)
    
    # Table legs
    legs = []
    leg_positions = [
        (position[0] - 0.5, position[1] - 0.3, position[2] - 0.35),
        (position[0] + 0.5, position[1] - 0.3, position[2] - 0.35),
        (position[0] - 0.5, position[1] + 0.3, position[2] - 0.35),
        (position[0] + 0.5, position[1] + 0.3, position[2] - 0.35)
    ]
    
    for i, leg_pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cube_add(size=1)
        leg = bpy.context.active_object
        leg.name = f"TableLeg_{i}"
        
        leg.location = leg_pos
        leg.scale = (0.05, 0.05, 0.35)
        
        if leg.data.materials:
            leg.data.materials[0] = table_material
        else:
            leg.data.materials.append(table_material)
        
        legs.append(leg)
    
    # Chairs
    chairs = []
    chair_positions = [
        (position[0], position[1] - 0.6, position[2] - 0.35),
        (position[0], position[1] + 0.6, position[2] - 0.35),
    ]
    
    for i, chair_pos in enumerate(chair_positions):
        # Chair seat
        bpy.ops.mesh.primitive_cube_add(size=1)
        chair_seat = bpy.context.active_object
        chair_seat.name = f"ChairSeat_{i}"
        
        chair_seat.location = chair_pos
        chair_seat.scale = (0.4, 0.4, 0.05)
        
        chair_material = create_furniture_material((0.3, 0.2, 0.1, 1))  # Dark wood
        if chair_seat.data.materials:
            chair_seat.data.materials[0] = chair_material
        else:
            chair_seat.data.materials.append(chair_material)
        
        chairs.append(chair_seat)
        
        # Chair back
        bpy.ops.mesh.primitive_cube_add(size=1)
        chair_back = bpy.context.active_object
        chair_back.name = f"ChairBack_{i}"
        
        chair_back.location = (chair_pos[0], chair_pos[1] - 0.2, chair_pos[2] + 0.3)
        chair_back.scale = (0.4, 0.05, 0.3)
        
        if chair_back.data.materials:
            chair_back.data.materials[0] = chair_material
        else:
            chair_back.data.materials.append(chair_material)
        
        chairs.append(chair_back)
    
    return [table] + legs + chairs

def create_realistic_kitchen_counter(position):
    """Create a realistic kitchen counter with appliances"""
    # Counter base
    bpy.ops.mesh.primitive_cube_add(size=1)
    counter = bpy.context.active_object
    counter.name = "KitchenCounter"
    
    counter.location = position
    counter.scale = (2.0/2, 0.6/2, 0.9)
    
    counter_material = create_furniture_material((0.9, 0.9, 0.9, 1))  # White
    if counter.data.materials:
        counter.data.materials[0] = counter_material
    else:
        counter.data.materials.append(counter_material)
    
    # Counter top
    bpy.ops.mesh.primitive_cube_add(size=1)
    counter_top = bpy.context.active_object
    counter_top.name = "CounterTop"
    
    counter_top.location = (position[0], position[1], position[2] + 0.45)
    counter_top.scale = (2.0/2, 0.6/2, 0.05)
    
    top_material = create_furniture_material((0.8, 0.8, 0.8, 1))  # Light gray
    if counter_top.data.materials:
        counter_top.data.materials[0] = top_material
    else:
        counter_top.data.materials.append(top_material)
    
    # Sink
    bpy.ops.mesh.primitive_cube_add(size=1)
    sink = bpy.context.active_object
    sink.name = "Sink"
    
    sink.location = (position[0] - 0.3, position[1], position[2] + 0.47)
    sink.scale = (0.3, 0.4, 0.02)
    
    sink_material = create_furniture_material((0.7, 0.7, 0.7, 1))  # Stainless steel
    if sink.data.materials:
        sink.data.materials[0] = sink_material
    else:
        sink.data.materials.append(sink_material)
    
    # Stove
    bpy.ops.mesh.primitive_cube_add(size=1)
    stove = bpy.context.active_object
    stove.name = "Stove"
    
    stove.location = (position[0] + 0.3, position[1], position[2] + 0.47)
    stove.scale = (0.3, 0.4, 0.02)
    
    stove_material = create_furniture_material((0.2, 0.2, 0.2, 1))  # Black
    if stove.data.materials:
        stove.data.materials[0] = stove_material
    else:
        stove.data.materials.append(stove_material)
    
    return [counter, counter_top, sink, stove]

def create_realistic_roof(house_width, house_length, wall_height):
    """Create a realistic sloped roof"""
    # Create roof mesh
    bpy.ops.mesh.primitive_cube_add(size=1)
    roof = bpy.context.active_object
    roof.name = "Roof"
    
    # Position roof above walls
    roof.location = (house_width/2, house_length/2, wall_height + 1.5)
    roof.scale = (house_width/2 + 0.5, house_length/2 + 0.5, 0.3)
    
    # Apply roof material
    roof_material = create_roof_material()
    if roof.data.materials:
        roof.data.materials[0] = roof_material
    else:
        roof.data.materials.append(roof_material)
    
    return roof

def create_realistic_3bhk_house():
    """Create a realistic 3BHK house with proper architecture"""
    print(" Creating realistic 3BHK house...")
    
    # House dimensions based on land area
    house_width = 18
    house_length = 22
    wall_height = 3.0
    
    print(f"🏠 House Dimensions: {house_width}x{house_length}x{wall_height} meters")
    
    # Create materials
    wall_material = create_wall_material()
    floor_material = create_floor_material()
    
    # Define room layouts for 3BHK
    rooms = [
        # Bedroom 1 (Master)
        {'name': 'Master Bedroom', 'x': 0, 'y': 0, 'width': 4, 'height': 4},
        # Bedroom 2
        {'name': 'Bedroom 2', 'x': 4, 'y': 0, 'width': 4, 'height': 4},
        # Bedroom 3
        {'name': 'Bedroom 3', 'x': 8, 'y': 0, 'width': 4, 'height': 4},
        # Kitchen
        {'name': 'Kitchen', 'x': 0, 'y': 4, 'width': 6, 'height': 4},
        # Living Room
        {'name': 'Living Room', 'x': 6, 'y': 4, 'width': 8, 'height': 6},
        # Dining Area
        {'name': 'Dining Area', 'x': 6, 'y': 10, 'width': 6, 'height': 4},
        # Bathroom 1
        {'name': 'Bathroom 1', 'x': 12, 'y': 10, 'width': 2, 'height': 3},
        # Bathroom 2
        {'name': 'Bathroom 2', 'x': 14, 'y': 10, 'width': 2, 'height': 3},
        # Entrance Hall
        {'name': 'Entrance Hall', 'x': 0, 'y': 8, 'width': 6, 'height': 2},
        # Balcony
        {'name': 'Balcony', 'x': 0, 'y': 14, 'width': 6, 'height': 2},
    ]
    
    # Create walls and floors for each room
    all_walls = []
    all_floors = []
    
    for room in rooms:
        # Create realistic room
        walls, floor = create_realistic_room(room, wall_material, floor_material)
        all_walls.extend(walls)
        all_floors.append(floor)
    
    # Create doors
    doors = []
    door_positions = [
        (2, 8, 1.05),    # Entrance door
        (2, 4, 1.05),    # Kitchen door
        (6, 4, 1.05),    # Living room door
        (8, 2, 1.05),    # Bedroom 1 door
        (12, 2, 1.05),   # Bedroom 2 door
        (16, 2, 1.05),   # Bedroom 3 door
        (13, 10, 1.05),  # Bathroom 1 door
        (15, 10, 1.05),  # Bathroom 2 door
    ]
    
    for pos in door_positions:
        door_parts = create_realistic_door(pos)
        doors.extend(door_parts)
    
    # Create windows
    windows = []
    window_positions = [
        (2, 0, 1.5),     # Bedroom 1 window
        (6, 0, 1.5),     # Bedroom 2 window
        (10, 0, 1.5),    # Bedroom 3 window
        (3, 4, 1.5),     # Kitchen window
        (10, 4, 1.5),    # Living room window 1
        (14, 4, 1.5),    # Living room window 2
    ]
    
    for pos in window_positions:
        window_parts = create_realistic_window(pos)
        windows.extend(window_parts)
    
    # Create realistic roof
    roof = create_realistic_roof(house_width, house_length, wall_height)
    
    # Add furniture based on user preferences
    furniture_objects = []
    
    if 'beds' in furniture_list:
        # Add beds to bedrooms
        bed_positions = [
            (2, 2, 0.3),    # Master bedroom
            (6, 2, 0.3),    # Bedroom 2
            (10, 2, 0.3),   # Bedroom 3
        ]
        
        for pos in bed_positions:
            bed_parts = create_realistic_bed(pos, "double")
            furniture_objects.extend(bed_parts)
    
    if 'sofa' in furniture_list:
        # Add sofa to living room
        sofa_parts = create_realistic_sofa((10, 7, 0.4))
        furniture_objects.extend(sofa_parts)
    
    if 'dining_table' in furniture_list:
        # Add dining table
        table_parts = create_realistic_dining_table((9, 12, 0.4))
        furniture_objects.extend(table_parts)
    
    if 'kitchen_counter' in furniture_list:
        # Add kitchen counter
        counter_parts = create_realistic_kitchen_counter((3, 6, 0.45))
        furniture_objects.extend(counter_parts)
    
    # Setup realistic lighting
    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), math.radians(45), 0)
    
    # Ambient lighting
    bpy.ops.object.light_add(type='AREA', location=(house_width/2, house_length/2, wall_height + 2))
    ambient = bpy.context.active_object
    ambient.data.energy = 2.0
    ambient.data.size = 10.0
    
    # Setup camera
    bpy.ops.object.camera_add(location=(25, -15, 15))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    
    # Set camera as active
    bpy.context.scene.camera = camera
    
    print("✅ Realistic 3BHK house created successfully!")
    return len(all_walls) + len(all_floors) + len(doors) + len(windows) + 1 + len(furniture_objects)

def create_realistic_duplex_house():
    """Create a realistic duplex house with two floors"""
    print("🏗️ Creating realistic Duplex house...")
    
    # House dimensions based on land area
    house_width = 15
    house_length = 20
    wall_height = 3.0
    
    print(f"🏠 House Dimensions: {house_width}x{house_length}x{wall_height} meters")
    
    # Create materials
    wall_material = create_wall_material()
    floor_material = create_floor_material()
    
    # Define room layouts for Duplex (Ground Floor)
    ground_floor_rooms = [
        # Living Room
        {'name': 'Living Room', 'x': 0, 'y': 0, 'width': 8, 'height': 6},
        # Kitchen
        {'name': 'Kitchen', 'x': 8, 'y': 0, 'width': 7, 'height': 4},
        # Dining Area
        {'name': 'Dining Area', 'x': 8, 'y': 4, 'width': 7, 'height': 4},
        # Bathroom 1
        {'name': 'Bathroom 1', 'x': 0, 'y': 6, 'width': 3, 'height': 3},
        # Entrance Hall
        {'name': 'Entrance Hall', 'x': 3, 'y': 6, 'width': 5, 'height': 3},
        # Staircase
        {'name': 'Staircase', 'x': 0, 'y': 9, 'width': 4, 'height': 4},
    ]
    
    # Define room layouts for Duplex (First Floor)
    first_floor_rooms = [
        # Master Bedroom
        {'name': 'Master Bedroom', 'x': 0, 'y': 0, 'width': 6, 'height': 5},
        # Bedroom 2
        {'name': 'Bedroom 2', 'x': 6, 'y': 0, 'width': 6, 'height': 5},
        # Bedroom 3
        {'name': 'Bedroom 3', 'x': 12, 'y': 0, 'width': 3, 'height': 5},
        # Bathroom 2
        {'name': 'Bathroom 2', 'x': 0, 'y': 5, 'width': 3, 'height': 3},
        # Family Hall
        {'name': 'Family Hall', 'x': 3, 'y': 5, 'width': 12, 'height': 4},
        # Balcony
        {'name': 'Balcony', 'x': 0, 'y': 9, 'width': 15, 'height': 2},
    ]
    
    # Create ground floor
    all_walls = []
    all_floors = []
    
    # Ground floor rooms
    for room in ground_floor_rooms:
        walls, floor = create_realistic_room(room, wall_material, floor_material)
        all_walls.extend(walls)
        all_floors.append(floor)
    
    # Create first floor (elevated)
    for room in first_floor_rooms:
        # Adjust Y position for first floor
        room['y'] += 13  # Elevate first floor
        walls, floor = create_realistic_room(room, wall_material, floor_material)
        all_walls.extend(walls)
        all_floors.append(floor)
    
    # Create doors
    doors = []
    door_positions = [
        # Ground floor doors
        (4, 6, 1.05),    # Entrance door
        (8, 0, 1.05),    # Kitchen door
        (8, 4, 1.05),    # Dining door
        (0, 6, 1.05),    # Bathroom 1 door
        (2, 9, 1.05),    # Staircase door
        # First floor doors
        (3, 13, 4.05),   # Master bedroom door
        (9, 13, 4.05),   # Bedroom 2 door
        (13.5, 13, 4.05), # Bedroom 3 door
        (1.5, 18, 4.05), # Bathroom 2 door
    ]
    
    for pos in door_positions:
        door_parts = create_realistic_door(pos)
        doors.extend(door_parts)
    
    # Create windows
    windows = []
    window_positions = [
        # Ground floor windows
        (4, 0, 1.5),     # Living room window 1
        (12, 0, 1.5),    # Kitchen window
        (12, 4, 1.5),    # Dining window
        # First floor windows
        (3, 13, 4.5),    # Master bedroom window
        (9, 13, 4.5),    # Bedroom 2 window
        (13.5, 13, 4.5), # Bedroom 3 window
        (7.5, 18, 4.5),  # Family hall window
    ]
    
    for pos in window_positions:
        window_parts = create_realistic_window(pos)
        windows.extend(window_parts)
    
    # Create realistic roof for duplex
    roof = create_realistic_roof(house_width, house_length, wall_height + 3)
    
    # Add furniture based on user preferences
    furniture_objects = []
    
    if 'beds' in furniture_list:
        # Add beds to bedrooms (first floor)
        bed_positions = [
            (3, 15, 3.3),    # Master bedroom
            (9, 15, 3.3),    # Bedroom 2
            (13.5, 15, 3.3), # Bedroom 3
        ]
        
        for pos in bed_positions:
            bed_parts = create_realistic_bed(pos, "double")
            furniture_objects.extend(bed_parts)
    
    if 'sofa' in furniture_list:
        # Add sofa to living room (ground floor)
        sofa_parts = create_realistic_sofa((4, 3, 0.4))
        furniture_objects.extend(sofa_parts)
    
    if 'dining_table' in furniture_list:
        # Add dining table (ground floor)
        table_parts = create_realistic_dining_table((11.5, 6, 0.4))
        furniture_objects.extend(table_parts)
    
    if 'kitchen_counter' in furniture_list:
        # Add kitchen counter (ground floor)
        counter_parts = create_realistic_kitchen_counter((11.5, 2, 0.45))
        furniture_objects.extend(counter_parts)
    
    # Setup realistic lighting
    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), math.radians(45), 0)
    
    # Ambient lighting
    bpy.ops.object.light_add(type='AREA', location=(house_width/2, house_length/2, wall_height + 5))
    ambient = bpy.context.active_object
    ambient.data.energy = 2.0
    ambient.data.size = 12.0
    
    # Setup camera
    bpy.ops.object.camera_add(location=(25, -20, 20))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    
    # Set camera as active
    bpy.context.scene.camera = camera
    
    print("✅ Realistic Duplex house created successfully!")
    return len(all_walls) + len(all_floors) + len(doors) + len(windows) + 1 + len(furniture_objects)

# Generate the house
if args.house_type == "3BHK":
    total_objects = create_realistic_3bhk_house()
elif args.house_type == "Duplex":
    total_objects = create_realistic_duplex_house()
else:
    print(f"❌ House type {args.house_type} not implemented yet")
    total_objects = 0

print(f"📦 Total objects created: {total_objects}")

# Export the model with proper scene setup
output_path = bpy.path.abspath(f"//{args.output}")
print(f"💾 Exporting to: {output_path}")

try:
    # Ensure we have a proper scene setup
    if len(bpy.context.scene.objects) == 0:
        print("❌ No objects in scene to export")
        exit(1)
    
    # Make sure all objects are visible and selectable
    for obj in bpy.context.scene.objects:
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    
    # Ensure we have a camera
    if bpy.context.scene.camera is None:
        print("⚠️ No camera found, creating default camera")
        bpy.ops.object.camera_add(location=(10, -10, 10))
        bpy.context.scene.camera = bpy.context.active_object
    
    # Ensure we have proper lighting
    if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
        print("⚠️ No lights found, creating default lighting")
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    
    if args.format == 'glb':
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=False,
            export_cameras=True,
            export_lights=True,
            export_extras=True
        )
    elif args.format == 'obj':
        bpy.ops.export_scene.obj(
            filepath=output_path,
            use_selection=False
        )
    elif args.format == 'fbx':
        bpy.ops.export_scene.fbx(
            filepath=output_path,
            use_selection=False
        )
    
    print(f"✅ Successfully exported to: {output_path}")
    
except Exception as e:
    print(f"❌ Export error: {e}")
    import traceback
    traceback.print_exc()
