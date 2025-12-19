#!/usr/bin/env python3
"""
Install Azure SDK packages for QGIS
Run from QGIS Python Console with: exec(open('path/to/install_azure.py').read())
"""

import subprocess
import sys

packages = [
    "azure-cognitiveservices-vision-computervision",
    "msrest",
    "python-dotenv"
]

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"\nInstalling packages: {', '.join(packages)}\n")

for package in packages:
    print(f"\n{'='*60}")
    print(f"Installing: {package}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Successfully installed {package}")
        else:
            print(f"❌ Failed to install {package}")
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")

print("\n" + "="*60)
print("Installation complete!")
print("Please restart QGIS to load the new packages.")
print("="*60)
