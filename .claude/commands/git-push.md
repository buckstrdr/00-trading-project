# Push All Changes to GitHub

Execute the following git workflow to commit and push all changes:

1. **Check Status:**
   - Run `git status` to see all changes
   - If no changes, inform user and stop

2. **Stage All Changes:**
   - Run `git add -A` to stage all files (new, modified, and deleted)

3. **Generate Commit Message:**
   - Run `git diff --cached --stat` to see what's being committed
   - Create a descriptive commit message based on the changes:
     - If multiple files: "Update multiple files"
     - If single file: "Update [filename]"
     - If new files added: "Add new files"
     - If files deleted: "Remove unnecessary files"
   - Include a brief summary of key changes

4. **Commit Changes:**
   - Run `git commit -m "[generated message]"`
   - If commit fails, show the error and how to fix it

5. **Push to GitHub:**
   - Run `git push origin main` (or current branch)
   - If push fails due to remote changes, run `git pull --rebase origin main` first
   - Then retry the push
   - Show success message with link to repository if possible

6. **Confirm Success:**
   - Run `git log --oneline -1` to show the latest commit
   - Inform user that all changes have been pushed to GitHub

Handle common issues:
- If not a git repository, offer to initialize one
- If no remote set up, help configure GitHub remote
- If authentication needed, guide through GitHub token setup