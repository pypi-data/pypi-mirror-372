#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import sqlite3
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


def compute_quality_score(accomplishments, errors, breakthrough=None, decisions=None, bugs_fixed=None):
    """
    Compute session quality score based on content and outcomes.
    
    Args:
        accomplishments (list): List of accomplishment strings
        errors (list): List of error strings  
        breakthrough (str, optional): Breakthrough moment text
        decisions (list, optional): List of decision strings
        bugs_fixed (list, optional): List of bug fix strings
        
    Returns:
        int: Quality score from 1-10
        
    Scoring System:
        - Base score: 5 (neutral starting point)
        - Accomplishments: +1 to +3 points (capped at 3 max)
        - Errors: -1 to -2 points (capped at 2 max)
        - Breakthrough: +1 point if substantial content (>30 chars)
        - Rich content: +1 point if total session content >500 chars
        - Final range: 1-10 (clamped to prevent overflow)
    """
    score = 5  # neutral base
    
    # Accomplishments contribution (max +3)
    score += min(3, len(accomplishments))
    
    # Errors penalty (max -2)
    score -= min(2, len(errors))
    
    # Breakthrough bonus (+1 if substantial)
    if breakthrough and len(breakthrough) > 30:
        score += 1
    
    # Rich content bonus - include all content types
    total_content_length = 0
    total_content_length += sum(len(str(x)) for x in accomplishments)
    total_content_length += len(breakthrough or "")
    
    if decisions:
        total_content_length += sum(len(str(x)) for x in decisions)
    
    if bugs_fixed:
        total_content_length += sum(len(str(x)) for x in bugs_fixed)
    
    if total_content_length > 500:
        score += 1  # rich content bonus
    
    # Clamp to valid range [1, 10]
    return max(1, min(10, score))


def backup_database():
    """Create database backup with timestamp and maintain max 10 files"""
    try:
        db_path = Path(".claude/memory/project.db")
        if not db_path.exists():
            print("WARNING: Database does not exist, skipping backup")
            return False
        
        # Create backup directory
        backup_dir = Path(".claude/memory/backup")
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        backup_filename = f"project_{timestamp}.db"
        backup_path = backup_dir / backup_filename
        
        # Copy database to backup
        shutil.copy2(db_path, backup_path)
        
        # Clean old backups - keep only 10 most recent
        backup_files = sorted(backup_dir.glob("project_*.db"), key=lambda f: f.stat().st_mtime)
        if len(backup_files) > 10:
            files_to_delete = backup_files[:-10]
            for old_file in files_to_delete:
                old_file.unlink()
        
        return True
    except Exception as e:
        print(f"ERROR: Critical backup failure: {e}")
        return False

def parse_arguments():
    """Parse command line arguments manually"""
    import sys
    
    args = sys.argv[1:]
    if len(args) < 4 or '-session' not in args or '-message' not in args:
        print(json.dumps({
            "error": "Usage: script.py -session 'session_data' -message 'message_data'",
            "example": "script.py -session 'accomplishments: Fixed bug. decisions: Chose X.' -message 'conversation_flow: Q: What? A: Fixed bug. total_exchanges: 10 duration_minutes: 30'"
        }))
        return None, None
    
    try:
        session_idx = args.index('-session') + 1
        message_idx = args.index('-message') + 1
        return args[session_idx], args[message_idx]
    except (IndexError, ValueError):
        print(json.dumps({"error": "Invalid arguments format"}))
        return None, None

def parse_field(text, field_name):
    """Extract field content from text"""
    # Clean emojis with simple regex
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Extract field content
    pattern = rf"{field_name}:\s*(.*?)(?=\s+(?:accomplishments|decisions|bugs_fixed|errors_encountered|breakthrough_moment|next_session_priority|conversation_flow|total_exchanges|duration_minutes):|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        content = match.group(1).strip()
        if content and content.lower() not in ['none', 'n/a', 'nothing', 'empty']:
            # Add line breaks for readability
            content = content.replace('. ', '.\n').replace('? ', '?\n').replace('! ', '!\n')
            content = re.sub(r'\n\s*\n', '\n', content)
            return content.strip()
    return ""

