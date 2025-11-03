---
name: iw-research-executor
description: Gather information from diverse sources including academic papers, code repositories, and technical documentation, then automatically generate a comprehensive research report. This skill should be used after creating a research plan to execute information gathering, organize findings, and produce the final report. Automatically adapts strategy based on source type.
---

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

**Actions:**
1. Read `.docs/research/<research-name>/research-plan.md`
2. Extract research questions
3. Identify source types needed
4. Understand organization strategy (thematic, chronological, etc.)

### Step 2: Source Detection and Routing

For each source needed, detect type and route to appropriate gathering strategy:

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

### Step 3: Information Gathering

For each source type, follow the appropriate strategy:

#### Academic Papers Strategy

1. **Find Papers:**
   - Use WebSearch with targeted queries
   - Search sites: Google Scholar, arXiv, PubMed, ACM Digital Library, IEEE Xplore
   - Example: `site:scholar.google.com [topic] [keywords]`

2. **Extract Information:**
   - Read abstract first - does it address research questions?
   - Check methodology - is it sound and relevant?
   - Extract key findings - what did they discover?
   - Note limitations - what didn't they address?
   - Capture citations in simple format

3. **Record Source:**
   - Use `add_source.py` script or manual entry to sources.md
   - Format: `[Author et al., Year] "Title" - URL`
   - Add key contribution note

4. **Extract Findings:**
   - Identify findings relevant to research questions
   - Use `add_finding.py` to add to findings.md under appropriate theme
   - Include source reference

#### Code Repository Strategy

1. **Find Repositories:**
   - GitHub search with filters (stars, recent activity, language)
   - Look for official organization repos
   - Check Awesome lists for curated collections

2. **Explore Repository:**
   - Start with README - understand purpose and architecture
   - Use WebFetch for key files
   - Use Task/Explore agents for deeper investigation
   - Look at tests for usage examples

3. **Extract Information:**
   - Implementation patterns and architecture
   - Code examples with file:line references
   - Best practices demonstrated
   - Common patterns used

4. **Record Source:**
   - Add to sources.md with repo URL
   - Note examined files and line ranges
   - Example: `[Repo Name] org/repo - Examined: src/auth/jwt.js:45-80`

5. **Extract Findings:**
   - Identify patterns relevant to research questions
   - Include code snippets with proper attribution
   - Format: `file_path:line_number`
   - Use `add_finding.py` to organize by theme

#### Technical Documentation Strategy

1. **Find Documentation:**
   - Official documentation sites
   - API references
   - Developer guides
   - Architecture decision records (ADRs)

2. **Extract Information:**
   - Overview/getting started - basic concepts
   - Core concepts - how it works
   - API reference - specific capabilities
   - Best practices - recommended patterns
   - Limitations/gotchas - what to avoid

3. **Record Source:**
   - Add to sources.md with doc URL
   - Note sections examined
   - Example: `[Framework Name] Official Documentation - Section: Authentication`

4. **Extract Findings:**
   - Key concepts and capabilities
   - Usage patterns and examples
   - Limitations and constraints
   - Use `add_finding.py` to organize thematically

### Step 4: Findings Organization

Organize extracted information by theme in `findings.md`:

**Thematic Organization:**
1. **Identify Themes:**
   - Look for recurring concepts across sources
   - Group related findings together
   - Note agreements and contradictions
   - Identify patterns

2. **Structure Findings:**
   - Create theme sections in findings.md
   - Group findings under themes
   - Cross-reference multiple sources
   - Show how sources support or contradict each other

3. **Example Structure:**
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

4. **Use add_finding.py Script:**
   ```bash
   python3 .claude/skills/iw-research-executor/scripts/add_finding.py <research-name> \
     "Theme Name" \
     "Finding description" \
     "Source #1"
   ```

### Step 5: Progress Tracking

Update research plan with:
- Sources investigated (mark checkboxes in research-plan.md)
- Questions addressed (note which findings address which questions)
- Remaining gaps (what still needs investigation)

**Update Status:**
- Change research-plan.md status from "Planning" to "In Progress"
- Add notes about progress
- Document any scope adjustments needed

### Step 6: Completion Check

When done, verify:
- All research questions have findings
- All planned source types explored
- Findings organized thematically
- Sources properly tracked

**Completion Checklist:**
- [ ] Each research question has at least 3-5 relevant findings
- [ ] Findings are organized by theme, not just by source
- [ ] All sources are documented in sources.md
- [ ] Cross-references between sources are noted
- [ ] Contradictions or disagreements are highlighted
- [ ] Code examples include file:line references
- [ ] Citations are captured for academic sources

**Present Completion Summary:**
```
✓ Research Execution Complete

Research: [research-name]
Location: .docs/research/[research-name]/

Sources Gathered:
- Academic Papers: [count]
- Code Repositories: [count]
- Technical Documentation: [count]
- Blog Posts/Articles: [count]
Total: [count] sources

Findings Organized:
- [Theme 1]: [count] findings
- [Theme 2]: [count] findings
- [Theme 3]: [count] findings
Total: [count] findings across [N] themes

Research Questions Addressed:
✓ Question 1: [X findings]
✓ Question 2: [Y findings]
✓ Question 3: [Z findings]

Files Updated:
- sources.md: [count] sources added
- findings.md: [count] findings organized by [N] themes
- research-plan.md: Status updated to "Completed"

Proceeding to report generation...
```

### Step 7: Automatic Report Generation

After completing information gathering, automatically invoke the synthesizer to generate the final report.

**Action:**
Use the Skill tool to invoke `iw-research-synthesizer`:

```
Skill tool: command = "iw-research-synthesizer"
```

The synthesizer will:
1. Load all research data (plan, sources, findings)
2. Analyze findings across sources
3. Generate executive summary
4. Structure key findings by theme
5. Create detailed analysis per research question
6. Compile sources section
7. Add recommendations
8. Generate final report at `.docs/research/[research-name]/research-report.md`

**Note:** The synthesis happens automatically. You don't need to manually invoke the synthesizer unless you want to regenerate the report after editing findings.

## Resources

### scripts/add_finding.py

Python script that adds findings to findings.md organized by theme.

**Usage:**
```bash
python3 .claude/skills/iw-research-executor/scripts/add_finding.py <research-name> <theme> <finding> <source-ref>
```

**Example:**
```bash
python3 .claude/skills/iw-research-executor/scripts/add_finding.py auth-research \
  "Token Security" \
  "httpOnly cookies prevent XSS attacks on JWT tokens" \
  "Paper #1, GitHub repo #3"
```

### references/research-best-practices.md

Comprehensive guide for effective research gathering across different source types. Includes:
- Academic paper research strategies
- Code repository exploration techniques
- Technical documentation extraction methods
- Thematic organization approaches
- Quality indicators for sources

Load this reference when you need detailed guidance on gathering strategies.
