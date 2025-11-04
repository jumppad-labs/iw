# Installation & GitHub API Learnings

## 2025-11-03 - Clone Repo Instead of Individual API Requests

**Context:** Planning fix for issue #10 - GitHub API rate limiting during /iw-install

**Learning:** Initial approach was to add GitHub token authentication to individual API requests (80-100+ requests per installation). User corrected this: instead of authenticating individual API requests, clone the entire repository once and copy files from the local clone. This is simpler, more reliable, and completely avoids rate limiting.

**Impact:**
- Installation becomes faster (one clone vs 100 API requests)
- No rate limiting issues regardless of authentication
- Simpler implementation (git clone + file copy)
- More robust (works offline after initial clone, can cache clone)
- No need for token management, environment variables, or retry logic

**Related:**
- Issue #10
- Plan: `.docs/issues/10/`
- File: `.claude/skills/iw-install/scripts/manage_workflow.py`

**Approach:**
- Use `git clone --depth 1` to clone only latest commit (shallow clone)
- Clone to temporary directory
- Copy files from `.claude/` subdirectory to target location
- Clean up temporary clone
- Much simpler than managing 100+ individual HTTP requests
