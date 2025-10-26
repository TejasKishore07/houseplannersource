"""
Django views for the Smart House Planner with AI integration
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from datetime import datetime
from .logic.floor_plan import get_house_type, calculate_room_config
from .logic.front_view import get_front_design, get_color_scheme, get_modern_design_elements
from .logic.blender_3d import generate_3d_house
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Optional imports for full planning; guarded to allow running without them
try:
    from automated_house_planner import AutomatedHousePlanner
except Exception:
    AutomatedHousePlanner = None
try:
    from house_planning_agent import HousePlanningAgent
except Exception:
    HousePlanningAgent = None

# Initialize the automated house planner only if available
planner = None
if AutomatedHousePlanner is not None:
    try:
        planner = AutomatedHousePlanner()
    except Exception:
        planner = None

# Initialize a lightweight AI agent even if planner is disabled
simple_agent = None
if HousePlanningAgent is not None:
    try:
        simple_agent = HousePlanningAgent()
    except Exception:
        simple_agent = None

def home(request):
    """Home page with house planning form"""
    return render(request, 'home.html')

def result(request):
    """Display house planning results"""
    if request.method == 'POST':
        # Get form data
        land_cents = int(request.POST.get('land_cents', 1))
        orientation = request.POST.get('orientation', 'North')
        # Simplified form: remove family_size and preferences; parse budget with commas
        family_size = 3
        raw_budget = request.POST.get('budget', '0')
        try:
            budget = int(str(raw_budget).replace(',', '').strip() or '0')
        except Exception:
            budget = 0
        preferences = ''
        
        # Create user input for automated planner
        user_input = {
            'land_cents': land_cents,
            'family_size': family_size,
            'budget': budget,
            'orientation': orientation,
            'preferences': preferences,
            'location': 'Urban'
        }
        
        # Generate house plan using automated planner if available
        try:
            if planner is None:
                raise RuntimeError('Planner not available')
            result = planner.plan_house(user_input)
            
            context = {
                'land_cents': land_cents,
                'orientation': orientation,
                'family_size': family_size,
                'budget': budget,
                'preferences': preferences,
                'house_type': result['analysis']['house_type'],
                'rooms': result['analysis']['rooms'],
                'features': result['analysis']['features'],
                'cost_estimation': result['cost_estimation'],
                'ai_suggestions': result['ai_suggestions'],
                '3d_model_success': result['3d_model']['success'],
                '3d_model_path': result['3d_model']['path'],
                'project_id': result['project_id'],
                'reports': result['reports'],
                'sqft': int(round(land_cents * 435.6))
            }
            
            return render(request, 'result.html', context)
            
        except Exception as e:
            # Fallback to basic planning if automated planner fails
            house_type = get_house_type(land_cents)
            room_config = calculate_room_config(land_cents)
            front_design = get_front_design(house_type, orientation)
            color_scheme = get_color_scheme(house_type, orientation)
            design_elements = get_modern_design_elements(house_type)
            
            # Try to generate 3D model
            model_success, model_message = generate_3d_house(land_cents, house_type, orientation, room_config)
            
            # Create a fallback project id and ensure a downloadable GLB exists
            from datetime import datetime as _dt
            fallback_project_id = _dt.now().strftime('%Y%m%d_%H%M%S')
            try:
                import os as _os, shutil as _shutil
                output_dir = getattr(planner, 'output_directory', 'generated_house_plans') if planner else 'generated_house_plans'
                _os.makedirs(output_dir, exist_ok=True)
                target_glb = _os.path.join(output_dir, f"3d_model_{fallback_project_id}.glb")
                # Map land_cents to fallback GLB
                if land_cents <= 3:
                    source_glb = '1bhk.glb'
                elif 4 <= land_cents <= 6:
                    source_glb = '2bhk.glb'
                elif 7 <= land_cents <= 10:
                    source_glb = '3bhk.glb'
                else:
                    source_glb = 'villa.glb'
                candidates = [
                    source_glb,
                    _os.path.join('assets','models',source_glb),
                    _os.path.join(_os.path.dirname(__file__),'assets','models',source_glb)
                ]
                src = next((p for p in candidates if _os.path.exists(p)), None)
                if src and not _os.path.exists(target_glb):
                    _shutil.copyfile(src, target_glb)
                fallback_3d_path = target_glb if _os.path.exists(target_glb) else None
            except Exception:
                fallback_3d_path = None

            # Generate minimal fallback reports and project data so downloads work
            try:
                output_dir = getattr(planner, 'output_directory', 'generated_house_plans') if planner else 'generated_house_plans'
                os.makedirs(output_dir, exist_ok=True)

                sqft = int(round(land_cents * 435.6))

                # Build a structured summary report per house type
                if str(house_type).upper().startswith('1BHK'):
                    summary_content = (
                        "\U0001F3E0 House Summary Report\n\n"
                        "1BHK Apartment\n\n"
                        f"Project ID: {fallback_project_id}\n\n"
                        "House Type: 1BHK\n\n"
                        f"Orientation: {orientation}\n\n"
                        "Approx. Area: 500–700 sq ft\n\n"
                        "Rooms & Areas:\n\n"
                        "- Bedroom: ~110–140 sq ft\n\n"
                        "- Living/Hall: ~160–220 sq ft\n\n"
                        "- Kitchen: ~70–100 sq ft\n\n"
                        "- Bathroom/Toilet: ~35–50 sq ft\n\n"
                        "- Balcony: Small/Medium\n\n"
                        "- Parking: 1-car\n\n"
                        "Amenities & Features:\n\n"
                        "- Efficient circulation, minimal corridors\n\n"
                        "- Provision for washing machine and basic storage\n\n"
                        "- Natural light and ventilation prioritized\n\n"
                        "Notes: Ideal for singles/small families. Compact planning with focus on functionality and low maintenance.\n"
                    )
                elif str(house_type).upper().startswith('2BHK'):
                    summary_content = (
                        "\U0001F3E0 House Summary Report\n\n"
                        "2BHK Apartment\n\n"
                        f"Project ID: {fallback_project_id}\n\n"
                        "House Type: 2BHK\n\n"
                        f"Orientation: {orientation}\n\n"
                        "Approx. Area: 900–1200 sq ft\n\n"
                        "Rooms & Areas:\n\n"
                        "- Bedrooms: 2 (each ~110–140 sq ft)\n\n"
                        "- Bathrooms: 2 (one attached)\n\n"
                        "- Living/Dining: ~220–300 sq ft\n\n"
                        "- Kitchen + Utility: ~100–130 sq ft\n\n"
                        "- Balcony: Medium\n\n"
                        "- Parking: 1–2 cars\n\n"
                        "Amenities & Features:\n\n"
                        "- Better privacy zoning (living vs bedroom cluster)\n\n"
                        "- Dedicated utility space and wardrobe niches\n\n"
                        "- Option for study nook or compact home office\n\n"
                        "Notes: Balanced plan for small families with comfortable living and sensible storage.\n"
                    )
                elif str(house_type).upper().startswith('3BHK'):
                    summary_content = (
                        "\U0001F3E0 House Summary Report\n\n"
                        "3BHK Apartment\n\n"
                        f"Project ID: {fallback_project_id}\n\n"
                        "House Type: 3BHK\n\n"
                        f"Orientation: {orientation}\n\n"
                        "Approx. Area: 1200–1800 sq ft\n\n"
                        "Rooms & Areas:\n\n"
                        "- Bedrooms: 3 (Master ~150–180 sq ft, others ~120–140 sq ft)\n\n"
                        "- Bathrooms: 2–3 (master attached + common)\n\n"
                        "- Living/Dining: ~280–360 sq ft\n\n"
                        "- Kitchen + Utility: ~110–150 sq ft\n\n"
                        "- Balcony/Terrace: Large\n\n"
                        "- Parking: 1–2 cars\n\n"
                        "Amenities & Features:\n\n"
                        "- Option for family lounge/pooja/store room\n\n"
                        "- Better acoustic privacy and cross-ventilation\n\n"
                        "- Space for study/work-from-home setup\n\n"
                        "Notes: Comfortable for medium-sized families with scope for premium finishes and zoning.\n"
                    )
                else:
                    # Default to Villa-style detailed output with actual computed area
                    summary_content = (
                        "\U0001F3E0 House Summary Report\n\n"
                        "Villa\n\n"
                        f"Project ID: {fallback_project_id}\n\n"
                        "House Type: Villa\n\n"
                        f"Orientation: {orientation}\n\n"
                        f"Approx. Area: {sqft} sq ft\n\n"
                        "Rooms & Areas:\n\n"
                        "- Bedrooms: 4–5 (master with walk-in)\n\n"
                        "- Bathrooms: 3–5 (premium fittings)\n\n"
                        "- Living + Family lounge: 2 spacious halls\n\n"
                        "- Kitchens: 1 main + 1 utility/service\n\n"
                        "- Parking: 2-car covered garage\n\n"
                        "- Balcony/Terrace: Large balcony + landscaped terrace\n\n"
                        f"Total Area Considered: {sqft} sq ft\n\n"
                        "Amenities & Features:\n\n"
                        "- Home theatre/office/gym room options\n\n"
                        "- Garden, sit-out, water feature/landscaping provisions\n\n"
                        "- Smart home readiness (security/lighting)\n\n"
                        "Notes: Premium living with generous spatial planning, ideal for multi-generational families and luxury finishes.\n"
                    )
                # Technical specifications by house type
                if str(house_type).upper().startswith('1BHK'):
                    technical_content = (
                        "Technical Specifications Report\n\n"
                        "1BHK Apartment\n\n"
                        "House Type: 1BHK\n"
                        "Approx. Area: 500–700 sq ft\n\n"
                        "1. Structural\n\n"
                        "RCC framed structure with earthquake-resistant design\n\n"
                        "Foundation: Isolated/combined footings with reinforced concrete\n\n"
                        "Flooring: Vitrified tiles in living, anti-skid tiles in bathroom\n\n"
                        "Walls: Cement plaster with POP finishing\n\n"
                        "2. Architectural\n\n"
                        "Doors: Teakwood/main door, flush doors for interiors\n\n"
                        "Windows: UPVC/Aluminum with sliding or casement\n\n"
                        "Balcony: Iron railing or glass railing\n\n"
                        "Painting: Acrylic emulsion for interiors, weatherproof exterior paint\n\n"
                        "3. Electrical & Plumbing\n\n"
                        "Electrical: Copper wiring with modular switches, MCBs, sufficient sockets\n\n"
                        "Lighting: LED fittings in all rooms\n\n"
                        "Plumbing: CPVC pipes, standard sanitary fittings, hot/cold provision\n\n"
                        "Water: Underground and overhead water tanks, borewell/corporation water connection\n\n"
                        "4. Kitchen & Bathroom\n\n"
                        "Kitchen: Granite/Quartz countertop, SS sink, modular cabinets\n\n"
                        "Bathroom: Anti-skid floor tiles, wall tiles up to 7 ft, premium sanitaryware\n"
                    )
                elif str(house_type).upper().startswith('2BHK'):
                    technical_content = (
                        "Technical Specifications Report\n\n"
                        "2BHK Apartment\n\n"
                        "House Type: 2BHK\n"
                        "Approx. Area: 900–1200 sq ft\n\n"
                        "1. Structural\n\n"
                        "RCC frame structure with seismic-resistant design\n\n"
                        "Flooring: Vitrified tiles in living/dining, ceramic tiles in bathrooms\n\n"
                        "Walls: Smooth plaster with POP punning\n\n"
                        "2. Architectural\n\n"
                        "Doors: Teakwood main door, flush/engineered wood interior doors\n\n"
                        "Windows: Powder-coated aluminum/UPVC sliding windows\n\n"
                        "Balcony: Glass/steel railing, provision for planters\n\n"
                        "Painting: Emulsion for interiors, exterior weatherproof paint\n\n"
                        "3. Electrical & Plumbing\n\n"
                        "Copper wiring with adequate sockets and MCBs\n\n"
                        "LED lighting & fans in all rooms\n\n"
                        "Plumbing: CPVC lines, premium sanitary fittings, provision for water purifier\n\n"
                        "Water: Underground & overhead tanks with sump\n\n"
                        "4. Kitchen & Bathroom\n\n"
                        "Kitchen: Granite countertop, stainless steel sink, modular cabinets\n\n"
                        "Bathroom: Anti-skid tiles, wall tiles, branded sanitary fittings\n"
                    )
                elif str(house_type).upper().startswith('3BHK'):
                    technical_content = (
                        "Technical Specifications Report\n\n"
                        "3BHK Apartment\n\n"
                        "House Type: 3BHK\n"
                        "Approx. Area: 1200–1800 sq ft\n\n"
                        "1. Structural\n\n"
                        "RCC framed structure with earthquake resistance\n\n"
                        "Flooring: Vitrified tiles in living/dining, laminated wooden flooring in master bedroom, ceramic in bathrooms\n\n"
                        "Walls: POP punning with smooth finish\n\n"
                        "2. Architectural\n\n"
                        "Doors: Teakwood main door, engineered wood for interiors\n\n"
                        "Windows: UPVC/aluminum sliding with mosquito mesh\n\n"
                        "Balcony/Terrace: Glass railing, waterproofing treatment\n\n"
                        "Painting: Premium acrylic emulsion interior, weatherproof exterior paint\n\n"
                        "3. Electrical & Plumbing\n\n"
                        "Copper wiring with MCBs & RCCB\n\n"
                        "LED light fixtures, ceiling fans, provisions for AC\n\n"
                        "Plumbing: CPVC lines, premium sanitaryware, geyser provision\n\n"
                        "Water: Underground and overhead tanks, borewell & municipal supply\n\n"
                        "4. Kitchen & Bathroom\n\n"
                        "Kitchen: Granite countertop, SS sink, modular cabinets, exhaust provision\n\n"
                        "Bathroom: Anti-skid tiles, wall tiles up to 7–8 ft, premium sanitaryware & fittings\n"
                    )
                else:
                    technical_content = (
                        "Technical Specifications Report\n\n"
                        "Villa\n\n"
                        "House Type: Villa\n"
                        f"Approx. Area: {sqft} sq ft\n\n"
                        "1. Structural\n\n"
                        "RCC framed structure with advanced seismic design\n\n"
                        "Flooring: Vitrified tiles in common areas, wooden flooring in bedrooms, premium tiles in bathrooms\n\n"
                        "Walls: Smooth plaster with POP finish, designer textures in select walls\n\n"
                        "Terrace: Waterproofing with insulation layer\n\n"
                        "2. Architectural\n\n"
                        "Doors: Teakwood main door, designer flush doors/engineered wood interiors\n\n"
                        "Windows: Double-glass UPVC/aluminum for energy efficiency\n\n"
                        "Balcony/Terrace: Tempered glass railing, pergola or landscaping provision\n\n"
                        "Painting: Premium acrylic emulsion interiors, weatherproof exterior finishes\n\n"
                        "3. Electrical & Plumbing\n\n"
                        "Electrical: Copper wiring, modular switches, MCBs, RCCB, provision for smart home systems\n\n"
                        "Lighting: LED downlights, decorative lighting, provisions for outdoor lighting\n\n"
                        "Plumbing: CPVC/PPR pipes, branded sanitaryware, hot & cold water lines in all bathrooms\n\n"
                        "Water: Underground & overhead tanks, RO plant provision, sump tank\n\n"
                        "4. Kitchen & Bathrooms\n\n"
                        "Kitchen: Granite/Quartz countertops, stainless steel sink, modular cabinets, chimney & hob provision\n\n"
                        "Bathrooms: Anti-skid tiles, wall tiles, premium fittings, shower cubicles, geyser provision\n"
                    )

                # Cost breakdown by house type
                if str(house_type).upper().startswith('1BHK'):
                    cost_content = (
                        "Cost Breakdown Report\n\n"
                        "Assumption: Construction cost = ₹1,800–₹2,500 per sq ft (mid-range), interiors and finishes are medium to premium quality.\n\n"
                        "1BHK Apartment\n\n"
                        "Approx. Area: 600 sq ft\n\n"
                        "Base Construction Cost (₹1,800/sq ft): ₹10,80,000\n\n"
                        "Interiors & Furnishing: ₹1,50,000 – ₹2,00,000\n\n"
                        "Electrical & Plumbing: ₹50,000 – ₹70,000\n\n"
                        "Parking Provision: ₹50,000\n\n"
                        "Professional Fees & Approvals: ₹40,000 – ₹70,000\n\n"
                        "Contingency (10%): ₹1,20,000 – ₹1,60,000\n\n"
                        "Total Estimated Cost: ₹15,00,000 – ₹17,00,000\n\n"
                        "Timeline: 4–6 months (site dependent)\n\n"
                        "Notes: Budget-friendly; upgrade finishes or add wardrobe/kitchen modules as needed. Prices vary by city and contractor.\n"
                    )
                elif str(house_type).upper().startswith('2BHK'):
                    cost_content = (
                        "Cost Breakdown Report\n\n"
                        "Assumption: Construction cost = ₹1,800–₹2,500 per sq ft (mid-range), interiors and finishes are medium to premium quality.\n\n"
                        "2BHK Apartment\n\n"
                        "Approx. Area: 1,100 sq ft\n\n"
                        "Base Construction Cost (₹1,800/sq ft): ₹19,80,000\n\n"
                        "Interiors & Furnishing: ₹2,50,000 – ₹3,50,000\n\n"
                        "Electrical & Plumbing: ₹70,000 – ₹1,00,000\n\n"
                        "Parking Provision: ₹1,00,000\n\n"
                        "Professional Fees & Approvals: ₹70,000 – ₹1,00,000\n\n"
                        "Contingency (8–10%): ₹2,00,000 – ₹2,50,000\n\n"
                        "Total Estimated Cost: ₹26,50,000 – ₹29,00,000\n\n"
                        "Timeline: 6–8 months\n\n"
                        "Notes: Suitable for small families; optimize costs via modular interiors and phased upgrades.\n"
                    )
                elif str(house_type).upper().startswith('3BHK'):
                    cost_content = (
                        "Cost Breakdown Report\n\n"
                        "Assumption: Construction cost = ₹1,800–₹2,500 per sq ft (mid-range), interiors and finishes are medium to premium quality.\n\n"
                        "3BHK Apartment\n\n"
                        "Approx. Area: 1,600 sq ft\n\n"
                        "Base Construction Cost (₹2,000/sq ft): ₹32,00,000\n\n"
                        "Interiors & Furnishing: ₹4,00,000 – ₹5,00,000\n\n"
                        "Electrical & Plumbing: ₹1,00,000 – ₹1,50,000\n\n"
                        "Parking Provision: ₹1,50,000\n\n"
                        "Professional Fees & Approvals: ₹1,00,000 – ₹1,50,000\n\n"
                        "Contingency (8–10%): ₹3,50,000 – ₹4,00,000\n\n"
                        "Total Estimated Cost: ₹44,00,000 – ₹48,00,000\n\n"
                        "Timeline: 8–10 months\n\n"
                        "Notes: Medium-sized families; allocate extra for premium wardrobes, kitchen, and lighting layers.\n"
                    )
                else:
                    villa_base_cost = sqft * 2500
                    cost_content = (
                        "Cost Breakdown Report\n\n"
                        "Assumption: Construction cost = ₹1,800–₹2,500 per sq ft (mid-range), interiors and finishes are medium to premium quality.\n\n"
                        "Villa\n\n"
                        f"Approx. Area: {sqft:,} sq ft\n\n"
                        f"Base Construction Cost (₹2,500/sq ft): ₹{villa_base_cost:,}\n\n"
                        "Interiors & Furnishing: ₹20,00,000 – ₹30,00,000\n\n"
                        "Electrical & Plumbing: ₹5,00,000 – ₹8,00,000\n\n"
                        "Parking Provision (2-car garage): ₹3,00,000\n\n"
                        "Landscaping & Terrace: ₹5,00,000 – ₹7,00,000\n\n"
                        "Professional Fees, Design & Approvals: ₹3,00,000 – ₹6,00,000\n\n"
                        "Contingency (8–10%): add as buffer on subtotal\n\n"
                        "Total Estimated Cost: ₹1,85,00,000 – ₹2,05,00,000 (excl. land, GST)\n\n"
                        "\U0001F4A1 Cost Summary Table\n"
                        "House Type\tArea (sq ft)\tBase Construction\tInteriors & Furnishing\tElectrical & Plumbing\tParking\tTotal Cost (₹)\n"
                        "1BHK\t600\t10,80,000\t1,50,000 – 2,00,000\t50,000 – 70,000\t50,000\t13,30,000 – 14,50,000\n"
                        "2BHK\t1,100\t19,80,000\t2,50,000 – 3,50,000\t70,000 – 1,00,000\t1,00,000\t24,00,000 – 25,50,000\n"
                        "3BHK\t1,600\t32,00,000\t4,00,000 – 5,00,000\t1,00,000 – 1,50,000\t1,50,000\t38,50,000 – 40,00,000\n"
                        f"Villa\t{sqft:,}\t{villa_base_cost:,}\t20,00,000 – 30,00,000\t5,00,000 – 8,00,000\t3,00,000\t1,85,00,000 – 2,05,00,000\n"
                    )

                with open(os.path.join(output_dir, f"summary_report_{fallback_project_id}.txt"), 'w', encoding='utf-8') as f:
                    f.write(summary_content)
                with open(os.path.join(output_dir, f"technical_specifications_{fallback_project_id}.txt"), 'w', encoding='utf-8') as f:
                    f.write(technical_content)
                with open(os.path.join(output_dir, f"cost_breakdown_{fallback_project_id}.txt"), 'w', encoding='utf-8') as f:
                    f.write(cost_content)

                # Save minimal project data to support later lookups
                project_data = {
                    'project_id': fallback_project_id,
                    'analysis': {
                        'house_type': house_type,
                        'land_cents': land_cents,
                        'orientation': orientation,
                        'rooms': room_config,
                    },
                    '3d_model': {
                        'success': model_success,
                        'path': fallback_3d_path,
                    }
                }
                with open(os.path.join(output_dir, f"project_data_{fallback_project_id}.json"), 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            
            context = {
                'land_cents': land_cents,
                'orientation': orientation,
                'family_size': family_size,
                'budget': budget,
                'preferences': preferences,
                'house_type': house_type,
                'room_config': room_config,
                'front_design': front_design,
                'color_scheme': color_scheme,
                'design_elements': design_elements,
                'model_success': model_success,
                'model_message': model_message,
                'error': f"Automated planning failed: {str(e)}",
                'sqft': int(round(land_cents * 435.6)),
                'project_id': fallback_project_id,
                '3d_model_path': fallback_3d_path,
                'reports': ['summary_report', 'technical_specifications', 'cost_breakdown']
            }
            
            return render(request, 'result.html', context)
    
    return redirect('home')

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_ai(request):
    """Chat with AI agent"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Always prefer a fresh agent per request so env var/model changes take effect
        response = None
        error_text = None
        if HousePlanningAgent is not None:
            try:
                agent = HousePlanningAgent()
                if agent and agent.model:
                    response = agent.ask_ai(message)
                else:
                    error_text = "AI model not initialized"
            except Exception as ex:
                error_text = str(ex)
        if response is None:
            response = _basic_advice(message) if not error_text else f"AI unavailable: {error_text}. Using basic advice: {_basic_advice(message)}"
        
        return JsonResponse({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Simple non-AI fallback advice
def _basic_advice(query: str) -> str:
    q = (query or '').lower()
    if any(k in q for k in ['cost', 'estimation', 'price']):
        return 'Rough build cost: ₹1,200–2,000 per sq ft depending on materials and location.'
    if 'orientation' in q or 'facing' in q:
        return 'North/East facing maximize daylight; add shading for West, buffer spaces for South.'
    if 'room' in q or 'size' in q:
        return 'Good sizes: Master 12x14 ft, Bedroom 10x12 ft, Living 16x20 ft, Kitchen 10x12 ft.'
    if 'budget' in q:
        return 'Allocate ~60% construction, 20% materials, 15% labor, 5% permits; keep 10% buffer.'
    return 'I can help with costs, sizes, orientation, and materials. Ask a specific question.'

@csrf_exempt
@require_http_methods(["POST"])
def generate_3d_model(request):
    """Generate 3D model on demand"""
    try:
        data = json.loads(request.body)
        land_cents = data.get('land_cents', 5)
        orientation = data.get('orientation', 'North')
        house_type = data.get('house_type', '2BHK')
        
        # Create house config
        house_config = {
            'land_cents': land_cents,
            'orientation': orientation,
            'house_type': house_type
        }
        
        # Generate 3D model
        if planner is None or getattr(planner, 'agent', None) is None:
            return JsonResponse({'error': '3D generator not available'}, status=503)
        success, message = planner.agent.create_3d_model(house_config)
        
        return JsonResponse({
            'success': success,
            'message': message,
            'model_path': message if success else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_house_suggestions(request):
    """Get AI-powered house suggestions"""
    try:
        data = json.loads(request.body)
        
        # Generate suggestions using AI agent
        suggestions = planner.agent.generate_house_suggestions(data)
        
        return JsonResponse({
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def download_report(request, report_type, project_id):
    """Download generated reports"""
    try:
        # Resolve output directory even when planner is unavailable
        output_dir = getattr(planner, 'output_directory', 'generated_house_plans') if planner else 'generated_house_plans'
        filename = f"{report_type}_{project_id}.txt"
        filepath = os.path.join(output_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            response = HttpResponse(content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse("Report not found", status=404)
            
    except Exception as e:
        return HttpResponse(f"Error downloading report: {str(e)}", status=500)

def download_3d_model(request, project_id):
    """Download 3D model"""
    try:
        # Resolve output directory even when planner is unavailable
        output_dir = getattr(planner, 'output_directory', 'generated_house_plans') if planner else 'generated_house_plans'
        filename = f"3d_model_{project_id}.glb"
        filepath = os.path.join(output_dir, filename)
        
        if not os.path.exists(filepath):
            # Attempt on-demand fallback: derive from saved project data and copy a sample GLB
            try:
                project_json = os.path.join(output_dir, f"project_data_{project_id}.json")
                if os.path.exists(project_json):
                    with open(project_json, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                    # First try to copy the exact generated path if present
                    generated_path = project_data.get('3d_model', {}).get('path')
                    if generated_path and os.path.exists(generated_path):
                        os.makedirs(output_dir, exist_ok=True)
                        import shutil
                        shutil.copyfile(generated_path, filepath)
                    
                    land_cents = project_data.get('analysis', {}).get('land_cents', 1)
                    # Exact rule per requirements
                    if land_cents <= 3:
                        source_glb = '1bhk.glb'
                    elif 4 <= land_cents <= 6:
                        source_glb = '2bhk.glb'
                    elif 7 <= land_cents <= 10:
                        source_glb = '3bhk.glb'
                    else:
                        source_glb = 'villa.glb'
                    # Search in common assets locations
                    candidate_paths = [
                        source_glb,
                        os.path.join(os.getcwd(), source_glb),
                        os.path.join('assets', 'models', source_glb),
                        os.path.join('planner', 'assets', 'models', source_glb),
                        os.path.join(os.path.dirname(__file__), 'assets', 'models', source_glb)
                    ]
                    src = next((p for p in candidate_paths if os.path.exists(p)), None)
                    if src:
                        os.makedirs(output_dir, exist_ok=True)
                        import shutil
                        shutil.copyfile(src, filepath)
                # If still not present after fallback, return 404
            except Exception:
                pass

        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse("3D model not found", status=404)
            
    except Exception as e:
        return HttpResponse(f"Error downloading 3D model: {str(e)}", status=500)

def api_status(request):
    """API status endpoint"""
    return JsonResponse({
        'status': 'active',
        'ai_available': bool(
            (planner and getattr(planner, 'agent', None) and planner.agent.model) or
            (simple_agent and simple_agent.model)
        ),
        'blender_available': bool(planner and getattr(planner, 'agent', None) and planner.agent.blender_available),
        'timestamp': datetime.now().isoformat()
    })