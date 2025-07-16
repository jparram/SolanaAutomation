#!/usr/bin/env python3
import sys
import os

print("Python test script starting...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Environment variables loaded: {os.path.exists('.env')}")

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("dotenv loaded successfully")
    
    # Test the app launcher
    print("Attempting to import app_launcher...")
    sys.path.insert(0, '.')
    
    print("Starting app launcher...")
    exec(open('app_launcher.py').read())
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
