# Research Skills - Task Checklist

**Last Updated**: 2025-11-03
**Status**: Phase 1 Complete

## Phase 1: Core Infrastructure

- [x] **Task 1.1**: Create base skill directory structure
  - Files: `research-planner/`, `research-executor/`, `research-synthesizer/` directories
  - Effort: S
  - Dependencies: None
  - Acceptance: All three skill directories exist with subdirectories (scripts/, assets/, references/)
  - **Completed**: 2025-11-03

- [x] **Task 1.2**: Create init_research.py script
  - File: `research-planner/scripts/init_research.py`
  - Effort: M
  - Dependencies: Task 1.1
  - Acceptance: Script creates `.docs/research/<name>/` structure with all files
  - **Completed**: 2025-11-03

- [x] **Task 1.3**: Create research plan template
  - File: `research-planner/assets/research-plan-template.md`
  - Effort: S
  - Dependencies: None
  - Acceptance: Template includes all sections with {{PLACEHOLDERS}}
  - **Completed**: 2025-11-03

- [x] **Task 1.4**: Create report template
  - File: `research-synthesizer/assets/report-template.md`
  - Effort: S
  - Dependencies: None
  - Acceptance: Template includes executive summary, findings, sources sections
  - **Completed**: 2025-11-03

- [x] **Task 1.5**: Make scripts executable
  - Files: All `scripts/*.py` files
  - Effort: S
  - Dependencies: Tasks 1.2
  - Acceptance: `chmod +x` applied, scripts have shebang line
  - **Completed**: 2025-11-03

### Phase 1 Verification
- [x] Run: `python3 research-planner/scripts/init_research.py test-research`
- [x] Verify: Directory `.docs/research/test-research/` created
- [x] Verify: Template files contain proper placeholders
- [x] Verify: Scripts execute without import errors

---

## Phase 2: research-planner Skill

- [ ] **Task 2.1**: Create research-planner SKILL.md
  - File: `research-planner/SKILL.md`
  - Effort: L
  - Dependencies: Phase 1 complete
  - Acceptance: SKILL.md includes YAML frontmatter, complete workflow (Steps 1-6)

- [ ] **Task 2.2**: Implement workflow Step 1 (Understand Research Intent)
  - File: `research-planner/SKILL.md`
  - Effort: M
  - Dependencies: Task 2.1
  - Acceptance: Clear prompts for topic, questions, intended use

- [ ] **Task 2.3**: Implement workflow Step 2 (Define Research Questions)
  - File: `research-planner/SKILL.md`
  - Effort: M
  - Dependencies: Task 2.2
  - Acceptance: Guidance for creating good vs bad research questions with examples

- [ ] **Task 2.4**: Implement workflow Steps 3-6
  - File: `research-planner/SKILL.md`
  - Effort: M
  - Dependencies: Task 2.3
  - Acceptance: All workflow steps complete with clear instructions

- [ ] **Task 2.5**: Create add_source.py helper script
  - File: `research-planner/scripts/add_source.py`
  - Effort: M
  - Dependencies: Task 1.2
  - Acceptance: Script adds sources to sources.md with proper formatting

- [ ] **Task 2.6**: Update init_research.py to use templates
  - File: `research-planner/scripts/init_research.py`
  - Effort: M
  - Dependencies: Task 1.3
  - Acceptance: Script copies and populates template files

### Phase 2 Verification
- [ ] Test: Invoke research-planner skill on test topic
- [ ] Verify: Interactive workflow guides through all steps
- [ ] Verify: Research plan file created with complete structure
- [ ] Verify: Research questions are well-formed
- [ ] Verify: Scope boundaries clearly defined

---

## Phase 3: research-executor Skill

- [ ] **Task 3.1**: Create research-executor SKILL.md
  - File: `research-executor/SKILL.md`
  - Effort: L
  - Dependencies: Phase 2 complete
  - Acceptance: SKILL.md includes complete workflow for gathering from multiple source types

- [ ] **Task 3.2**: Implement Step 1 (Load Research Plan)
  - File: `research-executor/SKILL.md`
  - Effort: S
  - Dependencies: Task 3.1
  - Acceptance: Instructions to read and parse research-plan.md

- [ ] **Task 3.3**: Implement Step 2 (Source Detection and Routing)
  - File: `research-executor/SKILL.md`
  - Effort: L
  - Dependencies: Task 3.2
  - Acceptance: Logic for detecting source type and routing to appropriate gathering strategy

