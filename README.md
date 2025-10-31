# Implementation Workflow

A structured workflow for Claude Code that takes a plan and research-first approach to implementing features. This workflow provides skills, commands, and hooks to guide implementation from initial planning through to PR creation.

## Overview

The Implementation Workflow is a comprehensive set of Claude Code skills and commands that help you:

- **Plan systematically** - Create detailed implementation plans with research, code snippets, and clear phases
- **Execute methodically** - Follow plans with incremental progress tracking and user confirmation
- **Learn continuously** - Capture corrections and learnings for future reference
- **Integrate seamlessly** - Work with GitHub issues, PRs, and git workflows

## What Gets Installed

### Skills (10 total)
- **iw-planner** - Create detailed implementation plans through interactive research process
- **iw-executor** - Execute implementation plans with phase-based commits and tracking
- **iw-workflow** - Workflow guidance and documentation structure explanation
- **iw-learnings** - Search past learnings and corrections from previous work
- **iw-init** - Initialize .docs directory structure for plans and knowledge
- **iw-github-issue-reader** - Load comprehensive GitHub issue information
- **iw-github-pr-creator** - Create GitHub pull requests with plan summaries
- **iw-git-workflow** - Manage git operations with worktrees and phase commits
- **go-dev-guidelines** - Go development patterns and TDD workflow (language-specific)
- **skill-creator** - Guide for creating new skills

### Slash Commands (4 total)
- **/iw-plan** - Create detailed implementation plan
- **/iw-implement** - Execute implementation plan
- **/iw-help** - Show workflow guidance and available commands
- **/iw-install** - Manage workflow installation (install, update, uninstall)

### Hooks (2 total)
- **load_workflow.sh** - Session start hook showing documentation structure
- **list_skills.sh** - List available skills at session start

### Support Files
- Python scripts for plan management, task tracking, and GitHub integration
- Template files for plan structure (plan, tasks, context, research)
- Reference documentation for Go development guidelines

## Quick Start (Recommended)

### Option 1: Bootstrap Installation

Run this one-line command to install the workflow:

```bash
curl -sSL https://raw.githubusercontent.com/jumppad-labs/iw/main/bootstrap.sh | bash
```

This will:
1. Prompt you to choose project-level or user-level installation
2. Download and set up the `iw-install` skill
3. Provide instructions for completing installation

Then in Claude Code, run:
```
/iw-install
```

### Option 2: Manual Installation via Claude Code

1. Share this README URL with Claude Code
2. Ask Claude to install the Implementation Workflow
3. Claude will follow the installation steps below

## Installation Locations

You can install the workflow in two locations:

### Project-Level (Recommended for team workflows)
Install to `.claude/` in your project root:
- Committed to version control
- Shared with team members
- Project-specific configuration

### User-Level (Recommended for personal use)
Install to `~/.claude/`:
- Available in all projects
- Personal configuration
- Not committed to repos

## Usage

### Planning a Feature

For complex features or tasks that require research and structured planning:

```
/iw-plan 123
```
or
```
/iw-plan Add user authentication system
```

This will:
1. Load GitHub issue context (if issue number provided)
2. Search past learnings for relevant knowledge
3. Launch parallel research agents to explore the codebase
4. Guide you through context gathering and design decisions
5. Create structured plan files in `.docs/issues/<number>/` or `.docs/adhoc/<name>/`

### Implementing a Plan

After creating and reviewing a plan:

```
/iw-implement 123
```
or
```
/iw-implement .docs/issues/123/
```

This will:
1. Load the plan files (plan.md, tasks.md, context.md, research.md)
2. Create isolated worktree for implementation
3. Execute tasks phase by phase
4. Create commits after each phase
5. Track progress in tasks.md
6. Confirm with you at key milestones

### Getting Help

```
/iw-help
```

Shows workflow guidance, documentation structure, and available commands.

## Workflow Overview

The typical workflow for a planned feature:

1. **Plan**: `/iw-plan <issue-number>` creates detailed implementation plan
2. **Review**: Review plan files, request changes if needed
3. **Implement**: `/iw-implement <issue-number>` executes the plan
4. **Verify**: Confirm after each phase, run tests
5. **Complete**: Automatic PR creation and worktree cleanup

## Requirements

### Core Requirements
- **Claude Code** (latest version)
- **Git** (for version control operations)
- **Python 3.7+** (for helper scripts)

### Optional Requirements
- **GitHub CLI (gh)** - For GitHub issue and PR operations
- **jq** - For JSON processing in scripts

### Required for Language-Specific Skills
- **Go 1.21+** - If using go-dev-guidelines skill

## Updating the Workflow

### Via Install Command

If you used the bootstrap installation:
```
/iw-install --update
```

This fetches the latest version from GitHub and overwrites existing files.

### Manual Update

Re-run the bootstrap command or manual installation steps to get the latest version.

## Uninstalling

### Via Install Command

```
/iw-install --uninstall
```

### Manual Uninstall

Remove the installed directories:

**Project-level**:
```bash
rm -rf .claude/skills/iw-*
rm -rf .claude/skills/go-dev-guidelines
rm -rf .claude/skills/skill-creator
rm -f .claude/commands/iw-*.md
rm -f .claude/hooks/load_workflow.sh
rm -f .claude/hooks/list_skills.sh
```

**User-level**:
```bash
rm -rf ~/.claude/skills/iw-*
rm -rf ~/.claude/skills/go-dev-guidelines
rm -rf ~/.claude/skills/skill-creator
rm -f ~/.claude/commands/iw-*.md
rm -f ~/.claude/hooks/load_workflow.sh
rm -f ~/.claude/hooks/list_skills.sh
```

## Documentation Structure

The workflow creates a structured documentation approach:

```
.docs/
├── issues/              # Issue-based implementation plans
│   └── <number>/
│       ├── <number>-plan.md       # Implementation plan
│       ├── <number>-tasks.md      # Task checklist
│       ├── <number>-context.md    # Quick reference
│       └── <number>-research.md   # Research notes
├── adhoc/               # Ad-hoc plans not tied to issues
│   └── <name>/
│       └── (same structure)
└── knowledge/           # Institutional knowledge
    ├── learnings/       # Corrections and discoveries
    ├── architecture/    # Architecture documentation
    └── gotchas/         # Known issues and workarounds
```

## Customization

### Adding Language-Specific Guidelines

Create additional language-specific guideline skills following the pattern of `go-dev-guidelines`:

1. Create `.claude/skills/<language>-guidelines/SKILL.md`
2. Document coding standards, testing patterns, architecture patterns
3. Reference from `iw-planner` and `iw-executor` skills

### Adding Custom Skills

Use the `skill-creator` skill to create new custom skills.

## Troubleshooting

### Skills Not Loading

1. Verify files are in correct location (.claude/skills/)
2. Check SKILL.md has proper YAML frontmatter
3. Restart Claude Code session

### Scripts Not Executing

1. Ensure Python 3.7+ is installed
2. Check scripts are in `scripts/` subdirectory of skill
3. Verify script permissions (should be readable)

### Hooks Not Running

1. Check hooks are executable: `chmod +x .claude/hooks/*.sh`
2. Verify hooks are in correct location
3. Check hook configuration in settings

## Contributing

Contributions are welcome! Areas for contribution:

- Additional language-specific guidelines skills (Python, TypeScript, Rust, etc.)
- Enhanced GitHub integration features
- Additional helper scripts for common tasks
- Documentation improvements

## License

Apache 2 - See LICENSE file for details

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check existing issues for similar problems
- Review workflow documentation in skills

---

Generated with Claude Code Implementation Workflow
