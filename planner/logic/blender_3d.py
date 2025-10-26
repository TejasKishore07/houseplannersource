"""
Blender 3D Model Generation for Smart House Planner
"""

import os
import json

# Try to import Blender modules, but provide fallback if not available
try:
    import bpy
    import bmesh
    from mathutils import Vector
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    print("Blender Python API not available. 3D model generation will be simulated.")

def clear_scene():
    """Clear the current Blender scene"""
    if not BLENDER_AVAILABLE:
        return
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_floor_plan(land_cents, house_type, room_config):
    """Create a 3D floor plan based on land area and house specifications"""
    if not BLENDER_AVAILABLE:
        # Return simulated dimensions
        sqft = land_cents * 435.6
        if sqft <= 1000:
            return 30, 35  # Small house
        elif sqft <= 2000:
            return 40, 50  # Medium house
        else:
            return 50, 70  # Large house
    
    # Calculate dimensions based on land area
    sqft = land_cents * 435.6
    if sqft <= 1000:
        width, length = 30, 35  # Small house
    elif sqft <= 2000:
        width, length = 40, 50  # Medium house
    else:
        width, length = 50, 70  # Large house
    
    # Create ground plane
    bpy.ops.mesh.primitive_plane_add(size=1)
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.scale = (width, length, 1)
    ground.location = (0, 0, 0)
    
    # Create walls based on house type
    if house_type == "Single Floor House":
        create_single_floor_walls(width, length, room_config)
    elif house_type == "Duplex":
        create_duplex_walls(width, length, room_config)
    else:  # Villa
        create_villa_walls(width, length, room_config)
    
    return width, length

def create_single_floor_walls(width, length, room_config):
    """Create walls for single floor house"""
    if not BLENDER_AVAILABLE:
        return
    
    wall_height = 10
    
    # Create exterior walls
    wall_positions = [
        ((width/2, 0, wall_height/2), (width, 0.2, wall_height)),      # North wall
        ((-width/2, 0, wall_height/2), (width, 0.2, wall_height)),     # South wall
        ((0, length/2, wall_height/2), (0.2, length, wall_height)),    # East wall
        ((0, -length/2, wall_height/2), (0.2, length, wall_height)),   # West wall
    ]
    
    for pos, scale in wall_positions:
        bpy.ops.mesh.primitive_cube_add(location=pos)
        wall = bpy.context.active_object
        wall.name = "Wall"
        wall.scale = scale
        wall.data.name = "Wall"
    
    # Create interior walls based on room configuration
    create_interior_walls(width, length, wall_height, room_config)

def create_duplex_walls(width, length, room_config):
    """Create walls for duplex house"""
    if not BLENDER_AVAILABLE:
        return
    
    wall_height = 12
    
    # Create ground floor walls
    create_single_floor_walls(width, length, room_config)
    
    # Create second floor
    bpy.ops.mesh.primitive_plane_add(location=(0, 0, 10))
    second_floor = bpy.context.active_object
    second_floor.name = "SecondFloor"
    second_floor.scale = (width, length, 1)
    
    # Create second floor walls
    wall_height_2nd = 10
    wall_positions_2nd = [
        ((width/2, 0, 15), (width, 0.2, wall_height_2nd)),
        ((-width/2, 0, 15), (width, 0.2, wall_height_2nd)),
        ((0, length/2, 15), (0.2, length, wall_height_2nd)),
        ((0, -length/2, 15), (0.2, length, wall_height_2nd)),
    ]
    
    for pos, scale in wall_positions_2nd:
        bpy.ops.mesh.primitive_cube_add(location=pos)
        wall = bpy.context.active_object
        wall.name = "Wall_2nd"
        wall.scale = scale
        wall.data.name = "Wall_2nd"

