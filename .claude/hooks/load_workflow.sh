#!/bin/bash

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
