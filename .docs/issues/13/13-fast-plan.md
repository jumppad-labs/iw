# Issue #13 - Quick Implementation Plan

**Created**: 2025-11-04 13:44
**Issue**: https://github.com/jumppad-labs/iw/issues/13
**Mode**: Fast Plan (upgrade to detailed plan with /iw-plan 13 --detailed)

---

## Summary

Remove Claude Code attribution from commits and PRs created by the implementation workflow. Commits should only be authored by the configured git user without co-authorship or attribution footers.

## Context

- Issue #13 reports that iw-executor adds Claude Code co-authorship to commits and PRs
- Found in git log: commits contain `🤖 Generated with [Claude Code]` footer and `Co-Authored-By: Claude <noreply@anthropic.com>`
- The `create_phase_commit.py` script docstring mentions "co-authored-by attribution" (.claude/skills/iw-git-workflow/scripts/create_phase_commit.py:6)
- However, the script implementation does NOT currently add attribution (lines 91-117)
- Recent commits show the attribution exists in practice, suggesting it's being added somewhere else
- Two possible sources:
  1. Claude Code's built-in git commit instructions (system-level, not in skills)
  2. Direct commits made outside the script by iw-executor skill instructions

## Implementation Steps

1. **Update `create_phase_commit.py` docstring** (.claude/skills/iw-git-workflow/scripts/create_phase_commit.py:5-6)
   - Remove mention of "co-authored-by attribution" from docstring
   - Script already doesn't add attribution in code, just fix the doc

2. **Search for other commit creation locations**
   - Search iw-executor SKILL.md for any instructions to add attribution to commits
   - Search iw-git-workflow SKILL.md for attribution instructions
   - Check if `commit_plan_files.py` adds attribution

3. **Check PR creation for attribution** (.claude/skills/iw-github-pr-creator/scripts/create_pr.py:91-129)
   - Review `create_plan_based_pr_body()` function
   - Remove any Claude Code attribution from PR bodies if present

4. **Update skill documentation**
   - Remove any references to "proper attribution" that mean Claude Code attribution
   - Update iw-executor SKILL.md if it instructs Claude to add attribution

## Testing

- Create test commit using `create_phase_commit.py` script directly
- Verify commit message contains only: phase name, description, plan reference, issue number
- Verify NO co-authorship footer or Claude Code attribution
- Create test PR using `create_pr.py` script
- Verify PR body contains only plan summary, not Claude Code attribution

## Success Criteria

### Automated:
- [ ] Run: `python3 .claude/skills/iw-git-workflow/scripts/create_phase_commit.py --phase 1 --plan-path .docs/issues/13 --worktree .` (from test branch)
- [ ] Verify commit message format using: `git log -1 --format="%B"`
- [ ] Confirm no "Co-Authored-By: Claude" or "Generated with Claude Code" in output

### Manual:
- [ ] Review `create_phase_commit.py:5-6` docstring is updated
- [ ] Search confirms no attribution instructions in skill SKILL.md files
- [ ] Test commit message contains only phase info, no attribution
- [ ] Test PR body contains only plan summary, no attribution footer

## Notes

The actual implementation in `create_phase_commit.py` is already correct (doesn't add attribution). The main work is:
1. Fix the misleading docstring
2. Search for and remove any attribution instructions in skill documentation
3. Verify PR creation doesn't add attribution

<!-- Question: Should I search for where commits might be made directly via Bash rather than via the script? The git log shows commits with attribution that don't match the single-phase format from create_phase_commit.py, suggesting manual commits. -->

---

**Need more detail?** This is a quick plan focusing on the essentials. For comprehensive research, detailed code examples, and full test strategy, run:

```
/iw-plan 13 --detailed
```

Your comments and edits to this plan will be preserved when upgrading.
