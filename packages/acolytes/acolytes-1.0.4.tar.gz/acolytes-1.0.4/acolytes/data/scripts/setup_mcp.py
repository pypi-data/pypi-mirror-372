#!/usr/bin/env python3
"""
MCP Setup for Acolytes for Claude Code
Configures Model Context Protocol servers for the project.

Current MCPs configured:
- SQLite: Project database access
- Context7: Library documentation 
- Playwright: Web automation
- Server-Git: Git operations
- Server-Fetch: Web fetching
- Server-Everything: Testing/demo

Future MCPs to install manually:
- Chrome DevTools: Chrome debugging
- Puppeteer: Web automation alternative  
- PostgreSQL: PostgreSQL database access
"""
import os
import sys
import subprocess
from pathlib import Path

def find_project_root() -> Path:
    """Find project root by looking for .claude directory"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("No .claude directory found in current project")

def setup_mcp_sqlite():
    """Configure MCP SQLite server for the project"""
    
    # 1. Find project root (works from any subdirectory)
    try:
        project_root = find_project_root()
        print(f"Found project root: {project_root}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Make sure you're inside a project with .claude directory")
        return False
    
    claude_dir = project_root / ".claude"
    
    # 2. Check if SQLite MCP already exists
    try:
        check_result = subprocess.run([
            "claude", "mcp", "list"
        ], capture_output=True, text=True, timeout=30)
        
        if check_result.returncode == 0 and "MCP SQLite Server:" in check_result.stdout:
            print("\n[INFO] SQLite MCP already configured")
            print(f"[INFO] Database: {project_root}/.claude/memory/project.db")
            return True
    except subprocess.TimeoutExpired:
        print("[WARNING] MCP check timed out, continuing with setup...")
    except FileNotFoundError:
        print("[INFO] Claude CLI not found, continuing with setup...")
    except Exception as e:
        print(f"[WARNING] MCP check failed: {e}, continuing with setup...")
    
    # 2. Ensure memory directory exists
    memory_dir = claude_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    
    # 3. Set database path
    db_name = "project.db"
    db_path = memory_dir / db_name
    
    # 4. Create database if it doesn't exist
    if not db_path.exists():
        print(f"Creating database: {db_path}")
        # Initialize with schema
        init_sql = claude_dir / "scripts" / "init_db.sql"
        if init_sql.exists():
            import sqlite3
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    with open(init_sql, 'r', encoding='utf-8') as f:
                        conn.executescript(f.read())
                print("Database created with schema")
            except sqlite3.Error as e:
                print(f"ERROR: Failed to initialize database: {e}")
                return False
            except UnicodeDecodeError as e:
                print(f"ERROR: Failed to read SQL file (encoding issue): {e}")
                return False
        else:
            # Create empty database using context manager
            try:
                with open(db_path, 'a', encoding='utf-8') as f:
                    pass  # Just create the file
                print("Empty database created")
            except IOError as e:
                print(f"ERROR: Failed to create database file: {e}")
                return False
    
    # 5. Get absolute path for MCP configuration
    absolute_db_path = str(db_path.absolute())
    
    # For Windows, ensure proper path format
    if os.name == 'nt':
        # Windows path - use forward slashes or escaped backslashes
        absolute_db_path = absolute_db_path.replace('\\', '\\\\')
    
    print(f"\nDatabase path: {absolute_db_path}")
    
    # 6. Build MCP command
    # The command needs the full JSON configuration
    import json
    
    # Create the configuration JSON
    config = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite", str(db_path.absolute())]
    }
    config_json = json.dumps(config)
    
    mcp_args = [
        "claude", "mcp", "add",
        "--transport", "stdio",
        "sqlite",
        config_json
    ]
    
    print("\nConfiguring MCP SQLite...")
    print(f"Command: {' '.join(map(str, mcp_args))}")
    
    # 7. Execute MCP configuration using secure subprocess (works from within Claude Code)
    try:
        # Create secure JSON configuration without shell injection risk
        import json
        
        mcp_config = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sqlite", str(absolute_db_path)]
        }
        mcp_config_json = json.dumps(mcp_config)
        
        # Use list-based subprocess call instead of shell=True to prevent injection
        result = subprocess.run([
            "claude", "mcp", "add-json", "sqlite", mcp_config_json
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("\n[SUCCESS] SQLite MCP configured!")
            print(f"Output: {result.stdout.strip()}")
            print(f"\n[INFO] Database: {absolute_db_path}")
            print("[IMPORTANT] Restart Claude Code for changes to take effect")
            return True
        else:
            # Check if already exists
            if "already exists" in result.stderr or "already exists" in result.stdout:
                print("\n[INFO] SQLite MCP already configured")
                print("[ACTION] Remove with: claude mcp remove sqlite (if update needed)")
                return True
            
            print("\n[ERROR] Failed to configure SQLite MCP")
            print(f"Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Failed to execute MCP command: {e}")
        
        # Fallback to manual instructions
        print("\n[FALLBACK] Manual configuration:")
        print(f'claude mcp add-json sqlite \'{{\"command\":\"npx\",\"args\":[\"-y\",\"@modelcontextprotocol/server-sqlite\",\"{absolute_db_path}\"]}}\'')
        return False

def print_mcp_installation_guide():
    """Print manual installation guide for additional MCPs"""
    print("\n" + "="*60)
    print("ADDITIONAL MCP INSTALLATION GUIDE")
    print("="*60)
    print("\nTo install additional MCPs manually, use these commands:")
    print("\n1. Chrome DevTools MCP (benjaminr):")
    print('   claude mcp add-json chrome-devtools \'{"command": "python3", "args": ["server.py"], "env": {"CHROME_DEBUG_PORT": "9222"}}\'')
    
    print("\n2. Puppeteer MCP (Standard):")  
    print('   claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer')
    
    print("\n3. Puppeteer Real Browser MCP (Anti-detection):")
    print('   claude mcp add puppeteer-real-browser -- npx puppeteer-real-browser-mcp-server@latest')
    
    print("\n4. PostgreSQL MCP (requires PostgreSQL running):")
    print('   claude mcp add-json postgres \'{"command":"npx","args":["-y","@modelcontextprotocol/server-postgres","postgresql://user:password@localhost:5432/database"]}\'')
    
    print("\n5. Enhanced PostgreSQL MCP (Read/Write):")
    print('   claude mcp add-json postgres-enhanced \'{"command":"npx","args":["-y","@garethcott/enhanced-postgres","postgresql://user:password@localhost:5432/database"]}\'')
    
    print("\n\nMCP MANAGEMENT COMMANDS:")
    print("\n6. To list all installed MCPs:")
    print("   claude mcp list")
    print("\n7. To remove an MCP:")
    print("   claude mcp remove <mcp-name>")
    print("\n8. Windows users (native, not WSL) need cmd wrapper:")
    print("   claude mcp add my-server -- cmd /c npx -y @some/package")
    print("\nNOTE: Restart Claude Code after installing/removing MCPs")
    print("="*60)

def check_existing_mcps():
    """Check which MCPs are already configured"""
    print("\nChecking existing MCP configuration...")
    
    try:
        result = subprocess.run([
            "claude", "mcp", "list"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("Current MCPs:")
            print(result.stdout)
        else:
            print("Could not check MCP list")
    except subprocess.TimeoutExpired:
        print("MCP check timed out")
    except FileNotFoundError:
        print("Claude CLI not found")
    except Exception as e:
        print(f"Could not check MCP list: {e}")
    
    return True

if __name__ == "__main__":
    print("Acolytes for Claude Code MCP Setup")
    print("=" * 30)
    
    # Check existing MCPs
    check_existing_mcps()
    
    # Setup SQLite (core requirement)
    success = setup_mcp_sqlite()
    
    # Show installation guide for additional MCPs
    if success:
        print_mcp_installation_guide()
    
    sys.exit(0 if success else 1)