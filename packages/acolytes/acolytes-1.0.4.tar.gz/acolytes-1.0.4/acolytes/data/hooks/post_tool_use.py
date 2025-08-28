#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def update_tool_log(tool_data):
    """Update tool log with results in SQLite"""
    try:
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
        if not db_path.exists():
            return  # Database not initialized yet
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Extract tool info and results
        tool_name = tool_data.get('tool_name', 'unknown')
        tool_result = tool_data.get('tool_result', {})
        tool_error = tool_data.get('tool_error')
        
        # Determine success and extract summary
        success = tool_error is None
        error_message = str(tool_error) if tool_error else None
        
        # Create result summary based on tool type
        result_summary = None
        lines_changed = None
        bytes_processed = None
        
        if success and tool_result:
            if tool_name == 'Read':
                # Extract lines read and file size
                if isinstance(tool_result, str):
                    lines_changed = len(tool_result.splitlines())
                    bytes_processed = len(tool_result.encode('utf-8'))
                    result_summary = f"Read {lines_changed} lines"
            elif tool_name in ['Write', 'Edit', 'MultiEdit']:
                result_summary = "File modified successfully"
                if isinstance(tool_result, str) and 'lines' in tool_result:
                    # Try to extract line count from result message
                    import re
                    match = re.search(r'(\d+)\s+lines?', tool_result)
                    if match:
                        lines_changed = int(match.group(1))
            elif tool_name == 'Bash':
                if isinstance(tool_result, str):
                    bytes_processed = len(tool_result.encode('utf-8'))
                    result_summary = f"Command executed ({bytes_processed} bytes output)"
            elif tool_name in ['Grep', 'Glob']:
                if isinstance(tool_result, str):
                    match_count = len(tool_result.splitlines())
                    result_summary = f"Found {match_count} matches"
            elif tool_name == 'Task':
                result_summary = "Task delegated to subagent"
        
        # Update the most recent log entry for this tool in this session
        # (matches by tool_name and timestamp within last 60 seconds)
        cursor.execute("""
            UPDATE tool_logs
            SET success = ?,
                error_message = ?,
                result_summary = ?,
                lines_changed = ?,
                bytes_processed = ?
            WHERE id = (
                SELECT id FROM tool_logs
                WHERE tool_name = ?
                  AND datetime(timestamp) > datetime('now', '-60 seconds')
                ORDER BY id DESC
                LIMIT 1
            )
        """, (
            success, error_message, result_summary,
            lines_changed, bytes_processed,
            tool_name
        ))        
        conn.commit()
        conn.close()
        
    except Exception:
        pass  # Fail silently to not interrupt tool execution

def handle_todo_sync(tool_data):
    """Handle TodoWrite tool - sync with SQLite"""
    conn = None
    try:
        tool_name = tool_data.get('tool_name', 'unknown')
        
        # Only process TodoWrite tool
        if tool_name != 'TodoWrite':
            return
            
        # Get the todo items from tool_input
        tool_input = tool_data.get('tool_input', {})
        todos = tool_input.get('todos', [])
        
        if not todos:
            return
            
        # Connect to database
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
        if not db_path.exists():
            return
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Use transaction for atomic operation
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # Get current session_id if available
            cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
            session_result = cursor.fetchone()
            session_id = session_result[0] if session_result else None
            
            # Clear existing todos (within transaction for safety)
            cursor.execute("DELETE FROM todos")
            
            # Insert new todos with correct column names
            timestamp = datetime.now().isoformat()
            for todo in todos:
                # Map 'content' to 'task' (correct column name)
                task = todo.get('content', '')
                status = todo.get('status', 'pending')
                
                # Store activeForm in metadata as JSON
                metadata = json.dumps({
                    'activeForm': todo.get('activeForm', ''),
                    'source': 'TodoWrite'
                })
                
                cursor.execute("""
                    INSERT INTO todos (task, status, created_at, session_id, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    task,
                    status,
                    timestamp,
                    session_id,
                    metadata
                ))
            
            # Commit transaction
            conn.commit()
            
        except Exception as inner_e:
            # Rollback on any error
            if conn:
                conn.rollback()
            # Log error for debugging (but don't break hook)
            print(f"TodoWrite sync error: {inner_e}", file=sys.stderr)
        
    except Exception as e:
        # Log outer errors
        print(f"TodoWrite handler error: {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

def main():
    try:
        # Read JSON input from stdin
        tool_data = json.load(sys.stdin)
        
        # Check command line arguments
        args = sys.argv[1:]
        
        # Execute based on arguments
        if '--todowrite' in args:
            handle_todo_sync(tool_data)
        
        # Always update tool log (default behavior)
        update_tool_log(tool_data)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Exit cleanly on any other error
        sys.exit(0)

if __name__ == '__main__':
    main()