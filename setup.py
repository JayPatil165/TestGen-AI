"""
Custom setup script with post-install PATH configuration for Windows.
"""
import sys
import platform
from pathlib import Path
from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Custom install command that adds testgen to PATH on Windows."""
    
    def run(self):
        # Run the standard install
        install.run(self)
        
        # After installation, try to add to PATH on Windows
        if platform.system() == "Windows":
            self._setup_windows_path()
    
    def _setup_windows_path(self):
        """Add Python Scripts folder to Windows PATH."""
        try:
            import winreg
            
            # Find Scripts folder
            scripts_path = None
            candidate = Path(sys.executable).parent / "Scripts"
            if candidate.exists():
                scripts_path = str(candidate)
            
            if not scripts_path:
                candidate = Path(sys.prefix) / "Scripts"
                if candidate.exists():
                    scripts_path = str(candidate)
            
            if scripts_path:
                try:
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
                            print(f"\n✅ Added {scripts_path} to Windows PATH")
                            print("   Restart your terminal to use 'testgen' command directly\n")
                        except PermissionError:
                            print(f"\n⚠️  Could not add to PATH (admin required)")
                            print(f"   Use: python -m testgen (always works)")
                            print(f"   Or run: testgen setup (with admin terminal)\n")
                    
                    winreg.CloseKey(reg_key)
                except Exception as e:
                    print(f"\n⚠️  Could not configure PATH: {e}")
                    print(f"   Use: python -m testgen (always works)\n")
        except Exception:
            pass  # Silently fail


# Read pyproject.toml and extract settings
def get_version():
    """Extract version from pyproject.toml."""
    with open("pyproject.toml") as f:
        for line in f:
            if line.startswith("version ="):
                return line.split('"')[1]
    return "0.1.9"


setup(
    cmdclass={
        "install": PostInstallCommand,
    },
)
