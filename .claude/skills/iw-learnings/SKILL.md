---
name: iw-learnings
description: Search past learnings and corrections for relevant knowledge. This skill should be invoked in parallel with other research tasks at the start of planning or implementation to gather institutional knowledge from previous work.
---

# Plan Learnings Search

## Overview

Search through institutional learnings to find relevant corrections and important discoveries from previous work. This skill extracts knowledge from the `.docs/knowledge/learnings/` directory where all learnings are centrally documented.

**Designed for Parallel Execution:** This skill is optimized to run concurrently with other research tasks (GitHub issue analysis, codebase exploration, etc.) to maximize efficiency during planning and implementation startup.

## When to Use This Skill

Invoke this skill at the beginning of:
1. **Planning sessions** - To inform the plan with past learnings
2. **Implementation sessions** - To avoid repeating past mistakes
3. **Any time** - When investigating issues related to areas with known complications

**Always run in parallel** with other research agents for maximum speed.

## How It Works

This skill searches for learnings in the centralized knowledge directory:

```
.docs/knowledge/learnings/
├── README.md                 # Documentation guidelines
├── plugin-system.md          # Plugin system learnings
├── resource-providers.md     # Provider pattern learnings
├── testing.md               # Testing-related learnings
└── ...                      # Other topic-based files
```

Each learning file contains entries with this format:
```markdown
## [YYYY-MM-DD] - [Brief Title]

**Context:** [What were you working on?]
**Learning:** [What did you discover?]
**Impact:** [How does this affect future work?]
**Related:** [Link to issue/PR/plan]
```

## Usage

**Invoke with keywords/topics:**
```
/iw-learnings authentication JWT tokens
```

**Parameters:**
- Keywords: Space-separated terms related to your current task
- The skill will search for these terms in both the learnings content and the parent plan directories

## Workflow

### Step 1: Gather Search Context

When invoked, determine what to search for:

1. **If keywords provided in invocation:**
   - Use those keywords directly
   - Example: "authentication JWT tokens" → search for auth-related learnings

2. **If invoked without keywords:**
   - Ask user: "What topic or feature are you working on? (This helps find relevant past learnings)"
   - Extract keywords from response

3. **Keywords to search for:**
   - Main feature/component names (e.g., "authentication", "rate-limiting", "connector")
   - Technology names (e.g., "gRPC", "Redis", "PostgreSQL")
   - Pattern names (e.g., "retry logic", "circuit breaker", "pagination")
   - Problem areas (e.g., "performance", "concurrency", "error handling")

### Step 2: Search Learnings Files

Use multiple parallel search strategies for comprehensive results:

**Search Strategy 1 - Find Learning Files:**
```bash
find .docs/knowledge/learnings -name "*.md" -type f ! -name "README.md" 2>/dev/null
```

**Search Strategy 2 - Content Search by Keyword:**
For each keyword, search learning files:
```bash
# Use Grep tool to search for keywords in .docs/knowledge/learnings/
grep -i "keyword" .docs/knowledge/learnings/*.md
```

**Search Strategy 3 - Topic-Based Search:**
Check if a topic-specific file exists:
```bash
# e.g., plugin-system.md, testing.md, resource-providers.md
ls .docs/knowledge/learnings/<topic>.md
```

### Step 3: Extract and Parse Learnings

For each learning file found:

1. **Read the file** using Read tool
2. **Extract learning entries:**
   - Look for `## [YYYY-MM-DD] - [Title]` headers
   - Capture **Context**, **Learning**, **Impact**, and **Related** sections
   - Parse each entry as a structured learning
3. **Filter by relevance:**
   - Check if learning mentions any of the search keywords
   - Check if context/impact relates to the domain/feature
   - Include learning if it's relevant to current work
4. **Capture metadata:**
   - Date and title from the header
   - Topic file name (e.g., "plugin-system", "testing")
   - Full learning content including all fields

### Step 4: Present Findings

Format results for easy consumption:

```
Found [N] relevant learnings from institutional knowledge:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Plugin System Learnings
   File: .docs/knowledge/learnings/plugin-system.md

   ## 2025-10-31 - Plugin System Requires Snake_Case Naming

   **Context:** Planning ollama API endpoint resources for issue #385

   **Learning:** The Jumppad plugin system requires resource and provider
   structs to use snake_case naming (e.g., Ollama_Show, Show_Provider)
   instead of Go's standard PascalCase due to reflection requirements.

   **Impact:** All future resource and provider structs must use snake_case.
   This must be documented in plans and acknowledged as a deviation from
   Go conventions.

   **Related:** Issue #385, Plan: .docs/adhoc/ollama-api-endpoints/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Testing Learnings
   File: .docs/knowledge/learnings/testing.md

   ## 2025-10-28 - Mock Generation Requires Explicit Interfaces

   **Context:** Adding tests for database layer

   **Learning:** Mockery requires interfaces to be explicitly defined in
   separate files, not inline with implementations.

   **Impact:** Always define interfaces in interface.go files for mockability.

   **Related:** PR #342

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key themes identified:
- Plugin System: Naming convention requirements
- Testing: Mock generation patterns
- Architecture: Interface definition patterns

Recommendation: Review these learnings when designing resources and writing tests.
```

