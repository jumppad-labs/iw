---
name: iw-research-synthesizer
description: Generate comprehensive markdown research reports from gathered findings. This skill is automatically invoked by iw-research-executor after information gathering. Can also be manually invoked to regenerate reports after editing findings. Fully automated report generation with executive summary, detailed analysis, and references.
---

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

**Actions:**
```bash
# Read research files
cd .docs/research/<research-name>/
cat research-plan.md
cat sources.md
cat findings.md
```

Extract:
- Research questions from plan
- All themes and findings from findings.md
- All sources from sources.md
- Original scope and methodology

### Step 2: Analyze Findings

Identify:
- **Main themes**: What are the major topic areas?
- **Key insights**: What are the most important findings?
- **Patterns**: What commonalities across sources?
- **Contradictions**: Where do sources disagree?
- **Gaps**: What questions remain unanswered?

**Analysis Process:**
1. Review all findings across themes
2. Identify most impactful discoveries
3. Note patterns and recurring concepts
4. Highlight contradictions or debates
5. Assess completeness of research questions coverage

### Step 3: Generate Executive Summary

Create 2-3 paragraph summary covering:
1. **What was researched**: Topic and questions
2. **How it was researched**: Sources and methodology
3. **What was found**: Key insights and conclusions

**Quality criteria:**
- Concise but comprehensive (200-400 words)
- Accessible to someone unfamiliar with topic
- Highlights most important findings
- Sets context for detailed sections
- Written in clear, professional tone

**Structure:**
- Paragraph 1: Context and research scope
- Paragraph 2: Methodology and approach
- Paragraph 3: Key findings and conclusions

### Step 4: Structure Key Findings Section

For each theme identified in findings.md:
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

**Cross-source analysis:**
All sources agree on httpOnly cookies, but differ on token expiration strategies (Papers favor short-lived tokens, while production code shows longer durations for UX reasons).
```

### Step 5: Create Detailed Analysis Section

For each research question:
1. State the question
2. Summarize findings that address it
3. Provide detailed analysis with evidence from sources
4. Include code examples, diagrams, or quotes where relevant
5. Note any limitations or gaps

**Structure:**
```markdown
## Detailed Analysis

### Question 1: [Original research question]

**Summary:**
[2-3 sentence summary of what was found]

**Findings from sources:**
- Source #1 (Paper): [Key finding with context]
- Source #3 (Code): [Implementation approach]
- Source #5 (Docs): [Official recommendation]

**Analysis:**
[Deeper analysis comparing approaches, noting trade-offs, explaining implications]

**Code example:**
```language
// From: repo/path/file.ext:45-60
[Code snippet demonstrating concept]
```

**Limitations:**
[Any gaps, unanswered aspects, or areas needing further research]
```

### Step 6: Compile Sources Section

Create simple reference list organized by type:

**Structure:**
```markdown
## Sources Consulted

### Academic Papers
1. [Author et al., 2023] "Title of Paper" - URL
   - Key contribution: Brief description of main finding

2. [Author et al., 2024] "Another Paper" - URL
   - Key contribution: Description

### Code Repositories
3. [Repo Name] Organization/repo - URL
   - Examined: README.md, src/auth/jwt.js:45-80
   - Pattern: Description of implementation pattern

4. [Another Repo] org/repo - URL
   - Examined: List of files
   - Pattern: Description

### Technical Documentation
5. [Framework Name] Official Documentation - URL
   - Section: Authentication
   - Key points: Summary of key information

### Blog Posts and Articles
6. [Author] "Article Title" - URL
   - Published: Date
   - Key insights: Summary
```

### Step 7: Add Recommendations Section

Based on findings, suggest:
- **Next steps**: What to do with this research
- **Areas for further investigation**: Gaps or interesting tangents
- **Practical applications**: How to use these insights
- **Caveats**: Limitations of the research

**Structure:**
```markdown
## Next Steps & Recommendations

### Practical Applications
- [Recommendation 1 based on findings]
- [Recommendation 2 based on findings]

### Areas for Further Investigation
- [Gap or question that emerged]
- [Interesting tangent worth exploring]

### Implementation Considerations
- [Practical consideration based on findings]
- [Trade-off to be aware of]

