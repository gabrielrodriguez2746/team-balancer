#!/usr/bin/env python3
"""
Launcher script for the Streamlit Team Balancer
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application"""
    print("🚀 Starting Team Balancer (Streamlit)...")
    print("📱 Opening web interface...")
    print("🌐 Access the app at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "team_balancer_streamlit.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Team Balancer stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        print("💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main() 