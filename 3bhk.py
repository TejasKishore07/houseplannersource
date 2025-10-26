import bpy
import bmesh
from mathutils import Vector
import math
import random

def clear_scene():
    """Clear all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_material(name, color, roughness=0.8, metallic=0.0, texture_type=None):
    """Create a material with given properties and optional textures"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    # Add texture variation for realism
    if texture_type == 'brick':
        # Add brick texture node
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        mapping = nodes.new(type='ShaderNodeMapping')
        brick_tex = nodes.new(type='ShaderNodeTexBrick')
        brick_tex.inputs['Scale'].default_value = 5.0
        brick_tex.inputs['Color1'].default_value = (*color, 1.0)
        brick_tex.inputs['Color2'].default_value = (color[0]*0.8, color[1]*0.8, color[2]*0.8, 1.0)
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], brick_tex.inputs['Vector'])
        links.new(brick_tex.outputs['Color'], bsdf.inputs['Base Color'])
    
    elif texture_type == 'wood':
        # Add wood texture
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (0.1, 2.0, 0.1)
        wood_tex = nodes.new(type='ShaderNodeTexWave')
        wood_tex.inputs['Scale'].default_value = 10.0
        wood_tex.wave_type = 'BANDS'
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], wood_tex.inputs['Vector'])
        links.new(wood_tex.outputs['Color'], bsdf.inputs['Base Color'])
    
    elif texture_type == 'tile':
        # Add tile texture
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        mapping = nodes.new(type='ShaderNodeMapping')
        tile_tex = nodes.new(type='ShaderNodeTexChecker')
        tile_tex.inputs['Scale'].default_value = 8.0
        tile_tex.inputs['Color1'].default_value = (*color, 1.0)
        tile_tex.inputs['Color2'].default_value = (color[0]*0.9, color[1]*0.9, color[2]*0.9, 1.0)
        
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], tile_tex.inputs['Vector'])
        links.new(tile_tex.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Add output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_room_floor(x, y, width, length, name, material_type='tile'):
    """Create individual room floors with different materials"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    floor = bpy.context.active_object
    floor.name = f"Floor_{name}"
    floor.scale = (width, length, 0.05)
    floor.location = (x, y, 0.025)
    return floor

def create_exterior_walls(width, length, height):
    """Create exterior walls with window and door openings"""
    wall_thickness = 0.25
    walls = []
    
    # Front wall with main door opening
    bpy.ops.mesh.primitive_cube_add(size=1)
    front_wall = bpy.context.active_object
    front_wall.name = "Exterior_Front_Wall"
    front_wall.scale = (width, wall_thickness, height)
    front_wall.location = (0, -length/2, height/2)
    walls.append(front_wall)
    
    # Create door opening in front wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    door_opening = bpy.context.active_object
    door_opening.name = "Door_Opening"
    door_opening.scale = (1.0, wall_thickness + 0.1, 2.2)
    door_opening.location = (1.5, -length/2, 1.1)
    
    # Boolean operation to create opening
    modifier = front_wall.modifiers.new(name="DoorCut", type='BOOLEAN')
    modifier.operation = 'DIFFERENCE'
    modifier.object = door_opening
    bpy.context.view_layer.objects.active = front_wall
    bpy.ops.object.modifier_apply(modifier="DoorCut")
    bpy.data.objects.remove(door_opening, do_unlink=True)
    
    # Back wall
    bpy.ops.mesh.primitive_cube_add(size=1)
    back_wall = bpy.context.active_object
    back_wall.name = "Exterior_Back_Wall"
    back_wall.scale = (width, wall_thickness, height)
    back_wall.location = (0, length/2, height/2)
    walls.append(back_wall)
    
    # Left wall with windows
    bpy.ops.mesh.primitive_cube_add(size=1)
    left_wall = bpy.context.active_object
    left_wall.name = "Exterior_Left_Wall"
    left_wall.scale = (wall_thickness, length, height)
    left_wall.location = (-width/2, 0, height/2)
    walls.append(left_wall)
    
    # Right wall with windows
    bpy.ops.mesh.primitive_cube_add(size=1)
    right_wall = bpy.context.active_object
    right_wall.name = "Exterior_Right_Wall"
    right_wall.scale = (wall_thickness, length, height)
    right_wall.location = (width/2, 0, height/2)
    walls.append(right_wall)
    
    return walls

def create_interior_walls(width, length, height):
    """Create detailed interior walls for proper room layout"""
    wall_thickness = 0.12
    walls = []
    
    # Main corridor/hall separator
    bpy.ops.mesh.primitive_cube_add(size=1)
    main_wall = bpy.context.active_object
    main_wall.name = "Main_Corridor_Wall"
    main_wall.scale = (wall_thickness, length * 0.8, height)
    main_wall.location = (width * 0.15, 0, height/2)
    walls.append(main_wall)
    
    # Master bedroom walls
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_wall1 = bpy.context.active_object
    master_wall1.name = "Master_Bedroom_Wall1"
    master_wall1.scale = (width * 0.35, wall_thickness, height)
    master_wall1.location = (-width * 0.175, length * 0.25, height/2)
    walls.append(master_wall1)
    
    # Bedroom 2 separator
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom2_wall = bpy.context.active_object
    bedroom2_wall.name = "Bedroom2_Wall"
    bedroom2_wall.scale = (width * 0.35, wall_thickness, height)
    bedroom2_wall.location = (-width * 0.175, 0, height/2)
    walls.append(bedroom2_wall)
    
    # Bedroom 3 separator  
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom3_wall = bpy.context.active_object
    bedroom3_wall.name = "Bedroom3_Wall"
    bedroom3_wall.scale = (width * 0.35, wall_thickness, height)
    bedroom3_wall.location = (-width * 0.175, -length * 0.25, height/2)
    walls.append(bedroom3_wall)
    
    # Kitchen separator
    bpy.ops.mesh.primitive_cube_add(size=1)
    kitchen_wall = bpy.context.active_object
    kitchen_wall.name = "Kitchen_Wall"
    kitchen_wall.scale = (wall_thickness, length * 0.4, height)
    kitchen_wall.location = (width * 0.35, length * 0.3, height/2)
    walls.append(kitchen_wall)
    
    # Toilet 1 walls (Master bedroom toilet)
    bpy.ops.mesh.primitive_cube_add(size=1)
    toilet1_wall1 = bpy.context.active_object
    toilet1_wall1.name = "Toilet1_Wall1"
    toilet1_wall1.scale = (width * 0.15, wall_thickness, height)
    toilet1_wall1.location = (-width * 0.275, length * 0.35, height/2)
    walls.append(toilet1_wall1)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    toilet1_wall2 = bpy.context.active_object
    toilet1_wall2.name = "Toilet1_Wall2"
    toilet1_wall2.scale = (wall_thickness, length * 0.2, height)
    toilet1_wall2.location = (-width * 0.35, length * 0.4, height/2)
    walls.append(toilet1_wall2)
    
    # Common toilet walls
    bpy.ops.mesh.primitive_cube_add(size=1)
    toilet2_wall1 = bpy.context.active_object
    toilet2_wall1.name = "Toilet2_Wall1"
    toilet2_wall1.scale = (width * 0.15, wall_thickness, height)
    toilet2_wall1.location = (-width * 0.275, -length * 0.35, height/2)
    walls.append(toilet2_wall1)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    toilet2_wall2 = bpy.context.active_object
    toilet2_wall2.name = "Toilet2_Wall2"
    toilet2_wall2.scale = (wall_thickness, length * 0.2, height)
    toilet2_wall2.location = (-width * 0.35, -length * 0.4, height/2)
    walls.append(toilet2_wall2)
    
    return walls

def create_doors():
    """Create realistic doors for all rooms"""
    doors = []
    door_height = 2.0
    door_width = 0.8
    door_thickness = 0.05
    
    # Main entrance door
    bpy.ops.mesh.primitive_cube_add(size=1)
    main_door = bpy.context.active_object
    main_door.name = "Main_Door"
    main_door.scale = (door_width, door_thickness, door_height)
    main_door.location = (1.5, -6, 1.0)
    doors.append(main_door)
    
    # Master bedroom door
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_door = bpy.context.active_object
    master_door.name = "Master_Bedroom_Door"
    master_door.scale = (door_thickness, door_width, door_height)
    master_door.location = (1.5, 3, 1.0)
    doors.append(master_door)
    
    # Bedroom 2 door
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom2_door = bpy.context.active_object
    bedroom2_door.name = "Bedroom2_Door"
    bedroom2_door.scale = (door_thickness, door_width, door_height)
    bedroom2_door.location = (1.5, 0.5, 1.0)
    doors.append(bedroom2_door)
    
    # Bedroom 3 door
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom3_door = bpy.context.active_object
    bedroom3_door.name = "Bedroom3_Door"
    bedroom3_door.scale = (door_thickness, door_width, door_height)
    bedroom3_door.location = (1.5, -2.5, 1.0)
    doors.append(bedroom3_door)
    
    # Kitchen door
    bpy.ops.mesh.primitive_cube_add(size=1)
    kitchen_door = bpy.context.active_object
    kitchen_door.name = "Kitchen_Door"
    kitchen_door.scale = (door_thickness, door_width, door_height)
    kitchen_door.location = (4.2, 2, 1.0)
    doors.append(kitchen_door)
    
    # Toilet doors
    bpy.ops.mesh.primitive_cube_add(size=1)
    toilet1_door = bpy.context.active_object
    toilet1_door.name = "Toilet1_Door"
    toilet1_door.scale = (door_width * 0.7, door_thickness, door_height)
    toilet1_door.location = (-3.5, 4.2, 1.0)
    doors.append(toilet1_door)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    toilet2_door = bpy.context.active_object
    toilet2_door.name = "Toilet2_Door"
    toilet2_door.scale = (door_width * 0.7, door_thickness, door_height)
    toilet2_door.location = (-3.5, -4.2, 1.0)
    doors.append(toilet2_door)
    
    return doors

def create_windows():
    """Create windows with frames"""
    windows = []
    window_height = 1.2
    window_width = 1.5
    window_thickness = 0.08
    
    # Living room windows
    bpy.ops.mesh.primitive_cube_add(size=1)
    living_window = bpy.context.active_object
    living_window.name = "Living_Room_Window"
    living_window.scale = (window_width, window_thickness, window_height)
    living_window.location = (3, 6, 1.5)
    windows.append(living_window)
    
    # Master bedroom window
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_window = bpy.context.active_object
    master_window.name = "Master_Bedroom_Window"
    master_window.scale = (window_thickness, window_width, window_height)
    master_window.location = (-5, 3.5, 1.5)
    windows.append(master_window)
    
    # Bedroom 2 window
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom2_window = bpy.context.active_object
    bedroom2_window.name = "Bedroom2_Window"
    bedroom2_window.scale = (window_thickness, window_width, window_height)
    bedroom2_window.location = (-5, 0.5, 1.5)
    windows.append(bedroom2_window)
    
    # Bedroom 3 window
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedroom3_window = bpy.context.active_object
    bedroom3_window.name = "Bedroom3_Window"
    bedroom3_window.scale = (window_thickness, window_width, window_height)
    bedroom3_window.location = (-5, -2.5, 1.5)
    windows.append(bedroom3_window)
    
    # Kitchen window
    bpy.ops.mesh.primitive_cube_add(size=1)
    kitchen_window = bpy.context.active_object
    kitchen_window.name = "Kitchen_Window"
    kitchen_window.scale = (window_width, window_thickness, window_height)
    kitchen_window.location = (4, 6, 1.5)
    windows.append(kitchen_window)
    
    return windows

def create_detailed_furniture():
    """Create detailed furniture for each room"""
    furniture = []
    
    # LIVING ROOM FURNITURE
    # L-shaped sofa
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_main = bpy.context.active_object
    sofa_main.name = "Sofa_Main"
    sofa_main.scale = (2.5, 0.8, 0.4)
    sofa_main.location = (2.5, 2, 0.2)
    furniture.append(sofa_main)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    sofa_side = bpy.context.active_object
    sofa_side.name = "Sofa_Side"
    sofa_side.scale = (0.8, 1.5, 0.4)
    sofa_side.location = (3.7, 3.2, 0.2)
    furniture.append(sofa_side)
    
    # Coffee table
    bpy.ops.mesh.primitive_cube_add(size=1)
    coffee_table = bpy.context.active_object
    coffee_table.name = "Coffee_Table"
    coffee_table.scale = (1.2, 0.6, 0.15)
    coffee_table.location = (2.5, 3, 0.075)
    furniture.append(coffee_table)
    
    # TV unit
    bpy.ops.mesh.primitive_cube_add(size=1)
    tv_unit = bpy.context.active_object
    tv_unit.name = "TV_Unit"
    tv_unit.scale = (2.0, 0.4, 0.5)
    tv_unit.location = (2.5, 0.5, 0.25)
    furniture.append(tv_unit)
    
    # MASTER BEDROOM FURNITURE
    # King size bed
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_bed = bpy.context.active_object
    master_bed.name = "Master_Bed"
    master_bed.scale = (1.8, 2.0, 0.3)
    master_bed.location = (-3.5, 3.5, 0.15)
    furniture.append(master_bed)
    
    # Wardrobe
    bpy.ops.mesh.primitive_cube_add(size=1)
    master_wardrobe = bpy.context.active_object
    master_wardrobe.name = "Master_Wardrobe"
    master_wardrobe.scale = (2.0, 0.6, 2.2)
    master_wardrobe.location = (-2.5, 4.7, 1.1)
    furniture.append(master_wardrobe)
    
    # Bedside tables
    bpy.ops.mesh.primitive_cube_add(size=1)
    bedside1 = bpy.context.active_object
    bedside1.name = "Bedside_Table1"
    bedside1.scale = (0.4, 0.4, 0.5)
    bedside1.location = (-4.5, 3.5, 0.25)
    furniture.append(bedside1)
    
    # BEDROOM 2 FURNITURE
    # Single bed
    bpy.ops.mesh.primitive_cube_add(size=1)
    bed2 = bpy.context.active_object
    bed2.name = "Bedroom2_Bed"
    bed2.scale = (1.2, 2.0, 0.3)
    bed2.location = (-3.5, 0.5, 0.15)
    furniture.append(bed2)
    
    # Study table
    bpy.ops.mesh.primitive_cube_add(size=1)
    study_table = bpy.context.active_object
    study_table.name = "Study_Table"
    study_table.scale = (1.2, 0.6, 0.3)
    study_table.location = (-2.5, 1, 0.15)
    furniture.append(study_table)
    
    # Chair
    bpy.ops.mesh.primitive_cube_add(size=1)
    chair = bpy.context.active_object
    chair.name = "Study_Chair"
    chair.scale = (0.4, 0.4, 0.4)
    chair.location = (-2.5, 0.5, 0.2)
    furniture.append(chair)
    
    # BEDROOM 3 FURNITURE
    # Single bed
    bpy.ops.mesh.primitive_cube_add(size=1)
    bed3 = bpy.context.active_object
    bed3.name = "Bedroom3_Bed"
    bed3.scale = (1.2, 2.0, 0.3)
    bed3.location = (-3.5, -2.5, 0.15)
    furniture.append(bed3)
    
    # KITCHEN FURNITURE
    # Kitchen counter L-shape
    bpy.ops.mesh.primitive_cube_add(size=1)
    kitchen_counter1 = bpy.context.active_object
    kitchen_counter1.name = "Kitchen_Counter1"
    kitchen_counter1.scale = (2.5, 0.6, 0.45)
    kitchen_counter1.location = (3.5, 4.7, 0.225)
    furniture.append(kitchen_counter1)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    kitchen_counter2 = bpy.context.active_object
    kitchen_counter2.name = "Kitchen_Counter2"
    kitchen_counter2.scale = (0.6, 1.5, 0.45)
    kitchen_counter2.location = (4.7, 3.5, 0.225)
    furniture.append(kitchen_counter2)
    
    # Refrigerator
    bpy.ops.mesh.primitive_cube_add(size=1)
    fridge = bpy.context.active_object
    fridge.name = "Refrigerator"
    fridge.scale = (0.6, 0.6, 1.8)
    fridge.location = (2.5, 4.7, 0.9)
    furniture.append(fridge)
    
    # Dining table
    bpy.ops.mesh.primitive_cube_add(size=1)
    dining_table = bpy.context.active_object
    dining_table.name = "Dining_Table"
    dining_table.scale = (1.2, 0.8, 0.3)
    dining_table.location = (3.5, 2.5, 0.15)
    furniture.append(dining_table)
    
    return furniture

def create_bathroom_fixtures():
    """Create toilets, sinks, and other bathroom fixtures"""
    fixtures = []
    
    # TOILET 1 (Master bedroom toilet)
    # Toilet seat
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4)
    toilet1 = bpy.context.active_object
    toilet1.name = "Toilet1_Seat"
    toilet1.location = (-4, 4.5, 0.2)
    fixtures.append(toilet1)
    
    # Wash basin
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.1)
    basin1 = bpy.context.active_object
    basin1.name = "Toilet1_Basin"
    basin1.location = (-3, 4.5, 0.8)
    fixtures.append(basin1)
    
    # Shower area
    bpy.ops.mesh.primitive_cube_add(size=1)
    shower1 = bpy.context.active_object
    shower1.name = "Toilet1_Shower"
    shower1.scale = (0.8, 0.8, 0.05)
    shower1.location = (-4, 5.2, 0.025)
    fixtures.append(shower1)
    
    # TOILET 2 (Common toilet)
    # Toilet seat
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4)
    toilet2 = bpy.context.active_object
    toilet2.name = "Toilet2_Seat"
    toilet2.location = (-4, -4.5, 0.2)
    fixtures.append(toilet2)
    
    # Wash basin
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.1)
    basin2 = bpy.context.active_object
    basin2.name = "Toilet2_Basin"
    basin2.location = (-3, -4.5, 0.8)
    fixtures.append(basin2)
    
    # Shower area
    bpy.ops.mesh.primitive_cube_add(size=1)
    shower2 = bpy.context.active_object
    shower2.name = "Toilet2_Shower"
    shower2.scale = (0.8, 0.8, 0.05)
    shower2.location = (-4, -5.2, 0.025)
    fixtures.append(shower2)
    
    return fixtures

def create_room_floors():
    """Create different floor materials for different rooms"""
    floors = []
    
    # Living room floor (marble)
    living_floor = create_room_floor(2.8, 1.5, 3.6, 5, "Living_Room", "tile")
    floors.append(living_floor)
    
    # Master bedroom floor (wood)
    master_floor = create_room_floor(-3, 3.8, 3, 2.4, "Master_Bedroom", "wood")
    floors.append(master_floor)
    
    # Bedroom 2 floor (wood)
    bedroom2_floor = create_room_floor(-3, 0.5, 3, 2, "Bedroom2", "wood")
    floors.append(bedroom2_floor)
    
    # Bedroom 3 floor (wood)
    bedroom3_floor = create_room_floor(-3, -2.5, 3, 2, "Bedroom3", "wood")
    floors.append(bedroom3_floor)
    
    # Kitchen floor (tile)
    kitchen_floor = create_room_floor(4, 4, 2, 4, "Kitchen", "tile")
    floors.append(kitchen_floor)
    
    # Corridor floor (tile)
    corridor_floor = create_room_floor(0.7, 0, 1.4, 10, "Corridor", "tile")
    floors.append(corridor_floor)
    
    # Toilet floors (ceramic tile)
    toilet1_floor = create_room_floor(-3.7, 4.7, 1.4, 1.6, "Toilet1", "tile")
    floors.append(toilet1_floor)
    
    toilet2_floor = create_room_floor(-3.7, -4.7, 1.4, 1.6, "Toilet2", "tile")
    floors.append(toilet2_floor)
    
    return floors

def apply_realistic_materials():
    """Apply realistic materials to all objects"""
    # Create material library
    materials = {
        'wall_exterior': create_material("Exterior_Wall", (0.85, 0.82, 0.75), 0.7, 0.0, 'brick'),
        'wall_interior': create_material("Interior_Wall", (0.95, 0.94, 0.90), 0.8),
        'floor_wood': create_material("Wood_Floor", (0.6, 0.4, 0.2), 0.3, 0.0, 'wood'),
        'floor_tile': create_material("Tile_Floor", (0.9, 0.9, 0.85), 0.1, 0.0, 'tile'),
        'door': create_material("Door", (0.4, 0.25, 0.15), 0.4, 0.0, 'wood'),
        'window_frame': create_material("Window_Frame", (0.3, 0.3, 0.3), 0.2, 0.8),
        'window_glass': create_material("Glass", (0.8, 0.9, 1.0), 0.0, 0.0),
        'furniture_wood': create_material("Furniture_Wood", (0.5, 0.3, 0.2), 0.5, 0.0, 'wood'),
        'furniture_fabric': create_material("Fabric", (0.2, 0.3, 0.6), 0.9),
        'metal': create_material("Metal", (0.7, 0.7, 0.7), 0.2, 0.9),
        'ceramic': create_material("Ceramic", (1.0, 1.0, 1.0), 0.1),
        'marble': create_material("Marble", (0.9, 0.9, 0.9), 0.1)
    }
    
    # Apply materials based on object names
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if 'Exterior' in obj.name and 'Wall' in obj.name:
                obj.data.materials.append(materials['wall_exterior'])
            elif 'Wall' in obj.name:
                obj.data.materials.append(materials['wall_interior'])
            elif 'Floor' in obj.name:
                if 'Living_Room' in obj.name or 'Kitchen' in obj.name or 'Toilet' in obj.name or 'Corridor' in obj.name:
                    if 'Living_Room' in obj.name:
                        obj.data.materials.append(materials['marble'])
                    else:
                        obj.data.materials.append(materials['floor_tile'])
                else:
                    obj.data.materials.append(materials['floor_wood'])
            elif 'Door' in obj.name:
                obj.data.materials.append(materials['door'])
            elif 'Window' in obj.name:
                obj.data.materials.append(materials['window_frame'])
            elif 'Bed' in obj.name or 'Table' in obj.name or 'Counter' in obj.name or 'Wardrobe' in obj.name:
                obj.data.materials.append(materials['furniture_wood'])
            elif 'Sofa' in obj.name or 'Chair' in obj.name:
                obj.data.materials.append(materials['furniture_fabric'])
            elif 'Toilet' in obj.name and 'Seat' in obj.name:
                obj.data.materials.append(materials['ceramic'])
            elif 'Basin' in obj.name:
                obj.data.materials.append(materials['ceramic'])
            elif 'Shower' in obj.name:
                obj.data.materials.append(materials['floor_tile'])
            elif 'Refrigerator' in obj.name:
                obj.data.materials.append(materials['metal'])
            else:
                obj.data.materials.append(materials['furniture_wood'])

def create_lighting_system():
    """Create realistic lighting for each room"""
    lights = []
    
    # Natural sunlight from windows
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
    sun = bpy.context.active_object
    sun.name = "Sun_Light"
    sun.data.energy = 2.0
    sun.rotation_euler = (0.5, 0.3, 0.8)
    lights.append(sun)
    
    # Living room ceiling light
    bpy.ops.object.light_add(type='AREA', location=(2.5, 2, 2.8))
    living_light = bpy.context.active_object
    living_light.name = "Living_Room_Light"
    living_light.data.energy = 80
    living_light.data.size = 1.5
    living_light.data.color = (1.0, 0.95, 0.8)  # Warm white
    lights.append(living_light)
    
    # Master bedroom light
    bpy.ops.object.light_add(type='AREA', location=(-3, 3.5, 2.8))
    master_light = bpy.context.active_object
    master_light.name = "Master_Bedroom_Light"
    master_light.data.energy = 60
    master_light.data.size = 1.0
    master_light.data.color = (1.0, 0.9, 0.7)  # Warmer for bedroom
    lights.append(master_light)
    
    # Bedroom 2 light
    bpy.ops.object.light_add(type='AREA', location=(-3, 0.5, 2.8))
    bedroom2_light = bpy.context.active_object
    bedroom2_light.name = "Bedroom2_Light"
    bedroom2_light.data.energy = 50
    bedroom2_light.data.size = 0.8
    lights.append(bedroom2_light)
    
    # Bedroom 3 light
    bpy.ops.object.light_add(type='AREA', location=(-3, -2.5, 2.8))
    bedroom3_light = bpy.context.active_object
    bedroom3_light.name = "Bedroom3_Light"
    bedroom3_light.data.energy = 50
    bedroom3_light.data.size = 0.8
    lights.append(bedroom3_light)
    
    # Kitchen light
    bpy.ops.object.light_add(type='AREA', location=(4, 4, 2.8))
    kitchen_light = bpy.context.active_object
    kitchen_light.name = "Kitchen_Light"
    kitchen_light.data.energy = 70
    kitchen_light.data.size = 1.2
    kitchen_light.data.color = (1.0, 1.0, 1.0)  # Bright white for kitchen
    lights.append(kitchen_light)
    
    # Corridor lighting
    bpy.ops.object.light_add(type='AREA', location=(1, 0, 2.8))
    corridor_light = bpy.context.active_object
    corridor_light.name = "Corridor_Light"
    corridor_light.data.energy = 40
    corridor_light.data.size = 0.6
    lights.append(corridor_light)
    
    # Toilet lights
    bpy.ops.object.light_add(type='POINT', location=(-3.5, 4.5, 2.5))
    toilet1_light = bpy.context.active_object
    toilet1_light.name = "Toilet1_Light"
    toilet1_light.data.energy = 30
    lights.append(toilet1_light)
    
    bpy.ops.object.light_add(type='POINT', location=(-3.5, -4.5, 2.5))
    toilet2_light = bpy.context.active_object
    toilet2_light.name = "Toilet2_Light"
    toilet2_light.data.energy = 30
    lights.append(toilet2_light)
    
    return lights

def setup_camera_system():
    """Setup multiple camera views"""
    cameras = []
    
    # Main overview camera (top-down angled view)
    bpy.ops.object.camera_add(location=(8, -10, 12))
    main_camera = bpy.context.active_object
    main_camera.name = "Overview_Camera"
    main_camera.rotation_euler = (math.radians(50), 0, math.radians(35))
    cameras.append(main_camera)
    
    # Interior view camera
    bpy.ops.object.camera_add(location=(0, -3, 1.7))
    interior_camera = bpy.context.active_object
    interior_camera.name = "Interior_Camera"
    interior_camera.rotation_euler = (math.radians(90), 0, math.radians(90))
    cameras.append(interior_camera)
    
    # Set main camera as active
    bpy.context.scene.camera = main_camera
    
    return cameras

def add_architectural_details():
    """Add architectural details for realism"""
    details = []
    
    # Baseboards along walls
    baseboard_height = 0.1
    baseboard_depth = 0.05
    
    # Door frames
    for obj in bpy.data.objects:
        if 'Door' in obj.name and obj.type == 'MESH':
            # Create door frame
            bpy.ops.mesh.primitive_cube_add(size=1)
            frame = bpy.context.active_object
            frame.name = f"Door_Frame_{obj.name}"
            frame.scale = (obj.scale.x + 0.1, obj.scale.y + 0.05, obj.scale.z + 0.1)
            frame.location = obj.location
            frame.rotation_euler = obj.rotation_euler
            details.append(frame)
    
    # Window sills
    for obj in bpy.data.objects:
        if 'Window' in obj.name and obj.type == 'MESH':
            # Create window sill
            bpy.ops.mesh.primitive_cube_add(size=1)
            sill = bpy.context.active_object
            sill.name = f"Window_Sill_{obj.name}"
            sill.scale = (obj.scale.x + 0.2, obj.scale.y + 0.1, 0.05)
            sill_loc = list(obj.location)
            sill_loc[2] = obj.location[2] - obj.scale.z/2 - 0.1
            sill.location = sill_loc
            details.append(sill)
    
    return details

def create_exterior_elements():
    """Create exterior elements like balcony, entrance steps"""
    exterior = []
    
    # Main entrance steps
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1)
        step = bpy.context.active_object
        step.name = f"Entrance_Step_{i+1}"
        step.scale = (2.0, 0.3, 0.15)
        step.location = (1.5, -6.5 - (i * 0.3), (i * 0.15) + 0.075)
        exterior.append(step)
    
    # Front porch
    bpy.ops.mesh.primitive_cube_add(size=1)
    porch = bpy.context.active_object
    porch.name = "Front_Porch"
    porch.scale = (3.0, 1.5, 0.1)
    porch.location = (1.5, -6.8, 0.05)
    exterior.append(porch)
    
    # Balcony for master bedroom
    bpy.ops.mesh.primitive_cube_add(size=1)
    balcony = bpy.context.active_object
    balcony.name = "Master_Balcony"
    balcony.scale = (2.0, 0.8, 0.05)
    balcony.location = (-3.5, 5.8, 0.025)
    exterior.append(balcony)
    
    # Balcony railing
    bpy.ops.mesh.primitive_cube_add(size=1)
    railing = bpy.context.active_object
    railing.name = "Balcony_Railing"
    railing.scale = (2.0, 0.05, 0.8)
    railing.location = (-3.5, 6.2, 0.4)
    exterior.append(railing)
    
    return exterior

def main():
    """Main function to create the realistic 3BHK house"""
    print("Creating realistic 3BHK house model...")
    
    # Clear existing scene
    clear_scene()
    
    # House dimensions (in meters)
    house_width = 10
    house_length = 12
    house_height = 3
    
    print("Building structure...")
    # Create main structure (no ceiling for open-top view)
    exterior_walls = create_exterior_walls(house_width, house_length, house_height)
    interior_walls = create_interior_walls(house_width, house_length, house_height)
    
    print("Adding floors...")
    # Create room-specific floors
    floors = create_room_floors()
    
    print("Installing doors and windows...")
    # Add doors and windows
    doors = create_doors()
    windows = create_windows()
    
    print("Furnishing rooms...")
    # Add detailed furniture
    furniture = create_detailed_furniture()
    
    print("Installing bathroom fixtures...")
    # Add bathroom fixtures
    bathroom_fixtures = create_bathroom_fixtures()
    
    print("Adding architectural details...")
    # Add architectural details
    details = add_architectural_details()
    
    print("Creating exterior elements...")
    # Add exterior elements
    exterior = create_exterior_elements()
    
    print("Applying materials...")
    # Apply realistic materials
    apply_realistic_materials()
    
    print("Setting up lighting...")
    # Setup lighting
    lights = create_lighting_system()
    
    print("Configuring cameras...")
    # Setup cameras
    cameras = setup_camera_system()
    
    # Configure render settings for realism
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'  # Use Cycles for realistic rendering
    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    
    # Set viewport shading to Material Preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL_PREVIEW'
                    space.shading.use_scene_lights = True
                    break
    
    print("✅ Realistic 3BHK House model created successfully!")
    print("\n🏠 HOUSE LAYOUT:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📍 ROOMS INCLUDED:")
    print("  🛏️  Master Bedroom (with attached toilet)")
    print("  🛏️  Bedroom 2")
    print("  🛏️  Bedroom 3") 
    print("  🛋️  Living Room/Hall")
    print("  🍳  Kitchen")
    print("  🚽  Master Toilet (attached)")
    print("  🚽  Common Toilet")
    print("  🚪  Corridor/Passage")
    print("\n🪟 FEATURES:")
    print("  ✓ Realistic room proportions")
    print("  ✓ Proper door and window placement")
    print("  ✓ Complete furniture sets")
    print("  ✓ Bathroom fixtures (toilets, basins, showers)")
    print("  ✓ Different floor materials (wood, marble, tiles)")
    print("  ✓ Realistic lighting system")
    print("  ✓ Architectural details (door frames, window sills)")
    print("  ✓ Exterior elements (porch, steps, balcony)")
    print("  ✓ Open-top view for interior visualization")
    print("\n🎮 CONTROLS:")
    print("  • Middle Mouse: Rotate view")
    print("  • Scroll Wheel: Zoom in/out")
    print("  • Shift+Middle Mouse: Pan view")
    print("  • Numpad 0: Camera view")
    print("  • Tab: Edit mode")
    print("\n🎨 RENDERING:")
    print("  • Engine: Cycles (realistic)")
    print("  • Resolution: 1920x1080")
    print("  • Samples: 128")
    print("  • Press F12 to render")

# Run the script
if __name__ == "__main__":
    main()