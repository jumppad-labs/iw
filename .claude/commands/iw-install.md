---
description: Manage Implementation Workflow installation
argument-hint: Optional: --update, --uninstall, --verify, --list, --user
---

Manage the Implementation Workflow installation using the iw-install skill.

## Usage

**Install to current project** (default):
```
/iw-install
```

**Install to user directory** (~/.claude):
```
/iw-install --user
```

**Update existing installation**:
```
/iw-install --update
```

**Update user installation**:
```
/iw-install --update --user
```

**Uninstall from project**:
```
/iw-install --uninstall
```

**Uninstall from user directory**:
```
/iw-install --uninstall --user
```

**Verify installation**:
```
/iw-install --verify
```

**List installed components**:
```
/iw-install --list
```

## Arguments Provided

$ARGUMENTS

## Implementation

Parse the arguments to determine action and location:

- If no arguments or just `--user`: action = install
- If `--update` present: action = update
- If `--uninstall` present: action = uninstall
- If `--verify` present: action = verify
- If `--list` present: action = list
- If `--user` present: location = user, otherwise location = project

Then invoke the `iw-install` skill using the Skill tool with the determined action and location parameters.

The skill will use the `scripts/manage_workflow.py` script to:
- Fetch workflow files from GitHub
- Install to the specified location
- Handle updates and uninstallation
- Verify installation integrity
- List installed components

**Example invocation:**
- For `/iw-install`: Invoke skill with action=install, location=project
- For `/iw-install --user`: Invoke skill with action=install, location=user
- For `/iw-install --update`: Invoke skill with action=update, location=project
- For `/iw-install --uninstall --user`: Invoke skill with action=uninstall, location=user