def create_villa_walls(width, length, room_config):
    """Create walls for villa house"""
    if not BLENDER_AVAILABLE:
        return
    
    wall_height = 15
    
    # Create main structure
    create_single_floor_walls(width, length, room_config)
    
    # Add luxury features - columns at entrance
    column_positions = [
        (width/2 - 5, length/2 - 2, 7.5),
        (width/2 - 5, length/2 + 2, 7.5),
        (-width/2 + 5, length/2 - 2, 7.5),
        (-width/2 + 5, length/2 + 2, 7.5),
    ]
    
    for pos in column_positions:
        bpy.ops.mesh.primitive_cylinder_add(location=pos)
        column = bpy.context.active_object
        column.name = "Column"
        column.scale = (0.5, 0.5, 15)
        column.data.name = "Column"

def create_interior_walls(width, length, wall_height, room_config):
    """Create interior walls based on room configuration"""
    if not BLENDER_AVAILABLE:
        return
    
    bedrooms = room_config.get("Bedrooms", 2)
    
    if bedrooms == 2:
        # Create bedroom wall
        bpy.ops.mesh.primitive_cube_add(location=(0, length/4, wall_height/2))
        wall = bpy.context.active_object
        wall.name = "InteriorWall"
        wall.scale = (width, 0.1, wall_height)
        wall.data.name = "InteriorWall"
    
    elif bedrooms == 3:
        # Create two bedroom walls
        bpy.ops.mesh.primitive_cube_add(location=(0, length/6, wall_height/2))
        wall1 = bpy.context.active_object
        wall1.name = "InteriorWall1"
        wall1.scale = (width, 0.1, wall_height)
        
        bpy.ops.mesh.primitive_cube_add(location=(0, -length/6, wall_height/2))
        wall2 = bpy.context.active_object
        wall2.name = "InteriorWall2"
        wall2.scale = (width, 0.1, wall_height)

def create_roof(house_type, width, length):
    """Create roof based on house type"""
    if not BLENDER_AVAILABLE:
        return
    
    if house_type == "Single Floor House":
        # Flat roof
        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 10))
        roof = bpy.context.active_object
        roof.name = "Roof"
        roof.scale = (width, length, 1)
        roof.data.name = "Roof"
    
    elif house_type == "Duplex":
        # Sloped roof for duplex
        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 22))
        roof = bpy.context.active_object
        roof.name = "Roof"
        roof.scale = (width, length, 1)
        roof.rotation_euler = (0.3, 0, 0)  # Sloped roof
        roof.data.name = "Roof"
    
    else:  # Villa
        # Complex roof with multiple slopes
        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 17))
        roof = bpy.context.active_object
        roof.name = "Roof"
        roof.scale = (width, length, 1)
        roof.rotation_euler = (0.2, 0, 0)
        roof.data.name = "Roof"

def create_windows_and_doors(orientation, house_type, width, length):
    """Create windows and doors based on orientation and house type"""
    if not BLENDER_AVAILABLE:
        return
    
    # Create main entrance door
    bpy.ops.mesh.primitive_cube_add(location=(0, -length/2 + 1, 5))
    door = bpy.context.active_object
    door.name = "MainDoor"
    door.scale = (2, 0.1, 10)
    door.data.name = "MainDoor"
    
    # Create windows based on orientation
    window_positions = []
    if orientation == "North":
        window_positions = [
            (width/3, length/2 - 0.5, 5),
            (-width/3, length/2 - 0.5, 5),
        ]
    elif orientation == "South":
        window_positions = [
            (width/3, -length/2 + 0.5, 5),
            (-width/3, -length/2 + 0.5, 5),
        ]
    else:  # East/West
        window_positions = [
            (width/2 - 0.5, length/3, 5),
            (width/2 - 0.5, -length/3, 5),
            (-width/2 + 0.5, length/3, 5),
            (-width/2 + 0.5, -length/3, 5),
        ]
    
    for i, pos in enumerate(window_positions):
        bpy.ops.mesh.primitive_cube_add(location=pos)
        window = bpy.context.active_object
        window.name = f"Window_{i+1}"
        window.scale = (1.5, 0.1, 1.5)
        window.data.name = f"Window_{i+1}"

