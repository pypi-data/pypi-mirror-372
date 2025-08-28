"""
Init command for Acolytes - System initialization.

Initializes the Acolytes system with default configuration.
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import pkg_resources


def run() -> None:
    """Initialize Acolytes system."""
    print("🚀 Initializing Acolytes system...")
    
    try:
        # Step 1: Install uv if not present
        _install_uv_if_needed()
        
        # Step 2: Copy data files to ~/.claude/
        _copy_data_files()
        
        # Step 3: Generate settings.json
        _generate_settings_json()
        
        # Step 4: Show final status
        _show_final_status()
        
        print("✅ Initialization complete!")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)


def _install_uv_if_needed() -> None:
    """Install uv if not present on the system."""
    print("🔍 Checking for uv installation...")
    
    # Check if uv is already installed
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True, text=True)
        print("✅ uv is already installed")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 uv not found, installing...")
    
    system = platform.system().lower()
    
    try:
        if system == "windows":
            _install_uv_windows()
        else:
            _install_uv_unix()
        print("✅ uv installed successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not install uv automatically: {e}")
        print("💡 Please install uv manually from https://github.com/astral-sh/uv")


def _install_uv_windows() -> None:
    """Install uv on Windows using winget or PowerShell."""
    # Try winget first
    try:
        print("🔄 Attempting installation with winget...")
        subprocess.run(["winget", "install", "astral-sh.uv"], check=True, capture_output=True)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback to PowerShell installer
    print("🔄 Attempting installation with PowerShell...")
    powershell_cmd = [
        "powershell", "-Command",
        "Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression"
    ]
    subprocess.run(powershell_cmd, check=True)


def _install_uv_unix() -> None:
    """Install uv on Linux/Mac using curl."""
    print("🔄 Installing uv with curl...")
    curl_cmd = [
        "curl", "-LsSf", "https://astral.sh/uv/install.sh"
    ]
    sh_cmd = ["sh"]
    
    # Pipe curl output to sh
    curl_process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE)
    subprocess.run(sh_cmd, stdin=curl_process.stdout, check=True)
    curl_process.wait()


def _copy_data_files() -> None:
    """Copy data files to ~/.claude/ directory."""
    print("📂 Copying data files to ~/.claude/...")
    
    # Get target directory
    claude_dir = Path.home() / ".claude"
    claude_dir.mkdir(exist_ok=True)
    
    # Get package data directory
    try:
        data_dir = Path(pkg_resources.resource_filename('acolytes', 'data'))
    except Exception:
        # Fallback for development/editable installs
        current_dir = Path(__file__).parent.parent
        data_dir = current_dir / "data"
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Define directories to copy
    directories_to_copy = ['agents', 'commands', 'scripts', 'hooks', 'resources']
    total_files_copied = 0
    
    for dir_name in directories_to_copy:
        source_dir = data_dir / dir_name
        target_dir = claude_dir / dir_name
        
        if source_dir.exists():
            print(f"  📁 Copying {dir_name}/...")
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files recursively
            files_copied = _copy_directory_contents(source_dir, target_dir)
            total_files_copied += files_copied
            print(f"    ✅ {files_copied} files copied")
        else:
            print(f"  ⚠️  Directory not found: {source_dir}")
    
    # Note: All agents (including setup.*, flags, plan) are now in the agents directory
    # No need for separate internal agents handling
    
    print(f"✅ Total files copied: {total_files_copied}")


def _copy_directory_contents(source: Path, target: Path) -> int:
    """Copy directory contents recursively and return file count."""
    files_copied = 0
    
    for item in source.rglob('*'):
        if item.is_file():
            # Calculate relative path
            rel_path = item.relative_to(source)
            target_file = target / rel_path
            
            # Create parent directories if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(item, target_file)
            files_copied += 1
    
    return files_copied


def _generate_settings_json() -> None:
    """Generate settings.json configuration file."""
    print("⚙️  Generating settings.json...")
    
    claude_dir = Path.home() / ".claude"
    settings_file = claude_dir / "settings.json"
    
    # Detect Python command
    python_cmd = _detect_python_command()
    
    # Check if uv is available
    uv_available = _is_uv_available()
    
    # Generate settings
    settings = _create_settings_config(python_cmd, uv_available)
    
    # Write settings file
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Settings saved to {settings_file}")


def _detect_python_command() -> str:
    """Detect the best Python command to use."""
    candidates = ['python3', 'python', 'py']
    
    for cmd in candidates:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, check=True)
            if 'Python 3' in result.stdout:
                return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Default fallback
    return 'python'


def _is_uv_available() -> bool:
    """Check if uv is available on the system."""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _create_settings_config(python_cmd: str, uv_available: bool) -> Dict[str, Any]:
    """Create the settings configuration dictionary."""
    
    # Base Python command
    if uv_available:
        base_python_cmd = "uv run python"
    else:
        base_python_cmd = python_cmd
    
    settings = {
        "system": {
            "python_command": python_cmd,
            "uv_available": uv_available,
            "base_command": base_python_cmd
        },
        "hooks": {
            "session_start": {
                "enabled": True,
                "file": "session_start.py",
                "description": "Load previous session context from SQLite"
            },
            "todo_sync": {
                "enabled": True,
                "file": "todo_sync.py", 
                "description": "Sync TodoWrite with SQLite todos table"
            },
            "pre_tool_use": {
                "enabled": True,
                "file": "pre_tool_use.py",
                "description": "Tool usage tracking and Git MCP protection"
            },
            "post_tool_use": {
                "enabled": True,
                "file": "post_tool_use.py",
                "description": "Post tool execution processing"
            },
            "subagent_stop": {
                "enabled": True,
                "file": "subagent_stop.py",
                "description": "Handle agent completion with transcript parsing"
            },
            "user_prompt_submit": {
                "enabled": True,
                "file": "user_prompt_submit.py",
                "description": "Process user input"
            },
            "stop": {
                "enabled": True,
                "file": "stop.py",
                "description": "Session termination with auto-save"
            },
            "pre_compact": {
                "enabled": True,
                "file": "pre_compact.py",
                "description": "Pre-compaction memory optimization"
            }
        },
        "database": {
            "path": "~/.claude/memory/project.db",
            "mcp_server": "MCP_SQLite_Server"
        },
        "agents": {
            "total_count": 59,
            "global_agents": 52,
            "internal_agents": 7,
            "acolytes": "dynamic",
            "catalog_file": "~/.claude/resources/rules/agent-routing-catalog.md"
        },
        "features": {
            "flags_system": True,
            "parallel_execution": True,
            "autonomous_spawning": True,
            "memory_persistence": True,
            "hooks_system": True
        },
        "version": "1.0.0",
        "initialized": True
    }
    
    return settings


def _show_final_status() -> None:
    """Show final status and requirements check."""
    print("\n📋 Final Status Check:")
    
    claude_dir = Path.home() / ".claude"
    
    # Check directory structure
    required_dirs = ['agents', 'commands', 'scripts', 'hooks', 'resources']
    for dir_name in required_dirs:
        dir_path = claude_dir / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.rglob('*')))
            print(f"  ✅ {dir_name}/ ({file_count} files)")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
    
    # Check settings file
    settings_file = claude_dir / "settings.json"
    if settings_file.exists():
        print(f"  ✅ settings.json")
    else:
        print(f"  ❌ settings.json (missing)")
    
    # Check Python and uv
    python_cmd = _detect_python_command()
    uv_available = _is_uv_available()
    
    print(f"  ✅ Python: {python_cmd}")
    if uv_available:
        print(f"  ✅ uv: available")
    else:
        print(f"  ⚠️  uv: not available (recommended)")
    
    print("\n💡 Next steps:")
    print("  1. Restart Claude Code to load new configuration")
    print("  2. Run: claude /setup (to initialize project-specific settings)")
    print("  3. Use: /todo to manage tasks")
    print("  4. Use: @agent-name to invoke specific agents")
    print("  5. Check: ~/.claude/settings.json for configuration details")