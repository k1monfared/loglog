# Environment Setup Guide

This guide explains how to configure environment-specific settings for the LogLog project.

## Initial Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** to match your system configuration.

## Configuration Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PYTHON_PATH` | Path to your Python 3 interpreter | `/usr/bin/python3` or `/usr/local/bin/python3` |
| `CLAUDE_TRANSCRIPT_DIR` | Directory where Claude Code stores conversation transcripts | `~/.claude/projects/-home-username-Projects-loglog` |
| `CLAUDE_TRANSCRIPT_FILE` | Name of the current conversation transcript file | `02aac319-c5ec-404e-bc47-4d4525b45baf.jsonl` |
| `PROJECT_ROOT` | Root directory of the LogLog project | `.` (usually current directory) |

### Finding Your Claude Transcript Directory

1. **Locate your Claude directory:**
   ```bash
   find ~/.claude -name "*.jsonl" | head -5
   ```

2. **Identify your project's transcript directory:**
   - Look for a directory matching your project path
   - Format: `~/.claude/projects/-home-[username]-Projects-loglog`

3. **Find the most recent transcript file:**
   ```bash
   ls -t ~/.claude/projects/-home-[username]-Projects-loglog/*.jsonl | head -1
   ```

### Example Configuration

```bash
# .env file
PYTHON_PATH=/usr/bin/python3
CLAUDE_TRANSCRIPT_DIR=~/.claude/projects/-home-johndoe-Projects-loglog
CLAUDE_TRANSCRIPT_FILE=a1b2c3d4-e5f6-7890-abcd-ef1234567890.jsonl
PROJECT_ROOT=.
```

## Hook Configuration

The Claude Code hooks in `.claude/settings.json` use these environment variables:

- **Checklist Hook**: Uses `PYTHON_PATH` and transcript file location
- **Other Hooks**: May reference `PROJECT_ROOT` for file operations

## Mobile App Configuration

For Android development:

1. **Update build scripts** to use `[PROJECT_ROOT]` placeholder
2. **Replace absolute paths** in documentation with relative ones
3. **Use environment variables** for system-specific paths

## Troubleshooting

### Hook Execution Issues

If Claude Code hooks fail:

1. **Verify Python path:**
   ```bash
   which python3
   # Update PYTHON_PATH in .env
   ```

2. **Check transcript file exists:**
   ```bash
   ls -la $HOME/.claude/projects/-home-*-Projects-loglog/*.jsonl
   ```

3. **Test hook command manually:**
   ```bash
   echo '{"transcript_path": "'$HOME'/.claude/projects/-home-user-Projects-loglog/transcript.jsonl"}' | python3 .claude/checklist.py
   ```

### Path Resolution Issues

- Use `$HOME` instead of `/home/username`
- Use relative paths when possible: `./docs/` instead of `/absolute/path/docs/`
- Environment variables should be in UPPERCASE
- Always use forward slashes `/` even on Windows (most tools handle this)

## Security Notes

- **Never commit `.env` file** - it contains system-specific paths
- **Always use `.env.example`** as template for sharing
- **Keep personal directories private** - use environment variables or relative paths
- **Review commits** to ensure no absolute paths are accidentally included

## Platform-Specific Notes

### Linux/macOS
- Python usually at `/usr/bin/python3` or `/usr/local/bin/python3`
- Claude directory at `~/.claude/`
- Use `$HOME` for user directory references

### Windows
- Python may be at `/c/Python39/python.exe` or via Windows Store
- Claude directory typically at `%USERPROFILE%/.claude/`
- Environment variables may need Windows-style paths in some contexts

## Updating Configuration

When transcript files change (new conversations):

1. **Find new transcript file:**
   ```bash
   ls -t ~/.claude/projects/-home-*-Projects-loglog/*.jsonl | head -1
   ```

2. **Update `.env` file** with new `CLAUDE_TRANSCRIPT_FILE`

3. **Test hooks still work** after the update