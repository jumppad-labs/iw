---
name: iw-github-pr-creator
description: Create GitHub pull requests using the gh CLI. This skill should be used when creating PRs from implementation branches, whether from plan-based implementations or general feature branches. Supports plan-based PRs with phase summaries, generic PRs with commit summaries, and different PR templates for various change types.
---

# GitHub PR Creator

## Overview

Create well-formatted GitHub pull requests using the `gh` CLI. Extract information from implementation plans, commit messages, and branch context to generate comprehensive PR descriptions with proper linking to issues and plans.

**Plan-Based PRs:** When creating PRs for iw-executor work, automatically extract phase summaries, link to plan files, and reference the related issue.

**Generic PRs:** For any branch, create PRs with commit summaries, change descriptions, and testing instructions.

**Template Support:** Provide different PR templates for features, bugfixes, documentation, and refactoring to ensure appropriate structure.

## Quick Start

**Create PR from implementation plan:**
```bash
python3 scripts/create_pr.py --plan-path .docs/issues/123/ --branch issue-123-feature
```

**Create generic PR:**
```bash
python3 scripts/create_pr.py --branch feature-branch --template feature
```

**Create PR with custom title/body:**
```bash
gh pr create --title "Add Feature X" --body "Description here"
```

## Workflow

### Method 1: Plan-Based PR Creation

When creating PRs for implementations with plans:

1. **Extract Plan Information:**
   - Use `scripts/extract_plan_summary.py` to get plan details
   - Script extracts:
     - Plan title
     - Phase names and descriptions
     - Issue number (if applicable)
     - Testing instructions
     - Manual verification checklist
   - Returns structured data for PR body

2. **Generate PR Body:**
   - Create PR body using plan-based template:
     ```markdown
     # <Plan Title>

     ## Summary
     - Implemented Phase 1: <name>
     - Implemented Phase 2: <name>
     - Implemented Phase 3: <name>

     ## Changes
     <Brief description of what changed>

     ## Plan
     [Implementation Plan](<path-to-plan>)

     ## Testing
     ### Automated
     - [ ] Run test suite: `make test`
     - [ ] Run integration tests: `make integration`

     ### Manual Verification
     - [ ] <manual check 1>
     - [ ] <manual check 2>

     ## Related
     Closes #<issue-number>
     ```

3. **Create PR:**
   - Use `scripts/create_pr.py` to create PR with gh CLI
   - Specify branch, base branch, and plan path
   - Script does:
     - Extracts plan summary
     - Generates PR title from plan
     - Generates PR body from template
     - Creates PR with `gh pr create`
     - Returns PR URL

4. **Example:**
   ```bash
   python3 scripts/create_pr.py \
     --plan-path .docs/issues/123/ \
     --branch issue-123-add-rate-limiting \
     --base main
   ```

   Output:
   ```
   ✓ Pull request created

   Title: Add Rate Limiting to API
   URL: https://github.com/org/repo/pull/456
   Branch: issue-123-add-rate-limiting → main
   ```

### Method 2: Generic PR Creation

When creating PRs without implementation plans:

1. **Choose PR Template:**
   - Use `scripts/get_pr_template.py` to get appropriate template
   - Templates available:
     - `feature` - New functionality
     - `bugfix` - Bug fixes
     - `docs` - Documentation changes
     - `refactor` - Code refactoring
     - `chore` - Maintenance tasks

2. **Extract Commit Summary:**
   - Script gets recent commits on branch
   - Summarizes changes based on commit messages
   - Identifies key changes and files modified

3. **Generate PR Body:**
   - Use template with commit summary:
     ```markdown
     ## Changes
     <Description of changes>

     ## Commits
     - <commit 1 message>
     - <commit 2 message>
     - <commit 3 message>

     ## Testing
     - [ ] Tests pass locally
     - [ ] Manually verified changes

     ## Checklist
     - [ ] Code follows project guidelines
     - [ ] Tests added/updated
     - [ ] Documentation updated
     ```

4. **Create PR:**
   - Use `gh pr create` directly or via script
   - Provide title, body, and options

5. **Example:**
   ```bash
   python3 scripts/create_pr.py \
     --branch feature-improve-logging \
     --base main \
     --template feature \
     --title "Improve application logging"
   ```

### Method 3: Direct gh CLI Usage

For quick PR creation without scripts:

1. **Basic PR Creation:**
   ```bash
   gh pr create --title "Title" --body "Description"
   ```

2. **Interactive PR Creation:**
   ```bash
   gh pr create --web
   ```
   Opens browser for PR creation with form

3. **PR with Options:**
   ```bash
   gh pr create \
     --title "Fix authentication bug" \
     --body "Fixes issue with JWT token validation" \
     --assignee @me \
     --label bug \
     --reviewer username
   ```

## PR Templates

### Feature Template

Used for new functionality:

```markdown
## Summary
<Brief description of the feature>

## Changes
- <Change 1>
- <Change 2>
- <Change 3>

## Why?
<Motivation for this feature>

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manually tested feature

## Screenshots/Demos
<If UI changes, include screenshots>

## Documentation
- [ ] Updated README if needed
- [ ] Added code comments
- [ ] Updated API docs if needed
```

### Bugfix Template

Used for bug fixes:

