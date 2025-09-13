#!/bin/bash
# AegisSec Linux/macOS Launcher Script
# Developed by RunTime Terrors

echo ""
echo "========================================"
echo "   🛡️ AegisSec Security Scanner"
echo "   Developed by RunTime Terrors"
echo "   AI-Powered Penetration Testing"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ and try again"
    echo ""
    echo "On Kali Linux: sudo apt update && sudo apt install python3 python3-pip"
    echo "On Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "On macOS: brew install python3"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ ERROR: pip3 is not installed"
    echo "On Kali Linux: sudo apt install python3-pip"
    echo "On Ubuntu/Debian: sudo apt install python3-pip"
    echo "On macOS: python3 -m ensurepip --upgrade"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt --user --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        echo "Trying with sudo..."
        sudo pip3 install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install dependencies even with sudo"
            echo "Please install manually: pip3 install -r requirements.txt"
            exit 1
        fi
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️ requirements.txt not found, skipping dependency installation"
fi

# Check if config exists, if not create from example
if [ ! -f "config/config.json" ]; then
    echo "⚙️ Configuration not found. Creating from example..."
    if [ -f "config/config.example.json" ]; then
        cp config/config.example.json config/config.json
        echo "✅ Config created from example"
        echo "📝 Note: Edit config/config.json to set your API keys if needed"
    else
        echo "⚠️ No config example found, running setup..."
        python3 setup.py
        if [ $? -ne 0 ]; then
            echo "❌ Setup failed. Please check the error messages above."
            exit 1
        fi
    fi
    echo "✅ Configuration ready"
fi

# Check for common Kali tools
echo "🔧 Checking for penetration testing tools..."
TOOLS=("nmap" "nikto" "dirb" "hydra" "sqlmap")
MISSING_TOOLS=()

for tool in "${TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "⚠️ Some penetration testing tools are missing: ${MISSING_TOOLS[*]}"
    echo "📝 Install them with: sudo apt install ${MISSING_TOOLS[*]}"
    echo "🔄 AegisSec will still work but some features may be limited"
else
    echo "✅ All essential penetration testing tools found"
fi

# Set environment variable for the API key (optional)
export OPENROUTER_API_KEY="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"

echo ""
echo "🚀 Starting AegisSec AI-Powered Penetration Testing..."
echo "🤖 AI System: DeepSeek Chat v3.1 (Free)"
echo "🛡️ Mode: Intelligent Automation"
echo ""

# Run the main application
python3 main.py

echo ""
echo "Thank you for using AegisSec! 🛡️"
echo "Session logs saved in: logs/"
echo "Reports generated in: reports/"