def add_materials():
    """Add basic materials to the 3D model"""
    if not BLENDER_AVAILABLE:
        return
    
    # Create materials
    materials = {
        "Wall": (0.8, 0.8, 0.8, 1),      # Light gray
        "Roof": (0.3, 0.3, 0.3, 1),      # Dark gray
        "Ground": (0.2, 0.5, 0.2, 1),    # Green
        "Door": (0.4, 0.2, 0.1, 1),      # Brown
        "Window": (0.7, 0.9, 1.0, 1),    # Light blue
    }
    
    for mat_name, color in materials.items():
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color

def setup_scene_lighting():
    """Set up lighting for the 3D scene"""
    if not BLENDER_AVAILABLE:
        return
    
    # Add sun light
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5
    
    # Add camera
    bpy.ops.object.camera_add(location=(20, -20, 15))
    camera = bpy.context.active_object
    camera.rotation_euler = (0.7, 0, 0.8)
    
    # Set camera as active
    bpy.context.scene.camera = camera

def generate_3d_house(land_cents, house_type, orientation, room_config, **kwargs):
    """
    Generate a 3D house model with detailed specifications
    
    Args:
        land_cents: Land area in cents
        house_type: Type of house (1BHK, 2BHK, 3BHK, 4BHK)
        orientation: Plot orientation (North, South, East, West)
        room_config: Room configuration dictionary
        **kwargs: Additional parameters like kitchen_size, living_room, bathrooms, etc.
    """
    if not BLENDER_AVAILABLE:
        return True, "3D model generation simulated (Blender not available)"
    
    try:
        # Extract additional parameters
        kitchen_size = kwargs.get('kitchen_size', 'medium')
        living_room = kwargs.get('living_room', 'medium')
        bathrooms = kwargs.get('bathrooms', 1)
        balcony = kwargs.get('balcony', 'no')
        parking = kwargs.get('parking', 'no')
        garden = kwargs.get('garden', 'no')
        study_room = kwargs.get('study_room', 'no')
        furniture = kwargs.get('furniture', [])
        
        print(f"🏗️ Generating 3D house: {house_type}, {orientation}")
        print(f"🌱 Land: {land_cents} cents")
        print(f"🍳 Kitchen: {kitchen_size}")
        print(f"🛋️ Living Room: {living_room}")
        print(f"🚿 Bathrooms: {bathrooms}")
        print(f"🌱 Balcony: {balcony}")
        print(f"🚗 Parking: {parking}")
        print(f"🪑 Furniture: {furniture}")
        
        # Clear existing scene
        clear_scene()
        
        # Create floor plan with detailed specifications
        width, length = create_detailed_floor_plan(
            land_cents, house_type, room_config,
            kitchen_size=kitchen_size,
            living_room=living_room,
            bathrooms=bathrooms,
            balcony=balcony,
            parking=parking,
            garden=garden,
            study_room=study_room,
            furniture=furniture
        )
        
        # Create roof
        create_roof(house_type, width, length)
        
        # Create windows and doors
        create_windows_and_doors(orientation, house_type, width, length)
        
        # Add materials
        add_materials()
        
        # Setup lighting
        setup_scene_lighting()
        
        return True, f"3D house generated successfully: {house_type} with {bathrooms} bathrooms"
        
    except Exception as e:
        return False, f"Error generating 3D house: {str(e)}"

def create_detailed_floor_plan(land_cents, house_type, room_config, **kwargs):
    """Create a detailed floor plan with rooms and furniture"""
    if not BLENDER_AVAILABLE:
        # Return simulated dimensions
        sqft = land_cents * 435.6
        if sqft <= 1000:
            return 30, 35  # Small house
        elif sqft <= 2000:
            return 40, 50  # Medium house
        else:
            return 50, 70  # Large house
    
    # Calculate dimensions based on land area and house type
    sqft = land_cents * 435.6
    if house_type == "1BHK":
        width, length = 25, 30
    elif house_type == "2BHK":
        width, length = 35, 40
    elif house_type == "3BHK":
        width, length = 45, 50
    else:  # 4BHK
        width, length = 55, 60
    
    wall_height = 10
    
    # Create ground plane
    bpy.ops.mesh.primitive_plane_add(size=1)
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.scale = (width, length, 1)
    ground.location = (0, 0, 0)
    
    # Create exterior walls
    create_exterior_walls(width, length, wall_height)
    
    # Create interior walls based on house type
    create_detailed_interior_walls(width, length, wall_height, house_type, **kwargs)
    
    # Create furniture
    create_furniture(width, length, house_type, **kwargs)
    
    return width, length

