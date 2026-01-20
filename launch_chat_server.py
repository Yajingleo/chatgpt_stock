#!/usr/bin/env python3
"""
Quick Launcher for ADK Stock Chat Server

This script provides an easy way to launch the ADK Stock Chat Server
with different configuration options.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    """Main launcher interface"""
    print("🤖 ADK Stock Chat Server Launcher")
    print("=" * 50)
    
    # Check if the server file exists
    server_file = Path(__file__).parent / "adk_web_chat_server.py"
    if not server_file.exists():
        print("❌ Error: adk_web_chat_server.py not found!")
        return
    
    print("Choose an option:")
    print("1. 🚀 Quick Start (default settings)")
    print("2. ⚙️  Custom Settings")
    print("3. 🔧 Development Mode (no auto-browser)")
    print("4. ❓ Help")
    print("5. 🚪 Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1" or choice == "":
                launch_default()
                break
            elif choice == "2":
                launch_custom()
                break
            elif choice == "3":
                launch_dev_mode()
                break
            elif choice == "4":
                show_help()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

def launch_default():
    """Launch with default settings"""
    print("\n🚀 Launching ADK Stock Chat Server with default settings...")
    print("   Host: localhost")
    print("   Port: Auto-detect")
    print("   Browser: Will open automatically")
    print()
    
    try:
        subprocess.run([sys.executable, "adk_web_chat_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching server: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

def launch_custom():
    """Launch with custom settings"""
    print("\n⚙️ Custom Settings")
    
    # Get host
    host = input("Enter host (default: localhost): ").strip() or "localhost"
    
    # Get port
    while True:
        port_input = input("Enter port (default: 8080): ").strip()
        if not port_input:
            port = "8080"
            break
        try:
            port_num = int(port_input)
            if 1024 <= port_num <= 65535:
                port = port_input
                break
            else:
                print("❌ Port must be between 1024 and 65535")
        except ValueError:
            print("❌ Invalid port number")
    
    # Auto-open browser
    auto_browser = input("Auto-open browser? (y/N): ").strip().lower()
    no_browser = "--no-browser" if auto_browser not in ["y", "yes"] else ""
    
    print(f"\n🚀 Launching server at {host}:{port}")
    
    cmd = [sys.executable, "adk_web_chat_server.py", "--host", host, "--port", port]
    if no_browser:
        cmd.append(no_browser)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching server: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

def launch_dev_mode():
    """Launch in development mode"""
    print("\n🔧 Launching in development mode (no auto-browser)...")
    
    try:
        subprocess.run([sys.executable, "adk_web_chat_server.py", "--no-browser"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching server: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

def show_help():
    """Show help information"""
    print("\n❓ ADK Stock Chat Server Help")
    print("=" * 40)
    print()
    print("📋 Features:")
    print("• Natural language chat interface for stock analysis")
    print("• Real-time stock recommendations and sentiment analysis")
    print("• Integration with ADK Stock Agent system")
    print("• Modern, responsive web interface")
    print()
    print("💬 Example Queries:")
    print("• 'Give me stock recommendations'")
    print("• 'Analyze AAPL stock'")
    print("• 'What's the sentiment on Tesla?'")
    print("• 'How is the market doing today?'")
    print()
    print("🔧 Manual Launch:")
    print("python adk_web_chat_server.py [options]")
    print()
    print("Options:")
    print("  --host HOST     Host to bind to (default: localhost)")
    print("  --port PORT     Port to bind to (default: 8080)")
    print("  --no-browser    Don't open browser automatically")
    print()
    print("📝 Requirements:")
    print("• Python 3.9+")
    print("• ADK Stock Agent components")
    print("• Internet connection for stock data")
    print()

if __name__ == "__main__":
    main()