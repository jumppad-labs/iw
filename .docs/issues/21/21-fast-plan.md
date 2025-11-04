# Issue #21 - Quick Implementation Plan

**Created**: 2025-11-04 13:57
**Issue**: https://github.com/jumppad-labs/iw/issues/21
**Mode**: Fast Plan (upgrade to detailed plan with /iw-plan 21 --detailed)

---

## Summary

Make iw-planner intelligently default to fast planning mode for simple tasks. Claude should assess request complexity and only prompt for detailed planning when the task appears complex, minimizing user prompts while ensuring appropriate planning depth.

## Context

**Issue Requirements:**
1. Claude should quickly assess the request complexity
2. For simple tasks → run fast plan automatically
3. For complex tasks → prompt user to confirm detailed plan (or proceed with fast if user declines)
4. After fast plan → offer upgrade to detailed if needed
5. Minimize prompts to user overall

**Current Behavior:**
- Default mode is `--detailed` (line 66 in SKILL.md)
- User must explicitly request `--fast` flag
- No intelligent assessment of complexity

**Key Files:**
- `.claude/skills/iw-planner/SKILL.md:1-100+` - Main workflow logic, mode detection
- `.claude/commands/iw-plan.md:1-14` - Command that passes arguments to skill

**Past Learnings:**
- No specific learnings found related to planning mode selection

## Implementation Steps

1. **Add complexity assessment section to SKILL.md workflow (after line 100)**
   - Insert new "Step 0: Assess Task Complexity" before current workflow
   - Define complexity indicators:
     - **Simple**: CSS/styling, config updates, straightforward bug fixes, < 3 files
     - **Complex**: Multi-phase features, architectural changes, > 5 files, unclear requirements
   - Add decision logic: simple → fast mode, complex → prompt user

2. **Update default behavior in SKILL.md Workflow Decision Tree (line 100-130)**
   - Change: "If no flag → Execute Detailed Planning Workflow"
   - To: "If no flag → Execute Complexity Assessment → Choose workflow"
   - Keep explicit `--fast` and `--detailed` flags as overrides

3. **Add complexity assessment prompts**
   - For complex tasks: "This appears complex (multi-phase/architectural). Run detailed plan? (yes/no, default: yes)"
   - For simple tasks: Proceed directly to fast planning without prompting
   - After fast plan: "Review the plan. Need more detail? Run: /iw-plan 21 --detailed"

4. **Update iw-plan.md command description (line 2)**
   - Change hint text to reflect new intelligent default behavior
   - Note that explicit flags still override

5. **Test with various task descriptions**
   - Simple: "change button color", "fix typo", "update config"
   - Complex: "implement authentication system", "refactor database layer"

## Testing

**Manual Testing Scenarios:**
1. Run `/iw-plan "change button color"` → Should auto-select fast mode
2. Run `/iw-plan "implement user authentication"` → Should prompt for detailed
3. Run `/iw-plan 21 --fast` → Should honor explicit flag (bypass assessment)
4. Run `/iw-plan 21 --detailed` → Should honor explicit flag (bypass assessment)
5. After fast plan, verify upgrade prompt is shown

**Commands:**
- No automated tests for this (behavior change in skill logic)
- Validation through actual usage and observation

## Success Criteria

### Automated:
- N/A (this is a workflow/behavior change, not code change with tests)

### Manual:
- [ ] Simple tasks automatically use fast planning without prompts
- [ ] Complex tasks prompt user before running detailed plan
- [ ] Explicit `--fast` and `--detailed` flags override assessment
- [ ] Fast plans include upgrade prompt at the end
- [ ] Overall user prompts are minimized (no unnecessary questions)

## Notes

This is a workflow improvement that changes how the iw-planner skill makes decisions about planning mode. The main challenge is defining clear, reliable complexity indicators that don't require extensive analysis themselves (which would defeat the purpose of fast planning).

**Complexity Assessment Strategy:**
- Keep it simple: use keyword matching and heuristics
- Keywords like "implement", "refactor", "system", "architecture" → complex
- Keywords like "change", "fix", "update", "add" with single component → simple
- Number of files/components mentioned → simple if 1-3, complex if 4+
- If uncertain → default to fast and offer upgrade

**Consider for detailed plan:**
- Code examples for complexity assessment logic
- Full list of complexity indicator keywords
- Edge case handling (ambiguous requests)

---

**Need more detail?** This is a quick plan focusing on the essentials. For comprehensive research, detailed code examples, and full test strategy, run:

```
/iw-plan 21 --detailed
```

Your comments and edits to this plan will be preserved when upgrading.