- [ ] **Task 3.4**: Implement academic paper gathering workflow
  - File: `research-executor/SKILL.md`
  - Effort: M
  - Dependencies: Task 3.3
  - Acceptance: WebSearch + WebFetch integration, extraction logic documented

- [ ] **Task 3.5**: Implement code repository gathering workflow
  - File: `research-executor/SKILL.md`
  - Effort: M
  - Dependencies: Task 3.3
  - Acceptance: Task/Explore agent usage, pattern extraction documented

- [ ] **Task 3.6**: Implement documentation gathering workflow
  - File: `research-executor/SKILL.md`
  - Effort: S
  - Dependencies: Task 3.3
  - Acceptance: WebFetch integration for docs

- [ ] **Task 3.7**: Implement Step 4 (Findings Organization)
  - File: `research-executor/SKILL.md`
  - Effort: M
  - Dependencies: Tasks 3.4-3.6
  - Acceptance: Thematic organization instructions with examples

- [ ] **Task 3.8**: Create add_finding.py script
  - File: `research-executor/scripts/add_finding.py`
  - Effort: M
  - Dependencies: Task 3.1
  - Acceptance: Script adds findings to findings.md organized by theme

- [ ] **Task 3.9**: Create research-best-practices.md reference
  - File: `research-executor/references/research-best-practices.md`
  - Effort: M
  - Dependencies: Task 3.1
  - Acceptance: Complete guide for academic, code, and docs research

### Phase 3 Verification
- [ ] Test: Execute research on topic with mixed sources (paper + code + docs)
- [ ] Verify: WebSearch and WebFetch work for academic papers
- [ ] Verify: GitHub repos explored correctly
- [ ] Verify: Documentation fetched and extracted
- [ ] Verify: Findings organized by theme in findings.md
- [ ] Verify: Sources tracked in sources.md

---

## Phase 4: research-synthesizer Skill

- [ ] **Task 4.1**: Create research-synthesizer SKILL.md
  - File: `research-synthesizer/SKILL.md`
  - Effort: L
  - Dependencies: Phase 3 complete
  - Acceptance: SKILL.md includes complete synthesis workflow (Steps 1-10)

- [ ] **Task 4.2**: Implement Step 1 (Load Research Data)
  - File: `research-synthesizer/SKILL.md`
  - Effort: S
  - Dependencies: Task 4.1
  - Acceptance: Instructions to read plan, sources, findings files

- [ ] **Task 4.3**: Implement Step 2 (Analyze Findings)
  - File: `research-synthesizer/SKILL.md`
  - Effort: M
  - Dependencies: Task 4.2
  - Acceptance: Logic for identifying themes, patterns, contradictions, gaps

- [ ] **Task 4.4**: Implement Step 3 (Generate Executive Summary)
  - File: `research-synthesizer/SKILL.md`
  - Effort: M
  - Dependencies: Task 4.3
  - Acceptance: Quality criteria and structure for 2-3 paragraph summary

- [ ] **Task 4.5**: Implement Step 4 (Structure Key Findings)
  - File: `research-synthesizer/SKILL.md`
  - Effort: M
  - Dependencies: Task 4.4
  - Acceptance: Theme-based organization with examples

- [ ] **Task 4.6**: Implement Step 5 (Detailed Analysis)
  - File: `research-synthesizer/SKILL.md`
  - Effort: M
  - Dependencies: Task 4.5
  - Acceptance: Question-by-question analysis structure

- [ ] **Task 4.7**: Implement Steps 6-7 (Sources & Recommendations)
  - File: `research-synthesizer/SKILL.md`
  - Effort: S
  - Dependencies: Task 4.6
  - Acceptance: Simple reference format, actionable recommendations

- [ ] **Task 4.8**: Implement Steps 8-10 (Generate, Validate, Present)
  - File: `research-synthesizer/SKILL.md`
  - Effort: M
  - Dependencies: Task 4.7
  - Acceptance: Template population, quality checks, summary statistics

- [ ] **Task 4.9**: Create generate_report.py script
  - File: `research-synthesizer/scripts/generate_report.py`
  - Effort: L
  - Dependencies: Task 4.1
  - Acceptance: Script loads files, populates template, writes research-report.md

- [ ] **Task 4.10**: Implement template placeholder replacement
  - File: `research-synthesizer/scripts/generate_report.py`
  - Effort: M
  - Dependencies: Task 4.9
  - Acceptance: All {{PLACEHOLDERS}} replaced with actual content

