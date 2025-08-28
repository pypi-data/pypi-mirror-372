---
allowed-tools: [Bash, TodoWrite, mcp__MCP_SQLite_Server__query]
description: ♾️  Save session and messages to SQLite database | No parameters
---

# Save Command - WORKING SYSTEM

Saves current session and messages to SQLite database with rich English content and comprehensive metrics.

## 🔇 SILENT EXECUTION RULE

**CRITICAL**: During /save execution, Claude must:

- Show ONLY: "============================ 💾 Saving Session... ============================" at the start
- Execute ALL commands silently (no additional commentary)
- Show ONLY the final result summary
- NEVER add extra text between tool executions

## CODE INDEX REINDEXING

Before saving the session, Claude MUST silently execute:

```
mcp__code-index__set_project_path(current_project_path)
```

This ensures the code index is up-to-date for the next session (takes ~1 second).
The reindexing removes deleted files and adds new ones automatically.

## CRITICAL INFORMATION FOR FUTURE CLAUDE SESSIONS

### How It Works Now (TESTED & WORKING)

1. **Claude reindexes** the project silently (for next session's fast search)
2. **Claude analyzes** the conversation manually (script cannot read conversation)
3. **Claude executes** ONE command with rich English text
4. **Script parses** and saves to SQLite with proper formatting
5. **Database gets** rich content with line breaks, no emojis, all English

### EXACT COMMAND FORMAT

```bash
uv run ~/.claude/scripts/save_session.py \
  -session "accomplishments: [Rich detailed text]. decisions: [Rich detailed text]. bugs_fixed: [Rich detailed text]. errors_encountered: [Rich detailed text]. breakthrough_moment: [Rich detailed text]. next_session_priority: [Rich detailed text]." \
  -message "conversation_flow: [Rich Q&A format with detailed analysis]. total_exchanges: [number] duration_minutes: [number]"
```

### IMPORTANT RULES

- **ALL CONTENT IN ENGLISH** (never Spanish in database)
- **NO EMOJIS** (script auto-removes them)
- **RICH TEXT** not minimal summaries (detailed explanations, specific examples)
- **USE PERIODS** for auto line breaks in database
- **NO PIPE OPERATIONS** (hooks block them)
- **LENGTH LIMITS**: conversation_flow max 5000 characters, other fields no limit
- **FIELD VALIDATION**: Empty fields after "field:" will be rejected

## What Claude Must Analyze

### SESSION FIELDS (Required)

**accomplishments**: Specific things we actually accomplished

- Files created/modified with exact names
- Problems solved with technical details
- Features implemented with specifics
- Systems fixed/improved

**decisions**: Important technical and strategic choices

- Architecture decisions with reasoning
- Technology selections and why
- Approach changes and rationale

**bugs_fixed**: Actual problems resolved

- Specific errors encountered and fixed
- Broken scripts now working
- Implementation issues resolved

**errors_encountered**: Problems we faced

- Technical barriers hit
- Things that didn't work as expected
- Mistakes that needed correction

**breakthrough_moment**: Key insight that unlocked progress

- The "aha!" moment that solved major problem
- Critical realization that changed approach

**next_session_priority**: Most important next step

- Based on incomplete work
- Priority for next session

### MESSAGE FIELDS (Required)

**conversation_flow**: Rich Q&A analysis format

- Q: [Question about session]? A: [Detailed answer]
- Multiple Q&A pairs covering key aspects
- Comprehensive session narrative

**total_exchanges**: Estimated number of user-Claude exchanges
**duration_minutes**: Session duration in minutes

## WORKING EXAMPLE (COPY THIS FORMAT)

```bash
uv run ~/.claude/scripts/save_session.py \
  -session "accomplishments: Fixed critical save system issue where hooks were blocking pipe operations causing systematic failures in session persistence. Analyzed save_session.py architecture and identified stdin JSON approach as problematic. Implemented new argument-based rich text system replacing minimal JSON with comprehensive English content. decisions: Chose rich text approach over minimal JSON data structure for better session quality and readability. Selected command-line arguments as most efficient method avoiding file creation and token overhead. bugs_fixed: None identified in this session as focus was on architectural analysis rather than bug resolution. errors_encountered: Hook system blocking pipe operations preventing JSON data transfer via stdin to save script. User frustration with minimal session data quality in current system. breakthrough_moment: User without programming background identified most optimal technical solution demonstrating that practical efficiency often trumps complex technical approaches. next_session_priority: Complete frontend mobile agent creation using Context7 and WebSearch for proper documentation research followed by Final QA execution from fix.md checklist." \
  -message "conversation_flow: Q: What was the primary problem addressed in this session? A: Save system completely non-functional due to hook interference with pipe operations plus user dissatisfaction with minimal session data quality. Q: What solution was ultimately implemented? A: Command-line arguments with rich English text parsing automatic formatting with line breaks and emoji cleaning. total_exchanges: 18 duration_minutes: 30"
```

### ❌ INVALID FORMATS (Will Be Rejected)

**Common mistakes that cause script failures:**

```bash
# Missing colons in field definitions
❌ uv run ~/.claude/scripts/save_session.py -session "accomplishments Fixed save system"

# Empty or minimal field content
❌ uv run ~/.claude/scripts/save_session.py -session "accomplishments: . decisions: ."

# Using pipe operations (blocked by hooks)
❌ echo "data" | uv run ~/.claude/scripts/save_session.py -session "..."

# JSON format instead of text
❌ uv run ~/.claude/scripts/save_session.py -session '{"accomplishments": ["item1"]}'

# Missing required session argument
❌ uv run ~/.claude/scripts/save_session.py -message "conversation_flow: Q: Test? A: Yes"

# Swapped argument order or missing -message
❌ uv run ~/.claude/scripts/save_session.py "session data" "message data"

# Special characters without proper quoting
❌ uv run ~/.claude/scripts/save_session.py -session accomplishments: Fixed & improved system

# Mixing old JSON format with new text format
❌ uv run ~/.claude/scripts/save_session.py -session "{accomplishments: [Fixed system]}"
```

**Remember**: Always use the exact format from the working example above.

## EXPECTED SUCCESS OUTPUT

```json
{
  "session_id": "session_1276fe1ef796",
  "job_id": "job_f1a2g3s4y5s6",
  "quality_score": 8,
  "duration_minutes": 1183,
  "total_exchanges": 166,
  "message_id": 44,
  "timestamp": "2025-08-22 20:35",
  "new_session_id": "session_33117b8918f7",
  "next_session_ready": true
}
```

## TROUBLESHOOTING

**If you get "name 're' is not defined"**: Fixed - import re added to script  
**If you get "Missing field: errors"**: Fixed - validation uses errors_encountered  
**If you get hook blocking**: Don't use pipes (|) - use direct arguments only  
**If text too long**: No limit - script handles long rich text

## 🚨 CRITICAL FAILURE RECOVERY

**If save fails completely**:

1. **Check database integrity**:

   ```bash
   sqlite3 .claude/memory/project.db "PRAGMA integrity_check"
   ```

2. **Restore from backup** (if integrity check fails):

   ```bash
   cp .claude/memory/backup/latest.db .claude/memory/project.db
   ```

3. **Retry save with minimal data first**:
   ```bash
   uv run ~/.claude/scripts/save_session.py \
     -session "accomplishments: Basic session save test. decisions: Test recovery." \
     -message "conversation_flow: Q: Test? A: Recovery test. total_exchanges: 1 duration_minutes: 1"
   ```

**If script crashes**:

1. **Check Python syntax**: Look for unescaped quotes in your text
2. **Verify file permissions**: Ensure `.claude/memory/` is writable
3. **Clear corrupted session**: Delete current session and start fresh
4. **Manual backup**: Copy important session notes to a text file first

**Emergency fallback**:

- Use regular text editor to save session notes
- Create GitHub issue with session details
- Continue work and save later when system is stable

## TECHNICAL NOTES FOR DEVELOPERS

- **Text Processing**: Script adds line breaks at sentences (periods, questions, exclamations)
- **Emoji Cleaning**: Regex removes all Unicode emoji ranges automatically
- **Field Parsing**: Improved regex pattern handles edge cases with colons in content
- **Validation**: Semantic validation ensures meaningful content (min 10-15 chars per field)
- **Database Storage**: SQLite stores rich formatted text with line breaks
- **Session Duration**: Calculated from database timestamps, not user-provided duration
- **Quality Score**: Auto-calculated based on accomplishments vs errors ratio
- **Exchange Calculation**: Uses user-provided total_exchanges or estimates from tool count
- **Backup System**: Creates timestamped backups, maintains 10 most recent files
- **Error Handling**: Critical failures stop execution, warnings allow continuation

## Response Format

After executing script successfully, present results in this format:

```markdown
==============================================================================

# 📊 Session Saved Successfully

## Session Information

- **Session ID**: {session_id}
- **Job**: {job_id}
- **Quality Score**: {quality_score}/10 ⭐
- **Duration**: {duration_minutes} minutes
- **Total Exchanges**: {total_exchanges}

## 🎯 Accomplishments ({accomplishments_count})

{accomplishments_list_with_bullets}

## 🐛 Bugs Fixed ({bugs_count})

{bugs_list_with_bullets}

## ⚠️ Errors Encountered ({errors_count})

{errors_list_with_bullets}

## 💡 Breakthrough Moment

> "{breakthrough_moment}"

## 🚀 Next Session Priority

**{next_priority}**

## ⏳ Pending Tasks ({pending_count})

{pending_list_with_bullets}

## 📌 FLAGS Summary

- **Created**: {flags_created} FLAGS
- **Completed**: {flags_completed} ✅
- **Pending**: {flags_pending} ⏳

## 💬 Conversation Summary

A detailed chronological narrative has been saved to the **MESSAGES** table.

**Message ID**: {message_id}  
**Technical Metrics**: {tool_count} tools used ({successful_tools} successful, {failed_tools} failed)

### 🔄 Next Session

When you return, say **"Continue job {job_id}"** to load all context and continue where we left off.

_Session closed at {timestamp}_ ✨

==============================================================================
```