```markdown
## Problem
<Description of the bug>

## Root Cause
<What caused the bug>

## Solution
<How this PR fixes the bug>

## Testing
- [ ] Added test case for bug
- [ ] Verified fix works
- [ ] Checked for regression

## Related
Fixes #<issue-number>
```

### Documentation Template

Used for documentation changes:

```markdown
## Documentation Changes
<What documentation was updated>

## Reason
<Why these changes were needed>

## Preview
<Link to preview or screenshots if applicable>

## Checklist
- [ ] Spelling and grammar checked
- [ ] Links tested
- [ ] Examples verified
```

### Refactor Template

Used for code refactoring:

```markdown
## Refactoring Summary
<What was refactored>

## Motivation
<Why this refactoring was needed>

## Changes
- <Change 1>
- <Change 2>

## Impact
<Impact on performance, maintainability, etc.>

## Testing
- [ ] All existing tests pass
- [ ] No behavior changes
- [ ] Code coverage maintained
```

## Integration with Other Skills

### With iw-executor

The iw-executor skill uses iw-github-pr-creator for PR creation:

1. After implementation complete, executor asks user about PR
2. If user wants PR, executor invokes iw-github-pr-creator
3. Provides plan path and branch name
4. PR creator extracts plan info and creates PR

### With iw-git-workflow

The iw-git-workflow cleanup script can use iw-github-pr-creator:

1. When `--create-pr` flag used in cleanup
2. Calls iw-github-pr-creator with plan and branch info
3. PR gets created with proper formatting

This modular approach allows:
- Reusable PR creation across skills
- Consistent PR formatting
- Easy testing of PR generation
- Flexibility in PR creation methods

## Important Guidelines

### PR Titles

**Good titles:**
- Clear and descriptive
- Action-oriented (Add, Fix, Update, Refactor)
- Reference main change
- Example: "Add rate limiting to API endpoints"

**Avoid:**
- Vague titles like "Updates" or "Changes"
- Too long (> 72 chars)
- Missing context

### PR Descriptions

**Include:**
- Summary of changes (what changed)
- Motivation (why it changed)
- Testing instructions
- Link to related issues/plans
- Screenshots for UI changes
- Breaking changes if any

**Structure:**
- Use markdown formatting
- Use checklists for testing steps
- Use code blocks for examples
- Keep paragraphs short

### Linking Issues

**Always link related issues:**
- Use `Closes #123` for issues this PR resolves
- Use `Related to #123` for related but not resolved
- Use `Part of #123` for partial implementations

**Automatic closing:**
- `Closes #123` - GitHub closes issue when PR merges
- `Fixes #123` - Same as Closes
- `Resolves #123` - Same as Closes

### Labels and Reviewers

**Add appropriate labels:**
- `feature`, `bugfix`, `docs`, `refactor`
- `breaking-change` if API changes
- `needs-review` when ready

**Request reviewers:**
- Tag team members for review
- Use `--reviewer` flag with gh CLI
- Or add after PR creation

## Resources

### scripts/

This skill includes three Python scripts for PR creation:

**`create_pr.py`** - Main PR creation script
```bash
python3 scripts/create_pr.py --branch <branch> --base <base> [--plan-path <path>] [--template <type>]
```
Creates PR using gh CLI with extracted information.

**`extract_plan_summary.py`** - Extract summary from plan files
```bash
python3 scripts/extract_plan_summary.py --plan-path <path>
```
Returns JSON with plan title, phases, issue number, testing steps.

**`get_pr_template.py`** - Get PR template for type
```bash
python3 scripts/get_pr_template.py --type <feature|bugfix|docs|refactor>
```
Returns PR body template as string.

These scripts provide consistent PR creation across the project.

## Examples

### Example 1: Plan-Based Implementation PR

```bash
# After implementing from plan in .docs/issues/357/
python3 scripts/create_pr.py \
  --plan-path .docs/issues/357/ \
  --branch issue-357-add-ollama-provider \
  --base main
```

Creates PR:
```
Title: Add Ollama Model Provider
Body:
  # Add Ollama Model Provider

  ## Summary
  - Implemented Phase 1: Add Ollama client integration
  - Implemented Phase 2: Implement provider interface
  - Implemented Phase 3: Add configuration and tests

  ## Plan
  [Implementation Plan](.docs/issues/357/357-plan.md)

  ## Testing
  ### Automated
  - [ ] Run test suite: make test
  - [ ] Run integration tests: make integration

  ### Manual Verification
  - [ ] Test Ollama connection
  - [ ] Verify model listing
  - [ ] Test inference calls

  ## Related
  Closes #357
```

### Example 2: Generic Feature PR

```bash
python3 scripts/create_pr.py \
  --branch feature-improve-error-handling \
  --base main \
  --template feature \
  --title "Improve error handling in HTTP client"
```

Creates PR with feature template and commit summary.

### Example 3: Quick Bugfix PR

```bash
gh pr create \
  --title "Fix nil pointer in config loader" \
  --body "$(cat <<EOF
## Problem
Config loader crashes with nil pointer when file missing.

## Solution
Added nil check before accessing config.Data.

## Testing
- Added test case for missing config file
- Verified error message is clear

Fixes #345
EOF
)"
```

Uses gh CLI directly with heredoc for body.
