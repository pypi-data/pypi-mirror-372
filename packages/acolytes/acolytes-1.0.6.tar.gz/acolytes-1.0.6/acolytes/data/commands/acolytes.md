---
command: acolytes
description: ♾️  "Summoning the acolytes to serve... — ready to work, boss!"
---

When this command is invoked:

For `/acolytes` (no arguments):

- Invoke @flags.agent to orchestrate pending FLAGS
- @flags.agent will analyze all pending flags in SQLite database
- @flags.agent will determine optimal execution strategy (parallel vs sequential)
- @flags.agent will provide specific agent invocation instructions to Claude
- Claude will execute the recommended agent invocations

The @flags.agent handles:

- Priority rebalancing and degradation of excessive critical flags
- Conflict detection via related_files and agent name analysis
- Locked flag resolution sequences and timeout detection
- ChainFlag dependency tracking and proper sequencing
- Cross-module coordination and parallel execution optimization

Expected output from @flags.agent:

- Analysis of current flag system state
- Specific invocation commands: "invoke @agent-name" or "invoke in parallel: @agent1, @agent2"
- Conflict resolution decisions and serialization requirements
- Priority adjustments and rebalancing actions taken

For future expansion:

- `/acolytes --doctor`: Diagnose flag system issues (ONLY reports problems, user decides fixes)
  - Can receive Claude context for specific investigations
  - Reports: zombie flags, circular dependencies, timeout patterns, overload conditions
  - Does NOT auto-fix - only diagnostics

- `/acolytes --pending`