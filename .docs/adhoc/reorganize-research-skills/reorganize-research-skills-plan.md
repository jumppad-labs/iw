# Reorganize Research Skills Implementation Plan

**Created**: 2025-11-03
**Last Updated**: 2025-11-03

## Overview

Move the three research skills from the project root into `.claude/skills/` with the `iw-` prefix to match the standard implementation workflow naming convention. Update all documentation, slash commands, and the installer to reflect the new locations and names.

## Current State Analysis

### What Exists Now:

**Research Skills at Project Root:**
- `research-planner/` - Located at project root
  - `SKILL.md` (5.5 KB)
  - `scripts/init_research.py`, `add_source.py`
  - `assets/research-plan-template.md`
- `research-executor/` - Located at project root
  - `SKILL.md` (8.9 KB)
  - `scripts/add_finding.py`
  - `references/research-best-practices.md` (10.2 KB)
- `research-synthesizer/` - Located at project root
  - `SKILL.md` (10.9 KB)
  - `scripts/generate_report.py`
  - `assets/report-template.md`

**Slash Commands:**
- `.claude/commands/research-plan.md` - Invokes `research-planner`
- `.claude/commands/research-execute.md` - Invokes `research-executor`
- `.claude/commands/research-synthesize.md` - Invokes `research-synthesizer`

**Documentation References:**
- `README.md` - Lists research skills separately from iw-* skills (lines 27-30)
- `README.md` - Lists slash commands separately (lines 45-47)
- `README.md` - Research workflow section (lines 150-203)
- `.claude/skills/iw-install/SKILL.md` - Lists 10 skills, doesn't include research skills (lines 90-100)

### Key Constraints:
- Must maintain all functionality - skills work correctly as-is
- Must preserve all script functionality
- Must update skill names in YAML frontmatter
- Must update command descriptions to reference new names
- Install skill will need to include the 3 new skills (total becomes 13)

## Desired End State

### Skills in Standard Location:
```
.claude/skills/
├── iw-research-planner/
│   ├── SKILL.md (name: iw-research-planner)
│   ├── scripts/
│   └── assets/
├── iw-research-executor/
│   ├── SKILL.md (name: iw-research-executor)
│   ├── scripts/
│   └── references/
└── iw-research-synthesizer/
    ├── SKILL.md (name: iw-research-synthesizer)
    ├── scripts/
    └── assets/
```

### Updated Commands:
```
.claude/commands/
├── iw-research-plan.md (invokes iw-research-planner)
├── iw-research-execute.md (invokes iw-research-executor)
└── iw-research-synthesize.md (invokes iw-research-synthesizer)
```

### Updated Documentation:
- README.md shows 13 total skills (all with iw- prefix)
- README.md uses `/iw-research-*` command names
- iw-install/SKILL.md lists all 13 skills
- iw-help references correct command names
- iw-workflow references correct skill names

### Verification Method:
- All skills load correctly when invoked
- All slash commands work
- Scripts execute from new locations
- Documentation is consistent
- No references to old names remain

## What We're NOT Doing

- **NOT changing** skill functionality - only location and naming
- **NOT modifying** script logic - only paths if needed
- **NOT updating** `.docs/adhoc/research-skills/` plan files - historical record
- **NOT creating** new features or capabilities
- **NOT changing** the research workflow itself

## Implementation Approach

**Strategy**: Move files, update names, update references. This is a straightforward reorganization with three clear phases:

1. **Phase 1**: Move and rename skills
2. **Phase 2**: Update commands and documentation
3. **Phase 3**: Verify and clean up

**Key Design Decisions**:
1. **Use git mv** - Preserve file history in git
2. **Update YAML frontmatter** - Change `name:` field in each SKILL.md
3. **Rename commands** - Use `iw-` prefix for consistency
4. **Batch documentation updates** - Update all docs in one phase

---

## Phase 1: Move and Rename Skills