### Caveats and Limitations
- [Limitation of this research]
- [Context where findings may not apply]
```

### Step 8: Generate Final Report

Use template from `assets/report-template.md` and populate:
- Executive Summary (from Step 3)
- Research Questions (from plan)
- Key Findings (from Step 4, organized by theme)
- Detailed Analysis (from Step 5, organized by question)
- Sources Consulted (from Step 6, organized by type)
- Recommendations (from Step 7)

**Use generate_report.py script:**
```bash
python3 .claude/skills/iw-research-synthesizer/scripts/generate_report.py <research-name>
```

**Manual synthesis steps:**
1. Read template: `.claude/skills/iw-research-synthesizer/assets/report-template.md`
2. For each placeholder:
   - {{RESEARCH_NAME}}: Use research directory name
   - {{START_DATE}}: From research-plan.md created date
   - {{END_DATE}}: Current date
   - {{GENERATED_DATE}}: Current timestamp
   - {{EXECUTIVE_SUMMARY}}: Write 2-3 paragraph summary
   - {{RESEARCH_QUESTIONS}}: Extract from research-plan.md
   - {{KEY_FINDINGS}}: Synthesize from findings.md by theme
   - {{DETAILED_ANALYSIS}}: Analyze each question with evidence
   - {{SOURCES}}: Organize from sources.md by type
   - {{RECOMMENDATIONS}}: Generate based on findings
3. Write to `research-report.md`

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
- [ ] Code snippets are properly formatted
- [ ] Cross-references between sections work
- [ ] Professional tone throughout

### Step 10: Present Report

Show summary statistics and report location:

```
✅ Research Report Generated Successfully!

Report: .docs/research/<name>/research-report.md

Statistics:
- Research questions addressed: 5/5
- Sources consulted: 12 (4 papers, 5 repos, 3 docs)
- Themes identified: 3
- Word count: 2,847

The report includes:
- Executive summary (2-3 paragraphs)
- Key findings organized by theme
- Detailed analysis for each research question
- Complete source references (organized by type)
- Recommendations for next steps

Format: Obsidian-compatible markdown
Ready for review or export.

Next steps:
- Review the report for completeness
- Share with stakeholders
- Use findings to inform decisions
- Archive for future reference
```

## Synthesis Guidelines

### Writing Style

**Executive Summary:**
- Professional but accessible
- Active voice preferred
- Clear and concise language
- Avoid jargon without explanation
- Focus on "what" and "why", not just "how"

**Key Findings:**
- Organized by theme, not by source
- Lead with most important insights
- Support claims with source references
- Note agreements and contradictions
- Synthesize across multiple sources

**Detailed Analysis:**
- Address each research question directly
- Provide evidence for all claims
- Compare and contrast different approaches
- Explain trade-offs and implications
- Include practical examples

**Recommendations:**
- Actionable and specific
- Based on findings, not assumptions
- Consider different contexts
- Note limitations and caveats

### Citation Best Practices

**In-text references:**
- Use source numbers: "(Source #1, #3)"
- Or descriptive: "(Papers #1-3, Code repo #5)"
- Be specific about what came from where

**Code attribution:**
```markdown
// From: organization/repo - path/to/file.ext:45-50
[code snippet]
```

**Quote attribution:**
> "Direct quote from source"
> — [Author/Source], [Context]

### Synthesis vs Summary

**Summary (avoid):**
- Listing findings from each source separately
- No connections between sources
- No analysis or interpretation

**Synthesis (goal):**
- Combining findings across sources
- Identifying patterns and themes
- Analyzing relationships and contradictions
- Drawing conclusions from evidence

## Resources

### scripts/generate_report.py

Python script that orchestrates report generation from templates and findings.

**Usage:**
```bash
python3 .claude/skills/iw-research-synthesizer/scripts/generate_report.py <research-name>
```

**What it does:**
- Loads all research files (plan, sources, findings)
- Extracts research questions
- Reads template from assets/
- Provides framework for synthesis
- Writes research-report.md

**Note:** The script provides structure, but Claude performs the actual synthesis and analysis based on the gathered findings.

### assets/report-template.md

Template file with placeholders for report sections. Includes:
- Executive Summary
- Research Questions
- Key Findings
- Detailed Analysis
- Sources Consulted
- Recommendations

Standard markdown format, Obsidian-compatible.
