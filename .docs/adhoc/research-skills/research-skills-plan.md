# Research Skills Implementation Plan

**Created**: 2025-11-03
**Last Updated**: 2025-11-03

## Overview

Implement three specialized skills that give Claude "research superpowers" following academic research best practices. The skills will work together to plan, execute, and synthesize research from diverse sources (academic papers, code repositories, technical documentation) into comprehensive, well-structured markdown reports with citations.

## Current State Analysis

### What Exists Now:
- Empty project at `/home/nicj/code/github.com/nicholasjackson/claude-research-skills`
- No existing code or skills
- User has existing skill infrastructure in `~/.claude/skills/` with 11 installed skills including:
  - `skill-creator` - Provides skill creation guidance
  - `iw-planner` - Creates implementation plans with 4-file structure
  - `iw-learnings` - Searches institutional knowledge
  - `go-dev-guidelines` - Language-specific guidelines

### Key Patterns Discovered:

**From `~/.claude/skills/skill-creator/SKILL.md`:**
- Standard structure: `SKILL.md` + optional `scripts/`, `references/`, `assets/`
- YAML frontmatter with name and description required
- Progressive disclosure: Metadata → SKILL.md → Bundled resources
- Use imperative/infinitive form, not second person

**From `~/.claude/skills/iw-planner/`:**
- Template system with `{{PLACEHOLDER}}` replacement
- Python scripts for deterministic operations (`init_plan.py`)
- 4-file plan structure: plan.md, research.md, context.md, tasks.md
- Extensive use of Task tool for parallel agent spawning

**From Academic Research Methodology:**
- Standard workflow: Plan → Literature Review → Methodology → Analysis → Report
- Report structure: Summary → Detailed Findings → References
- Citation formats: APA, MLA, Chicago, IEEE
- Synthesis techniques: Thematic organization, concept mapping, evidence hierarchies

## Desired End State

Three specialized skills that work together:

1. **research-planner**: Defines research scope, questions, and methodology
2. **research-executor**: Gathers information from diverse sources (academic papers, code, docs)
3. **research-synthesizer**: Generates comprehensive markdown reports automatically

**Verification Method:**
- Can successfully plan a research project
- Can execute research gathering from multiple source types
- Can generate a well-structured markdown report with summary and citations
- Report is Obsidian-compatible for future integration

## What We're NOT Doing

- **NOT implementing** advanced citation formatting (APA/MLA/Chicago/IEEE) - using simple references only
- **NOT integrating** with iw-* workflow in initial version (future enhancement)
- **NOT implementing** Obsidian sync/export in initial version (noted for later)
- **NOT creating** separate code and academic research executors (using single flexible executor)
- **NOT implementing** collaboration features
- **NOT building** web scraping or complex API integrations beyond WebFetch/WebSearch

## Implementation Approach

**Strategy**: Build three standalone skills following the existing skill patterns discovered in research. Each skill will:
- Have a clear SKILL.md with workflow instructions
- Use Python scripts for deterministic operations (initialization, file management)
- Include templates for consistent output
- Work independently but compose together for complete workflow

**Key Design Decisions**:
1. **Single flexible executor** (not separate code/academic) - more comprehensive reports from mixed research
2. **Fully automated report generation** - minimal user intervention
3. **Simple references** - just track sources without complex formatting
4. **Obsidian-compatible structure** - standard markdown, ready for future integration
5. **Standalone initially** - iw-* integration as future enhancement

---

## Phase 1: Core Infrastructure

### Overview
Set up the foundational structure for all three research skills, including directory structure, initialization scripts, and templates.

### Changes Required:

#### 1. Create Base Skill Directories
**Action**: Create directory structure for three skills

**Structure to create:**
```
research-skills/
├── research-planner/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── init_research.py
│   └── assets/
│       └── research-plan-template.md
├── research-executor/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── add_source.py
│   │   └── add_finding.py
│   └── references/
│       └── research-best-practices.md
└── research-synthesizer/
    ├── SKILL.md
    ├── scripts/
    │   └── generate_report.py
    └── assets/
        └── report-template.md
```

**Reasoning**: Following the standard skill structure pattern observed in existing skills, with scripts for deterministic operations and assets for templates.

#### 2. Create Initialization Script
**File**: `research-planner/scripts/init_research.py`
**Purpose**: Creates `.docs/research/<research-name>/` directory structure

