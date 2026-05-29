"""
Installation and Setup Helper Script
Run this to verify and setup the AI Game Controller
"""

import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    print(f"\n✓ Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required!")
        return False
    return True

def check_packages():
    """Check if required packages are installed"""
    required_packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'pyautogui': 'pyautogui'
    }
    
    print("\nChecking installed packages:")
    missing = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (missing)")
            missing.append(package_name)
    
    return missing

def install_packages(packages):
    """Install missing packages"""
    if not packages:
        print("\n✓ All packages already installed!")
        return True
    
    print(f"\nInstalling {len(packages)} package(s)...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        print("✓ Installation complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Installation failed: {e}")
        return False

def check_webcam():
    """Check if webcam is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("\n✓ Webcam detected and accessible")
            cap.release()
            return True
        else:
            print("\n✗ Webcam not accessible")
            return False
    except Exception as e:
        print(f"\n✗ Error checking webcam: {e}")
        return False

def check_config():
    """Check if configuration files exist"""
    import os
    
    print("\nChecking configuration files:")
    files_to_check = [
        'config/settings.py',
        'gesture_detector.py',
        'input_controller.py',
        'ui_renderer.py',
        'main.py'
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Run setup checks"""
    print("="*60)
    print("🎮 AI WEBCAM GAME CONTROLLER - SETUP VERIFICATION")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        print("\nPlease upgrade Python to 3.8 or later")
        return False
    
    # Check and install packages
    missing = check_packages()
    if missing:
        print(f"\nMissing {len(missing)} package(s)")
        if not install_packages(missing):
            return False
    
    # Check webcam
    if not check_webcam():
        print("\nWarning: Webcam not detected. Install a webcam or check drivers.")
    
    # Check config files
    if not check_config():
        print("\nWarning: Some configuration files missing!")
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\nTo start the game controller, run:")
    print("  python main.py")
    print("\nFor quick start guide:")
    print("  cat QUICKSTART.txt")
    print("\n" + "="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