### Phase 4 Verification
- [ ] Test: Generate report from test research data
- [ ] Verify: Executive summary is clear and comprehensive
- [ ] Verify: All research questions addressed in report
- [ ] Verify: Findings organized logically by theme
- [ ] Verify: Sources properly referenced throughout
- [ ] Verify: Recommendations are actionable
- [ ] Verify: Markdown renders correctly (no syntax errors)
- [ ] Verify: Report works in Obsidian

---

## Phase 5: Integration & Polish

- [ ] **Task 5.1**: Create /research-plan slash command
  - File: `.claude/commands/research-plan.md`
  - Effort: S
  - Dependencies: Phase 2 complete
  - Acceptance: Command invokes research-planner skill

- [ ] **Task 5.2**: Create /research-execute slash command
  - File: `.claude/commands/research-execute.md`
  - Effort: S
  - Dependencies: Phase 3 complete
  - Acceptance: Command invokes research-executor skill

- [ ] **Task 5.3**: Create /research-synthesize slash command
  - File: `.claude/commands/research-synthesize.md`
  - Effort: S
  - Dependencies: Phase 4 complete
  - Acceptance: Command invokes research-synthesizer skill

- [ ] **Task 5.4**: Create example research project
  - Files: `examples/authentication-research/*`
  - Effort: L
  - Dependencies: Phases 2-4 complete
  - Acceptance: Complete example with plan, sources, findings, report

- [ ] **Task 5.5**: Create project README.md
  - File: `README.md`
  - Effort: M
  - Dependencies: None
  - Acceptance: Comprehensive documentation with quick start, features, examples

- [ ] **Task 5.6**: Create CONTRIBUTING.md
  - File: `CONTRIBUTING.md`
  - Effort: M
  - Dependencies: None
  - Acceptance: Guidelines for code style, testing, documentation, examples

- [ ] **Task 5.7**: Test complete end-to-end workflow
  - Files: All skills
  - Effort: L
  - Dependencies: All previous tasks
  - Acceptance: Can plan, execute, synthesize on real research topic

- [ ] **Task 5.8**: Verify Obsidian compatibility
  - Files: Generated reports
  - Effort: S
  - Dependencies: Task 5.7
  - Acceptance: Reports open and render correctly in Obsidian

### Phase 5 Verification
- [ ] Test: `/research-plan` command works
- [ ] Test: `/research-execute` command works
- [ ] Test: `/research-synthesize` command works
- [ ] Verify: Example project is complete and demonstrates best practices
- [ ] Verify: Documentation is clear and comprehensive
- [ ] Verify: All links in README work
- [ ] Verify: End-to-end workflow completes successfully
- [ ] Verify: No errors or rough edges in user experience

---

## Final Verification

### Automated Checks:
- [ ] All Python scripts execute: `python3 <script> --help` shows usage
- [ ] Directory structures created correctly
- [ ] Template files valid markdown (no syntax errors)
- [ ] Scripts have proper permissions (executable)

### Manual Checks:
- [ ] Complete workflow works end-to-end (plan → execute → synthesize)
- [ ] Reports are well-structured and readable
- [ ] Mixed source types (papers + code + docs) handled correctly
- [ ] Findings properly organized by theme
- [ ] Sources properly tracked and referenced
- [ ] Reports compatible with Obsidian
- [ ] Documentation complete and accurate
- [ ] Examples demonstrate best practices
- [ ] No user-facing errors or rough edges

### Edge Cases to Test:
- [ ] Empty research (no sources found)
- [ ] Single source type only (e.g., only code repos)
- [ ] Large number of sources (>20)
- [ ] Conflicting information across sources
- [ ] Very long findings (>10k words)
- [ ] Special characters in research names

## Notes Section

### Implementation Notes:
[Add notes during implementation]

### Blockers/Issues:
[Track any blockers discovered]

### Deferred Items:
- Advanced citation formatting (APA, MLA, Chicago, IEEE)
- Obsidian vault export/sync
- iw-* workflow integration
- Research templates
- Collaboration features
- Export to PDF/HTML/LaTeX
- Research metrics tracking
- BibTeX export

All deferred items documented in plan as future enhancements.

---

## Task Estimates Summary

**Phase 1 (Core Infrastructure):** 5 tasks, ~8 hours
**Phase 2 (research-planner):** 6 tasks, ~16 hours
**Phase 3 (research-executor):** 9 tasks, ~24 hours
**Phase 4 (research-synthesizer):** 10 tasks, ~20 hours
**Phase 5 (Integration & Polish):** 8 tasks, ~16 hours

**Total:** 38 tasks, ~84 hours estimated effort

**Note:** Estimates assume familiarity with Python, Claude tools, and existing skill patterns. Actual time may vary based on testing iterations and refinement.
