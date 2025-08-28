---
command: commit
description: ♾️  Smart commit with auto-changelog, version bump and git tagging | Optional: --wip (quick save), --push (auto push), --validate (CI/CD checks)
---

# Smart Git Commit with Auto-Versioning

I'll create an intelligent commit with automatic emoji selection, changelog update, and semantic version management. This is a complete workflow that handles everything from commit to release tagging.

## Complete Automated Workflow

When you run `/commit`, the following happens automatically:

1. **Pre-Analysis**: Verify repository status and analyze all changes
2. **Smart Commit**: Create commit with emoji and conventional format
3. **Auto-Changelog**: Invoke @docs.specialist to update CHANGELOG.md
4. **Version Detection**: Determine version bump type from commit
5. **Version Update**: Execute bump2version to update all version files
6. **Tag Creation**: Create annotated git tag (e.g., v1.0.1)

The entire process is automated based on your changes and commit type.

## Emoji Classification System

I'll automatically select the most appropriate emoji based on file changes and commit type:

### Core Types

- ✨ `feat`: New feature
- 🐛 `fix`: Bug fix
- 📝 `docs`: Documentation
- 💄 `style`: Formatting/style
- ♻️ `refactor`: Code refactoring
- ⚡️ `perf`: Performance improvements
- ✅ `test`: Tests
- 🔧 `chore`: Tooling, configuration

### Extended Classification

- 🚀 `ci`: CI/CD improvements
- 🗑️ `revert`: Reverting changes
- 🧪 `test`: Add a failing test
- 🚨 `fix`: Fix compiler/linter warnings
- 🔒️ `fix`: Fix security issues
- 👥 `chore`: Add or update contributors
- 🚚 `refactor`: Move or rename resources
- 🏗️ `refactor`: Make architectural changes
- 🔀 `chore`: Merge branches
- 📦️ `chore`: Add or update compiled files or packages
- ➕ `chore`: Add a dependency
- ➖ `chore`: Remove a dependency
- 🌱 `chore`: Add or update seed files
- 🧑‍💻 `chore`: Improve developer experience
- 🧵 `feat`: Add or update code related to multithreading or concurrency
- 🔍️ `feat`: Improve SEO
- 🏷️ `feat`: Add or update types
- 💬 `feat`: Add or update text and literals
- 🌐 `feat`: Internationalization and localization
- 👔 `feat`: Add or update business logic
- 📱 `feat`: Work on responsive design
- 🚸 `feat`: Improve user experience / usability
- 🩹 `fix`: Simple fix for a non-critical issue
- 🥅 `fix`: Catch errors
- 👽️ `fix`: Update code due to external API changes
- 🔥 `fix`: Remove code or files
- 🎨 `style`: Improve structure/format of the code
- 🚑️ `fix`: Critical hotfix
- 🎉 `chore`: Begin a project
- 🔖 `chore`: Release/Version tags
- 🚧 `wip`: Work in progress
- 💚 `fix`: Fix CI build
- 📌 `chore`: Pin dependencies to specific versions
- 👷 `ci`: Add or update CI build system
- 📈 `feat`: Add or update analytics or tracking code
- ✏️ `fix`: Fix typos
- ⏪️ `revert`: Revert changes
- 📄 `chore`: Add or update license
- 💥 `feat`: Introduce breaking changes
- 🍱 `assets`: Add or update assets
- ♿️ `feat`: Improve accessibility
- 💡 `docs`: Add or update comments in source code
- 🗃️ `db`: Perform database related changes
- 🔊 `feat`: Add or update logs
- 🔇 `fix`: Remove logs
- 🤡 `test`: Mock things
- 🥚 `feat`: Add or update an easter egg
- 🙈 `chore`: Add or update .gitignore file
- 📸 `test`: Add or update snapshots
- ⚗️ `experiment`: Perform experiments
- 🚩 `feat`: Add, update, or remove feature flags
- 💫 `ui`: Add or update animations and transitions
- ⚰️ `refactor`: Remove dead code
- 🦺 `feat`: Add or update code related to validation
- ✈️ `feat`: Improve offline support

## Semantic Version Bump Detection

Following [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) (SemVer), the commit emoji and type automatically determine the version bump:

**PATCH** (1.0.0 → 1.0.1) - Backward compatible bug fixes:

- 🐛 `fix:` Bug fixes
- 🩹 `fix:` Simple fixes
- 🚑️ `fix:` Critical hotfixes
- ✏️ `fix:` Typo corrections
- 🔇 `fix:` Remove logs
- 👽️ `fix:` External API updates
- 🥅 `fix:` Catch errors

**MINOR** (1.0.0 → 1.1.0) - Backward compatible new functionality:

- ✨ `feat:` New features
- ⚡️ `perf:` Performance improvements
- 🚸 `feat:` UX improvements
- ➕ `chore:` Add dependencies (if adds functionality)
- 🏷️ `feat:` Add types
- 🔊 `feat:` Add logs (if part of public API)
- 🦺 `feat:` Add validation

