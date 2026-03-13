#!/usr/bin/env python
"""
TestGen AI entry point with automatic Windows PATH configuration.
This script is called when 'testgen' command is executed.
"""
import sys
import platform
from pathlib import Path


def _ensure_in_path():
    """Ensure testgen Scripts folder is in Windows PATH."""
    if platform.system() != "Windows":
        return
    
    try:
        import winreg
        
        scripts_path = None
        candidate = Path(sys.executable).parent / "Scripts"
        if candidate.exists():
            scripts_path = str(candidate)
        
        if not scripts_path:
            candidate = Path(sys.prefix) / "Scripts"
            if candidate.exists():
                scripts_path = str(candidate)
        
        if scripts_path:
            key_path = r"Environment"
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            except FileNotFoundError:
                reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            
            try:
                path_value = winreg.QueryValueEx(reg_key, "Path")[0]
            except FileNotFoundError:
                path_value = ""
            
            # Check if already in PATH
            if not path_value or scripts_path.lower() not in path_value.lower():
                new_path = f"{path_value};{scripts_path}" if path_value else scripts_path
                try:
                    winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                except PermissionError:
                    pass  # Silently ignore
            
            winreg.CloseKey(reg_key)
    except Exception:
        pass


def main():
    """Entry point for testgen command."""
    # Try to ensure PATH is set (Windows only)
    try:
        _ensure_in_path()
    except Exception:
        pass
    
    # Import and run the CLI
    from testgen.main import cli
    cli()


if __name__ == "__main__":
    main()
