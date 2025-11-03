# Research Skills - Research & Working Notes

**Research Date**: 2025-11-03
**Researchers**: Claude + nicj

## Initial Understanding

User requested creation of "a skill or skills that gives claude research super powers" with the following requirements:
- Follow standard academic research procedures
- Look at existing projects, code, or papers
- Collect citations to include in research report
- Compiled report should be simple to digest and well-structured
- Summary at top, detail below
- Output in markdown format

Initial interpretation: Need to create skill(s) that enable Claude to conduct comprehensive research following academic best practices, gathering from diverse sources and synthesizing into professional reports.

## Research Process

### Files Examined:

**1. Existing Skill Infrastructure (`~/.claude/skills/`):**
- `skill-creator/SKILL.md` - Complete skill creation guidelines
  - Finding: Standard structure is SKILL.md + optional scripts/, references/, assets/
  - Finding: YAML frontmatter required with name and description
  - Finding: Progressive disclosure pattern (metadata → body → resources)
  - Finding: Use imperative form, not second person

- `iw-planner/SKILL.md` - Implementation planning workflow
  - Finding: Uses 4-file structure (plan, research, context, tasks)
  - Finding: Extensive use of Task tool for parallel agent spawning
  - Finding: Template system with {{PLACEHOLDER}} replacement
  - Pattern: Workflow-based structure with sequential steps

- `iw-planner/scripts/init_plan.py` - Plan initialization script
  - Finding: Python script creates directory structure deterministically
  - Pattern: Use argparse for CLI interface
  - Pattern: Return structured JSON/dict with results

- `iw-planner/assets/*.md` - Template files
  - Finding: Templates use {{PLACEHOLDER}} for dynamic content
  - Pattern: Separate templates for different purposes (plan, tasks, context, research)

- `iw-learnings/SKILL.md` - Institutional knowledge search
  - Finding: Designed for parallel execution with other research tasks
  - Pattern: Search and return findings, don't block workflow

**2. Academic Research Methodology (from research agent findings):**
- Standard workflow: Plan → Literature Review → Methodology → Analysis → Report
- Citation formats: APA, MLA, Chicago, IEEE (all different, complex)
- Report structure: Executive Summary → Introduction → Literature Review → Methodology → Findings → Discussion → Conclusion → References
- Synthesis techniques: Thematic organization, concept maps, evidence hierarchies
- Quality indicators: Validity, reliability, transparency, ethical standards

### Sub-tasks Spawned:

**1. Explore Existing Skill Patterns** (Task/Explore agent, haiku model)
- Result: Found 11 skills with clear patterns
- Key discovery: Progressive disclosure is fundamental design principle
- Key discovery: Scripts used for deterministic operations
- Key discovery: Templates stored in assets/ directory

**2. Research Academic Research Workflows** (Task/general-purpose, haiku)
- Result: Comprehensive overview of academic research methodology
- Key discovery: Research lifecycle has 7 phases
- Key discovery: Report structure varies by field but has common elements
- Key discovery: Multiple citation formats exist (APA, MLA, Chicago, IEEE)

**3. Find Skill-Creator Patterns** (Task/Explore, haiku)
- Result: Detailed guidelines from skill-creator/SKILL.md
- Key discovery: 6-step process for creating skills
- Key discovery: Four recommended SKILL.md structures (workflow, task, reference, capabilities)

**4. Research Markdown Formatting** (Task/Explore, haiku)
- Result: Extensive markdown patterns from existing skills
- Key discovery: Max H4 depth, never H5+
- Key discovery: Use tables for navigation and comparison
- Key discovery: Emoji indicators (✅/❌) for examples

**5. Search Past Learnings** (iw-learnings skill)
- Result: No learnings found (new project area)

### Questions Asked & Answers:

