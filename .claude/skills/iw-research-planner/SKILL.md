---
name: iw-research-planner
description: Define research scope and create structured research plan. This skill should be used when starting a new research project to define questions, scope, methodology, and success criteria. Supports both technical code research and academic paper research.
---

# Research Planner

## Overview

Create structured research plans through interactive scoping process. Defines research questions, scope, methodology, and success criteria before beginning information gathering.

## When to Use This Skill

Invoke when:
1. Starting a new research project
2. Need to understand a technical topic deeply
3. Investigating how something is implemented
4. Conducting literature review on a subject
5. Comparing different approaches or solutions

## Workflow

### Step 1: Understand Research Intent

Ask user:
1. What is the main topic or question you're researching?
2. What do you hope to learn or understand?
3. What will you do with this research? (inform decision, implement feature, write paper, etc.)

Extract:
- Research topic
- Primary questions
- Intended use/outcome

### Step 1.5: Select Workspace Location

After understanding intent, determine where to store research files during work.

**Detect Obsidian Vault (if available):**

1. **Check if obsidian-local-api skill is available:**
   - Try to invoke the obsidian-local-api skill
   - If successful, proceed with detection
   - If not available, skip Obsidian options

2. **Test Obsidian API connection:**
   ```bash
   # Use obsidian_client.py to test connection
   python3 .claude/skills/obsidian-local-api/scripts/obsidian_client.py --test
   ```

3. **Get vault information:**
   - If connection successful, get vault path from API
   - Offer vault root as workspace option

**Prompt user for workspace location:**

Present options using AskUserQuestion tool:

```
Where would you like to work on this research?

Options:
1. .docs/research (default) - Standard location in project docs
2. [Obsidian Vault Root] - Your Obsidian vault (if detected)
3. Custom path - Specify a different location

Default: .docs/research
```

**Save choice:**
- Pass selected workspace_path to init_research.py
- Create `.research-config.json` in workspace
- Store: research_name, workspace_path, created_date, obsidian_integration flag

### Step 2: Define Research Questions

Work with user to create 3-5 specific research questions.

**Good research questions:**
- Specific and answerable
- Relevant to the stated goal
- Scoped appropriately (not too broad)

**Examples:**
- ❌ "How does authentication work?" (too broad)
- ✅ "How do major web frameworks (Next.js, Django, Rails) implement JWT refresh token rotation?"

- ❌ "What is machine learning?" (too broad)
- ✅ "What are the trade-offs between transformer and LSTM architectures for time-series forecasting?"

### Step 3: Determine Source Types

Based on research questions, identify what sources are needed:
- Academic papers (Google Scholar, arXiv, PubMed)
- Code repositories (GitHub, GitLab)
- Technical documentation (official docs, API references)
- Blog posts and tutorials
- Books and reference materials
- Other domain-specific sources

### Step 4: Define Scope Boundaries

Explicitly document:
- **What's included**: Topics, technologies, timeframes to cover
- **What's excluded**: Related but out-of-scope topics to avoid scope creep

### Step 5: Create Research Plan File

Use `scripts/init_research.py` to initialize structure, then populate `research-plan.md` with:
- Research questions
- Scope (included/excluded)
- Source types needed
- Methodology (how to organize findings)
- Success criteria
- Timeline estimates are not required as this is an automated process

**Steps:**

1. **Initialize research directory:**
   ```bash
   python3 .claude/skills/iw-research-planner/scripts/init_research.py <research-name>
   ```
   This creates `.docs/research/<research-name>/` with template files.

2. **Populate research-plan.md:**
   - Use the Write or Edit tool to fill in the template
   - Include all research questions (from Step 2)
   - Define scope boundaries (from Step 4)
   - List source types needed (from Step 3)
   - Define methodology for organizing findings (thematic, chronological, by source type, etc.)
   - Define success criteria (how will you know research is complete?)

3. **Example research-plan.md structure:**
   ```markdown
   # Research Plan: [Research Name]

   **Created**: [Date]
   **Status**: Planning

   ## Research Questions

   1. [Question 1]
   2. [Question 2]
   3. [Question 3]

   ## Research Scope

   ### What's Included:
   - [Topic/area 1]
   - [Topic/area 2]

   ### What's Excluded:
   - [Out of scope item 1]
   - [Out of scope item 2]

   ### Source Types Needed:
   - [x] Academic papers and journals
   - [x] Code repositories and implementations
   - [ ] Technical documentation
   - [ ] Blog posts and articles

   ## Methodology

   ### Information Gathering Strategy:
   [How will you find and collect information?]

   ### Organization Strategy:
   [How will findings be organized? By theme? By source type? Chronologically?]

   ### Success Criteria:
   [How will you know the research is complete and thorough?]

   ## Output Format

   - Report structure: Executive Summary → Key Findings → Detailed Analysis → References
   - Citation style: Simple references (source list)
   - Special requirements: [Any specific needs]
   ```

### Step 6: Present Plan for Confirmation

Show research plan to user and confirm before proceeding to execution phase.

Present summary:
```
✓ Research Plan Created

Research: [research-name]
Workspace: [workspace-path]/[research-name]/
Obsidian integration: [enabled/disabled]

Research Questions:
1. [Question 1]
2. [Question 2]
3. [Question 3]

Scope: [Brief summary of what's included/excluded]

Source Types:
- [List of source types to investigate]

Methodology: [Brief description of organization strategy]

Success Criteria: [How completion will be measured]

The research plan is ready. Next step:
Use /iw-research-execute to gather information and generate report

Note: Final report location will be selected after synthesis completes.
Intermediate files will be cleaned up automatically.

Ready to proceed with research execution?
```

## Resources

### scripts/init_research.py

Python script that creates the research directory structure and initializes template files.

**Usage:**
```bash
python3 .claude/skills/iw-research-planner/scripts/init_research.py <research-name>
```

**With workspace selection:**
```bash
python3 .claude/skills/iw-research-planner/scripts/init_research.py <research-name> --workspace /path/to/workspace --obsidian
```

**Creates:**
- `<workspace>/<research-name>/` directory
- `research-plan.md` from template
- `sources.md` file
- `findings.md` file
- `assets/` subdirectory
- `.research-config.json` with workspace configuration

### scripts/detect_obsidian.py (Helper)

Helper script to detect Obsidian vault and test API connection.

**Usage:**
```bash
python3 .claude/skills/iw-research-planner/scripts/detect_obsidian.py
```

**Returns** (JSON):
```json
{
  "available": true,
  "vault_path": "/Users/username/Obsidian/MyVault",
  "vault_name": "MyVault",
  "api_version": "1.5.0"
}
```

**Or if not available:**
```json
{
  "available": false,
  "error": "Obsidian API not configured"
}
```

**Implementation**:
- Attempts to import obsidian_client from obsidian-local-api skill
- Tests API connection
- Queries vault information
- Returns structured result for skill to parse

### assets/research-plan-template.md

Template file with placeholders for creating new research plans. Contains standard sections for questions, scope, methodology, and success criteria.
