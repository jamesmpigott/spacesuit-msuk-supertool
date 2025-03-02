#!/bin/bash

# 1. Install Homebrew (if not installed)
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew already installed."
fi

# 2. Install create-dmg
if ! brew list create-dmg &>/dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
else
    echo "create-dmg already installed."
fi

# 3. Install pyinstaller
if ! pip list | grep pyinstaller &>/dev/null; then
    echo "Installing pyinstaller..."
    pip install pyinstaller
else
    echo "pyinstaller already installed."
fi

# 5. Convert Python script to an application bundle
echo "Converting Python script to macOS app bundle..."
pyinstaller gui.spec

# 6. Create the DMG installer
echo "Creating DMG installer..."
mkdir -p dist/dmg
rm -rf dist/dmg/*
cp -r "dist/Spacesuit-MSUK-SuperTool.app" dist/dmg
create-dmg \
  --volname "Spacesuit-MSUK-SuperTool" \
  --volicon "assets/favicon.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Spacesuit-MSUK-SuperTool.app" 175 120 \
  --hide-extension "Spacesuit-MSUK-SuperTool.app" \
  --app-drop-link 425 120 \
  "dist/Spacesuit-MSUK-SuperTool.dmg" \
  "dist/dmg/"

echo "Packaging complete. You can find the DMG installer in the dist/ directory."
