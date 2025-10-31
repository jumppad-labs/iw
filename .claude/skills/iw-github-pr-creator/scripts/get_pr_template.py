#!/usr/bin/env python3
"""
Get PR body template for a given type.

Returns appropriate PR body template for feature, bugfix, docs, refactor, etc.

Usage:
    python3 get_pr_template.py --type <template-type>

Output:
    PR body template as string
"""

import argparse
import sys


TEMPLATES = {
    "feature": """## Summary
<Brief description of the feature>

## Changes
- <Change 1>
- <Change 2>
- <Change 3>

## Why?
<Motivation for this feature>

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manually tested feature

## Screenshots/Demos
<If UI changes, include screenshots>

## Documentation
- [ ] Updated README if needed
- [ ] Added code comments
- [ ] Updated API docs if needed
""",

    "bugfix": """## Problem
<Description of the bug>

## Root Cause
<What caused the bug>

## Solution
<How this PR fixes the bug>

## Testing
- [ ] Added test case for bug
- [ ] Verified fix works
- [ ] Checked for regression

## Related
Fixes #<issue-number>
""",

    "docs": """## Documentation Changes
<What documentation was updated>

## Reason
<Why these changes were needed>

## Preview
<Link to preview or screenshots if applicable>

## Checklist
- [ ] Spelling and grammar checked
- [ ] Links tested
- [ ] Examples verified
""",

    "refactor": """## Refactoring Summary
<What was refactored>

## Motivation
<Why this refactoring was needed>

## Changes
- <Change 1>
- <Change 2>

## Impact
<Impact on performance, maintainability, etc.>

## Testing
- [ ] All existing tests pass
- [ ] No behavior changes
- [ ] Code coverage maintained
""",

    "chore": """## Changes
<Description of changes>

## Reason
<Why these changes were needed>

## Checklist
- [ ] No functional changes
- [ ] Build succeeds
- [ ] No breaking changes
"""
}


def main():
    parser = argparse.ArgumentParser(
        description="Get PR body template for a given type"
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=TEMPLATES.keys(),
        help="Type of PR template"
    )

    args = parser.parse_args()

    template = TEMPLATES[args.type]
    print(template)


if __name__ == "__main__":
    main()
