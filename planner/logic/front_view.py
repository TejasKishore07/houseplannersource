"""
Front elevation design logic for Smart House Planner
"""

def get_front_design(house_type, orientation):
    """
    Generate front elevation design based on house type and orientation
    """
    base = f"{orientation}-facing entry with modern light placement"
    
    if house_type == "Single Floor House":
        return f"Minimalist front with flat roof, linear windows, and {base}."
    elif house_type == "Duplex":
        return f"Contemporary style with glass balconies and {base}."
    else:
        return f"Luxury villa with large glass panels, landscaped porch, and {base}."

def get_modern_design_elements(house_type):
    """
    Get modern design elements based on house type
    """
    elements = {
        "Single Floor House": [
            "Clean geometric lines",
            "Large windows for natural light",
            "Minimalist entrance",
            "Flat roof design",
            "Neutral color palette"
        ],
        "Duplex": [
            "Glass balconies",
            "Split-level facade",
            "Modern materials (glass, steel)",
            "Contemporary entrance",
            "Rooftop terrace access"
        ],
        "Villa": [
            "Grand entrance with columns",
            "Large glass panels",
            "Landscaped front yard",
            "Luxury materials (marble, granite)",
            "Multiple balconies and terraces"
        ]
    }
    
    return elements.get(house_type, ["Standard design elements"])

def get_color_scheme(house_type, orientation):
    """
    Get color scheme recommendations based on house type and orientation
    """
    schemes = {
        "Single Floor House": {
            "North": "Light beige with white accents",
            "South": "Warm gray with cream highlights",
            "East": "Soft white with light blue accents",
            "West": "Warm beige with brown accents"
        },
        "Duplex": {
            "North": "Modern gray with white and black accents",
            "South": "Contemporary white with glass elements",
            "East": "Light gray with blue glass accents",
            "West": "Warm gray with wooden elements"
        },
        "Villa": {
            "North": "Luxury white with gold accents",
            "South": "Elegant beige with stone elements",
            "East": "Modern white with glass and steel",
            "West": "Warm stone with wooden elements"
        }
    }
    
    return schemes.get(house_type, {}).get(orientation, "Neutral color scheme")

def get_landscaping_suggestions(house_type, land_cents):
    """
    Get landscaping suggestions based on house type and land area
    """
    if land_cents <= 5:
        return [
            "Small front garden with low-maintenance plants",
            "Paved driveway",
            "Simple lawn area"
        ]
    elif land_cents <= 10:
        return [
            "Medium-sized garden with flowering plants",
            "Stone pathway to entrance",
            "Small water feature",
            "Outdoor seating area"
        ]
    else:
        return [
            "Extensive landscaping with multiple zones",
            "Large water feature or pool",
            "Outdoor entertainment area",
            "Garden lighting",
            "Multiple seating areas"
        ]