**Script functionality:**
```python
#!/usr/bin/env python3
"""
Initialize a new research project directory structure.

Usage:
    python3 init_research.py <research-name>

Creates:
    .docs/research/<research-name>/
    ├── research-plan.md       # Research scope and objectives
    ├── sources.md             # Collected sources with excerpts
    ├── findings.md            # Organized findings by theme
    ├── research-report.md     # Final synthesized report (generated)
    └── assets/                # Supporting files (PDFs, images, etc.)
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

def create_research_structure(research_name: str, base_path: Path = Path(".docs/research")) -> dict:
    """Create research directory structure."""
    research_dir = base_path / research_name

    # Create directories
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "assets").mkdir(exist_ok=True)

    # Create template files from assets
    # (Templates will be created in Phase 1.3)

    return {
        "research_dir": str(research_dir),
        "research_name": research_name,
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }

def main():
    parser = argparse.ArgumentParser(description="Initialize research project structure")
    parser.add_argument("research_name", help="Name of the research project")
    args = parser.parse_args()

    try:
        result = create_research_structure(args.research_name)
        print(f"✅ Research project initialized: {result['research_dir']}")
        print(f"\nNext steps:")
        print(f"1. Use /research-plan to define research scope")
        print(f"2. Use /research-execute to gather information")
        print(f"3. Use /research-synthesize to generate report")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Reasoning**: Similar to `iw-planner/scripts/init_plan.py`, provides deterministic directory creation and structure initialization.

#### 3. Create Template Files
**Files to create:**

**a) `research-planner/assets/research-plan-template.md`:**
```markdown
# Research Plan: {{RESEARCH_NAME}}

**Created**: {{CREATED_DATE}}
**Last Updated**: {{UPDATED_DATE}}
**Status**: Planning / In Progress / Completed

## Research Questions

[What questions are you trying to answer?]

1.
2.
3.

## Research Scope

### What's Included:
-

### What's Excluded:
-

### Source Types Needed:
- [ ] Academic papers and journals
- [ ] Code repositories and implementations
- [ ] Technical documentation
- [ ] Blog posts and articles
- [ ] API documentation
- [ ] Other:

## Methodology

### Information Gathering Strategy:
[How will you find and collect information?]

### Organization Strategy:
[How will findings be organized? By theme? By source type? Chronologically?]

### Success Criteria:
[How will you know the research is complete and thorough?]

## Timeline

- Start date: {{CREATED_DATE}}
- Target completion:
- Estimated effort:

## Output Format

- Report structure: Executive Summary → Key Findings → Detailed Analysis → References
- Citation style: Simple references (source list)
- Special requirements:
```

**b) `research-synthesizer/assets/report-template.md`:**
```markdown
# Research Report: {{RESEARCH_NAME}}

**Research Period**: {{START_DATE}} - {{END_DATE}}
**Report Generated**: {{GENERATED_DATE}}

---

## Executive Summary

[2-3 paragraph high-level overview of research topic, methodology, and key findings]

{{EXECUTIVE_SUMMARY}}

---

## Research Questions

{{RESEARCH_QUESTIONS}}

---

## Key Findings

{{KEY_FINDINGS}}

---

## Detailed Analysis

{{DETAILED_ANALYSIS}}

---

## Sources Consulted

{{SOURCES}}

---

## Next Steps & Recommendations

{{RECOMMENDATIONS}}

---