### Overview
Move the three research skill directories into `.claude/skills/` with `iw-` prefix names. Update YAML frontmatter in each SKILL.md.

### Changes Required:

#### 1. Move research-planner → iw-research-planner

**Action**: Move directory and update SKILL.md

**Commands**:
```bash
git mv research-planner .claude/skills/iw-research-planner
```

**File to Edit**: `.claude/skills/iw-research-planner/SKILL.md`

**Current YAML frontmatter** (lines 1-4):
```yaml
---
name: research-planner
description: Define research scope and create structured research plan. This skill should be used when starting a new research project to define questions, scope, methodology, and success criteria. Supports both technical code research and academic paper research.
---
```

**Updated YAML frontmatter**:
```yaml
---
name: iw-research-planner
description: Define research scope and create structured research plan. This skill should be used when starting a new research project to define questions, scope, methodology, and success criteria. Supports both technical code research and academic paper research.
---
```

**Reasoning**: Only the `name` field changes - the description remains accurate.

#### 2. Move research-executor → iw-research-executor

**Action**: Move directory and update SKILL.md

**Commands**:
```bash
git mv research-executor .claude/skills/iw-research-executor
```

**File to Edit**: `.claude/skills/iw-research-executor/SKILL.md`

**Current YAML frontmatter** (lines 1-4):
```yaml
---
name: research-executor
description: Gather information from diverse sources including academic papers, code repositories, and technical documentation. This skill should be used after creating a research plan to execute information gathering and organize findings. Automatically adapts strategy based on source type.
---
```

**Updated YAML frontmatter**:
```yaml
---
name: iw-research-executor
description: Gather information from diverse sources including academic papers, code repositories, and technical documentation. This skill should be used after creating a research plan to execute information gathering and organize findings. Automatically adapts strategy based on source type.
---
```

**Reasoning**: Only the `name` field changes.

#### 3. Move research-synthesizer → iw-research-synthesizer

**Action**: Move directory and update SKILL.md

**Commands**:
```bash
git mv research-synthesizer .claude/skills/iw-research-synthesizer
```

**File to Edit**: `.claude/skills/iw-research-synthesizer/SKILL.md`

**Current YAML frontmatter** (lines 1-4):
```yaml
---
name: research-synthesizer
description: Generate comprehensive markdown research reports from gathered findings. This skill should be used after research-executor has collected information to synthesize findings into a well-structured report with executive summary, detailed analysis, and references. Fully automated report generation.
---
```

**Updated YAML frontmatter**:
```yaml
---
name: iw-research-synthesizer
description: Generate comprehensive markdown research reports from gathered findings. This skill should be used after iw-research-executor has collected information to synthesize findings into a well-structured report with executive summary, detailed analysis, and references. Fully automated report generation.
---
```

**Reasoning**: Update both `name` field and the description reference to `iw-research-executor`.

### Testing for This Phase:

```bash
# Verify directories moved
ls -la .claude/skills/iw-research-*

# Verify old directories are gone
ls research-planner 2>&1 | grep "No such file"
ls research-executor 2>&1 | grep "No such file"
ls research-synthesizer 2>&1 | grep "No such file"

# Verify YAML frontmatter updated
head -5 .claude/skills/iw-research-planner/SKILL.md | grep "name: iw-research-planner"
head -5 .claude/skills/iw-research-executor/SKILL.md | grep "name: iw-research-executor"
head -5 .claude/skills/iw-research-synthesizer/SKILL.md | grep "name: iw-research-synthesizer"
```

### Success Criteria:

#### Automated Verification:
- [ ] `ls .claude/skills/iw-research-planner` shows skill directory
- [ ] `ls .claude/skills/iw-research-executor` shows skill directory
- [ ] `ls .claude/skills/iw-research-synthesizer` shows skill directory
- [ ] `ls research-planner` returns "No such file or directory"
- [ ] YAML frontmatter in all three SKILL.md files shows `iw-` prefix

