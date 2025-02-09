# SSM - MSUK Image Description Fixer
Small application to convert image descriptions (both IPTC and XMP) from Spacesuit Media's to Motorsport-UK's preferred format.

## macOS Installation
1. Download the latest release from [releases](https://github.com/jamesmpigott/iptc/releases)
2. Extract the zip
3. Run the installation script (installer.app)
4. Run the `.dmg` file and drag to "Applications"
5. Select and run "MSUK-Description-Fixer" from launchpad, spotlight, [RayCast](https://www.raycast.com/) etc

## Development

If you're me ([jamesmpigott](https://github.com/jamesmpigott)) or otherwise insane, here's how you can get this repo setup for local development.

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- [Homebrew](https://brew.sh/)
    - (if you don't have this installed, the installer script will install this for you)
- [exempi](https://formulae.brew.sh/formula/exempi)
- [create-dmg](https://formulae.brew.sh/formula/create-dmg)


### Initial Setup
```bash
# Install system-level dependencies via homebrew
brew install exempi create-dmg

# Clone repo
git clone https://github.com/jamesmpigott/iptc.git

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Optional - if you need to run create_dmg.sh locally
chmod +x create_dmg.sh
```

From this point, you've got a few files of note:
- `terminal.py`: Terminal-based version of the application
- `gui.py`: GUI-based version of the application
- `install_deps.py`: Installer script
- `create_dmg.sh`: Script to create .dmg file, based on [Kevin Marville's setup_and_package.sh](https://gist.github.com/Kvnbbg/84871ae4d642c2dd896e0423471b1b52#file-setup_and_package-sh) script.

### Compiling
```bash
# compile .py files
pyinstaller gui.spec 
pyinstaller installer.spec

# Create .dmg file
./create_dmg.sh
```

### Releasing a new version
push to `main`, with a tag in the following format: `v{version}`, i.e `v.1.2.5`. Please use [Semantic Versioning](https://semver.org/) for the version string.
The `build-release.yml` action should take care of the rest.