#!/usr/bin/env python3
"""Linting script for DawnAI Strategy SDK.

This script provides convenient commands to run various linting tools
on the codebase.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure the tool is installed: pip install ruff black mypy")
        return False


def main():
    """Main linting script."""
    parser = argparse.ArgumentParser(description="Lint the DawnAI Strategy SDK")
    parser.add_argument(
        "tool",
        nargs="?",
        choices=["all", "ruff", "black", "mypy", "format", "check"],
        default="all",
        help="Which linting tool to run (default: all)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply automatic fixes where possible",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Specific files to lint (default: all Python files)",
    )
    
    args = parser.parse_args()
    
    # Determine files to lint
    if args.files:
        files = args.files
    else:
        files = ["dawnai", "examples"]
    
    success = True
    
    if args.tool in ["all", "ruff"]:
        # Run ruff
        ruff_cmd = ["python3.13", "-m", "ruff", "check"] + files
        if args.fix:
            ruff_cmd.append("--fix")
        success &= run_command(ruff_cmd, "Ruff linting")
    
    if args.tool in ["all", "black"]:
        # Run black
        if args.fix:
            black_cmd = ["python3.13", "-m", "black"] + files
            success &= run_command(black_cmd, "Black formatting")
        else:
            black_cmd = ["python3.13", "-m", "black", "--check"] + files
            success &= run_command(black_cmd, "Black format checking")
    
    if args.tool in ["all", "mypy"]:
        # Run mypy
        mypy_cmd = ["python3.13", "-m", "mypy"] + files
        success &= run_command(mypy_cmd, "MyPy type checking")
    
    if args.tool == "format":
        # Only run formatting tools
        ruff_cmd = ["python3.13", "-m", "ruff", "check", "--fix"] + files
        success &= run_command(ruff_cmd, "Ruff auto-fixing")
        
        black_cmd = ["python3.13", "-m", "black"] + files
        success &= run_command(black_cmd, "Black formatting")
    
    if args.tool == "check":
        # Only run checking tools (no fixes)
        ruff_cmd = ["python3.13", "-m", "ruff", "check"] + files
        success &= run_command(ruff_cmd, "Ruff linting")
        
        black_cmd = ["python3.13", "-m", "black", "--check"] + files
        success &= run_command(black_cmd, "Black format checking")
        
        mypy_cmd = ["python3.13", "-m", "mypy"] + files
        success &= run_command(mypy_cmd, "MyPy type checking")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All linting checks passed!")
        sys.exit(0)
    else:
        print("💥 Some linting checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