#### Manual Verification:
- [ ] Git history preserved (use `git log --follow`)
- [ ] All subdirectories (scripts/, assets/, references/) moved correctly
- [ ] No broken symlinks or references
- [ ] File permissions preserved

---

## Phase 2: Update Commands and Documentation

### Overview
Update slash commands to use new skill names, update README.md to reflect unified naming, and update the installer skill to include the research skills.

### Changes Required:

#### 1. Rename and Update Slash Commands

**Action A**: Rename `research-plan.md` → `iw-research-plan.md`

**Commands**:
```bash
git mv .claude/commands/research-plan.md .claude/commands/iw-research-plan.md
```

**File to Edit**: `.claude/commands/iw-research-plan.md`

**Current content** (all 8 lines):
```markdown
---
description: Create a new research plan
---

Invoke the research-planner skill to create a structured research plan. This will guide you through defining research questions, scope, and methodology.

After the plan is created, use /research-execute to gather information.
```

**Updated content**:
```markdown
---
description: Create a new research plan
---

Invoke the iw-research-planner skill to create a structured research plan. This will guide you through defining research questions, scope, and methodology.

After the plan is created, use /iw-research-execute to gather information.
```

**Reasoning**: Update skill name and next-step command reference.

---

**Action B**: Rename `research-execute.md` → `iw-research-execute.md`

**Commands**:
```bash
git mv .claude/commands/research-execute.md .claude/commands/iw-research-execute.md
```

**File to Edit**: `.claude/commands/iw-research-execute.md`

**Current content** (all 8 lines):
```markdown
---
description: Execute research information gathering
---

Invoke the research-executor skill to gather information from diverse sources based on your research plan. This will systematically collect and organize findings.

After gathering information, use /research-synthesize to generate the report.
```

**Updated content**:
```markdown
---
description: Execute research information gathering
---

Invoke the iw-research-executor skill to gather information from diverse sources based on your research plan. This will systematically collect and organize findings.

After gathering information, use /iw-research-synthesize to generate the report.
```

**Reasoning**: Update skill name and next-step command reference.

---

**Action C**: Rename `research-synthesize.md` → `iw-research-synthesize.md`

**Commands**:
```bash
git mv .claude/commands/research-synthesize.md .claude/commands/iw-research-synthesize.md
```

**File to Edit**: `.claude/commands/iw-research-synthesize.md`

**Current content** (all 6 lines):
```markdown
---
description: Generate research report from findings
---

Invoke the research-synthesizer skill to synthesize gathered findings into a comprehensive markdown report with executive summary, detailed analysis, and references.
```

**Updated content**:
```markdown
---
description: Generate research report from findings
---

Invoke the iw-research-synthesizer skill to synthesize gathered findings into a comprehensive markdown report with executive summary, detailed analysis, and references.
```

**Reasoning**: Update skill name reference.

#### 2. Update README.md - Skills Section

**File**: `README.md`

**Current content** (lines 16-35):
```markdown
### Skills (13 total)

#### Implementation Workflow Skills
- **iw-planner** - Create detailed implementation plans through interactive research process
- **iw-executor** - Execute implementation plans with phase-based commits and tracking
- **iw-workflow** - Workflow guidance and documentation structure explanation
- **iw-learnings** - Search past learnings and corrections from previous work
- **iw-init** - Initialize .docs directory structure for plans and knowledge
- **iw-github-issue-reader** - Load comprehensive GitHub issue information
- **iw-github-pr-creator** - Create GitHub pull requests with plan summaries
- **iw-git-workflow** - Manage git operations with worktrees and phase commits

#### Research Skills
- **research-planner** - Define research scope and create structured research plans
- **research-executor** - Gather information from academic papers, code repos, and documentation
- **research-synthesizer** - Generate comprehensive markdown reports with citations

#### Development Guidelines
- **go-dev-guidelines** - Go development patterns and TDD workflow (language-specific)
- **skill-creator** - Guide for creating new skills
```

