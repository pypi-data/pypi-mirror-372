#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

# BACKUP: This is the original pre_tool_use.py content

import json
import sys
import re
import sqlite3
from datetime import datetime
from pathlib import Path

def is_dangerous_rm_command(command):
    """
    Comprehensive detection of dangerous rm commands.
    Matches various forms of rm -rf and similar destructive patterns.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = ' '.join(command.lower().split())
    
    # Pattern 1: Standard rm -rf variations
    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf, rm -fr, rm -Rf, etc.
        r'\brm\s+.*-[a-z]*f[a-z]*r',  # rm -fr variations
        r'\brm\s+--recursive\s+--force',  # rm --recursive --force
        r'\brm\s+--force\s+--recursive',  # rm --force --recursive
        r'\brm\s+-r\s+.*-f',  # rm -r ... -f
        r'\brm\s+-f\s+.*-r',  # rm -f ... -r
    ]
    
    # Check for dangerous patterns
    for pattern in patterns:
        if re.search(pattern, normalized):
            return True
    
    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    dangerous_paths = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~',           # Home directory
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards in general rm -rf context
        r'\.',          # Current directory
        r'\.\s*$',      # Current directory at end of command
    ]
    
    if re.search(r'\brm\s+.*-[a-z]*r', normalized):  # If rm has recursive flag
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True
    
    return False

def is_any_delete_command(command):
    """
    Block dangerous deletion commands while allowing legitimate scripts and tools.
    Protects against file/folder deletion but allows uv run, npm, etc.
    """
    # Normalize command
    normalized = ' '.join(command.lower().split())
    
    # Skip if it's a legitimate tool/script execution
    safe_patterns = [
        r'^uv\s+run',         # uv run commands
        r'^npm\s+',           # npm commands  
        r'^pip\s+',           # pip commands
        r'^python\s+',        # python scripts
        r'^node\s+',          # node scripts
        r'^cd\s+',            # directory changes
        r'\.py\s*$',          # python script execution
        r'\.js\s*$',          # javascript execution
        r'\.sh\s*$',          # shell script execution
    ]
    
    for pattern in safe_patterns:
        if re.search(pattern, normalized):
            return False
    
    # Now check for actual deletion command patterns
    delete_patterns = [
        r'^rm\s+',           # Direct rm command (not in file paths)
        r'\s+rm\s+',         # rm as separate command
        r'^rmdir\s+',        # Remove directory
        r'^del\s+',          # Windows delete
        r'^delete\s+',       # Delete command
        r'^unlink\s+',       # Unlink files
        r'^trash\s+',        # Move to trash
        r'^shred\s+',        # Secure delete
        r'^wipe\s+',         # Wipe files
        r'>\s*[^|>]',        # Dangerous redirects (but allow >> and pipes)
        r'^truncate\s+',     # Truncate command
    ]
    
    # Check for actual deletion patterns
    for pattern in delete_patterns:
        if re.search(pattern, normalized):
            return True
    
    # Block git clean (removes untracked files)
    if re.search(r'^git\s+clean', normalized):
        return True
    
    # Block find with -delete flag
    if re.search(r'^find\b.*-delete', normalized):
        return True
    
    # Block dangerous xargs rm combinations (but not in file paths)
    if re.search(r'xargs\s+rm\s+', normalized):
        return True
    
    return False

def is_env_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access .env files containing sensitive data.
    Allows setup.environment.md and other legitimate files with 'env' in the name.
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')
            # Only block exact .env files, not files containing 'env' in name
            filename = Path(file_path).name.lower()
            if filename == '.env' or (filename.startswith('.env.') and not filename.endswith('.sample')):
                return True
        
        # Check bash commands for .env file access
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            # Pattern to detect actual .env file access (but allow .env.sample and other files)
            env_patterns = [
                r'\b\.env\b(?!\.sample)(?!\w)',  # .env but not .env.sample or .environment
                r'cat\s+.*\.env\b(?!\.sample)(?!\w)',  # cat .env
                r'echo\s+.*>\s*\.env\b(?!\.sample)(?!\w)',  # echo > .env
                r'touch\s+.*\.env\b(?!\.sample)(?!\w)',  # touch .env
                r'cp\s+.*\.env\b(?!\.sample)(?!\w)',  # cp .env
                r'mv\s+.*\.env\b(?!\.sample)(?!\w)',  # mv .env
            ]
            
            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True
    
    return False

def is_dangerous_git_operation(tool_name, tool_input):
    """Check if git MCP operation could expose .git directory."""
    if tool_name != 'mcp__server-git__git_add':
        return False
    
    # Check if trying to add everything including .git
    if isinstance(tool_input, dict):
        files = tool_input.get('files', [])
        if files:
            # Convert to string to handle various formats
            files_str = str(files).lower()
            # Dangerous patterns that could include .git
            dangerous_patterns = ['.', '*', 'all', '.git']
            return any(pattern in files_str for pattern in dangerous_patterns)
    
    return False

def log_to_sqlite(tool_data, blocked=False, block_reason=None):
    """Log tool usage to SQLite database"""
    try:
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
        if not db_path.exists():
            return  # Database not initialized yet
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get current session_id
        cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
        session = cursor.fetchone()
        session_id = session[0] if session else None
        
        # Extract tool info
        tool_name = tool_data.get('tool_name', 'unknown')
        parameters = json.dumps(tool_data.get('tool_input', {}))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Determine tool category
        tool_category = 'unknown'
        if tool_name in ['Read', 'Write', 'Edit', 'MultiEdit']:
            tool_category = 'file'
        elif tool_name in ['Grep', 'Glob', 'LS']:
            tool_category = 'search'
        elif tool_name in ['Bash', 'BashOutput', 'KillBash']:
            tool_category = 'execution'
        elif tool_name in ['Task', 'WebSearch', 'WebFetch', 'TodoWrite']:
            tool_category = 'ai'
        elif tool_name.startswith('mcp__'):
            tool_category = 'mcp'
        
        # Extract file if applicable
        file_affected = None
        tool_input = tool_data.get('tool_input', {})
        if 'file_path' in tool_input:
            file_affected = tool_input['file_path']
        elif 'path' in tool_input:
            file_affected = tool_input['path']
        
        # Insert pre-tool log (will be updated in post_tool_use)
        cursor.execute("""
            INSERT INTO tool_logs (
                session_id, tool_name, tool_category, parameters,
                file_affected, blocked_by_hook, hook_message, 
                success, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, tool_name, tool_category, parameters,
            file_affected, blocked, block_reason,
            0 if blocked else 1, timestamp
        ))
        
        conn.commit()
        conn.close()
        
    except Exception:
        pass  # Fail silently to not interrupt tool execution

