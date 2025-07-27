#!/usr/bin/env python3
"""
Script to export conda environment for AI Agent Seller project.
This script helps create a comprehensive conda environment export.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return None

def export_current_environment():
    """Export the current conda environment."""
    print("🔍 Checking current conda environment...")
    
    # Get current environment name
    env_name = run_command("conda info --envs | grep '*' | awk '{print $1}'")
    if not env_name:
        print("❌ Could not determine current conda environment")
        return False
    
    print(f"📦 Current environment: {env_name}")
    
    # Export current environment
    output_file = f"conda-environment-current-{env_name}.yml"
    print(f"📝 Exporting to: {output_file}")
    
    result = run_command(f"conda env export > {output_file}")
    if result is not None:
        print(f"✅ Successfully exported to {output_file}")
        return True
    else:
        print("❌ Failed to export environment")
        return False

def create_minimal_export():
    """Create a minimal export with only explicitly installed packages."""
    print("🔍 Creating minimal export...")
    
    output_file = "conda-environment-minimal.yml"
    print(f"📝 Exporting to: {output_file}")
    
    result = run_command(f"conda env export --from-history > {output_file}")
    if result is not None:
        print(f"✅ Successfully exported minimal environment to {output_file}")
        return True
    else:
        print("❌ Failed to export minimal environment")
        return False

def list_installed_packages():
    """List all installed packages in current environment."""
    print("📋 Listing installed packages...")
    
    packages = run_command("conda list")
    if packages:
        print("Installed packages:")
        print(packages)
        return True
    else:
        print("❌ Could not list packages")
        return False

def main():
    """Main function."""
    print("🚀 AI Agent Seller - Conda Environment Exporter")
    print("=" * 50)
    
    # Check if conda is available
    if run_command("conda --version") is None:
        print("❌ Conda is not available. Please install conda first.")
        sys.exit(1)
    
    print("✅ Conda is available")
    
    # Check if we're in a conda environment
    if not os.environ.get('CONDA_DEFAULT_ENV'):
        print("⚠️  Not in a conda environment. Please activate your environment first.")
        print("   Example: conda activate ai-agent-seller")
        sys.exit(1)
    
    print(f"✅ In conda environment: {os.environ.get('CONDA_DEFAULT_ENV')}")
    
    # Menu
    while True:
        print("\n📋 Choose an option:")
        print("1. Export current environment (full)")
        print("2. Export minimal environment (from history)")
        print("3. List installed packages")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            export_current_environment()
        elif choice == "2":
            create_minimal_export()
        elif choice == "3":
            list_installed_packages()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 