**MAJOR** (1.0.0 → 2.0.0) - Backward incompatible changes:

- 💥 `feat:` Breaking changes (explicit)
- 🏗️ `refactor:` Architectural changes (only if breaking)
- 🗑️ `revert:` Major reversions (only if breaking)
- 🔥 `fix:` Remove code/files (if public API)

**NO VERSION BUMP** - Changes that don't affect functionality:

- 📝 `docs:` Documentation only
- 💄 `style:` Code formatting (no logic changes)
- ♻️ `refactor:` Code refactoring (non-breaking)
- ✅ `test:` Adding/updating tests
- 🔧 `chore:` Build/config changes
- 🎨 `style:` Code structure improvements
- 🚧 `wip:` Work in progress (with --wip flag)

## Execution Process

### Step 1: Repository Analysis & WIP Cleanup

```bash
# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    echo "This command requires git version control"
    exit 1
fi

# Check for WIP commits and clean them up
echo "Checking for WIP commits to consolidate..."
WIP_COUNT=0
while true; do
    # Get the last commit message
    LAST_MSG=$(git log -1 --pretty=%s 2>/dev/null)

    # Check if it starts with 🚧 WIP:
    if [[ "$LAST_MSG" == "🚧 WIP:"* ]]; then
        echo "Found WIP commit: $LAST_MSG"
        WIP_COUNT=$((WIP_COUNT + 1))
        # Soft reset to keep changes but remove the WIP commit
        git reset --soft HEAD~1
    else
        break
    fi
done

if [ $WIP_COUNT -gt 0 ]; then
    echo "Consolidated $WIP_COUNT WIP commit(s) into working directory"
    echo "All changes are preserved and will be included in the new commit"
fi

# Check if we have changes to commit
if ! git diff --cached --quiet || ! git diff --quiet; then
    echo "Changes detected:"
    git status --short
else
    echo "No changes to commit"
    exit 0
fi

# Show detailed changes
git diff --cached --stat
git diff --stat
```

### Step 2: Change Analysis

I'll analyze the changes to determine:

1. **File types**: Configuration, source code, documentation, assets
2. **Change patterns**: New files, deletions, modifications, renames
3. **Content analysis**: Feature additions, bug fixes, refactoring, etc.
4. **Scope detection**: Components or areas affected

### Step 3: Smart Emoji Selection

Based on file analysis, I'll select the most appropriate emoji:

- **package.json/requirements.txt changes**: ➕ (add dependency) or ➖ (remove dependency)
- **.gitignore changes**: 🙈 (update .gitignore)
- **CI/CD files**: 🚀 (CI improvements) or 👷 (CI build system)
- **Documentation files**: 📝 (docs) or 💡 (code comments)
- **Test files**: ✅ (tests), 🧪 (failing test), 📸 (snapshots), 🤡 (mocks)
- **Security fixes**: 🔒️ (security issues)
- **Performance**: ⚡️ (performance improvements)
- **UI/UX**: 💄 (style), 📱 (responsive), 🚸 (UX), 💫 (animations)
- **Database**: 🗃️ (database changes)
- **Breaking changes**: 💥 (breaking changes)
- **Critical fixes**: 🚑️ (critical hotfix)
- **Code structure**: 🎨 (structure), ♻️ (refactor), ⚰️ (dead code)
- **Assets**: 🍱 (assets)
- **Accessibility**: ♿️ (accessibility)
- **Logs**: 🔊 (add logs), 🔇 (remove logs)
- **Feature flags**: 🚩 (feature flags)
- **Validation**: 🦺 (validation)
- **Offline support**: ✈️ (offline support)

### Step 4: Stage Changes

```bash
# If nothing is staged, I'll stage all changes (including untracked)
if git diff --cached --quiet; then
    echo "No files staged. Staging all changes..."
    git add -A
fi

# Show what will be committed
git diff --cached --name-status
```

### Step 5: Create Smart Commit

I'll create a conventional commit message with emoji:

**Format**: `emoji type(scope): description`

- **Emoji**: Automatically selected from 110+ classification
- **Type**: Conventional commit type (feat, fix, docs, etc.)
- **Scope**: Component or area affected (optional)
- **Description**: Clear description in present tense
- **Session ID**: Included in footer for traceability

```bash
# Get current session ID from SQLite database
SESSION_ID=$(cd .claude && python -c "
import sqlite3
import os
db_path = os.path.join('memory', 'project.db')
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('SELECT session_id FROM sessions ORDER BY created_at DESC LIMIT 1')
    result = cursor.fetchone()
    print(result[0] if result else 'unknown')
    conn.close()
except Exception as e:
    print('unknown')
")

# Create commit with emoji, conventional format, and session tracking
git commit -m "✨ feat(auth): add OAuth2 integration with GitHub

session: $SESSION_ID"
```