DB_PATH_TODO = Path.cwd() / '.claude' / 'memory' / 'project.db'

def get_timestamp_todo_sync():
    """Get current timestamp without seconds for todo_sync operations"""
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def sync_todo_to_sqlite(todo, session_id=None):
    """Simple sync: copy Claude TODO to SQLite"""
    if not DB_PATH_TODO.exists():
        return None

    conn = sqlite3.connect(str(DB_PATH_TODO))
    cursor = conn.cursor()

    try:
        content = todo.get('content', '')
        status = todo.get('status', 'pending')
        claude_id = todo.get('id', '')

        timestamp = get_timestamp_todo_sync()
        completed_at = timestamp if status == 'completed' else None

        # Check if exists by claude_id in context JSON
        cursor.execute("SELECT id FROM todos WHERE json_extract(context, '$.claude_id') = ?", (claude_id,))

        existing = cursor.fetchone()

        if existing:
            # Update existing
            cursor.execute("""
                UPDATE todos SET
                    task = ?, status = ?, updated_at = ?, completed_at = ?, updated_by = 'claude'
                WHERE id = ?
            """, (content, status, timestamp, completed_at, existing[0]))
        else:
            # Create new
            context = {'claude_id': claude_id, 'auto_synced': True}
            cursor.execute("""
                INSERT INTO todos (task, status, created_at, updated_at, completed_at,
                                 created_by, context, auto_created, session_id)
                VALUES (?, ?, ?, ?, ?, 'claude', ?, 1, ?)
            """, (content, status, timestamp, timestamp, completed_at,
                  json.dumps(context), session_id))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_current_session_id_todo_sync():
    """Get current session ID for todo_sync operations"""
    if not DB_PATH_TODO.exists():
        return None

    try:
        conn = sqlite3.connect(str(DB_PATH_TODO))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
        session = cursor.fetchone()
        conn.close()
        return session[0] if session else None
    except Exception:
        return None

def process_todowrite_integrated(todos_data):
    """Simple process: sync all TODOs to SQLite (integrated)"""
    todos = todos_data.get('todos', [])
    if not todos:
        return

    session_id = get_current_session_id_todo_sync()

    for todo in todos:
        sync_todo_to_sqlite(todo, session_id)

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Block delete_file tool completely
        if tool_name == 'delete_file':
            log_to_sqlite(input_data, blocked=True, block_reason="delete_file tool is blocked")
            print("BLOCKED: The delete_file tool is disabled. File deletion is not allowed.", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Check for .env file access (blocks access to sensitive environment files)
        if is_env_file_access(tool_name, tool_input):
            log_to_sqlite(input_data, blocked=True, block_reason="Access to .env files not allowed")
            print("BLOCKED: Access to .env files containing sensitive data is prohibited", file=sys.stderr)
            print("Use .env.sample for template files instead", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Check for dangerous Git MCP operations
        if is_dangerous_git_operation(tool_name, tool_input):
            log_to_sqlite(input_data, blocked=True, block_reason="Git MCP operation could expose .git directory")
            print("BLOCKED: Git MCP operation with '.' or '*' could commit .git directory", file=sys.stderr)
            print("Use 'git add -A' via Bash tool instead for safety", file=sys.stderr)
            sys.exit(2)
        
        # Check for ANY deletion commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            
            # Block ALL deletion commands - complete protection
            if is_any_delete_command(command):
                log_to_sqlite(input_data, blocked=True, block_reason="Deletion command blocked - ALL deletions are prohibited")
                print("BLOCKED: Deletion commands are not allowed. ALL file/folder deletion is prohibited.", file=sys.stderr)
                print("Protected commands include: rm, rmdir, del, unlink, trash, shred, git clean, etc.", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
            
            # Also check for dangerous rm -rf patterns (redundant but kept for specific logging)
            elif is_dangerous_rm_command(command):
                log_to_sqlite(input_data, blocked=True, block_reason="Dangerous rm command detected")
                print("BLOCKED: Dangerous rm command detected and prevented", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Log successful pre-tool call to SQLite
        log_to_sqlite(input_data)
        
        # Special handling for TodoWrite
        if tool_name == 'TodoWrite':
            process_todowrite_integrated(tool_input)
        
        sys.exit(0)

    except Exception:
        # Log error but don\'t block
        pass # Fail silently to not interrupt tool execution
        sys.exit(0)

if __name__ == '__main__':
    main()