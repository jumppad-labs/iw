#!/bin/bash

# DEPRECATED: This bash hook is deprecated in favor of load_workflow.py
# For Windows compatibility, use the Python version: .claude/hooks/load_workflow.py
# This script remains for backward compatibility with existing Unix workflows.
#
# See load_workflow.py for the cross-platform Python version.

# Hook script to load the iw-workflow skill at session start
# This provides context about the project workflow and documentation structure

echo "Loading workflow guidance..."
echo ""
echo "Documentation Structure:"
echo "- CLAUDE.md: General Go development standards"
echo "- .docs/knowledge/: Jumppad-specific technical knowledge"
echo "- workflow skill: Process and methodology (auto-loaded)"
echo ""
echo "Use /iw-plan for complex features, /iw-implement to execute plans."
echo "See the workflow skill for full details on the planning and implementation process."
echo ""