def create_exterior_walls(width, length, wall_height):
    """Create exterior walls"""
    if not BLENDER_AVAILABLE:
        return
    
    wall_positions = [
        ((width/2, 0, wall_height/2), (width, 0.2, wall_height)),      # North wall
        ((-width/2, 0, wall_height/2), (width, 0.2, wall_height)),     # South wall
        ((0, length/2, wall_height/2), (0.2, length, wall_height)),    # East wall
        ((0, -length/2, wall_height/2), (0.2, length, wall_height)),   # West wall
    ]
    
    for pos, scale in wall_positions:
        bpy.ops.mesh.primitive_cube_add(location=pos)
        wall = bpy.context.active_object
        wall.name = "ExteriorWall"
        wall.scale = scale

def create_detailed_interior_walls(width, length, wall_height, house_type, **kwargs):
    """Create interior walls based on house type and specifications"""
    if not BLENDER_AVAILABLE:
        return
    
    if house_type == "1BHK":
        # Simple layout: bedroom + living + kitchen
        bpy.ops.mesh.primitive_cube_add(location=(0, length/4, wall_height/2))
        bedroom_wall = bpy.context.active_object
        bedroom_wall.name = "BedroomWall"
        bedroom_wall.scale = (width, 0.2, wall_height)
        
    elif house_type == "2BHK":
        # Two bedrooms + living + kitchen
        bpy.ops.mesh.primitive_cube_add(location=(0, length/3, wall_height/2))
        bedroom1_wall = bpy.context.active_object
        bedroom1_wall.name = "Bedroom1Wall"
        bedroom1_wall.scale = (width, 0.2, wall_height)
        
        bpy.ops.mesh.primitive_cube_add(location=(0, -length/3, wall_height/2))
        bedroom2_wall = bpy.context.active_object
        bedroom2_wall.name = "Bedroom2Wall"
        bedroom2_wall.scale = (width, 0.2, wall_height)
        
    elif house_type == "3BHK":
        # Three bedrooms + living + kitchen
        bpy.ops.mesh.primitive_cube_add(location=(0, length/2.5, wall_height/2))
        bedroom1_wall = bpy.context.active_object
        bedroom1_wall.name = "Bedroom1Wall"
        bedroom1_wall.scale = (width, 0.2, wall_height)
        
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, wall_height/2))
        bedroom2_wall = bpy.context.active_object
        bedroom2_wall.name = "Bedroom2Wall"
        bedroom2_wall.scale = (width, 0.2, wall_height)
        
        bpy.ops.mesh.primitive_cube_add(location=(0, -length/2.5, wall_height/2))
        bedroom3_wall = bpy.context.active_object
        bedroom3_wall.name = "Bedroom3Wall"
        bedroom3_wall.scale = (width, 0.2, wall_height)

