import bpy
import bmesh
from mathutils import Vector
import math
import random

def clear_scene():
    """Clear all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_advanced_material(name, base_color, roughness=0.8, metallic=0.0, texture_type=None, normal_strength=1.0):
    """Create advanced materials with procedural textures and normal maps"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    # Texture coordinate and mapping nodes
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    
    if texture_type == 'brick_wall':
        # Advanced brick texture with variation
        brick_tex = nodes.new(type='ShaderNodeTexBrick')
        brick_tex.inputs['Scale'].default_value = 8.0
        brick_tex.inputs['Mortar Size'].default_value = 0.02
        brick_tex.inputs['Bias'].default_value = 0.0
        brick_tex.inputs['Color1'].default_value = (*base_color, 1.0)
        brick_tex.inputs['Color2'].default_value = (base_color[0]*0.7, base_color[1]*0.7, base_color[2]*0.7, 1.0)
        brick_tex.inputs['Mortar'].default_value = (0.9, 0.9, 0.85, 1.0)
        
        # Add noise for variation
        noise_tex = nodes.new(type='ShaderNodeTexNoise')
        noise_tex.inputs['Scale'].default_value = 15.0
        noise_tex.inputs['Detail'].default_value = 2.0
        
        color_mix = nodes.new(type='ShaderNodeMix')
        color_mix.data_type = 'RGBA'
        color_mix.blend_type = 'MULTIPLY'
        color_mix.inputs['Fac'].default_value = 0.1
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], brick_tex.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
        links.new(brick_tex.outputs['Color'], color_mix.inputs['Color1'])
        links.new(noise_tex.outputs['Fac'], color_mix.inputs['Color2'])
        links.new(color_mix.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif texture_type == 'wood_floor':
        # Realistic wood texture
        mapping.inputs['Scale'].default_value = (0.1, 2.0, 0.1)
        wood_tex = nodes.new(type='ShaderNodeTexWave')
        wood_tex.inputs['Scale'].default_value = 12.0
        wood_tex.inputs['Distortion'].default_value = 0.5
        wood_tex.inputs['Detail'].default_value = 2.0
        wood_tex.wave_type = 'BANDS'
        wood_tex.rings_direction = 'Z'
        
        # Wood color variation
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.color_ramp.elements[0].color = (base_color[0]*0.6, base_color[1]*0.4, base_color[2]*0.2, 1.0)
        color_ramp.color_ramp.elements[1].color = (base_color[0]*1.2, base_color[1]*0.8, base_color[2]*0.4, 1.0)
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], wood_tex.inputs['Vector'])
        links.new(wood_tex.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif texture_type == 'ceramic_tile':
        # Ceramic tile pattern
        tile_tex = nodes.new(type='ShaderNodeTexChecker')
        tile_tex.inputs['Scale'].default_value = 12.0
        tile_tex.inputs['Color1'].default_value = (*base_color, 1.0)
        tile_tex.inputs['Color2'].default_value = (base_color[0]*0.95, base_color[1]*0.95, base_color[2]*0.95, 1.0)
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        mapping.inputs['Scale'].default_value = (12, 12, 1)
        links.new(mapping.outputs['Vector'], tile_tex.inputs['Vector'])
        links.new(tile_tex.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif texture_type == 'marble':
        # Marble texture with veining
        marble_tex = nodes.new(type='ShaderNodeTexNoise')
        marble_tex.inputs['Scale'].default_value = 8.0
        marble_tex.inputs['Detail'].default_value = 2.0
        marble_tex.inputs['Distortion'].default_value = 0.5
        
        # Marble color mixing
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.color_ramp.elements[0].color = (*base_color, 1.0)
        color_ramp.color_ramp.elements[1].color = (base_color[0]*0.9, base_color[1]*0.9, base_color[2]*0.9, 1.0)
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], marble_tex.inputs['Vector'])
        links.new(marble_tex.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
    elif texture_type == 'glass':
        # Glass material
        bsdf.inputs['Transmission'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.0
        bsdf.inputs['IOR'].default_value = 1.45
        
    elif texture_type == 'metal':
        # Metal material
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.2
    
    # Add output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_wall_with_opening(name, scale, location, opening_pos=None, opening_size=None):
    """Create wall with door/window opening using boolean operations"""
    # Create main wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    wall = bpy.context.active_object
    wall.name = name
    wall.scale = scale
    wall.location = location
    
    # Create opening if specified
    if opening_pos and opening_size:
        bpy.ops.mesh.primitive_cube_add(size=1)
        opening = bpy.context.active_object
        opening.name = f"{name}_Opening"
        opening.scale = opening_size
        opening.location = opening_pos
        
        # Boolean operation
        modifier = wall.modifiers.new(name="Opening", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = opening
        
        # Apply modifier
        bpy.context.view_layer.objects.active = wall
        bpy.ops.object.modifier_apply(modifier="Opening")
        
        # Remove opening object
        bpy.data.objects.remove(opening, do_unlink=True)
    
    return wall

def create_2bhk_structure():
    """Create the main structure of 2BHK house"""
    # House dimensions (realistic proportions)
    house_width = 9.0   # 9 meters width
    house_length = 11.0  # 11 meters length
    wall_height = 3.0    # 3 meters height
    wall_thickness = 0.23  # 230mm standard wall thickness
    
    walls = []
    
    # EXTERIOR WALLS
    # Front wall with main entrance
    front_wall = create_wall_with_opening(
        "Front_Wall", 
        (house_width, wall_thickness, wall_height),
        (0, -house_length/2, wall_height/2),
        (2.0, -house_length/2, 1.0),  # Door opening position
        (0.9, wall_thickness + 0.1, 2.1)  # Door opening size
    )
    walls.append(front_wall)
    
    # Back wall with kitchen window
    back_wall = create_wall_with_opening(
        "Back_Wall",
        (house_width, wall_thickness, wall_height),
        (0, house_length/2, wall_height/2),
        (3.0, house_length/2, 1.5),  # Kitchen window
        (1.5, wall_thickness + 0.1, 1.2)
    )
    walls.append(back_wall)
    
    # Left wall with bedroom windows
    left_wall = create_wall_with_opening(
        "Left_Wall",
        (wall_thickness, house_length, wall_height),
        (-house_width/2, 0, wall_height/2),
        (-house_width/2, 2.5, 1.5),  # Master bedroom window
        (wall_thickness + 0.1, 1.5, 1.2)
    )
    walls.append(left_wall)
    
    # Right wall with living room window
    right_wall = create_wall_with_opening(
        "Right_Wall",
        (wall_thickness, house_length, wall_height),
        (house_width/2, 0, wall_height/2),
        (house_width/2, -1.5, 1.5),  # Living room window
        (wall_thickness + 0.1, 2.0, 1.2)
    )
    walls.append(right_wall)
    
    # INTERIOR WALLS
    # Main partition wall (separating bedrooms from living area)
    main_partition = create_wall_with_opening(
        "Main_Partition_Wall",
        (wall_thickness * 0.7, house_length * 0.75, wall_height),
        (house_width * 0.15, 0.5, wall_height/2)
    )
    walls.append(main_partition)
    
    # Master bedroom separator
    master_separator = create_wall_with_opening(
        "Master_Bedroom_Wall",
        (house_width * 0.35, wall_thickness * 0.7, wall_height),
        (-house_width * 0.175, house_length * 0.2, wall_height/2),
        (-house_width * 0.175, house_length * 0.2 + 0.05, 1.0),  # Door opening
        (0.8, wall_thickness + 0.1, 2.0)
    )
    walls.append(master_separator)
    
    # Second bedroom separator
    bedroom2_separator = create_wall_with_opening(
        "Bedroom2_Wall", 
        (house_width * 0.35, wall_thickness * 0.7, wall_height),
        (-house_width * 0.175, -house_length * 0.15, wall_height/2),
        (-house_width * 0.175, -house_length * 0.15 + 0.05, 1.0),  # Door opening
        (0.8, wall_thickness + 0.1, 2.0)
    )
    walls.append(bedroom2_separator)
    
    # Kitchen partition
    kitchen_wall = create_wall_with_opening(
        "Kitchen_Partition",
        (wall_thickness * 0.7, house_length * 0.4, wall_height),
        (house_width * 0.32, house_length * 0.3, wall_height/2),
        (house_width * 0.32 + 0.05, house_length * 0.25, 1.0),  # Kitchen door
        (wall_thickness + 0.1, 0.8, 2.0)
    )
    walls.append(kitchen_wall)
    
    # TOILET WALLS
    # Master toilet walls
    master_toilet_wall1 = create_wall_with_opening(
        "Master_Toilet_Wall1",
        (house_width * 0.15, wall_thickness * 0.7, wall_height),
        (-house_width * 0.27, house_length * 0.35, wall_height/2),
        (-house_width * 0.25, house_length * 0.35 + 0.05, 1.0),  # Toilet door
        (0.6, wall_thickness + 0.1, 2.0)
    )
    walls.append(master_toilet_wall1)
    
    master_toilet_wall2 = create_wall_with_opening(
        "Master_Toilet_Wall2",
        (wall_thickness * 0.7, house_length * 0.2, wall_height),
        (-house_width * 0.35, house_length * 0.4, wall_height/2)
    )
    walls.append(master_toilet_wall2)
    
    # Common toilet walls
    common_toilet_wall1 = create_wall_with_opening(
        "Common_Toilet_Wall1",
        (house_width * 0.15, wall_thickness * 0.7, wall_height),
        (-house_width * 0.27, -house_length * 0.3, wall_height/2),
        (-house_width * 0.25, -house_length * 0.3 + 0.05, 1.0),  # Toilet door
        (0.6, wall_thickness + 0.1, 2.0)
    )
    walls.append(common_toilet_wall1)
    
    common_toilet_wall2 = create_wall_with_opening(
        "Common_Toilet_Wall2",
        (wall_thickness * 0.7, house_length * 0.18, wall_height),
        (-house_width * 0.35, -house_length * 0.36, wall_height/2)
    )
    walls.append(common_toilet_wall2)
    
    return walls, house_width, house_length, wall_height

def create_realistic_floors():
    """Create detailed floor sections for each room"""
    floors = []
    
    # Living room floor (Premium marble)
    bpy.ops.mesh.primitive_cube_add(size=1)
    living_floor = bpy.context.active_object
    living_floor.name = "Living_Room_Floor"
    living_floor.scale = (4.2, 5.0, 0.05)
    living_floor.location = (2.6, -1.0, 0.025)
    floors.append(living_floor)
    
    # Master bedroom floor (Engineered wood)
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_floor = bpy.context.active_object
    master_floor.name = "Master_Bedroom_Floor"
    master_floor.scale = (3.1, 3.0, 0.05)
    master_floor.location = (-2.7, 3.5, 0.025)
    floors.append(master_floor)
    
    # Second bedroom floor (Laminate wood)
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom2_floor = bpy.context.active_object
    bedroom2_floor.name = "Bedroom2_Floor"
    bedroom2_floor.scale = (3.1, 2.5, 0.05)
    bedroom2_floor.location = (-2.7, -0.75, 0.025)
    floors.append(bedroom2_floor)
    
    # Kitchen floor (Anti-slip ceramic tiles)
    bpy.ops.mesh.primitive_cube_add(size=1)
    kitchen_floor = bpy.context.active_object
    kitchen_floor.name = "Kitchen_Floor"
    kitchen_floor.scale = (2.8, 4.0, 0.05)
    kitchen_floor.location = (3.6, 3.5, 0.025)
    floors.append(kitchen_floor)
    
    # Corridor floor (Vitrified tiles)
    bpy.ops.mesh.primitive_cube_add(size=1)
    corridor_floor = bpy.context.active_object
    corridor_floor.name = "Corridor_Floor"
    corridor_floor.scale = (1.2, 8.0, 0.05)
    corridor_floor.location = (1.35, 0.5, 0.025)
    floors.append(corridor_floor)
    
    # Master toilet floor (Non-slip ceramic)
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_toilet_floor = bpy.context.active_object
    master_toilet_floor.name = "Master_Toilet_Floor"
    master_toilet_floor.scale = (1.3, 2.0, 0.05)
    master_toilet_floor.location = (-3.65, 4.5, 0.025)
    floors.append(master_toilet_floor)
    
    # Common toilet floor
    bpy.ops.mesh.primitive_cube_add(size=1)
    common_toilet_floor = bpy.context.active_object
    common_toilet_floor.name = "Common_Toilet_Floor"
    common_toilet_floor.scale = (1.3, 1.8, 0.05)
    common_toilet_floor.location = (-3.65, -3.6, 0.025)
    floors.append(common_toilet_floor)
    
    return floors

def create_ceiling():
    """Create ceiling with proper height"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    ceiling = bpy.context.active_object
    ceiling.name = "Main_Ceiling"
    ceiling.scale = (9.2, 11.2, 0.1)
    ceiling.location = (0, 0, 3.05)
    return ceiling

def create_premium_doors_windows():
    """Create realistic doors and windows with proper hardware"""
    elements = []
    
    # MAIN ENTRANCE DOOR (Premium wooden door)
    bpy.ops.mesh.primitive_cube_add(size=1)
    main_door = bpy.context.active_object
    main_door.name = "Main_Entrance_Door"
    main_door.scale = (0.9, 0.08, 2.1)
    main_door.location = (2.0, -5.44, 1.05)
    elements.append(main_door)
    
    # Door handle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.15)
    door_handle = bpy.context.active_object
    door_handle.name = "Main_Door_Handle"
    door_handle.rotation_euler = (0, math.radians(90), 0)
    door_handle.location = (2.35, -5.35, 1.0)
    elements.append(door_handle)
    
    # INTERIOR DOORS
    door_positions = [
        ("Master_Bedroom_Door", (-1.75, 2.25, 1.0)),
        ("Bedroom2_Door", (-1.75, -1.1, 1.0)),
        ("Kitchen_Door", (2.9, 2.75, 1.0)),
        ("Master_Toilet_Door", (-3.25, 4.25, 1.0)),
        ("Common_Toilet_Door", (-3.25, -2.95, 1.0))
    ]
    
    for door_name, pos in door_positions:
        bpy.ops.mesh.primitive_cube_add(size=1)
        door = bpy.context.active_object
        door.name = door_name
        if "Toilet" in door_name:
            door.scale = (0.6, 0.06, 2.0)
        else:
            door.scale = (0.8, 0.06, 2.0)
        door.location = pos
        elements.append(door)
        
        # Door handle
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.1)
        handle = bpy.context.active_object
        handle.name = f"{door_name}_Handle"
        handle.rotation_euler = (0, math.radians(90), 0)
        handle_pos = list(pos)
        handle_pos[0] += 0.25
        handle_pos[1] += 0.08
        handle.location = handle_pos
        elements.append(handle)
    
    # WINDOWS WITH FRAMES
    window_data = [
        ("Living_Room_Window", (4.44, -1.5, 1.5), (0.1, 2.0, 1.2)),
        ("Master_Bedroom_Window", (-4.44, 2.5, 1.5), (0.1, 1.5, 1.2)),
        ("Bedroom2_Window", (-4.44, -0.75, 1.5), (0.1, 1.5, 1.2)),
        ("Kitchen_Window", (3.0, 5.44, 1.5), (1.5, 0.1, 1.2))
    ]
    
    for window_name, pos, scale in window_data:
        # Window frame
        bpy.ops.mesh.primitive_cube_add(size=1)
        window_frame = bpy.context.active_object
        window_frame.name = f"{window_name}_Frame"
        window_frame.scale = scale
        window_frame.location = pos
        elements.append(window_frame)
        
        # Window glass (slightly inset)
        bpy.ops.mesh.primitive_cube_add(size=1)
        window_glass = bpy.context.active_object
        window_glass.name = f"{window_name}_Glass"
        glass_scale = list(scale)
        glass_pos = list(pos)
        if scale[0] < scale[1]:  # Vertical window
            glass_scale[0] = scale[0] * 0.3
            glass_scale[1] = scale[1] * 0.9
        else:  # Horizontal window
            glass_scale[0] = scale[0] * 0.9
            glass_scale[1] = scale[1] * 0.3
        glass_scale[2] = scale[2] * 0.9
        window_glass.scale = glass_scale
        window_glass.location = glass_pos
        elements.append(window_glass)
    
    return elements

def create_luxury_furniture():
    """Create high-quality furniture with realistic proportions"""
    furniture = []
    
    # LIVING ROOM FURNITURE SET
    # Premium L-shaped sectional sofa
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_main = bpy.context.active_object
    sofa_main.name = "Sectional_Sofa_Main"
    sofa_main.scale = (2.8, 0.9, 0.45)
    sofa_main.location = (3.2, 0.5, 0.225)
    furniture.append(sofa_main)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_chaise = bpy.context.active_object
    sofa_chaise.name = "Sectional_Sofa_Chaise"
    sofa_chaise.scale = (0.9, 1.6, 0.45)
    sofa_chaise.location = (4.5, 1.7, 0.225)
    furniture.append(sofa_chaise)
    
    # Sofa back cushions
    cushion_positions = [(2.5, 0.5, 0.6), (3.2, 0.5, 0.6), (3.9, 0.5, 0.6), (4.5, 1.2, 0.6)]
    for i, pos in enumerate(cushion_positions):
        bpy.ops.mesh.primitive_cube_add(size=1)
        cushion = bpy.context.active_object
        cushion.name = f"Sofa_Cushion_{i+1}"
        cushion.scale = (0.35, 0.15, 0.25)
        cushion.location = pos
        furniture.append(cushion)
    
    # Premium coffee table with glass top
    bpy.ops.mesh.primitive_cube_add(size=1)
    coffee_table_base = bpy.context.active_object
    coffee_table_base.name = "Coffee_Table_Base"
    coffee_table_base.scale = (1.2, 0.6, 0.12)
    coffee_table_base.location = (3.2, -0.8, 0.06)
    furniture.append(coffee_table_base)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    coffee_table_top = bpy.context.active_object
    coffee_table_top.name = "Coffee_Table_Glass"
    coffee_table_top.scale = (1.4, 0.8, 0.02)
    coffee_table_top.location = (3.2, -0.8, 0.21)
    furniture.append(coffee_table_top)
    
    # Entertainment center
    bpy.ops.mesh.primitive_cube_add(size=1)
    tv_unit = bpy.context.active_object
    tv_unit.name = "Entertainment_Center"
    tv_unit.scale = (2.2, 0.4, 0.6)
    tv_unit.location = (3.2, -2.8, 0.3)
    furniture.append(tv_unit)
    
    # Flat screen TV
    bpy.ops.mesh.primitive_cube_add(size=1)
    tv_screen = bpy.context.active_object
    tv_screen.name = "TV_Screen"
    tv_screen.scale = (1.2, 0.05, 0.7)
    tv_screen.location = (3.2, -2.5, 1.2)
    furniture.append(tv_screen)
    
    # MASTER BEDROOM FURNITURE
    # King size bed with headboard
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_bed_mattress = bpy.context.active_object
    master_bed_mattress.name = "Master_Bed_Mattress"
    master_bed_mattress.scale = (1.8, 2.0, 0.25)
    master_bed_mattress.location = (-3.2, 3.8, 0.125)
    furniture.append(master_bed_mattress)
    
    # Bed headboard
    bpy.ops.mesh.primitive_cube_add(size=1)
    headboard = bpy.context.active_object
    headboard.name = "Master_Bed_Headboard"
    headboard.scale = (1.9, 0.1, 1.2)
    headboard.location = (-3.2, 4.85, 0.6)
    furniture.append(headboard)
    
    # Wardrobe (3-door)
    bpy.ops.mesh.primitive_cube_add(size=1)
    wardrobe = bpy.context.active_object
    wardrobe.name = "Master_Wardrobe"
    wardrobe.scale = (2.2, 0.6, 2.4)
    wardrobe.location = (-1.9, 4.7, 1.2)
    furniture.append(wardrobe)
    
    # Wardrobe handles
    for i in range(3):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.08)
        handle = bpy.context.active_object
        handle.name = f"Wardrobe_Handle_{i+1}"
        handle.rotation_euler = (0, math.radians(90), 0)
        handle.location = (-1.4 + (i * 0.7), 4.4, 1.2)
        furniture.append(handle)
    
    # Bedside tables with drawers
    bedside_positions = [(-4.2, 3.8, 0.3), (-2.2, 3.8, 0.3)]
    for i, pos in enumerate(bedside_positions):
        bpy.ops.mesh.primitive_cube_add(size=1)
        bedside = bpy.context.active_object
        bedside.name = f"Bedside_Table_{i+1}"
        bedside.scale = (0.45, 0.4, 0.6)
        bedside.location = pos
        furniture.append(bedside)
        
        # Table lamps
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3)
        lamp = bpy.context.active_object
        lamp.name = f"Table_Lamp_{i+1}"
        lamp_pos = list(pos)
        lamp_pos[2] = 0.75
        lamp.location = lamp_pos
        furniture.append(lamp)
    
    # BEDROOM 2 FURNITURE
    # Single bed with storage
    bpy.ops.mesh.primitive_cube_add(size=1)
    bed2_mattress = bpy.context.active_object
    bed2_mattress.name = "Bedroom2_Bed_Mattress"
    bed2_mattress.scale = (1.2, 2.0, 0.25)
    bed2_mattress.location = (-3.5, -0.5, 0.125)
    furniture.append(bed2_mattress)
    
    # Study desk with drawers
    bpy.ops.mesh.primitive_cube_add(size=1)
    study_desk = bpy.context.active_object
    study_desk.name = "Study_Desk"
    study_desk.scale = (1.4, 0.7, 0.35)
    study_desk.location = (-2.0, -0.5, 0.175)
    furniture.append(study_desk)
    
    # Office chair
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.08)
    chair_seat = bpy.context.active_object
    chair_seat.name = "Office_Chair_Seat"
    chair_seat.location = (-2.0, 0.0, 0.45)
    furniture.append(chair_seat)
    
    # Chair backrest
    bpy.ops.mesh.primitive_cube_add(size=1)
    chair_back = bpy.context.active_object
    chair_back.name = "Office_Chair_Back"
    chair_back.scale = (0.4, 0.05, 0.5)
    chair_back.location = (-2.0, -0.15, 0.65)
    furniture.append(chair_back)
    
    # KITCHEN FURNITURE
    # Kitchen cabinets (lower)
    bpy.ops.mesh.primitive_cube_add(size=1)
    lower_cabinets = bpy.context.active_object
    lower_cabinets.name = "Kitchen_Lower_Cabinets"
    lower_cabinets.scale = (2.5, 0.6, 0.9)
    lower_cabinets.location = (3.8, 4.8, 0.45)
    furniture.append(lower_cabinets)
    
    # Kitchen cabinets (upper)
    bpy.ops.mesh.primitive_cube_add(size=1)
    upper_cabinets = bpy.context.active_object
    upper_cabinets.name = "Kitchen_Upper_Cabinets"
    upper_cabinets.scale = (2.5, 0.4, 0.7)
    upper_cabinets.location = (3.8, 4.9, 2.3)
    furniture.append(upper_cabinets)
    
    # Kitchen countertop
    bpy.ops.mesh.primitive_cube_add(size=1)
    countertop = bpy.context.active_object
    countertop.name = "Kitchen_Countertop"
    countertop.scale = (2.6, 0.65, 0.05)
    countertop.location = (3.8, 4.8, 0.925)
    furniture.append(countertop)
    
    # Refrigerator
    bpy.ops.mesh.primitive_cube_add(size=1)
    refrigerator = bpy.context.active_object
    refrigerator.name = "Refrigerator"
    refrigerator.scale = (0.6, 0.6, 1.8)
    refrigerator.location = (2.8, 4.8, 0.9)
    furniture.append(refrigerator)
    
    # Stove/Cooktop
    bpy.ops.mesh.primitive_cube_add(size=1)
    stove = bpy.context.active_object
    stove.name = "Kitchen_Stove"
    stove.scale = (0.6, 0.6, 0.1)
    stove.location = (4.2, 4.8, 0.975)
    furniture.append(stove)
    
    # Kitchen sink
    bpy.ops.mesh.primitive_cube_add(size=1)
    sink = bpy.context.active_object
    sink.name = "Kitchen_Sink"
    sink.scale = (0.6, 0.4, 0.15)
    sink.location = (3.4, 4.8, 0.95)
    furniture.append(sink)
    
    # Dining table
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.05)
    dining_table = bpy.context.active_object
    dining_table.name = "Dining_Table"
    dining_table.location = (2.5, 2.5, 0.75)
    furniture.append(dining_table)
    
    # Dining chairs
    chair_positions_dining = [
        (1.8, 2.5, 0.4), (3.2, 2.5, 0.4), (2.5, 1.8, 0.4), (2.5, 3.2, 0.4)
    ]
    for i, pos in enumerate(chair_positions_dining):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.06)
        dining_chair = bpy.context.active_object
        dining_chair.name = f"Dining_Chair_{i+1}"
        dining_chair.location = pos
        furniture.append(dining_chair)
        
        # Chair backrest
        bpy.ops.mesh.primitive_cube_add(size=1)
        chair_back = bpy.context.active_object
        chair_back.name = f"Dining_Chair_Back_{i+1}"
        chair_back.scale = (0.3, 0.03, 0.4)
        back_pos = list(pos)
        back_pos[2] = 0.7
        if i == 0:
            back_pos[1] -= 0.15
        elif i == 1:
            back_pos[1] += 0.15
        elif i == 2:
            back_pos[0] -= 0.15
        else:
            back_pos[0] += 0.15
        chair_back.location = back_pos
        furniture.append(chair_back)
    
    # BATHROOM FIXTURES
    # Master bathroom fixtures
    # Toilet
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4)
    master_toilet = bpy.context.active_object
    master_toilet.name = "Master_Toilet"
    master_toilet.location = (-3.8, 4.0, 0.2)
    furniture.append(master_toilet)
    
    # Wash basin
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.1)
    master_basin = bpy.context.active_object
    master_basin.name = "Master_Wash_Basin"
    master_basin.location = (-3.5, 4.8, 0.85)
    furniture.append(master_basin)
    
    # Shower area
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_shower = bpy.context.active_object
    master_shower.name = "Master_Shower_Area"
    master_shower.scale = (0.9, 0.9, 0.05)
    master_shower.location = (-4.0, 5.0, 0.025)
    furniture.append(master_shower)
    
    # Common bathroom fixtures
    # Toilet
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.4)
    common_toilet = bpy.context.active_object
    common_toilet.name = "Common_Toilet"
    common_toilet.location = (-3.8, -3.8, 0.2)
    furniture.append(common_toilet)
    
    # Wash basin
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.1)
    common_basin = bpy.context.active_object
    common_basin.name = "Common_Wash_Basin"
    common_basin.location = (-3.5, -3.2, 0.85)
    furniture.append(common_basin)
    
    return furniture

def create_bathroom_fixtures():
    """Create detailed bathroom fixtures"""
    fixtures = []
    
    # Master bathroom vanity
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_vanity = bpy.context.active_object
    master_vanity.name = "Master_Bathroom_Vanity"
    master_vanity.scale = (1.0, 0.5, 0.8)
    master_vanity.location = (-3.5, 4.6, 0.4)
    fixtures.append(master_vanity)
    
    # Master bathroom mirror
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_mirror = bpy.context.active_object
    master_mirror.name = "Master_Bathroom_Mirror"
    master_mirror.scale = (0.8, 0.02, 0.6)
    master_mirror.location = (-3.5, 4.4, 1.5)
    fixtures.append(master_mirror)
    
    # Common bathroom vanity
    bpy.ops.mesh.primitive_cube_add(size=1)
    common_vanity = bpy.context.active_object
    common_vanity.name = "Common_Bathroom_Vanity"
    common_vanity.scale = (0.9, 0.45, 0.75)
    common_vanity.location = (-3.5, -3.4, 0.375)
    fixtures.append(common_vanity)
    
    # Common bathroom mirror
    bpy.ops.mesh.primitive_cube_add(size=1)
    common_mirror = bpy.context.active_object
    common_mirror.name = "Common_Bathroom_Mirror"
    common_mirror.scale = (0.7, 0.02, 0.5)
    common_mirror.location = (-3.5, -3.2, 1.4)
    fixtures.append(common_mirror)
    
    return fixtures

def create_lighting():
    """Create realistic lighting setup"""
    lights = []
    
    # Main ceiling lights
    light_positions = [
        ("Living_Room_Light", (3.0, -1.0, 2.8)),
        ("Master_Bedroom_Light", (-2.5, 3.5, 2.8)),
        ("Bedroom2_Light", (-2.5, -0.7, 2.8)),
        ("Kitchen_Light", (3.5, 4.0, 2.8)),
        ("Corridor_Light", (1.2, 0.5, 2.8)),
        ("Master_Toilet_Light", (-3.5, 4.5, 2.8)),
        ("Common_Toilet_Light", (-3.5, -3.6, 2.8))
    ]
    
    for light_name, pos in light_positions:
        bpy.ops.object.light_add(type='AREA', location=pos)
        light = bpy.context.active_object
        light.name = light_name
        light.data.energy = 100
        light.data.size = 0.5
        lights.append(light)
        
        # Light fixture
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=pos)
        fixture = bpy.context.active_object
        fixture.name = f"{light_name}_Fixture"
        fixture_pos = list(pos)
        fixture_pos[2] -= 0.1
        fixture.location = fixture_pos
        lights.append(fixture)
    
    # Add sun lamp for overall lighting
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.name = "Sun_Light"
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(60), 0, math.radians(45))
    lights.append(sun)
    
    return lights

def apply_materials_to_objects():
    """Apply realistic materials to all objects"""
    
    # Create materials
    brick_material = create_advanced_material("Brick_Wall", (0.6, 0.4, 0.3), 0.8, 0.0, 'brick_wall')
    wood_floor_material = create_advanced_material("Wood_Floor", (0.4, 0.25, 0.15), 0.3, 0.0, 'wood_floor')
    ceramic_material = create_advanced_material("Ceramic_Tile", (0.9, 0.9, 0.85), 0.1, 0.0, 'ceramic_tile')
    marble_material = create_advanced_material("Marble_Floor", (0.95, 0.95, 0.9), 0.05, 0.0, 'marble')
    glass_material = create_advanced_material("Glass", (0.8, 0.9, 1.0), 0.0, 0.0, 'glass')
    metal_material = create_advanced_material("Metal", (0.7, 0.7, 0.7), 0.2, 1.0, 'metal')
    wood_material = create_advanced_material("Wood_Furniture", (0.5, 0.3, 0.2), 0.6, 0.0)
    fabric_material = create_advanced_material("Fabric", (0.2, 0.4, 0.7), 0.8, 0.0)
    
    # Apply materials to objects
    material_assignments = {
        # Walls
        'brick_wall': ['Front_Wall', 'Back_Wall', 'Left_Wall', 'Right_Wall', 'Main_Partition_Wall', 
                       'Master_Bedroom_Wall', 'Bedroom2_Wall', 'Kitchen_Partition',
                       'Master_Toilet_Wall1', 'Master_Toilet_Wall2', 'Common_Toilet_Wall1', 'Common_Toilet_Wall2'],
        
        # Floors
        'wood_floor': ['Master_Bedroom_Floor', 'Bedroom2_Floor'],
        'ceramic_tile': ['Kitchen_Floor', 'Corridor_Floor', 'Master_Toilet_Floor', 'Common_Toilet_Floor'],
        'marble': ['Living_Room_Floor'],
        
        # Windows and glass
        'glass': ['Living_Room_Window_Glass', 'Master_Bedroom_Window_Glass', 'Bedroom2_Window_Glass',
                  'Kitchen_Window_Glass', 'Coffee_Table_Glass', 'TV_Screen'],
        
        # Metal fixtures
        'metal': ['Main_Door_Handle', 'Master_Bedroom_Door_Handle', 'Bedroom2_Door_Handle',
                  'Kitchen_Door_Handle', 'Master_Toilet_Door_Handle', 'Common_Toilet_Door_Handle',
                  'Wardrobe_Handle_1', 'Wardrobe_Handle_2', 'Wardrobe_Handle_3', 'Kitchen_Sink', 'Refrigerator'],
        
        # Wood furniture
        'wood_furniture': ['Main_Entrance_Door', 'Master_Bedroom_Door', 'Bedroom2_Door', 'Kitchen_Door',
                          'Master_Toilet_Door', 'Common_Toilet_Door', 'Coffee_Table_Base', 'Entertainment_Center',
                          'Master_Bed_Headboard', 'Master_Wardrobe', 'Bedside_Table_1', 'Bedside_Table_2',
                          'Study_Desk', 'Kitchen_Lower_Cabinets', 'Kitchen_Upper_Cabinets', 'Dining_Table'],
        
        # Fabric
        'fabric': ['Sectional_Sofa_Main', 'Sectional_Sofa_Chaise', 'Master_Bed_Mattress', 'Bedroom2_Bed_Mattress']
    }
    
    materials = {
        'brick_wall': brick_material,
        'wood_floor': wood_floor_material,
        'ceramic_tile': ceramic_material,
        'marble': marble_material,
        'glass': glass_material,
        'metal': metal_material,
        'wood_furniture': wood_material,
        'fabric': fabric_material
    }
    
    # Apply materials
    for material_type, object_names in material_assignments.items():
        material = materials[material_type]
        for obj_name in object_names:
            if obj_name in bpy.data.objects:
                obj = bpy.data.objects[obj_name]
                if obj.data.materials:
                    obj.data.materials[0] = material
                else:
                    obj.data.materials.append(material)

def setup_camera_and_render():
    """Setup camera for optimal view and render settings"""
    
    # Position camera for best overview
    bpy.ops.object.camera_add(location=(15, -15, 8))
    camera = bpy.context.active_object
    camera.name = "House_Camera"
    camera.rotation_euler = (math.radians(55), 0, math.radians(45))
    
    # Set camera as active
    bpy.context.scene.camera = camera
    
    # Render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    
    return camera

def main():
    """Main function to create the complete 2BHK house"""
    print("Starting 2BHK House Generation...")
    
    # Clear existing scene
    clear_scene()
    
    print("Creating house structure...")
    walls, house_width, house_length, wall_height = create_2bhk_structure()
    
    print("Creating floors...")
    floors = create_realistic_floors()
    
    print("Creating ceiling...")
    ceiling = create_ceiling()
    
    print("Creating doors and windows...")
    doors_windows = create_premium_doors_windows()
    
    print("Creating furniture...")
    furniture = create_luxury_furniture()
    
    print("Creating bathroom fixtures...")
    bathroom_fixtures = create_bathroom_fixtures()
    
    print("Creating lighting...")
    lights = create_lighting()
    
    print("Applying materials...")
    apply_materials_to_objects()
    
    print("Setting up camera...")
    camera = setup_camera_and_render()
    
    print("2BHK House generation complete!")
    print(f"Total objects created: {len(bpy.data.objects)}")
    print("Switch to rendered view to see the final result.")

# Execute the main function
if __name__ == "__main__":
    main()