def get_current_session():
    """Get current active session"""
    try:
        conn = sqlite3.connect(".claude/memory/project.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, job_id, created_at FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise Exception("No active session found")
        return {'session_id': result[0], 'job_id': result[1], 'created_at': result[2]}
    except Exception as e:
        raise Exception(f"Failed to get session: {e}")

def save_to_database(session_data, session_text, message_text):
    """Save session data to database"""
    try:
        # Parse session fields
        accomplishments_text = parse_field(session_text, 'accomplishments')
        decisions_text = parse_field(session_text, 'decisions') 
        bugs_text = parse_field(session_text, 'bugs_fixed')
        errors_text = parse_field(session_text, 'errors_encountered')
        breakthrough = parse_field(session_text, 'breakthrough_moment')
        next_priority = parse_field(session_text, 'next_session_priority')
        
        # Convert to arrays for database
        accomplishments = [s.strip() for s in accomplishments_text.split('\n') if s.strip()] if accomplishments_text else []
        decisions = [s.strip() for s in decisions_text.split('\n') if s.strip()] if decisions_text else []
        bugs_fixed = [s.strip() for s in bugs_text.split('\n') if s.strip()] if bugs_text else []
        errors = [s.strip() for s in errors_text.split('\n') if s.strip()] if errors_text else []
        
        # Parse message fields
        conversation_flow = parse_field(message_text, 'conversation_flow')
        
        # Extract numbers
        exchanges_match = re.search(r'total_exchanges:\s*(\d+)', message_text, re.IGNORECASE)
        total_exchanges = int(exchanges_match.group(1)) if exchanges_match else len(accomplishments) + len(errors)
        
        # duration_minutes is parsed but actual duration calculated from database timestamps
        
        # Calculate actual duration from database
        start_time = datetime.strptime(session_data['created_at'], '%Y-%m-%d %H:%M')
        actual_duration = int((datetime.now() - start_time).total_seconds() / 60)
        
        # Basic validation
        if not accomplishments and not decisions and not bugs_fixed:
            raise Exception("Session must have some accomplishments, decisions, or bugs fixed")
        
        if conversation_flow and len(conversation_flow) > 20:
            if "Q:" not in conversation_flow or "A:" not in conversation_flow:
                raise Exception("conversation_flow must contain Q&A format")
        
        if len(conversation_flow) > 5000:
            raise Exception("conversation_flow too long (>5000 chars)")
        
        # Calculate quality score using extracted pure function
        quality_score = compute_quality_score(
            accomplishments=accomplishments,
            errors=errors, 
            breakthrough=breakthrough,
            decisions=decisions,
            bugs_fixed=bugs_fixed
        )
        
        # Save to database
        conn = sqlite3.connect(".claude/memory/project.db")
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Check if quality_score column exists and add if missing
        def ensure_quality_score_column():
            try:
                # Check table schema
                cursor.execute("PRAGMA table_info(sessions)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'quality_score' not in columns:
                    # Add column if missing
                    cursor.execute("ALTER TABLE sessions ADD COLUMN quality_score INTEGER DEFAULT NULL")
                    conn.commit()
                    print("Added quality_score column to sessions table")
                    
            except sqlite3.OperationalError as e:
                print(f"Warning: Could not add quality_score column: {e}")
                return False
            return True
        
        # Ensure column exists
        has_quality_score = ensure_quality_score_column()
        
        # Update session with defensive column handling
        try:
            if has_quality_score:
                # Full update with quality_score
                cursor.execute("""
                    UPDATE sessions SET
                        accomplishments = ?, decisions = ?, bugs_fixed = ?, errors_encountered = ?,
                        breakthrough_moment = ?, next_session_priority = ?, quality_score = ?, ended_at = ?
                    WHERE id = ?
                """, (
                    json.dumps(accomplishments), json.dumps(decisions), 
                    json.dumps(bugs_fixed), json.dumps(errors),
                    breakthrough, next_priority, quality_score, timestamp,
                    session_data['session_id']
                ))
            else:
                # Fallback update without quality_score
                cursor.execute("""
                    UPDATE sessions SET
                        accomplishments = ?, decisions = ?, bugs_fixed = ?, errors_encountered = ?,
                        breakthrough_moment = ?, next_session_priority = ?, ended_at = ?
                    WHERE id = ?
                """, (
                    json.dumps(accomplishments), json.dumps(decisions), 
                    json.dumps(bugs_fixed), json.dumps(errors),
                    breakthrough, next_priority, timestamp,
                    session_data['session_id']
                ))
                
        except sqlite3.OperationalError as e:
            # Final fallback - retry without quality_score if UPDATE fails
            print(f"Warning: Full update failed, retrying without quality_score: {e}")
            cursor.execute("""
                UPDATE sessions SET
                    accomplishments = ?, decisions = ?, bugs_fixed = ?, errors_encountered = ?,
                    breakthrough_moment = ?, next_session_priority = ?, ended_at = ?
                WHERE id = ?
            """, (
                json.dumps(accomplishments), json.dumps(decisions), 
                json.dumps(bugs_fixed), json.dumps(errors),
                breakthrough, next_priority, timestamp,
                session_data['session_id']
            ))
            # Set quality_score to None for return value consistency
            quality_score = None
        
        # Insert message
        cursor.execute("""
            INSERT INTO messages (session_id, conversation_flow, total_exchanges, duration_minutes, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_data['session_id'], conversation_flow, total_exchanges, actual_duration, timestamp))
        
        message_id = cursor.lastrowid
        
        # Create next session
        import secrets
        new_session_id = f"session_{secrets.token_hex(6)}"
        
        # Get claude_session_id from most recent transcript file
        claude_session_id = None
        try:
            # Build the Claude projects path for current directory
            import os
            import hashlib
            
            # Normalize path and replace all separators with hyphens
            current_dir = os.path.abspath(os.getcwd())
            sanitized_dir = current_dir.replace('\\', '-').replace('/', '-').replace(':', '-')
            
            # If path is too long (>100 chars), use hash instead
            if len(sanitized_dir) > 100:
                # Use first 16 chars of SHA256 hash for uniqueness
                dir_hash = hashlib.sha256(current_dir.encode()).hexdigest()[:16]
                sanitized_dir = f"project-{dir_hash}"
            
            claude_projects_dir = Path(os.path.expanduser(f"~/.claude/projects/{sanitized_dir}"))
            
            if claude_projects_dir.exists():
                # Find the most recent .jsonl file
                jsonl_files = list(claude_projects_dir.glob("*.jsonl"))
                if jsonl_files:
                    # Sort by modification time and get the most recent
                    most_recent = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                    # The filename without extension IS the claude_session_id
                    claude_session_id = most_recent.stem
                    # Validate the session ID format (should be alphanumeric with hyphens/underscores)
                    if not re.match(r'^[a-zA-Z0-9_-]+$', claude_session_id):
                        claude_session_id = None
        except Exception:
            # If we can't get the claude_session_id, continue without it
            pass
        
        cursor.execute("""
            INSERT INTO sessions (id, job_id, created_at, claude_session_id)
            VALUES (?, ?, ?, ?)
        """, (new_session_id, session_data['job_id'], timestamp, claude_session_id))
        
        conn.commit()
        
        # Get FLAGS summary for this session
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
            FROM flags 
            WHERE session_id = ?
        """, (session_data['session_id'],))
        
        flags_data = cursor.fetchone()
        flags_summary = {
            'created': flags_data[0] if flags_data else 0,
            'completed': flags_data[1] if flags_data else 0,
            'pending': flags_data[2] if flags_data else 0
        }
        
        conn.close()
        
        return {
            'session_id': session_data['session_id'],
            'job_id': session_data['job_id'],
            'quality_score': quality_score,
            'duration_minutes': actual_duration,
            'total_exchanges': total_exchanges,
            'accomplishments': accomplishments,
            'decisions': decisions,
            'bugs_fixed': bugs_fixed,
            'errors': errors,
            'breakthrough_moment': breakthrough,
            'next_session_priority': next_priority,
            'message_id': message_id,
            'timestamp': timestamp,
            'new_session_id': new_session_id,
            'next_session_ready': True,
            'flags_summary': flags_summary
        }
        
    except Exception as e:
        raise Exception(f"Database save failed: {e}")

def main():
    """Main function - simple and direct"""
    try:
        # Backup database first - critical step
        backup_success = backup_database()
        if not backup_success:
            print(json.dumps({
                "error": "Failed to create database backup",
                "recommendation": "Check database file permissions and disk space"
            }))
            return 1
        
        # Parse arguments
        session_text, message_text = parse_arguments()
        if not session_text or not message_text:
            return 1
        
        # Get current session
        session_data = get_current_session()
        
        # Save everything
        result = save_to_database(session_data, session_text, message_text)
        
        # Output result
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return 1

if __name__ == "__main__":
    exit(main())