# Learnings & Corrections

This directory captures important learnings and corrections discovered during planning and implementation. These are institutional knowledge items that future work should be aware of.

## Purpose

Document:
- **User corrections** during planning or implementation
- **Mistakes discovered** and how they were caught
- **Important clarifications** that differed from initial assumptions
- **Implementation discoveries** that differed from the plan
- **Things that surprised us** during development
- **Gotchas to avoid** in future work

## Structure

Learnings are organized by topic/area:

```
learnings/
├── README.md (this file)
├── plugin-system.md       # Plugin system learnings
├── resource-providers.md  # Provider pattern learnings
├── testing.md            # Testing-related learnings
└── ...                   # Other topic-based files
```

## When to Add Learnings

### During Planning

Add learnings when:
- User corrects an assumption you made
- Research reveals something unexpected
- You discover a pattern that contradicts your initial understanding
- A limitation or constraint is clarified

### During Implementation

Add learnings when:
- Implementation reveals the plan was incorrect
- You discover an undocumented behavior
- A workaround or solution differs from the plan
- You hit an unexpected obstacle

### After Implementation

Add learnings when:
- Code review reveals issues
- Testing uncovers unexpected behavior
- You identify patterns for future work

## How to Document

### Format

Each learning entry should include:

```markdown
## [Date] - [Brief Title]

**Context:** [What were you working on?]

**Learning:** [What did you discover?]

**Impact:** [How does this affect future work?]

**Related:** [Link to PR, issue, or plan if applicable]
```

### Example

```markdown
## 2025-10-31 - Plugin System Requires Snake_Case Naming

**Context:** Planning ollama API endpoint resources (issue #385)

**Learning:** The plugin system requires resource and provider structs
to use snake_case (e.g., `Ollama_Model`) instead of Go's standard PascalCase
(e.g., `OllamaModel`). This is due to how the plugin system uses reflection
to map HCL resource names to Go structs.

**Impact:** All future resource and provider structs must use snake_case.
This should be documented in plans and acknowledged as a deviation from
standard conventions. Updated architecture docs in `.docs/knowledge/architecture/plugin-system.md`.

**Related:**
- Issue #385
- Plan: `.docs/adhoc/ollama-api-endpoints/`
- Docs: [plugin-system.md](../architecture/plugin-system.md)
```

## Relationship to Other Docs

- **Learnings** → Temporary, evolving knowledge from active development
- **Architecture docs** → Permanent, formalized knowledge about system design
- **Gotchas** → Known issues and workarounds
- **Plan files** → Specific to one implementation, references learnings

### Workflow

1. **Discover learning** during planning/implementation
2. **Document immediately** in appropriate learnings file
3. **Reference in plan** if relevant to that work
4. **Promote to architecture docs** if it becomes formalized knowledge
5. **Move to gotchas** if it's a persistent issue/workaround

## Quick Reference

| Scenario | Action |
|----------|--------|
| User corrects assumption | Add to relevant learnings file immediately |
| Implementation differs from plan | Add to learnings with context |
| Pattern becomes established | Promote from learnings to architecture docs |
| Recurring workaround needed | Move from learnings to gotchas |
| One-time issue | Document in learnings, reference in plan |

## Contributing

1. **Add immediately** - Document learnings when they happen, not later
2. **Be specific** - Include context and impact
3. **Link to work** - Reference the issue/PR/plan
4. **Update architecture docs** - When learnings become formalized
5. **Keep organized** - Use topic-based files, not one giant file
