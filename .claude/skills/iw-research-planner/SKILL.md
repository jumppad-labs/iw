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
Location: .docs/research/[research-name]/

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

Ready to proceed with research execution?
```

## Resources

### scripts/init_research.py

Python script that creates the research directory structure and initializes template files.

**Usage:**
```bash
python3 .claude/skills/iw-research-planner/scripts/init_research.py <research-name>
```

**Creates:**
- `.docs/research/<research-name>/` directory
- `research-plan.md` from template
- `sources.md` file
- `findings.md` file
- `assets/` subdirectory

### assets/research-plan-template.md

Template file with placeholders for creating new research plans. Contains standard sections for questions, scope, methodology, and success criteria.
