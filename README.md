# 🏡 Smart House Planner - AI-Powered House Planning System

A comprehensive house planning automation system that combines AI intelligence, 3D modeling, and cost estimation to help you design your dream home.

## ✨ aaaaaa

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd house
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Gemini AI (Optional)**
   ```bash
   python setup_gemini.py
   # Follow instructions to set GEMINI_API_KEY
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the server**
   ```bash
   python manage.py runserver
   ```

7. **Open browser**
   ```
   http://127.0.0.1:8000/
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=True
SECRET_KEY=your_secret_key_here
```

### Blender Setup
1. Download and install Blender from https://www.blender.org/
2. Add Blender to your system PATH
3. Test installation: `blender --version`

## 📖 Usage

### Web Interface
1. **Enter Requirements**: Land area, family size, orientation, budget
2. **Add Preferences**: Describe your dream house features
3. **Generate Plan**: Click "Generate House Plan"
4. **View Results**: See AI recommendations, 3D model, cost estimation
5. **Chat with AI**: Ask questions about your house design
6. **Download Reports**: Get detailed reports and 3D models

### API Endpoints
- `POST /api/chat/` - Chat with AI assistant
- `POST /api/generate-3d/` - Generate 3D model
- `POST /api/suggestions/` - Get AI house suggestions
- `GET /api/status/` - Check system status

### Python API
```python
from automated_house_planner import AutomatedHousePlanner

# Initialize planner
planner = AutomatedHousePlanner()

# Plan a house
user_input = {
    'land_cents': 7,
    'family_size': 4,
    'budget': 5000000,
    'orientation': 'North',
    'preferences': 'Modern design with garden'
}

result = planner.plan_house(user_input)
print(f"House Type: {result['analysis']['house_type']}")
print(f"Cost: ₹{result['cost_estimation']['total_cost']:,.0f}")
```

## 🏗️ Architecture

### Components
- **Django Backend**: Web framework and API
- **House Planning Agent**: AI-powered planning logic
- **Automated House Planner**: Main orchestration system
- **Blender Integration**: 3D model generation
- **Gemini AI**: Natural language processing and recommendations

### File Structure
```
house/
├── automated_house_planner.py    # Main planning system
├── house_planning_agent.py       # AI agent with Gemini integration
├── planner/                      # Django app
│   ├── views.py                  # Web views and API endpoints
│   ├── templates/                # HTML templates
│   └── logic/                    # Business logic modules
├── generated_house_plans/        # Output directory
└── requirements.txt              # Python dependencies
```

## 🎯 Supported House Types

### 1BHK (1 Bedroom)
- Master Bedroom
- Living Room
- Kitchen
- Bathroom

### 2BHK (2 Bedrooms)
- 2 Bedrooms
- Living Room
- Kitchen
- Bathroom
- Balcony

### 3BHK (3 Bedrooms)
- 3 Bedrooms
- Living Room
- Kitchen
- 2 Bathrooms
- Balcony

### Duplex
- 3 Bedrooms (2nd floor)
- Living Room (1st floor)
- Kitchen (1st floor)
- 2 Bathrooms
- Study Room
- Balcony

### Villa
- 4+ Bedrooms
- Living Room
- Kitchen
- 3+ Bathrooms
- Study Room
- Garden
- Multiple floors

## 💡 AI Features

### Smart Recommendations
- House type selection based on land area and family size
- Material suggestions based on budget and preferences
- Energy efficiency recommendations
- Modern design trends integration

### Interactive Chat
- Ask questions about house design
- Get advice on materials and construction
- Discuss cost optimization strategies
- Learn about architectural best practices

### Natural Language Processing
- Understand complex requirements
- Process preference descriptions
- Generate contextual responses
- Provide detailed explanations

## 🔧 Troubleshooting

### Common Issues

1. **Blender not found**
   - Install Blender and add to PATH
   - Test with: `blender --version`

2. **Gemini AI not working**
   - Set GEMINI_API_KEY environment variable
   - Run: `python setup_gemini.py`

3. **3D model generation fails**
   - Check Blender installation
   - Verify disk space
   - Check file permissions

4. **Django server issues**
   - Run migrations: `python manage.py migrate`
   - Check database: `python manage.py check`

### Debug Mode
Enable debug mode in settings.py:
```python
DEBUG = True
```

## 📊 Performance

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **CPU**: Multi-core processor recommended
- **GPU**: DirectX 11 compatible (for Blender)

### Optimization Tips
- Use SSD storage for faster 3D model generation
- Close other applications during 3D generation
- Use smaller land areas for faster processing
- Enable hardware acceleration in Blender

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🔮 Future Enhancements

- [ ] VR/AR visualization
- [ ] Mobile app
- [ ] Advanced AI features
- [ ] Integration with construction companies
- [ ] Real-time collaboration
- [ ] Advanced cost optimization
- [ ] Sustainability analysis
- [ ] Regulatory compliance checking

---

**Built with ❤️ using Django, Blender, and Gemini AI**