**Updated content**:
```markdown
### Skills (13 total)

#### Implementation Workflow Skills
- **iw-planner** - Create detailed implementation plans through interactive research process
- **iw-executor** - Execute implementation plans with phase-based commits and tracking
- **iw-workflow** - Workflow guidance and documentation structure explanation
- **iw-learnings** - Search past learnings and corrections from previous work
- **iw-init** - Initialize .docs directory structure for plans and knowledge
- **iw-github-issue-reader** - Load comprehensive GitHub issue information
- **iw-github-pr-creator** - Create GitHub pull requests with plan summaries
- **iw-git-workflow** - Manage git operations with worktrees and phase commits
- **iw-research-planner** - Define research scope and create structured research plans
- **iw-research-executor** - Gather information from academic papers, code repos, and documentation
- **iw-research-synthesizer** - Generate comprehensive markdown reports with citations

#### Development Guidelines
- **go-dev-guidelines** - Go development patterns and TDD workflow (language-specific)
- **skill-creator** - Guide for creating new skills
```

**Reasoning**: Merge research skills into Implementation Workflow Skills section with `iw-` prefix. Remove separate "Research Skills" section.

#### 3. Update README.md - Commands Section

**File**: `README.md`

**Current content** (lines 37-48):
```markdown
### Slash Commands (7 total)

#### Implementation Workflow Commands
- **/iw-plan** - Create detailed implementation plan
- **/iw-implement** - Execute implementation plan
- **/iw-help** - Show workflow guidance and available commands
- **/iw-install** - Manage workflow installation (install, update, uninstall)

#### Research Commands
- **/research-plan** - Create new research plan with questions and scope
- **/research-execute** - Gather information from diverse sources
- **/research-synthesize** - Generate comprehensive research report
```

**Updated content**:
```markdown
### Slash Commands (7 total)

- **/iw-plan** - Create detailed implementation plan
- **/iw-implement** - Execute implementation plan
- **/iw-help** - Show workflow guidance and available commands
- **/iw-install** - Manage workflow installation (install, update, uninstall)
- **/iw-research-plan** - Create new research plan with questions and scope
- **/iw-research-execute** - Gather information from diverse sources
- **/iw-research-synthesize** - Generate comprehensive research report
```

**Reasoning**: Merge into single list with updated command names.

#### 4. Update README.md - Research Workflow Section

**File**: `README.md`

**Current section** (lines 150-203):
Contains references to `/research-plan`, `/research-execute`, `/research-synthesize`

**Changes needed**:
- Line 157: `/research-plan` → `/iw-research-plan`
- Line 170: `/research-execute` → `/iw-research-execute`
- Line 186: `/research-synthesize` → `/iw-research-synthesize`

**Find and replace**:
```bash
# In the Research Workflow section:
/research-plan → /iw-research-plan
/research-execute → /iw-research-execute
/research-synthesize → /iw-research-synthesize
```

**Reasoning**: Update all command references to match new names.

#### 5. Update iw-install/SKILL.md

**File**: `.claude/skills/iw-install/SKILL.md`

**Current content** (lines 88-100):
```markdown
## What Gets Installed

The installer manages these workflow components:

### Skills (10 total)
1. **iw-planner** - Create detailed implementation plans
2. **iw-executor** - Execute implementation plans
3. **iw-workflow** - Workflow guidance and documentation
4. **iw-learnings** - Search past learnings
5. **iw-init** - Initialize .docs structure
6. **iw-github-issue-reader** - Load GitHub issue context
7. **iw-github-pr-creator** - Create GitHub pull requests
8. **iw-git-workflow** - Manage git operations
9. **go-dev-guidelines** - Go development patterns
10. **skill-creator** - Guide for creating skills
```

**Updated content**:
```markdown
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
10. **iw-research-executor** - Gather information from diverse sources
11. **iw-research-synthesizer** - Generate comprehensive research reports
12. **go-dev-guidelines** - Go development patterns
13. **skill-creator** - Guide for creating skills
```