**Q1: What type of research will this skill primarily support?**
- A: "Ideally mixed research, but if it is better to have two skills that support code and academic then we should do that"
- Follow-up research: Decided single flexible executor is better for comprehensive reports that combine multiple source types
- Rationale: Real research questions often need both code examples and academic backing

**Q2: How should the research skill be structured?**
- A: "Multiple Specialized Skills"
- Decision: Three skills - planner, executor, synthesizer
- Rationale: Better separation of concerns, follows existing skill patterns

**Q3: What citation and referencing features do you need?**
- A: "Simple References Only"
- Decision: Just track sources without complex formatting
- Rationale: Avoids complexity of APA/MLA/Chicago/IEEE, can add later

**Q4: What level of automation do you want for report generation?**
- A: "Fully Automated"
- Decision: Synthesizer generates complete reports with minimal intervention
- Rationale: User wants research superpowers, not manual report writing

**Q5: Should we integrate with existing iw-* workflow?**
- User clarification: "I think the integration with the existing iw skills we can do later once we have tested this skill"
- Decision: Make skills standalone initially, iw-* integration as future enhancement
- Rationale: Keep initial implementation focused, add integration after testing

**Q6: What about Obsidian integration?**
- User clarification: "I would also like to integrate this into obsidian at some point. Maybe we add a feature later to do this."
- Decision: Design Obsidian-compatible structure now, add export/sync later
- Rationale: Standard markdown works in Obsidian, future features can add wikilinks/sync

## Key Discoveries

### Technical Discoveries:

1. **Progressive Disclosure Pattern is Fundamental**
   - Location: `~/.claude/skills/skill-creator/SKILL.md:77-85`
   - Discovery: Skills use 3-level loading: metadata (~100 words) → SKILL.md (<5k) → resources (unlimited)
   - Impact: Keep SKILL.md lean, move detailed info to references/

2. **Template System Uses Placeholder Replacement**
   - Location: `~/.claude/skills/iw-planner/scripts/init_plan.py:25-29`
   - Discovery: Python scripts replace {{PLACEHOLDER}} with actual values
   - Pattern: Use dict for replacements, iterate and replace

3. **Parallel Agent Spawning is Preferred**
   - Location: `~/.claude/skills/iw-planner/SKILL.md:162-194`
   - Discovery: Launch 5-7 Task agents concurrently for maximum efficiency
   - Pattern: Use Explore for codebase, general-purpose for complex tasks

4. **Academic Research Has Standard Phases**
   - From research agent findings
   - Discovery: Research lifecycle: Plan → Literature Review → Methodology → Analysis → Report
   - Impact: Can model research-planner workflow after this

5. **Citations Are Complex (4+ Major Formats)**
   - From research agent findings
   - Discovery: APA, MLA, Chicago, IEEE all have different formats
   - Decision: Use simple references only initially, avoid complexity

### Patterns to Follow:

1. **Workflow-Based SKILL.md Structure**
   - Pattern: Overview → When to Use → Workflow (Step 1, 2, 3...) → Resources
   - Example: `iw-planner/SKILL.md`
   - Application: Use for all three research skills

2. **Python Scripts for Deterministic Operations**
   - Pattern: Scripts create directories, manipulate files, generate output
   - Example: `iw-planner/scripts/init_plan.py`
   - Application: init_research.py, add_source.py, add_finding.py, generate_report.py

