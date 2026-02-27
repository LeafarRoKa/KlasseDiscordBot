#!/bin/bash

# Ensure we exit on any command failure
set -e

echo "Starting KlasseDiscordBot setup process..."

# 1. Update system dependencies implicitly
echo "Ensuring Tesseract-OCR is installed..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr python3-venv

# 2. Check if the environment directory exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# 3. Activate the environment
echo "Activating virtual environment..."
source venv/bin/activate

# 4. Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Execute the bot script
echo "Starting the Discord bot..."
python3 main.py
