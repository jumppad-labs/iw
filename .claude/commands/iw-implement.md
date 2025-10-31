# Implement Plan

Execute an implementation plan created by the iw-planner skill.

## Usage

Provide the path to the plan directory:

```
/implement .docs/issues/123/
```

or

```
/implement .docs/adhoc/feature-name/
```

If no path is provided, the iw-executor skill will be activated and you can provide the path when prompted.

## What This Does

This command activates the **iw-executor** skill, which will:

1. Load all four plan files (plan.md, tasks.md, context.md, research.md)
2. Activate language-specific guidelines (e.g., go-dev-guidelines for Go)
3. Execute tasks phase by phase following the detailed plan
4. Update tasks.md to mark tasks as complete incrementally
5. Update context.md with discoveries and findings
6. Confirm with you after each phase and when issues arise

## How It Works

The iw-executor skill follows a structured workflow:

- **Loads the plan** - Parses all plan files to understand phases and tasks
- **Detects language** - Activates appropriate coding guidelines
- **Executes by phase** - Works through each phase systematically
- **Tracks progress** - Updates tasks.md and context.md as work progresses
- **Handles deviations** - Stops and prompts when plan needs updating
- **Confirms milestones** - Asks for confirmation after each phase

## When to Use

Use this command when:
- You have a complete implementation plan ready to execute
- The plan was created using iw-planner skill
- You want systematic, tracked execution with incremental progress

## Examples

Execute an issue-based plan:
```
/implement .docs/issues/357/
```

Execute an ad-hoc plan:
```
/implement .docs/adhoc/refactor-auth/
```

---

**Invoke the iw-executor skill now** with the plan path provided in the command arguments, or ask for the path if none was provided.