**Reasoning**: Add three research skills to installer's managed components list, update count to 13.

#### 6. Update iw-help Command (if needed)

**File**: `.claude/commands/iw-help.md`

**Check**: Does this file reference research commands?

**Current content** (lines 10-15):
```markdown
Use the Skill tool to invoke the `iw-workflow` skill, which provides:
- Available commands (/iw-plan, /iw-implement, /iw-init)
- Documentation structure (CLAUDE.md vs .docs/knowledge/ vs iw-workflow skill)
- Planning and implementation workflow
- Learning capture process
- Where to document different types of information
```

**Action**: If research commands are mentioned, update them. Otherwise, no changes needed.

**Reasoning**: iw-workflow skill dynamically lists commands, so likely no hardcoded references.

### Testing for This Phase:

```bash
# Verify command files renamed
ls .claude/commands/iw-research-*.md | wc -l  # Should be 3

# Verify old command files gone
ls .claude/commands/research-*.md 2>&1 | grep "No such file"

# Verify README updates
grep -c "iw-research-" README.md  # Should be multiple occurrences
grep "### Research Commands" README.md  # Should return nothing (section removed)

# Verify skill count
grep "Skills (13 total)" README.md
grep "Skills (13 total)" .claude/skills/iw-install/SKILL.md
```

### Success Criteria:

#### Automated Verification:
- [ ] Three command files exist: `iw-research-plan.md`, `iw-research-execute.md`, `iw-research-synthesize.md`
- [ ] Old command files (`research-*.md`) don't exist
- [ ] `grep "research-planner" .claude/commands/*.md` returns nothing
- [ ] `grep "iw-research-" README.md` finds multiple references
- [ ] Skills count shows "13 total" in README.md and iw-install/SKILL.md

#### Manual Verification:
- [ ] README.md has unified skills list (no separate "Research Skills" section)
- [ ] All command references use `/iw-research-*` pattern
- [ ] Documentation is clear and consistent
- [ ] iw-install skill lists all 13 skills

---

## Phase 3: Verification and Cleanup

### Overview
Test that all skills and commands work correctly, verify no broken references exist, and remove any orphaned files.

### Changes Required:

#### 1. Test Skill Invocations

**Action**: Test each skill loads correctly

**Test commands**:
```bash
# These would be run in Claude Code session
# /iw-research-plan
# /iw-research-execute
# /iw-research-synthesize
```

**Expected behavior**:
- Each command should invoke the corresponding skill
- Skills should load without errors
- YAML frontmatter should show correct `name:` field
- No "skill not found" errors

#### 2. Test Script Execution

**Action**: Verify scripts work from new location

**Test commands**:
```bash
# Test init_research.py
python3 .claude/skills/iw-research-planner/scripts/init_research.py test-verify

# Test add_source.py
python3 .claude/skills/iw-research-planner/scripts/add_source.py test-verify "https://example.com" "paper"

# Test add_finding.py
python3 .claude/skills/iw-research-executor/scripts/add_finding.py test-verify "Theme" "Finding" "Source"

# Test generate_report.py
python3 .claude/skills/iw-research-synthesizer/scripts/generate_report.py test-verify

# Clean up test directory
rm -rf .docs/research/test-verify
```

**Expected behavior**:
- All scripts execute without import errors
- Scripts create expected files
- No hardcoded path issues

#### 3. Search for Remaining Old References

**Action**: Find any lingering references to old names

**Search commands**:
```bash
# Find any remaining references to old skill names
grep -r "research-planner" --exclude-dir=.git --exclude-dir=.docs .
grep -r "research-executor" --exclude-dir=.git --exclude-dir=.docs .
grep -r "research-synthesizer" --exclude-dir=.git --exclude-dir=.docs .

# Check .docs/adhoc/research-skills/ is preserved (historical record)
ls .docs/adhoc/research-skills/
```