3. **Template Files in assets/**
   - Pattern: Store templates with placeholders, scripts populate them
   - Example: `iw-planner/assets/plan-template.md`
   - Application: research-plan-template.md, report-template.md

4. **Thematic Organization of Findings**
   - Pattern from academic research: Group findings by theme, not by source
   - Application: findings.md organized by theme with cross-references to sources

### Constraints Identified:

1. **No WebScraping Beyond WebFetch/WebSearch**
   - Constraint: Only use built-in tools, no custom web scraping
   - Impact: Limited to what WebFetch can extract from pages

2. **Obsidian Integration Must Come Later**
   - Constraint: User wants to test skills standalone first
   - Impact: Design compatible structure, add sync features later

3. **iw-* Workflow Integration Later**
   - Constraint: Integration with existing workflow deferred
   - Impact: Skills work standalone, can add issue tracking/git workflow later

4. **Simple References Only (Initially)**
   - Constraint: No complex citation formatting
   - Impact: Track sources with simple format, can add APA/MLA/etc. later

## Design Decisions

### Decision 1: Three Specialized Skills vs Single Unified Skill

**Options considered:**
- Option A: Single comprehensive research skill handling all phases
- Option B: Two skills (planner + executor/synthesizer combined)
- Option C: Three skills (planner, executor, synthesizer)

**Chosen**: Option C - Three specialized skills

**Rationale**:
- Better separation of concerns
- Each skill has focused purpose
- User requested "Multiple Specialized Skills"
- Follows pattern from existing skills (iw-planner, iw-executor, iw-git-workflow)
- Easier to maintain and extend
- User can invoke just the phase they need

### Decision 2: Single Flexible Executor vs Separate Code/Academic Executors

**Options considered:**
- Option A: Single executor adapts to source type (code, papers, docs)
- Option B: Two separate executors (code-research-executor, academic-research-executor)

**Chosen**: Option A - Single flexible executor

**Rationale**:
- Real research questions often need both code examples and academic papers
- More comprehensive reports from mixed research
- Simpler user experience (one workflow vs two)
- Can still use different gathering strategies internally
- User preference: "Ideally mixed research"
- If complexity becomes problematic, can split later

### Decision 3: Fully Automated vs Template-Based Report Generation

**Options considered:**
- Option A: Fully automated - skill generates complete report
- Option B: Template-based - skill populates template, user edits
- Option C: Assisted manual - skill organizes, user writes

**Chosen**: Option A - Fully automated

**Rationale**:
- User requested "Fully Automated"
- Aligns with "research superpowers" goal
- Claude excels at synthesis and writing
- User can still edit generated report if desired
- Reduces manual effort significantly

### Decision 4: Simple References vs Advanced Citation Formatting

**Options considered:**
- Option A: Simple references (source list with URLs)
- Option B: Full citation formatting (APA, MLA, Chicago, IEEE)
- Option C: Hybrid (simple with option to upgrade format)

**Chosen**: Option A - Simple references

**Rationale**:
- User selected "Simple References Only"
- Avoids complexity of 4+ citation formats
- Can add advanced formatting later if needed
- Sufficient for initial use case
- Easier to implement and maintain

### Decision 5: Standalone vs iw-* Integration

**Options considered:**
- Option A: Integrate with iw-* workflow from start (issues, git, learnings)
- Option B: Build standalone, add integration later

**Chosen**: Option B - Standalone initially

**Rationale**:
- User clarified: "integration with the existing iw skills we can do later once we have tested this skill"
- Keeps implementation focused and simple
- Can validate skills work well before adding integration
- Future enhancement clearly documented

### Decision 6: Obsidian Compatibility

**Options considered:**
- Option A: Standard markdown only
- Option B: Obsidian-specific features (wikilinks, frontmatter, etc.)
- Option C: Obsidian-compatible structure, add features later

**Chosen**: Option C - Obsidian-compatible structure

**Rationale**:
- User wants "to integrate this into obsidian at some point"
- Standard markdown works in Obsidian already
- Easy to add wikilinks/frontmatter/sync later
- No downside to compatible structure
- Flexible for future enhancement

## Open Questions (During Research)

All questions resolved during planning process:

- [x] **Should skills be separate or unified?** → Resolved: Three separate skills
- [x] **Single or separate executors?** → Resolved: Single flexible executor
- [x] **Citation format?** → Resolved: Simple references
- [x] **Automation level?** → Resolved: Fully automated
- [x] **Integrate with iw-* workflow?** → Resolved: Later, after testing
- [x] **Obsidian integration?** → Resolved: Compatible structure, features later

No open questions remain. Plan is complete and actionable.

## Corrections During Planning

User provided helpful clarifications:

**Correction 1: Integration timing**
- Initially planned: Integrate with iw-* workflow in implementation
- Clarified: "I think the integration with the existing iw skills we can do later once we have tested this skill"
- Impact: Moved iw-* integration to "Future Enhancements" section
- Updated: Phases 1-5 now focus on standalone skills

**Correction 2: Obsidian features**
- Initially planned: Basic markdown output
- Clarified: "I would also like to integrate this into obsidian at some point. Maybe we add a feature later to do this"
- Impact: Designed Obsidian-compatible structure from start
- Updated: Noted future enhancement for export/sync features

These corrections improved the plan by keeping initial implementation focused while setting up for future enhancements.

## Code Snippets Reference

### Relevant Existing Code:

**Template Replacement Pattern:**
```python
# From ~/.claude/skills/iw-planner/scripts/init_plan.py:25-29
def replace_placeholders(content, replacements):
    """Replace placeholders in content with actual values."""
    for placeholder, value in replacements.items():
        content = content.replace(f"{{{{{placeholder}}}}}", value)
    return content
```
Application: Use in init_research.py and generate_report.py

**Directory Creation Pattern:**
```python
# From ~/.claude/skills/iw-planner/scripts/init_plan.py:45-50
def create_plan_structure(plan_name: str, plan_type: str) -> dict:
    """Create plan directory structure."""
    if plan_type == "issue":
        plan_dir = Path(".docs/issues") / plan_name
    else:
        plan_dir = Path(".docs/adhoc") / plan_name

    plan_dir.mkdir(parents=True, exist_ok=True)
```
Application: Adapt for .docs/research/<research-name>/ structure

**CLI Argument Parsing Pattern:**
```python
# From ~/.claude/skills/iw-planner/scripts/init_plan.py:75-85
def main():
    parser = argparse.ArgumentParser(description="Initialize plan structure")
    parser.add_argument("name", help="Plan or issue number")
    parser.add_argument("--type", choices=["issue", "adhoc"], required=True)
    args = parser.parse_args()
```
Application: Use in all Python scripts for consistent CLI interface

### Similar Patterns Found:

**Workflow-Based SKILL.md Structure:**
```markdown
# From ~/.claude/skills/iw-planner/SKILL.md

## Workflow

### Step 1: Context Gathering & Initial Analysis
[Instructions for step 1]

### Step 2: Research & Discovery
[Instructions for step 2]

### Step 3: Plan Structure Development
[Instructions for step 3]
```
Application: Model research-planner, research-executor, research-synthesizer after this

**YAML Frontmatter:**
```yaml
# From ~/.claude/skills/skill-creator/SKILL.md:1-5
---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
---
```
Application: Use for all three research skills with appropriate descriptions

**Template with Placeholders:**
```markdown
# From ~/.claude/skills/iw-planner/assets/plan-template.md
# {{TASK_NAME}} Implementation Plan

**Created**: {{CREATED_DATE}}
**Last Updated**: {{UPDATED_DATE}}

## Overview
[Brief description of what we're implementing and why]
```
Application: Create research-plan-template.md and report-template.md with similar structure

## Research Summary

**Total research conducted:**
- 5 Task agents spawned for parallel research
- 1 Skill invocation (iw-learnings)
- 5+ files examined in detail
- 2,000+ lines of existing skill code analyzed
- Academic research methodology documented

**Key findings that shaped the plan:**
1. Progressive disclosure is fundamental to skill design
2. Template system with placeholders is proven pattern
3. Python scripts provide deterministic operations
4. Workflow-based structure is most appropriate
5. Simple references avoid citation complexity
6. Standalone skills can integrate later

**Plan confidence level: High**
- All questions answered
- Clear patterns from existing skills
- User preferences clarified
- No blocking unknowns
- Implementation path is clear
