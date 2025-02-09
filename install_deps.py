import platform
import subprocess
import sys
from pathlib import Path

def check_exempi():
    try:
        import libxmp
        return True
    except Exception:
        return False

def install_exempi():
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        try:
            # Check if Homebrew is installed
            subprocess.run(['which', 'brew'], check=True, capture_output=True)

        except subprocess.CalledProcessError:
            print("Homebrew not found. Installing...")
            try:
                install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                subprocess.run(install_cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                print("Failed to install Homebrew")
                return False
        
        # Install exempi
        try:
            subprocess.run(['brew', 'install', 'exempi'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    elif system == "linux":
        try:
            # Detect package manager
            if Path("/usr/bin/apt").exists():
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'libexempi8'], check=True)
                return True
            elif Path("/usr/bin/dnf").exists():
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'exempi'], check=True)
                return True
        except subprocess.CalledProcessError:
            return False
    
    print(f"Unsupported system: {system}")
    return False

def main():
    if check_exempi():
        print("Exempi already installed!")
        return 0
    
    print("Installing exempi...")
    if install_exempi():
        print("Installation successful!")
        return 0
    else:
        print("Installation failed. Please install exempi manually.")
        return 1

if __name__ == "__main__":
    sys.exit(main())