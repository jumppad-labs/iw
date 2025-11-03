# Research Skills - Context & Dependencies

**Last Updated**: 2025-11-03

## Quick Summary

Implement three specialized Claude skills (research-planner, research-executor, research-synthesizer) that work together to give Claude "research superpowers" - planning research projects, gathering information from diverse sources (academic papers, code repositories, documentation), and synthesizing findings into comprehensive, well-structured markdown reports with simple references. Fully automated report generation following academic research best practices, with Obsidian-compatible output.

## Key Files & Locations

### Files to Create:

**research-planner skill:**
- `research-planner/SKILL.md` - Main skill file (workflow-based)
- `research-planner/scripts/init_research.py` - Initialize research directory structure
- `research-planner/scripts/add_source.py` - Add sources to sources.md
- `research-planner/assets/research-plan-template.md` - Research plan template

**research-executor skill:**
- `research-executor/SKILL.md` - Main skill file (workflow-based)
- `research-executor/scripts/add_finding.py` - Add findings to findings.md
- `research-executor/references/research-best-practices.md` - Research gathering guide

**research-synthesizer skill:**
- `research-synthesizer/SKILL.md` - Main skill file (workflow-based)
- `research-synthesizer/scripts/generate_report.py` - Generate final report
- `research-synthesizer/assets/report-template.md` - Report template

**Project-level files:**
- `.claude/commands/research-plan.md` - Slash command for planning
- `.claude/commands/research-execute.md` - Slash command for execution
- `.claude/commands/research-synthesize.md` - Slash command for synthesis
- `README.md` - Project documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `examples/authentication-research/` - Complete example workflow

### Files to Reference:

**Pattern examples:**
- `~/.claude/skills/skill-creator/SKILL.md` - Skill creation guidelines
- `~/.claude/skills/iw-planner/SKILL.md` - Workflow pattern
- `~/.claude/skills/iw-planner/scripts/init_plan.py` - Script pattern
- `~/.claude/skills/iw-planner/assets/*.md` - Template patterns
- `~/.claude/skills/iw-learnings/SKILL.md` - Search patterns

### Research Output Structure:

`.docs/research/<research-name>/` contains:
- `research-plan.md` - Scope, questions, methodology
- `sources.md` - Sources with excerpts
- `findings.md` - Organized findings by theme
- `research-report.md` - Final synthesized report (generated)
- `assets/` - Supporting files (PDFs, images, etc.)

## Dependencies

### Code Dependencies:

**Python standard library** (no external packages required):
- `argparse` - CLI argument parsing
- `pathlib` - Path manipulation
- `datetime` - Timestamps
- `sys` - System operations
- `re` - Regular expressions for parsing

**Claude tools:**
- `WebSearch` - Find academic papers, articles
- `WebFetch` - Extract content from web pages
- `Task` - Spawn research agents (Explore, general-purpose)
- `Skill` - Invoke other skills if needed
- `Read/Write` - File operations
- `Bash` - Script execution

### External Dependencies:

- None (standalone skills, no external services required)
- Future: Obsidian vault for export/sync (enhancement)
- Future: iw-* workflow integration (enhancement)

## Key Technical Decisions

1. **Three Specialized Skills**: Planner, executor, synthesizer for clear separation of concerns
2. **Single Flexible Executor**: Handles both code and academic sources in one skill for comprehensive reports
3. **Simple References**: Just track sources, no complex citation formatting (APA/MLA/etc.)
4. **Fully Automated Reports**: Synthesizer generates complete markdown reports automatically
5. **Standalone Initially**: No iw-* workflow integration until skills are tested
6. **Obsidian-Compatible**: Standard markdown structure, ready for future vault integration
7. **Template-Based**: Use {{PLACEHOLDER}} replacement pattern from iw-planner
8. **Python Scripts**: Deterministic file operations following existing skill patterns
9. **Progressive Disclosure**: Keep SKILL.md lean, detailed guidance in references/
10. **Workflow-Based Structure**: Sequential steps following iw-planner pattern

## Integration Points

### Internal Integration (between research skills):

- **research-planner** → creates research-plan.md → used by **research-executor**
- **research-executor** → creates sources.md, findings.md → used by **research-synthesizer**
- **research-synthesizer** → reads all files → generates research-report.md

### Tool Integration:

- **WebSearch**: Finding academic papers (Google Scholar, arXiv, PubMed)
- **WebFetch**: Extracting content from papers, docs, GitHub READMEs
- **Task/Explore**: Deep code repository exploration
- **Task/general-purpose**: Complex analysis and synthesis

### Future Integration Points (deferred):

- **iw-init**: Create .docs/research/ structure (or create independently)
- **iw-learnings**: Search past research findings
- **iw-git-workflow**: Version control for research
- **iw-github-issue-reader**: Link research to issues
- **Obsidian vault**: Export/sync with wikilinks

## Environment Requirements

- **Python**: 3.7+ (for type hints and pathlib)
- **Claude Code**: Running environment (for tool access)
- **Working directory**: Project root with `.docs/` structure
- **No environment variables required**
- **No database required**
- **No external API keys required**

## Related Documentation

- Original request: User message about "research superpowers"
- Research notes: `research-skills-research.md` (this directory)
- Implementation plan: `research-skills-plan.md` (this directory)
- Task checklist: `research-skills-tasks.md` (this directory)

## Implementation Progress

### Phase 1: Core Infrastructure (COMPLETE - 2025-11-03)

**Created Files:**
- `research-planner/scripts/init_research.py` - Directory initialization script
- `research-planner/assets/research-plan-template.md` - Research plan template
- `research-synthesizer/assets/report-template.md` - Report generation template

**Directory Structure:**
```
research-planner/
  scripts/
  assets/
research-executor/
  scripts/
  references/
research-synthesizer/
  scripts/
  assets/
```

**Key Discoveries:**
- Linting caught unused `os` import and unnecessary f-strings in init_research.py
- Script successfully creates `.docs/research/<name>/` structure
- Templates use `{{PLACEHOLDER}}` format as planned
- Python 3 type hints work correctly for Path objects

**Verification Results:**
- ✅ All scripts execute without errors
- ✅ Directory structure matches design
- ✅ Templates contain proper placeholders
- ✅ Test directory created successfully

## Project Structure

```
research-skills/
├── .docs/
│   ├── adhoc/
│   │   └── research-skills/          # This plan
│   └── research/                      # Future research outputs
├── research-planner/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── init_research.py
│   │   └── add_source.py
│   └── assets/
│       └── research-plan-template.md
├── research-executor/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── add_finding.py
│   └── references/
│       └── research-best-practices.md
├── research-synthesizer/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── generate_report.py
│   └── assets/
│       └── report-template.md
├── .claude/
│   └── commands/
│       ├── research-plan.md
│       ├── research-execute.md
│       └── research-synthesize.md
├── examples/
│   └── authentication-research/       # Complete example
├── README.md
└── CONTRIBUTING.md
```

## Obsidian Compatibility

**Current design (Obsidian-compatible):**
- Standard GitHub-flavored markdown
- Clean file organization in .docs/research/
- Relative links between files
- Frontmatter-ready structure

**Future enhancements for Obsidian:**
- Add YAML frontmatter to reports (tags, dates, etc.)
- Convert references to wikilinks [[source-name]]
- Add graph view connections
- Sync to Obsidian vault
- Obsidian daily notes integration
- Dataview queries for research tracking

## Workflow Summary

**User workflow:**
1. `/research-plan` → Define research questions and scope
2. `/research-execute` → Gather from academic papers, code, docs
3. `/research-synthesize` → Generate comprehensive markdown report

**Behind the scenes:**
1. Planner creates `.docs/research/<name>/` with research-plan.md
2. Executor gathers info, populates sources.md and findings.md (organized by theme)
3. Synthesizer reads all files, generates research-report.md with executive summary

**Output:**
- Professional markdown report
- Executive summary (2-3 paragraphs)
- Key findings by theme
- Detailed analysis
- Simple source references
- Recommendations for next steps
- Obsidian-compatible format

## Future Enhancement Notes

**Documented for later implementation:**

1. **Advanced Citations**: Add APA, MLA, Chicago, IEEE formatting
2. **Obsidian Integration**: Export to vault, wikilinks, frontmatter, sync
3. **iw-* Workflow**: Integrate with issues, git, learnings
4. **Templates**: Pre-built research templates (literature review, comparative analysis, how-to)
5. **Collaboration**: Multi-user research, shared findings
6. **Export Formats**: PDF, HTML, LaTeX output
7. **Research Metrics**: Track progress, coverage, quality indicators
8. **Source Management**: BibTeX export, citation management integration

All enhancements deferred until core skills are tested and validated.