### Step 6: Update Changelog

After the commit is created, I'll automatically invoke @docs.specialist to:

- Analyze the commit message
- Update CHANGELOG.md with technical details
- Maintain proper version history

### Step 7: Automatic Version Bump

Based on the commit type, bump2version will:

- Detect version bump type (patch/minor/major)
- Update all version files automatically
- Create annotated git tag

```bash
# Execute version bump based on commit type
bump2version [patch|minor|major] --no-commit --tag
```

## Commit Examples

- `✨ feat(auth): add OAuth2 integration with GitHub` → Minor version bump
- `🐛 fix(api): resolve timeout issue in user endpoints` → Patch version bump
- `📝 docs(readme): update installation instructions` → Patch version bump
- `⚡️ perf(database): optimize query performance` → Minor version bump
- `🔒️ fix(security): patch XSS vulnerability` → Patch version bump
- `💥 feat(api): breaking API changes` → Major version bump
- `♻️ refactor(components): extract reusable logic` → No version bump
- `➕ chore(deps): add lodash for utilities` → Minor version bump
- `🎨 style(components): improve code structure` → Patch version bump
- `🚑️ fix(critical): patch memory leak` → Patch version bump

## Requirements

- **bump2version** installed: `pip install bump2version`
- **.bumpversion.cfg** configured in project root
- **@docs.specialist** agent available

## Important Notes

**I will NEVER:**

- Add "Co-authored-by" or any Claude signatures
- Include "Generated with Claude Code" or similar messages
- Modify git config or user credentials
- Add any AI/assistant attribution to the commit

The commit will use only your existing git user configuration, maintaining full ownership and authenticity of your commits.

---

## Optional Command Arguments

You can customize the behavior with these optional arguments:

### `/commit --wip`

**Work In Progress** - Quick save of unfinished work:

- Adds 🚧 emoji and "WIP:" prefix automatically
- Skips ALL validations (tests, linting, build)
- NO version bump or changelog update
- Stages all changes automatically (git add -A)
- Perfect for end-of-day saves or branch switches

**Automatic WIP consolidation**: When you run `/commit` (without --wip), Claude automatically:

1. Detects all consecutive WIP commits
2. Consolidates them into the working directory
3. Creates a single proper commit with all changes

```bash
# Day 1: Quick save
/commit --wip
# Result: "🚧 WIP: working on authentication"

# Day 2: Another quick save
/commit --wip
# Result: "🚧 WIP: continuing auth implementation"

# Day 3: Ready to make proper commit
/commit
# Claude automatically:
# - Finds the 2 WIP commits
# - Consolidates them (git reset --soft)
# - Creates: "✨ feat: add complete authentication system"
```

### `/commit --push`

Automatically push to remote after successful commit:

- Creates commit with all normal workflow
- Executes `git push` to current branch
- Fails safely if push is rejected

```bash
# Commit and push to current branch
/commit --push

# Combine with other options
/commit --wip --push  # WIP commit + push
```

### `/commit --validate`

**Professional CI/CD validations** before committing:

- Invokes @test.quality agent for comprehensive testing
- Runs test suite, linting, type checking
- Build verification and security scans
- If any validation fails, commit is aborted

```bash
# Full validation before commit
/commit --validate

# Combine with other options
/commit --validate --push  # Validated commit + push
```

---

## Examples

**Quick saves:**

```bash
/commit --wip              # Quick WIP commit, no validations
/commit --wip --push       # WIP + push to share with team
```

**Professional workflow:**

```bash
/commit                    # Normal commit with emoji + changelog + version
/commit --validate         # Validate everything before commit
/commit --validate --push  # Validate, commit, and push
```

==============================================================================

● Tienes razón, el commit.md podría estar más claro sobre el orden exacto. El flujo que describiste es mucho más lógico:

Flujo correcto debería ser:

1. Analizar cambios → determinar tipo de commit (feat/fix/etc)
2. Planear mensaje de commit mentalmente (sin ejecutar)
3. Invocar @docs.specialist con el commit planeado → actualiza CHANGELOG.md
4. Ejecutar bump2version → actualiza archivos de versión + crea tag (pero NO commitea)
5. UN SOLO git commit final con:

   - Todos los cambios originales
   - CHANGELOG.md actualizado
   - Archivos de versión actualizados
   - El mensaje planeado en paso 2

Esto tiene sentido porque:

- El tag queda apuntando al commit correcto (no a uno intermedio)
- Un solo commit atomic con todo
- El CHANGELOG refleja los cambios antes de commitear

El documento actual dice "Step 5: Create Smart Commit" antes de "Step 6: Update Changelog", lo cual es confuso porque
implica que primero commiteas y luego actualizas el CHANGELOG.

¿Quieres que proponga una versión más clara del commit.md con el orden correcto?

==============================================================================
