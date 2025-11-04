---
description: Create implementation plan (intelligently defaults to fast for simple tasks, detailed for complex)
argument-hint: Describe what you need planned or provide issue number. Optional flags: --fast (force quick plan), --detailed (force comprehensive plan)
---

Use the iw-planner skill to create an implementation plan.

Arguments: $ARGUMENTS

Note:
- **Intelligent default**: Claude assesses task complexity and chooses appropriate mode automatically
- Use --fast to force quick planning (~100 lines, single file, minimal research)
- Use --detailed to force comprehensive planning (full 4-file plan, extensive research)
- Simple tasks auto-select fast mode; complex tasks prompt before running detailed
- You can upgrade from fast to detailed later: /iw-plan <issue> --detailed