**Report generated by research-synthesizer skill**
```

**Reasoning**: Templates provide consistent structure and make it easy for scripts to generate well-formatted output.

### Testing for This Phase:

1. **Test directory creation:**
```bash
cd /home/nicj/code/github.com/nicholasjackson/claude-research-skills
python3 research-planner/scripts/init_research.py test-research
ls -la .docs/research/test-research/
```

2. **Verify structure:**
```bash
# Should see:
# - research-plan.md
# - sources.md
# - findings.md
# - assets/ directory
```

### Success Criteria:

#### Automated Verification:
- [ ] Scripts execute without errors: `python3 research-planner/scripts/init_research.py test-research`
- [ ] Directory structure created: `ls .docs/research/test-research`
- [ ] Template files exist and are valid markdown
- [ ] Python scripts have executable permissions: `chmod +x research-planner/scripts/*.py`

#### Manual Verification:
- [ ] Directory structure matches planned layout
- [ ] Templates contain all necessary placeholders
- [ ] Scripts follow existing skill patterns (similar to iw-planner scripts)

---

## Phase 2: research-planner Skill

### Overview
Implement the research-planner skill that interactively defines research scope, questions, and methodology through a guided workflow.

### Changes Required:

#### 1. Create research-planner SKILL.md
**File**: `research-planner/SKILL.md`
**Purpose**: Main skill file defining the research planning workflow

**YAML Frontmatter:**
```yaml
---
name: research-planner
description: Define research scope and create structured research plan. This skill should be used when starting a new research project to define questions, scope, methodology, and success criteria. Supports both technical code research and academic paper research.
---
```

**Key sections to include:**
```markdown
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

### Step 6: Present Plan for Confirmation

Show research plan to user and confirm before proceeding to execution phase.
```

**Reasoning**: Follows workflow-based structure pattern (like iw-planner), with clear sequential steps and user interaction points.

#### 2. Add Helper Scripts
**File**: `research-planner/scripts/add_source.py`
**Purpose**: Helper to add sources during planning phase

```python
#!/usr/bin/env python3
"""Add a source to the research sources list."""

import sys
import argparse
from pathlib import Path
from datetime import datetime

def add_source(research_name: str, source_url: str, source_type: str, notes: str = ""):
    """Add source to sources.md file."""
    research_dir = Path(".docs/research") / research_name
    sources_file = research_dir / "sources.md"

    # Create sources.md if it doesn't exist
    if not sources_file.exists():
        with open(sources_file, 'w') as f:
            f.write(f"# Sources for {research_name}\n\n")
            f.write("**Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n")

    # Append source
    with open(sources_file, 'a') as f:
        f.write(f"\n## {source_type}: {source_url}\n")
        f.write(f"**Added**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        if notes:
            f.write(f"**Notes**: {notes}\n")
        f.write("\n")

    print(f"✅ Source added to {sources_file}")

def main():
    parser = argparse.ArgumentParser(description="Add source to research")
    parser.add_argument("research_name", help="Research project name")
    parser.add_argument("source_url", help="Source URL or reference")
    parser.add_argument("source_type", help="Type: paper, code, docs, blog, book")
    parser.add_argument("--notes", default="", help="Additional notes")

    args = parser.parse_args()
    add_source(args.research_name, args.source_url, args.source_type, args.notes)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Reasoning**: Provides deterministic way to add sources, similar to how iw-executor uses scripts for updates.

### Testing for This Phase:

1. **Test skill invocation:**
```bash
# Invoke research-planner skill
# Follow prompts to create a test research plan
```

2. **Verify research plan file:**
```bash
cat .docs/research/test-research/research-plan.md
# Should contain: questions, scope, methodology, success criteria
```

### Success Criteria:

#### Automated Verification:
- [ ] Skill metadata validates: Check YAML frontmatter format
- [ ] Script executes: `python3 research-planner/scripts/init_research.py test`
- [ ] Research plan file created with correct structure

#### Manual Verification:
- [ ] Interactive workflow guides user through all steps
- [ ] Research questions are well-formed and specific
- [ ] Scope boundaries are clearly defined
- [ ] Plan file is readable and comprehensive
- [ ] User can confirm plan before proceeding

---

## Phase 3: research-executor Skill

### Overview
Implement the flexible research executor that gathers information from diverse sources (academic papers, code repositories, documentation) and organizes findings by theme.

### Changes Required:

#### 1. Create research-executor SKILL.md
**File**: `research-executor/SKILL.md`
**Purpose**: Execute research gathering from multiple source types

**YAML Frontmatter:**
```yaml
---
name: research-executor
description: Gather information from diverse sources including academic papers, code repositories, and technical documentation. This skill should be used after creating a research plan to execute information gathering and organize findings. Automatically adapts strategy based on source type.
---
```

**Key workflow sections:**
```markdown
# Research Executor

## Overview

Execute research information gathering from diverse sources. Adapts gathering strategy based on source type (academic papers, code, docs) and organizes findings thematically.

## When to Use This Skill

Invoke after research-planner has created a research plan. Use when:
1. Ready to gather information for defined research questions
2. Need to investigate multiple sources systematically
3. Want to organize findings as research progresses

## Workflow

### Step 1: Load Research Plan

Read research plan file to understand:
- Research questions to answer
- Source types to investigate
- Organization strategy
- Success criteria

### Step 2: Source Detection and Routing

For each source in the plan, detect type and route to appropriate gathering strategy:

**Academic Papers:**
- Use WebSearch to find papers on Google Scholar, arXiv, etc.
- Use WebFetch to extract paper content
- Extract: Title, authors, year, key findings, methodology, conclusions
- Track: Citation information (simple format)

**Code Repositories:**
- Use WebFetch for GitHub repos (README, key files)
- Use Task/Explore agents for deep code exploration
- Extract: Implementation patterns, architecture, code examples
- Track: Repo URL, relevant file paths with line numbers

**Technical Documentation:**
- Use WebFetch for official docs, API references
- Extract: Feature descriptions, usage patterns, examples, constraints
- Track: Doc URL, section references

**Blog Posts/Articles:**
- Use WebFetch for content
- Extract: Key points, examples, practical insights
- Track: URL, author, date if available

### Step 3: Information Extraction

For each source, extract:
- **Key points**: Main findings or insights
- **Quotes/Examples**: Relevant excerpts (with proper attribution)
- **Code snippets**: If applicable (with file:line or URL references)
- **Relevance**: Which research questions this addresses

### Step 4: Findings Organization

Organize extracted information by theme in `findings.md`:
- Group related findings together
- Create thematic sections
- Link findings to sources
- Note patterns and contradictions

**Example structure:**
```markdown
## Theme 1: Authentication Implementation Patterns

### JWT Token Storage (Sources: #1, #3, #5)
- Finding from source #1: Cookies preferred over localStorage for XSS protection
- Finding from source #3: httpOnly flag prevents JavaScript access
- Code example from source #5:
  ```javascript
  // From repo: nextjs/examples/auth/lib/auth.js:45-50
  res.setHeader('Set-Cookie', cookie.serialize('token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7 // 1 week
  }));
  ```

### Refresh Token Rotation (Sources: #2, #4)
- Finding from source #2: Prevents token replay attacks...
```

### Step 5: Progress Tracking

Update research plan with:
- Sources investigated
- Questions addressed
- Remaining gaps

### Step 6: Completion Check

When done, verify:
- All research questions have findings
- All planned source types explored
- Findings organized thematically
- Sources properly tracked
```

**Reasoning**: Flexible executor handles multiple source types with different gathering strategies, similar to how Task tool uses different subagent types.

#### 2. Create Source Gathering Reference
**File**: `research-executor/references/research-best-practices.md`
**Purpose**: Guide for effective research gathering

**Content:**
```markdown
# Research Gathering Best Practices

## Academic Paper Research

### Finding Papers:
- Google Scholar: `site:scholar.google.com <topic>`
- arXiv: `site:arxiv.org <field> <keywords>`
- PubMed: For medical/biological research
- ACM Digital Library: For computer science
- IEEE Xplore: For engineering/technology

### Extracting Information:
1. Read abstract first - does it address research questions?
2. Check methodology - is it sound and relevant?
3. Extract key findings - what did they discover?
4. Note limitations - what didn't they address?
5. Capture citations - in simple format (Author, Year, Title, URL)

### Quality Indicators:
- Peer-reviewed publications preferred
- Recent publications (last 5 years) unless historical context needed
- Highly-cited papers indicate impact
- Check for conflicts of interest

## Code Repository Research

### Finding Repos:
- GitHub search with filters (stars, recent activity)
- Awesome lists for curated collections
- Official organization repos (e.g., facebook/react)

### Extracting Information:
1. Start with README - understand purpose and architecture
2. Check documentation - how is it used?
3. Examine key files - implementation patterns
4. Look at tests - usage examples
5. Note file paths and line numbers for code examples

### Quality Indicators:
- Active maintenance (recent commits)
- Good documentation
- Test coverage
- Community adoption (stars, forks)

## Technical Documentation Research

### Finding Docs:
- Official documentation sites
- API references
- Developer guides
- Architecture decision records (ADRs)

### Extracting Information:
1. Overview/getting started - basic concepts
2. Core concepts - how it works
3. API reference - specific capabilities
4. Best practices - recommended patterns
5. Limitations/gotchas - what to avoid

## Thematic Organization

### Identify Themes:
- Look for recurring concepts across sources
- Group related findings
- Note agreements and contradictions
- Identify patterns

### Example Themes:
- Implementation patterns
- Performance considerations
- Security best practices
- Common pitfalls
- Evolution over time

### Cross-Reference:
- Link findings to multiple sources
- Show how sources support or contradict each other
- Build comprehensive understanding from diverse viewpoints
```

**Reasoning**: References file provides detailed guidance loaded when needed, keeping main SKILL.md lean (progressive disclosure pattern).

#### 3. Add Finding Management Script
**File**: `research-executor/scripts/add_finding.py`
**Purpose**: Add findings to findings.md in structured format

```python
#!/usr/bin/env python3
"""Add a finding to the research findings file."""

import sys
import argparse
from pathlib import Path
from datetime import datetime

def add_finding(research_name: str, theme: str, finding: str, source_ref: str):
    """Add finding to findings.md under specified theme."""
    research_dir = Path(".docs/research") / research_name
    findings_file = research_dir / "findings.md"

    # Create findings.md if doesn't exist
    if not findings_file.exists():
        with open(findings_file, 'w') as f:
            f.write(f"# Research Findings: {research_name}\n\n")
            f.write("**Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n")

    # Read existing content
    with open(findings_file, 'r') as f:
        content = f.read()

    # Check if theme exists
    theme_header = f"## {theme}"
    if theme_header not in content:
        # Add new theme section
        content += f"\n{theme_header}\n\n"

    # Find theme section and append finding
    lines = content.split('\n')
    new_lines = []
    in_theme = False
    added = False

    for line in lines:
        new_lines.append(line)
        if line.strip() == theme_header:
            in_theme = True
        elif in_theme and line.startswith('## ') and line.strip() != theme_header:
            # Reached next theme, insert before it
            new_lines.insert(-1, f"- {finding} *(Source: {source_ref})*\n")
            added = True
            in_theme = False

    if not added:
        # Add at end
        new_lines.append(f"- {finding} *(Source: {source_ref})*\n")

    # Write back
    with open(findings_file, 'w') as f:
        f.write('\n'.join(new_lines))

    print(f"✅ Finding added to theme '{theme}' in {findings_file}")

def main():
    parser = argparse.ArgumentParser(description="Add finding to research")
    parser.add_argument("research_name", help="Research project name")
    parser.add_argument("theme", help="Theme/category for this finding")
    parser.add_argument("finding", help="The finding or insight")
    parser.add_argument("source_ref", help="Source reference (e.g., 'Paper #1', 'GitHub repo X')")

    args = parser.parse_args()
    add_finding(args.research_name, args.theme, args.finding, args.source_ref)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Reasoning**: Script provides deterministic way to organize findings by theme, ensuring consistent structure.

### Testing for This Phase:

1. **Test academic paper research:**
```bash
# Research a topic with papers
# Verify WebSearch and WebFetch are used appropriately
# Check findings.md for extracted information
```

2. **Test code repository research:**
```bash
# Research a code implementation
# Verify GitHub repos are explored
# Check findings.md for code examples with file:line references
```

3. **Test finding organization:**
```bash
python3 research-executor/scripts/add_finding.py test-research "Authentication" "JWT tokens stored in httpOnly cookies" "Source #1"
cat .docs/research/test-research/findings.md
# Should show finding under "Authentication" theme
```

### Success Criteria:

#### Automated Verification:
- [ ] Scripts execute: `python3 research-executor/scripts/add_finding.py --help`
- [ ] Findings file created with proper structure
- [ ] Sources file populated with references

#### Manual Verification:
- [ ] Can successfully gather from academic papers (WebSearch, WebFetch work)
- [ ] Can successfully gather from code repos (proper extraction)
- [ ] Can successfully gather from documentation
- [ ] Findings are organized by theme
- [ ] Sources are properly tracked with citations
- [ ] Research questions are addressed by findings

---

## Phase 4: research-synthesizer Skill

### Overview
Implement the report synthesizer that analyzes findings, identifies themes, and generates comprehensive markdown reports automatically.

### Changes Required:

#### 1. Create research-synthesizer SKILL.md
**File**: `research-synthesizer/SKILL.md`
**Purpose**: Generate comprehensive research reports from gathered findings

**YAML Frontmatter:**
```yaml
---
name: research-synthesizer
description: Generate comprehensive markdown research reports from gathered findings. This skill should be used after research-executor has collected information to synthesize findings into a well-structured report with executive summary, detailed analysis, and references. Fully automated report generation.
---
```

**Key workflow sections:**
```markdown
# Research Synthesizer

## Overview

Analyze research findings and generate comprehensive, well-structured markdown reports. Fully automated synthesis with executive summary, thematic organization, detailed analysis, and source references.

## When to Use This Skill

Invoke after research-executor has gathered findings. Use when:
1. Ready to synthesize findings into final report
2. Need comprehensive summary of research
3. Want to share research outcomes with others
4. Need to document research for future reference

## Workflow

### Step 1: Load Research Data

Read all research files:
- `research-plan.md` - Research questions and scope
- `sources.md` - All sources consulted
- `findings.md` - Organized findings by theme

### Step 2: Analyze Findings

Identify:
- **Main themes**: What are the major topic areas?
- **Key insights**: What are the most important findings?
- **Patterns**: What commonalities across sources?
- **Contradictions**: Where do sources disagree?
- **Gaps**: What questions remain unanswered?

### Step 3: Generate Executive Summary

Create 2-3 paragraph summary covering:
1. **What was researched**: Topic and questions
2. **How it was researched**: Sources and methodology
3. **What was found**: Key insights and conclusions

**Quality criteria:**
- Concise but comprehensive
- Accessible to someone unfamiliar with topic
- Highlights most important findings
- Sets context for detailed sections

### Step 4: Structure Key Findings Section

For each theme identified:
1. **Theme header**: Clear, descriptive name
2. **Overview**: 1-2 sentence summary of this theme
3. **Findings**: Specific discoveries with source references
4. **Synthesis**: How findings relate to each other and research questions

**Example structure:**
```markdown
## Key Findings

### Authentication Security Patterns

Modern web frameworks consistently prioritize httpOnly cookies over localStorage for JWT storage to mitigate XSS attacks (Sources: #1, #3, #5). Refresh token rotation is implemented by 80% of surveyed frameworks as a defense against token replay attacks (Sources: #2, #4).

**Key insights:**
- Security-first design trumps developer convenience
- Multiple layers of defense preferred (httpOnly + Secure + SameSite flags)
- Automatic rotation reduces attack window

**Implementation examples:**
[Code snippets from sources with file:line references]
```

### Step 5: Create Detailed Analysis Section

For each research question:
1. State the question
2. Summarize findings that address it
3. Provide detailed analysis with evidence from sources
4. Include code examples, diagrams, or quotes where relevant
5. Note any limitations or gaps

### Step 6: Compile Sources Section

Create simple reference list:
```markdown
## Sources Consulted

### Academic Papers
1. [Author et al., 2023] "Title of Paper" - URL
   - Key contribution: ...

### Code Repositories
2. [Repo Name] Organization/repo - URL
   - Examined: README.md, src/auth/jwt.js:45-80
   - Pattern: ...

### Technical Documentation
3. [Framework Name] Official Documentation - URL
   - Section: Authentication
   - Key points: ...
```

### Step 7: Add Recommendations Section

Based on findings, suggest:
- **Next steps**: What to do with this research
- **Areas for further investigation**: Gaps or interesting tangents
- **Practical applications**: How to use these insights
- **Caveats**: Limitations of the research

### Step 8: Generate Final Report

Use template from `assets/report-template.md` and populate:
- Executive Summary
- Research Questions
- Key Findings (by theme)
- Detailed Analysis (by question)
- Sources Consulted
- Recommendations

Write to `research-report.md` in Obsidian-compatible markdown format.

### Step 9: Quality Validation

Check report for:
- [ ] All research questions addressed
- [ ] Executive summary is clear and comprehensive
- [ ] Findings are organized logically
- [ ] Sources are properly cited
- [ ] No unsupported claims
- [ ] Markdown formatting is correct
- [ ] Links and references work

### Step 10: Present Report

Show summary statistics and report location:
```
✅ Research report generated successfully!

Report: .docs/research/<name>/research-report.md

Statistics:
- Research questions addressed: 5/5
- Sources consulted: 12 (4 papers, 5 repos, 3 docs)
- Themes identified: 3
- Word count: 2,847

The report includes:
- Executive summary
- Key findings organized by theme
- Detailed analysis for each research question
- Complete source references
- Recommendations for next steps

Obsidian-compatible markdown format, ready for review or export.
```
```

**Reasoning**: Comprehensive workflow ensures high-quality automated report generation following academic research report structure.

#### 2. Create Report Generation Script
**File**: `research-synthesizer/scripts/generate_report.py`
**Purpose**: Orchestrate report generation from templates and findings

```python
#!/usr/bin/env python3
"""
Generate research report from gathered findings.

Usage:
    python3 generate_report.py <research-name>
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import re

def load_file(file_path: Path) -> str:
    """Load file content or return empty string if not found."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def extract_research_questions(plan_content: str) -> list:
    """Extract research questions from plan file."""
    questions = []
    lines = plan_content.split('\n')
    in_questions = False

    for line in lines:
        if '## Research Questions' in line:
            in_questions = True
            continue
        elif in_questions and line.startswith('##'):
            break
        elif in_questions and line.strip() and not line.strip().startswith('['):
            # Extract numbered questions
            match = re.match(r'^\d+\.\s*(.+)$', line.strip())
            if match:
                questions.append(match.group(1))

    return questions

def generate_executive_summary(plan: str, findings: str, sources: str) -> str:
    """Generate executive summary based on research content."""
    # This would use Claude's summarization capabilities
    # For now, return placeholder
    return "[Executive summary would be generated here by Claude based on the research content]"

def generate_report(research_name: str) -> dict:
    """Generate complete research report."""
    research_dir = Path(".docs/research") / research_name

    # Load all research files
    plan = load_file(research_dir / "research-plan.md")
    sources = load_file(research_dir / "sources.md")
    findings = load_file(research_dir / "findings.md")

    # Extract components
    questions = extract_research_questions(plan)

    # Load template
    template_path = Path(__file__).parent.parent / "assets" / "report-template.md"
    template = load_file(template_path)

    # Generate components
    # (In practice, Claude would do this synthesis)
    exec_summary = generate_executive_summary(plan, findings, sources)

    # Replace placeholders
    report = template.replace("{{RESEARCH_NAME}}", research_name)
    report = report.replace("{{START_DATE}}", "TBD")
    report = report.replace("{{END_DATE}}", datetime.now().strftime("%Y-%m-%d"))
    report = report.replace("{{GENERATED_DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
    report = report.replace("{{EXECUTIVE_SUMMARY}}", exec_summary)
    report = report.replace("{{RESEARCH_QUESTIONS}}", "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions)))
    report = report.replace("{{KEY_FINDINGS}}", findings)
    report = report.replace("{{DETAILED_ANALYSIS}}", "[Generated detailed analysis]")
    report = report.replace("{{SOURCES}}", sources)
    report = report.replace("{{RECOMMENDATIONS}}", "[Generated recommendations]")

    # Write report
    report_file = research_dir / "research-report.md"
    with open(report_file, 'w') as f:
        f.write(report)

    return {
        "report_file": str(report_file),
        "questions_count": len(questions),
        "word_count": len(report.split())
    }

def main():
    parser = argparse.ArgumentParser(description="Generate research report")
    parser.add_argument("research_name", help="Research project name")

    args = parser.parse_args()

    try:
        result = generate_report(args.research_name)
        print(f"✅ Research report generated!")
        print(f"\nReport: {result['report_file']}")
        print(f"Questions addressed: {result['questions_count']}")
        print(f"Word count: {result['word_count']}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Reasoning**: Script provides framework for report generation. In practice, Claude would handle the synthesis logic when the skill is invoked.

### Testing for This Phase:

1. **Test report generation:**
```bash
# After gathering research, generate report
python3 research-synthesizer/scripts/generate_report.py test-research
```

2. **Verify report structure:**
```bash
cat .docs/research/test-research/research-report.md
# Should contain:
# - Executive Summary
# - Research Questions
# - Key Findings (organized by theme)
# - Detailed Analysis
# - Sources
# - Recommendations
```

3. **Check Obsidian compatibility:**
```bash
# Verify markdown renders correctly
# Check links work
# Verify frontmatter if added
```

### Success Criteria:

#### Automated Verification:
- [ ] Script executes: `python3 research-synthesizer/scripts/generate_report.py test`
- [ ] Report file created: `ls .docs/research/test/research-report.md`
- [ ] Markdown is valid (no syntax errors)
- [ ] All placeholders replaced

#### Manual Verification:
- [ ] Executive summary is clear and comprehensive
- [ ] All research questions are addressed
- [ ] Findings are organized logically by theme
- [ ] Sources are properly referenced throughout
- [ ] Recommendations are actionable
- [ ] Report is readable and well-structured
- [ ] Markdown renders correctly in Obsidian

---

## Phase 5: Integration & Polish

### Overview
Add slash commands, refine documentation, create examples, and prepare for distribution.

### Changes Required:

#### 1. Create Slash Commands
**Files to create in project `.claude/commands/`:**

**a) `/research-plan` command:**
```markdown
---
description: Create a new research plan
---

Invoke the research-planner skill to create a structured research plan. This will guide you through defining research questions, scope, and methodology.

After the plan is created, use /research-execute to gather information.
```

**b) `/research-execute` command:**
```markdown
---
description: Execute research information gathering
---

Invoke the research-executor skill to gather information from diverse sources based on your research plan. This will systematically collect and organize findings.

After gathering information, use /research-synthesize to generate the report.
```

**c) `/research-synthesize` command:**
```markdown
---
description: Generate research report from findings
---

Invoke the research-synthesizer skill to synthesize gathered findings into a comprehensive markdown report with executive summary, detailed analysis, and references.
```

**Reasoning**: Slash commands provide convenient workflow access, similar to existing `/plan` command.

#### 2. Create Example Research Project
**Action**: Create complete example in `examples/authentication-research/`

Demonstrates:
- Well-formed research plan
- Mixed sources (papers + code + docs)
- Organized findings by theme
- Complete synthesized report
- Shows best practices

**Reasoning**: Examples help users understand expected workflow and output quality.

#### 3. Add Main README
**File**: `README.md` at project root

**Content:**
```markdown
# Research Skills for Claude

Give Claude academic research superpowers with three specialized skills for planning, executing, and synthesizing comprehensive research reports.

## Overview

These skills enable Claude to:
- Plan structured research projects with clear questions and scope
- Gather information from diverse sources (academic papers, code repos, documentation)
- Synthesize findings into well-structured markdown reports with citations
- Follow academic research best practices

## Skills Included

### 1. research-planner
Define research scope, questions, and methodology through interactive workflow.

**Use when:** Starting a new research project

### 2. research-executor
Gather information from multiple source types with adaptive strategies.

**Use when:** Ready to collect information for defined research questions

### 3. research-synthesizer
Generate comprehensive markdown reports automatically from findings.

**Use when:** Ready to synthesize findings into final report

## Quick Start

1. **Create a research plan:**
   ```
   /research-plan
   ```
   Follow prompts to define questions, scope, and methodology.

2. **Gather information:**
   ```
   /research-execute
   ```
   Claude will systematically gather from planned sources and organize findings.

3. **Generate report:**
   ```
   /research-synthesize
   ```
   Produces comprehensive markdown report with summary and references.

## Example Workflow

See `examples/authentication-research/` for a complete example demonstrating:
- Research plan for JWT authentication best practices
- Findings from papers, code repos, and documentation
- Final synthesized report with recommendations

## Output Structure

Research projects are stored in `.docs/research/<research-name>/`:
```
<research-name>/
├── research-plan.md       # Scope, questions, methodology
├── sources.md             # Sources with excerpts
├── findings.md            # Organized findings by theme
├── research-report.md     # Final synthesized report
└── assets/                # Supporting files
```

## Features

- ✅ Mixed research (code + academic sources)
- ✅ Thematic organization of findings
- ✅ Simple reference tracking
- ✅ Fully automated report generation
- ✅ Obsidian-compatible markdown
- ✅ Academic research best practices

## Future Enhancements

- [ ] Advanced citation formatting (APA, MLA, Chicago, IEEE)
- [ ] Obsidian vault export/sync with wikilinks
- [ ] Integration with iw-* workflow skills
- [ ] Collaboration features
- [ ] Research templates (literature review, comparative analysis)

## Installation

[Installation instructions TBD - package skills and provide installation commands]

## License

[License TBD]
```

**Reasoning**: Clear documentation helps users understand capabilities and workflow.

#### 4. Create CONTRIBUTING.md
**File**: `CONTRIBUTING.md`

Guidelines for:
- How to contribute improvements
- Code style for Python scripts
- Skill documentation standards
- Testing requirements
- How to submit examples

**Reasoning**: Encourages community contributions and maintains quality.

### Testing for This Phase:

1. **Test slash commands:**
```bash
/research-plan
# Should invoke research-planner skill

/research-execute
# Should invoke research-executor skill

/research-synthesize
# Should invoke research-synthesizer skill
```

2. **Test example project:**
```bash
# Follow example workflow
# Verify all files exist and are complete
```

3. **Verify documentation:**
```bash
# Read README.md
# Ensure all links work
# Check examples are clear
```

### Success Criteria:

#### Automated Verification:
- [ ] Slash commands load correctly
- [ ] Example files exist and are valid markdown
- [ ] All documentation links work
- [ ] Scripts have proper permissions

#### Manual Verification:
- [ ] Complete workflow works end-to-end
- [ ] Documentation is clear and comprehensive
- [ ] Examples demonstrate best practices
- [ ] Skills can be packaged for distribution
- [ ] No errors or rough edges in user experience

---

## Testing Strategy

### Unit Testing (Scripts):
- Test each Python script independently
- Verify error handling for edge cases
- Check file creation and updates work correctly

**Test commands:**
```bash
# Test init script
python3 research-planner/scripts/init_research.py test-research
ls -la .docs/research/test-research/

# Test add_finding script
python3 research-executor/scripts/add_finding.py test-research "Theme" "Finding" "Source"
cat .docs/research/test-research/findings.md

# Test report generation
python3 research-synthesizer/scripts/generate_report.py test-research
cat .docs/research/test-research/research-report.md
```

### Integration Testing (End-to-End):
1. **Complete research workflow:**
   - Create plan with /research-plan
   - Execute gathering with /research-execute
   - Generate report with /research-synthesize
   - Verify output quality

2. **Mixed source types:**
   - Research topic requiring papers + code + docs
   - Verify each source type handled correctly
   - Check findings properly organized

3. **Edge cases:**
   - Empty research (no sources)
   - Single source type only
   - Large number of sources (>20)
   - Conflicting information across sources

### Manual Testing Steps:
1. Create research plan for real topic (e.g., "GraphQL vs REST API design")
2. Gather from at least 3 different source types
3. Verify findings are organized thematically
4. Generate report and review quality
5. Check Obsidian compatibility
6. Verify markdown renders correctly

## Performance Considerations

**Information Gathering:**
- WebSearch and WebFetch can be slow for many sources
- Consider batching or parallel requests where possible
- Progress indication during long operations

**Report Generation:**
- Large findings files may take time to synthesize
- Consider streaming output for long reports
- Provide progress updates during generation

**File I/O:**
- Multiple reads/writes during research execution
- Scripts should handle concurrent access gracefully
- Use atomic writes where possible

## Migration Notes

Not applicable - new implementation with no existing data to migrate.

## References

### Research Sources:
- Existing skill patterns from `~/.claude/skills/`
- Academic research methodology best practices
- Markdown documentation standards

### Key Files Examined:
- `~/.claude/skills/skill-creator/SKILL.md` - Skill creation guidelines
- `~/.claude/skills/iw-planner/SKILL.md` - Planning workflow patterns
- `~/.claude/skills/iw-planner/scripts/init_plan.py` - Script patterns
- `~/.claude/skills/iw-planner/assets/*.md` - Template patterns
- `~/.claude/skills/iw-learnings/SKILL.md` - Search patterns

### Similar Patterns:
- Progressive disclosure: `skill-creator` metadata approach
- Workflow-based structure: `iw-planner` sequential steps
- Template system: `iw-planner` placeholders
- Script-driven operations: `iw-planner` deterministic file creation
