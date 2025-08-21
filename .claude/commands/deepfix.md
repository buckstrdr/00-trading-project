---
name: deepfix
description: Complete bug fix workflow with historical context
arguments: bug_description
---

# Deep Fix

I'll help you fix the bug: $ARGUMENTS

First, let's check history:
@sub-agent dr-elizabeth-chen-historical-archivist Has anyone tried to fix "$ARGUMENTS" before? What worked or failed?

Now deploying the fix team:
@sub-agent team:fix Fix: $ARGUMENTS

Cleaning up debug artifacts:
/cleanproject

Running tests to verify fix:
/test

Creating a smart commit:
/commit

Documenting the fix:
@sub-agent documentation-specialist Document the fix for "$ARGUMENTS" and what solution worked

Bug fix complete with full documentation!