def create_furniture(width, length, house_type, **kwargs):
    """Create furniture based on specifications"""
    if not BLENDER_AVAILABLE:
        return
    
    furniture_list = kwargs.get('furniture', [])
    
    if "beds" in furniture_list:
        # Create beds in bedrooms
        if house_type == "1BHK":
            bpy.ops.mesh.primitive_cube_add(location=(0, length/4, 0.5))
            bed = bpy.context.active_object
            bed.name = "Bed1"
            bed.scale = (1.5, 2, 0.3)
        elif house_type == "2BHK":
            bpy.ops.mesh.primitive_cube_add(location=(0, length/2, 0.5))
            bed1 = bpy.context.active_object
            bed1.name = "Bed1"
            bed1.scale = (1.5, 2, 0.3)
            
            bpy.ops.mesh.primitive_cube_add(location=(0, -length/2, 0.5))
            bed2 = bpy.context.active_object
            bed2.name = "Bed2"
            bed2.scale = (1.5, 2, 0.3)
        elif house_type == "3BHK":
            bpy.ops.mesh.primitive_cube_add(location=(0, length/1.5, 0.5))
            bed1 = bpy.context.active_object
            bed1.name = "Bed1"
            bed1.scale = (1.5, 2, 0.3)
            
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
            bed2 = bpy.context.active_object
            bed2.name = "Bed2"
            bed2.scale = (1.5, 2, 0.3)
            
            bpy.ops.mesh.primitive_cube_add(location=(0, -length/1.5, 0.5))
            bed3 = bpy.context.active_object
            bed3.name = "Bed3"
            bed3.scale = (1.5, 2, 0.3)
    
    if "sofa" in furniture_list:
        # Create sofa in living room
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.4))
        sofa = bpy.context.active_object
        sofa.name = "Sofa"
        sofa.scale = (2.5, 1, 0.4)
    
    if "dining_table" in furniture_list:
        # Create dining table
        bpy.ops.mesh.primitive_cube_add(location=(width/3, 0, 0.8))
        dining_table = bpy.context.active_object
        dining_table.name = "DiningTable"
        dining_table.scale = (1.5, 1, 0.1)
    
    if "kitchen_counter" in furniture_list:
        # Create kitchen counter
        bpy.ops.mesh.primitive_cube_add(location=(-width/3, length/3, 0.9))
        kitchen_counter = bpy.context.active_object
        kitchen_counter.name = "KitchenCounter"
        kitchen_counter.scale = (2, 0.6, 0.1)

def export_model(filepath, format_type="glb"):
    """Export the 3D model"""
    if not BLENDER_AVAILABLE:
        # Create a proper GLB file structure for simulation
        if format_type == "glb":
            # Create a minimal valid GLB file
            import struct
            with open(filepath, 'wb') as f:
                # GLB header (12 bytes)
                f.write(b'glTF')  # Magic
                f.write(struct.pack('<I', 2))  # Version
                f.write(struct.pack('<I', 0))  # Length (will be updated)
                
                # JSON chunk header (8 bytes)
                json_data = '{"asset":{"version":"2.0"},"scene":0,"scenes":[{"nodes":[]}],"nodes":[],"meshes":[]}'
                json_bytes = json_data.encode('utf-8')
                json_length = len(json_bytes)
                f.write(struct.pack('<I', json_length))  # JSON chunk length
                f.write(b'JSON')  # JSON chunk type
                f.write(json_bytes)
                
                # Pad to 4-byte boundary
                padding = (4 - (json_length % 4)) % 4
                f.write(b'\x20' * padding)
                
                # Update total length
                total_length = 12 + 8 + json_length + padding
                f.seek(8)
                f.write(struct.pack('<I', total_length))
        else:
            # For other formats, create a simple text file
            with open(filepath, 'w') as f:
                f.write(f"# Simulated 3D model export ({format_type.upper()})\n")
                f.write(f"# House model data would be exported here\n")
                f.write(f"# Format: {format_type}\n")
        return
    
    if format_type == "glb":
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=False
        )
    elif format_type == "obj":
        bpy.ops.export_scene.obj(
            filepath=filepath,
            use_selection=False
        )
    elif format_type == "fbx":
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=False
        )

def render_preview(filepath):
    """Render a preview image of the 3D model"""
    try:
        if not BLENDER_AVAILABLE:
            # Create a dummy preview image
            with open(filepath, 'w') as f:
                f.write("Simulated preview image data")
            return True, "Preview simulation completed"
        
        bpy.context.scene.render.filepath = filepath
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.ops.render.render(write_still=True)
        return True, "Preview rendered successfully"
    except Exception as e:
        return False, f"Error rendering preview: {str(e)}"
