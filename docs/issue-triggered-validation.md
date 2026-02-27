# Issue-Triggered Validation

This document describes how to trigger URL validation scans using GitHub issues.

## Overview

The repository includes an automated system that monitors GitHub issues and triggers validation scans based on issue titles. This allows you to schedule validation runs using different patterns without manually running workflows.

## How It Works

1. **Issue Detection**: Every hour, a GitHub Actions workflow checks for open issues with specific title prefixes
2. **Scan Execution**: When a trigger issue is found, the system runs a full URL validation scan across all countries
3. **Report Generation**: After validation completes, a detailed report is posted as a comment to the issue
4. **Issue Management**: 
   - One-time scans (`SCAN:` prefix) close the issue automatically
   - Periodic scans keep the issue open for future runs

## Supported Trigger Prefixes

### One-Time Scans

**`SCAN: <description>`**
- Runs validation once
- Posts results as a comment
- Automatically closes the issue when complete
- Example: `SCAN: Validate URL`

### Periodic Scans

These prefixes trigger validation on a schedule but keep the issue open:

- **`QUARTERLY: <description>`** - Intended for quarterly validation cycles
- **`MONTHLY: <description>`** - Intended for monthly validation cycles
- **`WEEKLY: <description>`** - Intended for weekly validation cycles
- **`MONDAYS: <description>`** - Intended for Monday validation runs
- **`TUESDAYS: <description>`** - Intended for Tuesday validation runs
- **`WEDNESDAYS: <description>`** - Intended for Wednesday validation runs
- **`THURSDAYS: <description>`** - Intended for Thursday validation runs
- **`FRIDAYS: <description>`** - Intended for Friday validation runs
- **`SATURDAYS: <description>`** - Intended for Saturday validation runs
- **`SUNDAYS: <description>`** - Intended for Sunday validation runs

**Note:** The workflow checks for trigger issues every hour. The day/frequency names are semantic hints for organization, but all periodic scans are checked on the same schedule.

## Creating a Trigger Issue

### Step 1: Create a New Issue

1. Go to the **Issues** tab in the repository
2. Click **New Issue**
3. Enter a title with one of the supported prefixes
4. Add optional description explaining the validation request

### Example Titles

```
SCAN: Validate URL
SCAN: Emergency URL check after domain migration
QUARTERLY: Validate URL
MONTHLY: Regular maintenance scan
WEEKLY: Validate URL
MONDAYS: Start-of-week validation
```

### Step 2: Wait for Execution

- The workflow runs every hour on the hour
- Check the **Actions** tab to see the workflow run
- Results will be posted as a comment to your issue

### Step 3: Review Results

The system will post a detailed report including:
- Summary statistics (total URLs, valid, invalid, etc.)
- Per-country breakdown
- Validation timestamp
- Links to download full results

## Validation Report Format

The automated report includes:

```markdown
## URL Validation Report

**Trigger:** SCAN: (one-time) or QUARTERLY: (quarterly)
**Completed:** 2026-02-27 15:30:00 UTC
**Countries Processed:** 40

### Summary

| Metric | Count |
|--------|-------|
| Total URLs | 80,423 |
| Validated | 78,650 |
| Valid | 76,230 (96.9%) |
| Invalid | 2,420 (3.1%) |
| Redirected | 1,850 |
| Removed (failed 2x) | 350 |

### Country Details

| Country | Total | Valid | Invalid | Redirected | Removed |
|---------|-------|-------|---------|------------|---------|
| AUSTRIA | 2,450 | 2,380 | 70 | 45 | 8 |
...
```

## Managing Trigger Issues

### Closing a Periodic Issue

If you want to stop a periodic validation:
1. Manually close the issue
2. The system will skip closed issues

### Reopening for Another Run

To trigger another one-time scan:
1. Create a new issue with `SCAN:` prefix
2. Or reopen a closed issue (it will run once more)

### Checking Status

- View the **Actions** tab to see workflow runs
- Check issue comments for validation reports
- Download artifacts from workflow runs for detailed data

## Workflow Details

**Workflow File:** `.github/workflows/issue-triggered-validation.yml`

**Schedule:** Runs every hour (`0 * * * *` cron)

**Permissions Required:**
- `contents: write` - Download/upload artifacts
- `issues: write` - Post comments and close issues

**Timeout:** 110 minutes (same as batch validation)

**Artifacts:**
- Validation metadata database is automatically saved
- 90-day retention period
- Shared across all validation workflows

## Best Practices

1. **Use Clear Descriptions**: Add context in the issue title after the prefix
   - Good: `SCAN: Validate URL after security updates`
   - Okay: `SCAN: Validate URL`

2. **One Active Scan per Type**: Avoid creating multiple open issues with the same prefix to prevent duplicate runs

3. **Monitor Progress**: Check the Actions tab during long validations

4. **Review Reports**: Check the validation report for errors and failures

5. **Close When Done**: For one-time scans, the issue closes automatically. For periodic scans, close manually when no longer needed.

## Troubleshooting

**Issue not triggering validation:**
- Ensure the title starts with an exact prefix (case-insensitive, but must match exactly)
- Check that the issue is open (closed issues are skipped)
- Wait for the next hourly workflow run
- Check the Actions tab for errors

**Validation timing out:**
- The system has the same 110-minute timeout as batch validation
- For very large validations, consider using the batch workflow instead
- Check workflow logs for timeout messages

**Report not posted:**
- Check workflow logs for errors
- Ensure GitHub token has issues:write permission
- Verify the issue is still open when validation completes

## Related Documentation

- [Batch Validation System](batched-validation.md) - For scheduled, chunked validation
- [URL Validation Scanner](url-validation-scanner.md) - For manual validation
- [GitHub Actions Validation](github-action-validation.md) - For UI-based validation

## Technical Details

**Implementation:**
- CLI: `src/cli/issue_triggered_validation.py`
- Handler: `src/services/issue_trigger_handler.py`
- Workflow: `.github/workflows/issue-triggered-validation.yml`

**Data Storage:**
- Uses same metadata database as other validation workflows
- Stored in GitHub Actions artifacts
- 90-day retention
- Not committed to repository
