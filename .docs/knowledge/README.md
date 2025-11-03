# Project Knowledge

This directory contains project-specific technical knowledge, architectural decisions, and institutional knowledge.

## Directory Structure

### `/architecture/` - Architectural Decisions and Patterns

Formalized system architecture and design patterns.

### `/conventions/` - Project-Specific Conventions

Project-specific naming, structure, and coding conventions that differ from general standards.

### `/learnings/` - Learnings & Corrections

Discoveries and corrections from planning and implementation. See `learnings/README.md` for documentation format.

### `/gotchas/` - Known Issues and Workarounds

Persistent issues, limitations, and their workarounds.

## When to Add to This Directory

Add to `.docs/knowledge/` when you discover:

- **Project-specific patterns** that differ from general practices
- **System limitations** (like plugin naming requirements)
- **Architectural decisions** that affect multiple features
- **Common gotchas** that future developers should know
- **Integration patterns** specific to this project

## How to Document

1. **Create a focused document** in the appropriate subdirectory
2. **Update this README** with a link and brief description
3. **Keep it DRY** - Don't duplicate information
4. **Use examples** - Show concrete code when possible
5. **Explain the "why"** - Document reasoning behind decisions

## Contributing

When you discover new project-specific knowledge during implementation:

1. Check if it belongs in `.docs/knowledge/` (project-specific)
2. Create or update the appropriate document
3. Add entry to this README
4. Keep documents focused and scannable
