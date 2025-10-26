# Blender Installation Guide for Smart House Planner

## 🎯 Why Blender is Required

The Smart House Planner uses Blender to generate realistic 3D house models in GLB format. Without Blender installed, you'll encounter the error:

```
Bad glTF: json error: Expecting value: line 1 column 1 (char 0)
```

This happens because the application tries to generate 3D models but can't create valid GLB files without Blender.

## 📥 Installing Blender

### Windows Installation

1. **Download Blender**
   - Go to [https://www.blender.org/download/](https://www.blender.org/download/)
   - Click "Download Blender" (latest stable version)
   - Choose Windows x64 installer

2. **Install Blender**
   - Run the downloaded `.exe` file
   - Follow the installation wizard
   - **Important**: Make sure to check "Add Blender to PATH" during installation
   - Complete the installation

3. **Verify Installation**
   - Open Command Prompt or PowerShell
   - Run: `blender --version`
   - You should see Blender version information

### Alternative: Manual PATH Setup

If Blender is installed but not in PATH:

1. **Find Blender Installation**
   - Usually located at: `C:\Program Files\Blender Foundation\Blender 3.x\`
   - Or: `C:\Users\[YourUsername]\AppData\Local\Programs\Blender Foundation\`

2. **Add to PATH**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add the Blender installation path
   - Click "OK" on all dialogs

3. **Restart Command Prompt**
   - Close and reopen Command Prompt
   - Test with: `blender --version`

## 🔧 Troubleshooting

### "Blender is not recognized" Error

1. **Check if Blender is installed**
   - Look in Program Files or AppData folders
   - If not found, reinstall Blender

2. **Check PATH variable**
   - Run: `echo %PATH%`
   - Look for Blender installation path
   - If missing, add it manually

3. **Restart your system**
   - Sometimes PATH changes require a restart

### "Permission Denied" Error

1. **Run as Administrator**
   - Right-click Command Prompt
   - Select "Run as administrator"

2. **Check antivirus software**
   - Some antivirus may block Blender
   - Add Blender to exceptions

### GLB File Still Corrupted

1. **Check Blender version**
   - Ensure you have Blender 3.0 or higher
   - Older versions may have export issues

2. **Test Blender manually**
   ```bash
   blender --background --python -c "import bpy; print('Blender Python API working')"
   ```

3. **Check disk space**
   - Ensure you have at least 1GB free space
   - GLB files can be large

## 🚀 After Installation

Once Blender is properly installed:

1. **Restart your Django server**
   ```bash
   python manage.py runserver
   ```

2. **Test 3D generation**
   - Go to the house planner
   - Generate a house plan
   - Try the 3D model features

3. **Verify GLB files**
   - Generated GLB files should be > 1KB
   - They should open in 3D viewers

## 📋 System Requirements

- **Windows 10/11** (64-bit)
- **4GB RAM** minimum (8GB recommended)
- **2GB free disk space**
- **DirectX 11** compatible graphics card

## 🆘 Still Having Issues?

If you continue to have problems:

1. **Check the Django logs** for detailed error messages
2. **Try running Blender manually** to test installation
3. **Verify Python environment** is properly set up
4. **Contact support** with specific error messages

## 🔗 Useful Links

- [Blender Official Download](https://www.blender.org/download/)
- [Blender Documentation](https://docs.blender.org/)
- [GLB File Format](https://www.khronos.org/gltf/)
- [Django Documentation](https://docs.djangoproject.com/)

---

**Note**: The Smart House Planner will work without Blender for basic features, but 3D model generation requires Blender to be installed and properly configured.
