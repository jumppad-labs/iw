#!/bin/bash
set -e

# DEPRECATED: This bash script is deprecated in favor of bootstrap.py
# For Windows compatibility, please use: python3 bootstrap.py
# This script remains for backward compatibility with existing Unix workflows.
#
# See bootstrap.py for the cross-platform Python version.

# Implementation Workflow Bootstrap Script
# This script installs the iw-install skill which can then install the full workflow

REPO_URL="https://raw.githubusercontent.com/jumppad-labs/iw/main"
SKILL_NAME="iw-install"

echo "=============================================="
echo "Implementation Workflow Bootstrap"
echo "=============================================="
echo ""
echo "This script will install the iw-install skill,"
echo "which you can then use to install the full workflow."
echo ""

# Prompt for installation location
echo "Where would you like to install the workflow?"
echo ""
echo "1) Project-level (.claude in current directory)"
echo "   - Committed to version control"
echo "   - Shared with team members"
echo "   - Project-specific configuration"
echo ""
echo "2) User-level (~/.claude in home directory)"
echo "   - Available in all projects"
echo "   - Personal configuration"
echo "   - Not committed to repos"
echo ""
read -p "Enter choice [1 or 2]: " choice

case $choice in
  1)
    INSTALL_DIR=".claude"
    INSTALL_TYPE="project"
    echo ""
    echo "Installing to project-level: $PWD/$INSTALL_DIR"
    ;;
  2)
    INSTALL_DIR="$HOME/.claude"
    INSTALL_TYPE="user"
    echo ""
    echo "Installing to user-level: $INSTALL_DIR"
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

# Create directory structure
echo ""
echo "Creating directory structure..."
mkdir -p "$INSTALL_DIR/skills/$SKILL_NAME/scripts"
mkdir -p "$INSTALL_DIR/commands"

# Download iw-install skill
echo "Downloading iw-install skill..."
curl -sSL "$REPO_URL/.claude/skills/$SKILL_NAME/SKILL.md" \
  -o "$INSTALL_DIR/skills/$SKILL_NAME/SKILL.md" 2>/dev/null || {
  echo "Error: Failed to download SKILL.md"
  exit 1
}

# Download manage_workflow.py script
echo "Downloading installation script..."
curl -sSL "$REPO_URL/.claude/skills/$SKILL_NAME/scripts/manage_workflow.py" \
  -o "$INSTALL_DIR/skills/$SKILL_NAME/scripts/manage_workflow.py" 2>/dev/null || {
  echo "Error: Failed to download manage_workflow.py"
  exit 1
}

# Make script executable (not strictly necessary for Python, but good practice)
chmod +x "$INSTALL_DIR/skills/$SKILL_NAME/scripts/manage_workflow.py" 2>/dev/null || true

# Download /iw-install command
echo "Downloading /iw-install command..."
curl -sSL "$REPO_URL/.claude/commands/iw-install.md" \
  -o "$INSTALL_DIR/commands/iw-install.md" 2>/dev/null || {
  echo "Error: Failed to download iw-install.md"
  exit 1
}

echo ""
echo "=============================================="
echo "Bootstrap Complete!"
echo "=============================================="
echo ""
echo "The iw-install skill has been installed to:"
echo "  $INSTALL_DIR/skills/$SKILL_NAME/"
echo ""
echo "Next steps:"
echo ""
echo "1. Start or restart Claude Code"
echo ""
echo "2. Run the installation command:"
if [ "$INSTALL_TYPE" = "project" ]; then
  echo "   /iw-install"
  echo ""
  echo "   This will install the full workflow to your project."
else
  echo "   /iw-install --user"
  echo ""
  echo "   This will install the full workflow to ~/.claude/"
fi
echo ""
echo "3. Start using the workflow:"
echo "   /iw-help          - Show workflow guidance"
echo "   /iw-plan <task>   - Create implementation plan"
echo "   /iw-implement <#> - Execute plan"
echo ""
echo "For more information, see:"
echo "  https://github.com/jumppad-labs/iw"
echo ""
