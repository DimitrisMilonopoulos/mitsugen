#!/bin/bash

echo "Installing required files..."

echo "Creating required directories..."
mkdir -p ~/.themes
mkdir -p ~/.local/share/themes

echo "Copying dark shell theme..."
cp -r ./assets/Marble-blue-dark ~/.themes

echo "Copying light shell theme..."
cp -r ./assets/Marble-blue-light ~/.themes

echo "Copying dark gtk3 themes..."
cp -r ./assets/custom-dark ~/.local/share/themes/

echo "Copying light gtk3 themes..."
cp -r ./assets/custom-light ~/.local/share/themes/

echo "All set!"
