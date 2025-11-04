---
name: iw-install
description: Install, update, or uninstall the Implementation Workflow. Manages all workflow skills, commands, and hooks by fetching them from GitHub and installing to project or user .claude directory.
---

# Implementation Workflow Installer

## Overview

Manage the Installation Workflow installation programmatically. This skill handles installing, updating, and uninstalling all workflow components by fetching them directly from GitHub.

**Installation Locations:**
- **Project-level**: `.claude/` in current working directory (shared with team, committed to VCS)
- **User-level**: `~/.claude/` in home directory (personal, available across all projects)

## Usage

### Install Workflow

**Install to current project** (default):
```
Invoke this skill with action: install
```

**Install to user directory** (~/.claude):
```
Invoke this skill with action: install, location: user
```

### Update Workflow

Update an existing installation to the latest version from GitHub:

**Update project installation**:
```
Invoke this skill with action: update
```

**Update user installation**:
```
Invoke this skill with action: update, location: user
```

### Uninstall Workflow

Remove the workflow completely:

**Uninstall from project**:
```
Invoke this skill with action: uninstall
```

**Uninstall from user directory**:
```
Invoke this skill with action: uninstall, location: user
```

### Verify Installation

Check that all workflow files are correctly installed:

**Verify project installation**:
```
Invoke this skill with action: verify
```

**Verify user installation**:
```
Invoke this skill with action: verify, location: user
```

### List Installed Components

Show what workflow components are currently installed:

**List project installation**:
```
Invoke this skill with action: list
```

**List user installation**:
```
Invoke this skill with action: list, location: user
```

## What Gets Installed

The installer manages these workflow components:

### Skills (13 total)
1. **iw-planner** - Create detailed implementation plans
2. **iw-executor** - Execute implementation plans
3. **iw-workflow** - Workflow guidance and documentation
4. **iw-learnings** - Search past learnings
5. **iw-init** - Initialize .docs structure
6. **iw-github-issue-reader** - Load GitHub issue context
7. **iw-github-pr-creator** - Create GitHub pull requests
8. **iw-git-workflow** - Manage git operations
9. **iw-research-planner** - Define research scope and create plans
10. **iw-research-executor** - Gather information and generate reports
11. **iw-research-synthesizer** - Generate reports (auto-invoked by executor)
12. **go-dev-guidelines** - Go development patterns
13. **skill-creator** - Guide for creating skills
14. **iw-install** - This installer skill (self)

### Slash Commands (6 total)
1. **/iw-plan** - Create implementation plan
2. **/iw-implement** - Execute plan
3. **/iw-help** - Show workflow guidance
4. **/iw-install** - Manage installation
5. **/iw-research-plan** - Create research plan
6. **/iw-research-execute** - Gather information and generate report

### Hooks (6 total)
1. **load_workflow.py** - Cross-platform session start hook
2. **list_skills.py** - Cross-platform skills listing hook
3. **check_workflow_version.py** - Cross-platform version check hook
4. **load_workflow.sh** - Deprecated bash version (backward compatibility)
5. **list_skills.sh** - Deprecated bash version (backward compatibility)
6. **check_workflow_version.sh** - Deprecated bash version (backward compatibility)

### Support Files
- Python scripts for each skill
- Template files for plans
- Reference documentation
- Assets and resources

## Installation Process

When you invoke this skill with action `install`:

1. **Determine Target Location**
   - Project: `$CWD/.claude/`
   - User: `~/.claude/`

2. **Clone Repository**
   - Uses `git clone --depth 1` to shallow clone the repository
   - Clones to temporary directory
   - Fast and avoids GitHub API rate limiting

3. **Copy Files**
   - Copies entire `.claude/` directory from clone to target
   - Preserves directory structure
   - Makes hook scripts executable

4. **Cleanup**
   - Removes temporary clone directory
   - Installation complete
   ```
   .claude/
   ├── skills/
   ├── commands/
   └── hooks/
   ```

