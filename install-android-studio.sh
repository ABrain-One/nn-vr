#!/bin/bash

# Define variables
ANDROID_STUDIO_URL="https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.1.1.28/android-studio-2023.1.1.28-linux.tar.gz" # Example URL, update if needed to specific version
INSTALL_DIR="$HOME/android-studio"
DOWNLOAD_FILE="android-studio.tar.gz"

echo "Downloading Android Studio..."
wget -O $DOWNLOAD_FILE $ANDROID_STUDIO_URL

echo "Extracting..."
tar -xzf $DOWNLOAD_FILE -C $HOME

echo "Cleaning up..."
rm $DOWNLOAD_FILE

echo "Android Studio installed to $INSTALL_DIR"
echo "Run it with: $INSTALL_DIR/bin/studio.sh"