**If no learnings found:**
```
No relevant learnings found for: [keywords]

This might be a new area, or learnings haven't been documented yet.
Proceed with normal research and remember to document any discoveries in .docs/knowledge/learnings/.
```

### Step 5: Provide Context References

Along with findings, provide file references so users can read full context:

```
Full context available in:
- .docs/issues/123/context.md
- .docs/adhoc/refactor-database/context.md

To read a specific plan's full context, use the Read tool with the file path above.
```

## Learning Entry Format

When documenting learnings (done by other skills, not this one), use this format:

```markdown
## Learnings & Corrections

- [YYYY-MM-DD] [What was assumed/planned] → [What was actually correct/needed] - [Why this matters for future work]
```

**Examples:**

```markdown
- [2025-10-31] Assumed database uses auto-incrementing IDs → Actually uses UUIDs - impacts foreign key relationships and migration scripts

- [2025-10-30] Planned to use standard HTTP client → Needed custom client with retry logic - network is unreliable in production environment

- [2025-10-29] Expected synchronous API calls → API is async-only - requires Promise handling throughout codebase
```

## Integration with Other Skills

### Used by Implementation Planner

The planner invokes this skill in parallel with other research:

```markdown
Launch all research tasks concurrently:
1. iw-github-issue-reader (if issue-based)
2. iw-learnings (THIS SKILL)
3. Codebase exploration (Task/Explore)
4. Pattern discovery (Task/Explore)
5. Testing strategy (Task/Explore)
6. Architecture analysis (Task/general-purpose)
```

### Used by Implementation Executor

The executor invokes this skill when loading a plan:

```markdown
After loading plan files, invoke iw-learnings:
- Search for learnings related to the plan's topic
- Present findings before starting implementation
- Reference during implementation when relevant areas are encountered
```

## Search Optimization

**Parallel Execution:**
- Use Bash tool to run multiple grep commands concurrently
- Read multiple context files in parallel when possible
- Aggregate results efficiently

**Relevance Ranking:**
- Exact keyword matches rank highest
- Related terms in same domain rank next
- Date relevance (recent learnings may be more relevant)
- Issue/plan size (larger plans may have more substantial learnings)

**Performance:**
- Cache file list to avoid repeated `find` operations
- Use grep for initial filtering before reading full files
- Only read files that likely contain relevant learnings

## Important Notes

**Read-Only Operation:**
- This skill ONLY reads existing context files
- It does NOT create or modify any files
- Logging of new learnings is done by planner/executor skills

**No Learnings Directory:**
- All learnings are stored in individual plan context.md files
- No central learnings database needed
- This keeps learnings co-located with their source plans

**Keyword Quality:**
- Better keywords = better results
- Use feature names, component names, technology names
- Avoid generic terms like "code" or "function"

## Example Invocations

**During planning:**
```
User: /plan 358
Planner: [Launches multiple parallel agents including:]
  - iw-github-issue-reader for issue #358
  - iw-learnings "connector gRPC retry"
  - Task/Explore for codebase structure
  - Task/Explore for testing patterns
  ...
```

**During implementation:**
```
Executor: Loading plan from .docs/issues/358/
Executor: [Launches iw-learnings "connector gRPC retry" in parallel]
Executor: Found 2 relevant learnings from past plans...
```

**Ad-hoc search:**
```
User: Are there any learnings about database migrations?
User: /iw-learnings database migrations
Skill: [Searches and returns relevant learnings]
```

## Success Criteria

A successful learnings search should:
1. Complete quickly (run in parallel, don't block other operations)
2. Find all relevant learnings (comprehensive search)
3. Filter out irrelevant results (good keyword matching)
4. Present findings clearly (easy to understand format)
5. Provide file references (user can read full context)
6. Indicate when no learnings found (don't leave user wondering)

## Limitations

- Only finds documented learnings (requires discipline to document)
- Keywords must match (won't find synonyms without explicit search)
- Can't infer learnings (only finds explicitly documented ones)
- Requires context.md files to follow the standard format
