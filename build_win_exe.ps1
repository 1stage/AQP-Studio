# Build script for packaging AQP Studio as a standalone Windows executable using PyInstaller
# Usage: Run this script in PowerShell from the project directory...
# powershell -ExecutionPolicy Bypass -File build_win_exe.ps1

# Ensure required packages are installed
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow numpy



# Generate the Windows icon from assets/win-icon.png
# python utils\make_icon.py

# Run PyInstaller to build the executable with the generated icon
pyinstaller --onefile --windowed --add-data "assets;assets" --name "AQP Studio" --icon "assets\win-icon.ico" aqp_studio.py

# Output executable will be in the 'dist' folder
Write-Host "Build complete. Find your executable in the 'dist' folder."
