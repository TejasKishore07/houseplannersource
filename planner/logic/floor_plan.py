"""
Floor plan logic for Smart House Planner
"""

def get_house_type(land_cents):
    """
    Determine house type based on land area in cents
    """
    if land_cents <= 5:
        return "Single Floor House"
    elif land_cents <= 10:
        return "Duplex"
    else:
        return "Villa"

def calculate_room_config(land_cents):
    """
    Calculate room configuration based on land area
    """
    sqft = land_cents * 435.6
    
    if sqft <= 1000:
        return {
            "Bedrooms": 2,
            "Bathrooms": 1,
            "Kitchen": 1,
            "Hall": 1,
            "Parking": "1 compact",
            "Balcony": "Small balcony",
            "Total Area": f"{sqft:.0f} sq ft"
        }
    elif sqft <= 2000:
        return {
            "Bedrooms": 3,
            "Bathrooms": 2,
            "Kitchen": 1,
            "Hall": 1,
            "Parking": "1 car",
            "Balcony": "Medium balcony",
            "Total Area": f"{sqft:.0f} sq ft"
        }
    else:
        return {
            "Bedrooms": 4,
            "Bathrooms": 3,
            "Kitchen": 2,
            "Hall": 2,
            "Parking": "2-car garage",
            "Balcony": "Large balcony + terrace",
            "Total Area": f"{sqft:.0f} sq ft"
        }

def get_floor_plan_suggestions(house_type, land_cents):
    """
    Get floor plan suggestions based on house type and land area
    """
    suggestions = {
        "Single Floor House": [
            "Open concept living area",
            "Efficient space utilization",
            "Natural light optimization",
            "Compact kitchen design"
        ],
        "Duplex": [
            "Split-level design",
            "Private master suite upstairs",
            "Open living area downstairs",
            "Balcony access from bedrooms"
        ],
        "Villa": [
            "Luxury master suite with walk-in closet",
            "Formal dining area",
            "Home office space",
            "Entertainment room",
            "Landscaped garden area"
        ]
    }
    
    return suggestions.get(house_type, ["Standard layout"])
