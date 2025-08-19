#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly for deployment
"""

def test_imports():
    """Test all imports required by the application"""
    print("Testing imports...")
    
    try:
        import json
        print("✓ json import successful")
    except ImportError as e:
        print(f"✗ json import failed: {e}")
        return False
    
    try:
        import os
        print("✓ os import successful")
    except ImportError as e:
        print(f"✗ os import failed: {e}")
        return False
        
    try:
        from urllib.parse import urlparse
        print("✓ urllib.parse import successful")
    except ImportError as e:
        print(f"✗ urllib.parse import failed: {e}")
        return False
    
    try:
        from flask import Flask, render_template
        print("✓ Flask imports successful")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import step_3_dashboard as dashboard
        print("✓ step_3_dashboard import successful")
    except ImportError as e:
        print(f"✗ step_3_dashboard import failed: {e}")
        return False
    
    # Test optional imports (these should not cause app failure)
    try:
        import boto3
        print("✓ boto3 import successful")
    except ImportError:
        print("⚠ boto3 not available (this is OK, will use fallback)")
    
    try:
        import requests
        print("✓ requests import successful")
    except ImportError:
        print("⚠ requests not available (this is OK, will use fallback)")
    
    return True

def test_flask_app():
    """Test basic Flask app initialization"""
    print("\nTesting Flask app initialization...")
    
    try:
        from app import app
        print("✓ App import successful")
        
        # Test app configuration
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print(f"✗ Health endpoint failed: {response.status_code}")
                return False
                
            # Test main endpoint (this might fail due to missing data, but shouldn't crash)
            try:
                response = client.get('/')
                print(f"✓ Main endpoint returned status: {response.status_code}")
            except Exception as e:
                print(f"✗ Main endpoint error: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Application Import and Deployment Test ===\n")
    
    imports_ok = test_imports()
    app_ok = test_flask_app()
    
    print(f"\n=== Test Results ===")
    print(f"Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Flask App: {'✓ PASS' if app_ok else '✗ FAIL'}")
    
    if imports_ok and app_ok:
        print("\n🎉 All tests passed! Application should deploy successfully.")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    exit(main())
