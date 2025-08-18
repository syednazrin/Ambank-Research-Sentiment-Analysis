#!/usr/bin/env python3
"""
Environment Setup Script for Nestle Sentiment Analysis Project
This script helps set up the Python environment and install required dependencies.
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error: pip is not available!")
        return False

def install_dependencies():
    """Install required dependencies from requirements.txt"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create a .env file template for API keys"""
    env_content = """# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set your preferred model
OPENAI_MODEL=gpt-4o-mini

# Optional: Set temperature for responses (0.0 = deterministic, 1.0 = creative)
OPENAI_TEMPERATURE=0.0
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit .env file and add your OpenAI API key")
    else:
        print("ℹ️  .env file already exists")

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🧪 Testing imports...")
    required_packages = [
        'langchain',
        'langchain_openai', 
        'langchain_community',
        'pandas',
        'numpy',
        'plotly',
        'openai'
    ]
    
    failed_imports = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def main():
    """Main setup function"""
    print("🚀 Setting up Nestle Sentiment Analysis Environment")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create environment file
    create_env_file()
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup incomplete. Please check the errors above.")
        return False
    
    print("\n🎉 Environment setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("2. Run: python step_2_sentimnt_analysis.py")
    print("3. Run: python step_3_dashboard.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