3. **Fetch Workflow Components from GitHub**
   - Uses GitHub API to list all files
   - Downloads each file directly from main branch
   - Preserves directory structure

4. **Install Skills**
   - Downloads SKILL.md for each skill
   - Downloads scripts/ directory contents
   - Downloads assets/ and references/ if present
   - Makes hook scripts executable

5. **Install Commands**
   - Downloads all /iw-*.md command files
   - Places in commands/ directory

6. **Install Hooks**
   - Downloads hook scripts
   - Makes executable with chmod +x

7. **Verify Installation**
   - Checks all expected files are present
   - Reports any issues

8. **Display Summary**
   - Shows installation location
   - Lists installed components
   - Provides next steps

## Update Process

When you invoke with action `update`:

1. **Verify Existing Installation**
   - Checks if workflow is installed
   - Identifies current location

2. **Create Backup** (optional)
   - Can create .backup copies of existing files
   - Preserves user modifications

3. **Fetch Latest from GitHub**
   - Downloads latest version of all files
   - Overwrites existing files

4. **Verify Update**
   - Ensures all files updated successfully
   - Reports any issues

5. **Display Update Summary**
   - Shows what was updated
   - Notes any new components added

## Uninstall Process

When you invoke with action `uninstall`:

1. **Verify Installation Exists**
   - Checks for workflow files
   - Identifies location

2. **List Components to Remove**
   - Shows all workflow files found
   - Confirms removal

3. **Remove Workflow Files**
   - Deletes all skills (iw-*, go-dev-guidelines, skill-creator)
   - Removes commands (/iw-*.md)
   - Removes hooks (load_workflow.sh, list_skills.sh)
   - Preserves user's custom skills/commands

4. **Clean Empty Directories**
   - Removes empty skill directories
   - Keeps .claude/ structure

5. **Display Removal Summary**
   - Shows what was removed
   - Notes any files preserved

## Script Usage

The skill uses `scripts/manage_workflow.py` for all operations:

### Install
```bash
python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location project
python3 .claude/skills/iw-install/scripts/manage_workflow.py install --location user
```

### Update
```bash
python3 .claude/skills/iw-install/scripts/manage_workflow.py update --location project
python3 .claude/skills/iw-install/scripts/manage_workflow.py update --location user
```

### Uninstall
```bash
python3 .claude/skills/iw-install/scripts/manage_workflow.py uninstall --location project
python3 .claude/skills/iw-install/scripts/manage_workflow.py uninstall --location user
```

### Verify
```bash
python3 .claude/skills/iw-install/scripts/manage_workflow.py verify --location project
```

### List
```bash
python3 .claude/skills/iw-install/scripts/manage_workflow.py list --location project
```

## Parameters

When invoking this skill, specify:

**action** (required): One of:
- `install` - Install workflow
- `update` - Update existing installation
- `uninstall` - Remove workflow
- `verify` - Check installation integrity
- `list` - Show installed components

**location** (optional, defaults to "project"):
- `project` - Use `.claude/` in current directory
- `user` - Use `~/.claude/` in home directory

**force** (optional, defaults to False):
- `true` - Force overwrite without prompting
- `false` - Prompt for confirmation on conflicts

## Examples

### Example 1: Fresh Project Installation
```
User: Install the implementation workflow to this project
Assistant: Invoking iw-install skill with action=install, location=project

[Skill executes installation]

Installation complete!

Location: /home/user/myproject/.claude/
Installed:
- 10 skills
- 4 commands
- 2 hooks

Next steps:
1. Run /iw-help to see workflow guidance
2. Use /iw-plan to create your first plan
```

### Example 2: Update User Installation
```
User: Update my workflow to the latest version
Assistant: Invoking iw-install skill with action=update, location=user

[Skill checks for updates and installs]

Update complete!

Location: ~/.claude/
Updated: 10 skills, 4 commands, 2 hooks
New components: None
```

