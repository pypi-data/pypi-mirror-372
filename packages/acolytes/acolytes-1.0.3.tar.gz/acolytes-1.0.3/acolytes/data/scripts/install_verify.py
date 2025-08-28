#!/usr/bin/env python
"""
Acolytes for Claude Code - Installation Verification Script
Verifies that all components are properly installed and accessible
Works cross-platform thanks to Git Bash on Windows
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_mark():
    """Return check mark without emoji for Windows compatibility"""
    return f"{GREEN}[OK]{RESET}"

def cross_mark():
    """Return cross mark without emoji for Windows compatibility"""
    return f"{RED}[FAIL]{RESET}"

def warning_mark():
    """Return warning mark without emoji for Windows compatibility"""
    return f"{YELLOW}[WARN]{RESET}"

def info_mark():
    """Return info mark without emoji for Windows compatibility"""
    return f"{BLUE}[INFO]{RESET}"

def check_python():
    """Check Python version"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 10:
            print(f"{check_mark()} Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"{cross_mark()} Python {version.major}.{version.minor} (need 3.10+)")
            return False
    except:
        print(f"{cross_mark()} Python not detected")
        return False

def check_command(command, name=None):
    """Check if a command is available"""
    if name is None:
        name = command
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0] if result.stdout else "installed"
            print(f"{check_mark()} {name}: {version}")
            return True
    except:
        pass
    print(f"{cross_mark()} {name} not found")
    return False

def check_claude_directories():
    """Check Claude directory structure"""
    home = Path.home()
    claude_dir = home / '.claude'
    
    required_dirs = [
        '.claude',
        '.claude/agents', 
        '.claude/commands',
        '.claude/hooks',
        '.claude/memory',
        '.claude/resources',
        '.claude/scripts'
    ]
    
    print(f"\n{info_mark()} Checking Claude directories:")
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = home / dir_name
        if dir_path.exists():
            # Count files in agents directory
            if dir_name == '.claude/agents':
                agent_count = len(list(dir_path.glob('*.md')))
                print(f"  {check_mark()} {dir_name} ({agent_count} agents)")
            else:
                print(f"  {check_mark()} {dir_name}")
        else:
            print(f"  {cross_mark()} {dir_name} missing")
            all_good = False
    
    return all_good

def check_mcp_servers():
    """Check MCP server installations"""
    print(f"\n{info_mark()} Checking MCP servers:")
    
    # Try to run claude mcp list
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            
            # Parse MCP server list
            servers = {
                'sqlite': 'SQLite (Critical)',
                'server-git': 'Git MCP',
                'server-fetch': 'Fetch MCP',
                'code-index': 'Code Index (Speed)',
                'puppeteer': 'Puppeteer (Optional)',
                '21st-dev_magic': 'Magic UI (Optional)'
            }
            
            for server_key, server_name in servers.items():
                if server_key in output:
                    if 'Connected' in output or 'connected' in output:
                        print(f"  {check_mark()} {server_name}")
                    else:
                        print(f"  {warning_mark()} {server_name} (not connected)")
                else:
                    if 'Critical' in server_name or 'Speed' in server_name:
                        print(f"  {cross_mark()} {server_name} - REQUIRED")
                    else:
                        print(f"  {warning_mark()} {server_name} - optional")
            return True
    except Exception as e:
        print(f"  {cross_mark()} Could not check MCP servers: {e}")
        return False

def check_project_setup(project_path=None):
    """Check if current project is set up"""
    if project_path is None:
        project_path = Path.cwd()
    
    print(f"\n{info_mark()} Checking project setup in: {project_path}")
    
    checks = {
        '.claude/CLAUDE.md': 'Project configuration',
        '.claude/memory/project.db': 'SQLite database',
        '.claude/project/vision.md': 'Vision documentation',
        '.claude/project/architecture.md': 'Architecture documentation',
        '.claude/agents': 'Project acolytes'
    }
    
    all_good = True
    for path, description in checks.items():
        full_path = project_path / path
        if full_path.exists():
            if path.endswith('.db'):
                # Check database size
                size = full_path.stat().st_size / 1024 / 1024  # MB
                print(f"  {check_mark()} {description} ({size:.1f} MB)")
            elif path.endswith('agents'):
                # Count acolytes
                acolyte_count = len(list(full_path.glob('acolyte.*.md')))
                print(f"  {check_mark()} {description} ({acolyte_count} acolytes)")
            else:
                print(f"  {check_mark()} {description}")
        else:
            print(f"  {warning_mark()} {description} not found")
            if 'database' in description.lower():
                all_good = False
    
    return all_good

def check_git_bash():
    """Check if running in Git Bash on Windows"""
    if sys.platform == 'win32':
        # Check for MSYSTEM variable (Git Bash indicator)
        msystem = os.environ.get('MSYSTEM')
        if msystem:
            print(f"{check_mark()} Running in Git Bash ({msystem})")
            return True
        else:
            print(f"{warning_mark()} Not in Git Bash - Claude may have issues")
            return False
    return True  # Not Windows, so OK

def main():
    """Main verification function"""
    print("=" * 60)
    print("Acolytes for Claude Code - Installation Verification")
    print("=" * 60)
    
    results = {}
    
    # System checks
    print(f"\n{info_mark()} System Requirements:")
    results['python'] = check_python()
    results['git'] = check_command('git', 'Git')
    results['node'] = check_command('node', 'Node.js')
    results['npm'] = check_command('npm', 'npm')
    results['uv'] = check_command('uv', 'uv (Python package manager)')
    results['claude'] = check_command('claude', 'Claude CLI')
    
    if sys.platform == 'win32':
        results['git_bash'] = check_git_bash()
    
    # Claude structure
    results['directories'] = check_claude_directories()
    
    # MCP servers
    results['mcp'] = check_mcp_servers()
    
    # Project setup
    results['project'] = check_project_setup()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    critical_ok = all([
        results.get('python'),
        results.get('git'),
        results.get('claude'),
        results.get('directories')
    ])
    
    if critical_ok:
        print(f"{check_mark()} Critical components installed")
    else:
        print(f"{cross_mark()} Missing critical components")
    
    if results.get('project'):
        print(f"{check_mark()} Project is set up")
    else:
        print(f"{warning_mark()} Project needs setup - run: claude /setup")
    
    # Installation commands for missing components
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    if not results.get('uv'):
        print("\nInstall uv:")
        if sys.platform == 'win32':
            print("  winget install astral-sh.uv")
        else:
            print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
    
    if not results.get('directories'):
        print("\nClone and install Acolytes for Claude Code:")
        print("  git clone https://github.com/unmasSk/Acolytes.git")
        print("  cd Acolytes")
        if sys.platform == 'win32':
            print("  xcopy /e /i .claude %USERPROFILE%\\.claude")
        else:
            print("  cp -r .claude/* ~/.claude/")
    
    if not results.get('mcp'):
        print("\nInstall critical MCP servers:")
        print("  claude mcp add sqlite -s user -- npx -y @modelcontextprotocol/server-sqlite")
        print("  claude mcp add server-git -s user -- npx -y @modelcontextprotocol/server-git")
        print("  claude mcp add code-index -s user -- npx -y @modelcontextprotocol/server-code-index")
    
    if not results.get('project'):
        print("\nSet up your project:")
        print("  cd /path/to/your/project")
        print("  claude /setup")
    
    print("\n" + "=" * 60)
    
    # Exit code
    if critical_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()