**Expected results**:
- No matches in active code/docs (only in .docs/adhoc/research-skills/ historical plan)
- Historical plan files remain unchanged

#### 4. Verify Git History

**Action**: Ensure file history preserved

**Commands**:
```bash
# Verify git history follows renamed files
git log --follow --oneline .claude/skills/iw-research-planner/SKILL.md
git log --follow --oneline .claude/skills/iw-research-executor/SKILL.md
git log --follow --oneline .claude/skills/iw-research-synthesizer/SKILL.md
```

**Expected behavior**:
- History shows commits from before the move
- `git mv` preserved file history

#### 5. Update .gitignore (if needed)

**Action**: Check if .gitignore needs updates

**File**: `.gitignore`

**Check for**:
- Any references to `research-planner/`, `research-executor/`, `research-synthesizer/`
- If found, remove them (skills are in .claude/skills/ now)

**Expected**: Likely no changes needed - research skills weren't gitignored.

### Testing for This Phase:

```bash
# Comprehensive grep for old names
grep -r "research-planner\|research-executor\|research-synthesizer" \
  --exclude-dir=.git \
  --exclude-dir=.docs \
  --include="*.md" \
  --include="*.py" \
  .

# Should only find references in:
# - .docs/adhoc/research-skills/ (historical - OK to keep)
# - Nothing else

# Verify scripts work
cd .claude/skills/iw-research-planner/scripts/
python3 init_research.py --help  # Should show usage
```

### Success Criteria:

#### Automated Verification:
- [ ] All three skills invoke without errors
- [ ] All four Python scripts execute successfully
- [ ] No references to old skill names outside `.docs/adhoc/research-skills/`
- [ ] Git history preserved for all moved files

#### Manual Verification:
- [ ] Complete workflow works: plan → execute → synthesize
- [ ] Commands listed correctly when running `/help`
- [ ] Documentation reads naturally with unified naming
- [ ] No broken links or references in README.md
- [ ] .docs/adhoc/research-skills/ preserved (historical plan intact)

---

## Testing Strategy

### Unit Testing:
Test each skill individually:
1. Invoke `/iw-research-plan` - should start planning workflow
2. Invoke `/iw-research-execute` - should start execution workflow
3. Invoke `/iw-research-synthesize` - should start synthesis workflow

### Integration Testing:
Test complete workflow:
1. Create a test research plan
2. Add some findings
3. Generate a report
4. Verify all steps work end-to-end

### Verification Testing:
1. Run all grep commands to find stray references
2. Test scripts from new locations
3. Verify documentation accuracy
4. Check git history preservation

## Performance Considerations

**No performance impact expected**:
- Skills load from different location but same mechanism
- Scripts execute with same performance
- No additional processing overhead

## Migration Notes

**Git history**:
- Use `git mv` to preserve file history
- Verify with `git log --follow` after moves

**No data migration**:
- No user data affected
- `.docs/research/` structure unchanged
- Research output files unaffected

**Backward compatibility**:
- Old command names won't work after update
- Users need to use new `/iw-research-*` commands
- Historical plan files reference old names (OK - they're documentation)

## References

### Key Files to Modify:
- `research-planner/SKILL.md` (line 2) → `.claude/skills/iw-research-planner/SKILL.md`
- `research-executor/SKILL.md` (line 2, 4) → `.claude/skills/iw-research-executor/SKILL.md`
- `research-synthesizer/SKILL.md` (line 2, 4) → `.claude/skills/iw-research-synthesizer/SKILL.md`
- `.claude/commands/research-*.md` (all lines) → `.claude/commands/iw-research-*.md`
- `README.md` (lines 16-48, 150-203)
- `.claude/skills/iw-install/SKILL.md` (lines 88-100)

### Pattern to Follow:
- Existing iw-* skills structure in `.claude/skills/`
- Existing command naming in `.claude/commands/`
- README.md structure for skill and command lists