### Example 3: Uninstall from Project
```
User: Remove the workflow from this project
Assistant: Invoking iw-install skill with action=uninstall, location=project

[Skill removes workflow files]

Uninstall complete!

Removed from: .claude/
- 10 skills removed
- 4 commands removed
- 2 hooks removed

Your custom skills and commands were preserved.
```

## Error Handling

The skill handles common errors gracefully:

- **Network errors**: Retries download with exponential backoff
- **Permission errors**: Suggests running with appropriate permissions
- **Directory conflicts**: Reports conflicts and suggests resolution
- **Partial installation**: Rolls back on failure, reports state
- **Missing dependencies**: Checks for Python, git, curl availability

## Requirements

- **Python 3.7+** - For running the management script
- **git** - For cloning the workflow repository
- **Internet connection** - To clone from GitHub

Optional:
- **gh CLI** - For GitHub integration features (issue reader, PR creator)

## Windows Support

The workflow is fully compatible with Windows 10/11:

- ✅ Python scripts work on Windows natively
- ✅ UTF-8 encoding configured for Unicode output
- ✅ Cross-platform path handling with pathlib
- ✅ Git for Windows supported
- ✅ Works in PowerShell, Command Prompt, and Git Bash

**Requirements for Windows:**
- Python 3.7+ (from python.org or Microsoft Store)
- Git for Windows (from git-scm.com)
- Any terminal (PowerShell, Command Prompt, or Git Bash)

**Known Issues:**
- Older Windows terminals may not display Unicode characters (✓, ✗)
- Scripts use ASCII fallback automatically if UTF-8 unavailable
- Use Windows Terminal or PowerShell 7+ for best experience

## Workflow Integration

This skill is part of the Implementation Workflow suite:

- **Installed by**: Bootstrap script (bootstrap.sh)
- **Manages**: All other workflow skills and commands
- **Used by**: Users to maintain workflow installation
- **Updates**: Fetches from GitHub main branch

## Repository

Source: https://github.com/jumppad-labs/iw

The installer fetches all files from:
`https://raw.githubusercontent.com/jumppad-labs/iw/main/`

## Important Notes

1. **Git Required**: Installation requires git to be installed and available in PATH
2. **Force Overwrite**: Installation always overwrites existing workflow files (force=true by default)
3. **Preserves Custom Content**: Your custom skills, commands, and settings are never removed
4. **Network Required**: Clone operation requires internet access to GitHub
5. **No Rate Limiting**: Git clone eliminates GitHub API rate limiting issues
6. **Self-Updating**: The iw-install skill can update itself
7. **No Config Changes**: Never modifies settings.json or other configuration

## Troubleshooting

### Installation Fails
1. **Check git is installed**: `git --version`
   - Ubuntu/Debian: `sudo apt-get install git`
   - macOS: `brew install git`
   - Windows: https://git-scm.com/download/win
2. **Check internet connection**: `ping github.com`
3. **Verify Python 3.7+ installed**: `python3 --version`
4. **Check permissions for target directory**: `ls -ld .claude`
5. **Check disk space**: `df -h .`

### Clone Fails
1. **Verify GitHub is accessible**: `git ls-remote https://github.com/jumppad-labs/iw.git`
2. **Check for network proxy**: `echo $https_proxy`
3. **Try manual clone**: `git clone https://github.com/jumppad-labs/iw.git /tmp/test-clone`

### Rate Limiting (No Longer an Issue)
The new git clone approach eliminates rate limiting issues. You can run installations as many times as needed.

### Skills Not Loading After Install
1. Restart Claude Code
2. Verify files in correct location: `ls .claude/skills/`
3. Check SKILL.md files have proper frontmatter
4. Run verify action to check installation

### Update Shows No Changes
- Installation is already at latest version
- Check GitHub repo for recent commits
- Try forcing reinstall with uninstall then install

## Support

For issues with installation:
1. Check GitHub issues for similar problems
2. Run verify action to diagnose
3. Review installation logs
4. Open issue with error details

---

Generated with Claude Code Implementation Workflow
