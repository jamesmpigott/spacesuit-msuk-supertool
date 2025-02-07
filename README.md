# IPTC Image Description Processor

## Overview
A GUI application for processing image IPTC metadata descriptions.

## Prerequisites
- Python 3.7+
- pip (Python package manager)

## System-Specific Setup

### macOS (Homebrew Python)
```bash
# Install Python Tkinter
brew install python-tk

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Linux (Ubuntu/Debian)
```bash
# Install Python Tkinter
sudo apt-get install python3-tk

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Windows
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
# Note: Tkinter is usually included with Python on Windows
```

## Running the Application
```bash
python iptc_processor.py
```

## Packaging for Distribution
If you want to create a standalone executable for easy sharing:

1. Install PyInstaller
```bash
pip install pyinstaller
```

2. Create executable
```bash
pyinstaller --onefile --windowed iptc_processor.py
```

The executable will be in the `dist/` directory and can be shared without requiring Python installation.