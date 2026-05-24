# Update Docs and Commit

Review the most recent code changes on the current branch and update the project documentation to reflect them, then commit everything together.

## Steps

1. **Identify what changed**
   Run `git diff main...HEAD --name-only` to list all files changed on this branch vs main.
   Run `git log main...HEAD --oneline` to read the commit history.

2. **Decide which docs need updating**
   Cross-reference the changed files against these docs:

   | Doc                       | Update when…                                                                                  |
   | ------------------------- | --------------------------------------------------------------------------------------------- |
   | `docs/architecture.md`    | New layers, route patterns, auth flow, middleware changes, new lib modules, API proxy changes |
   | `docs/project_spec.md`    | New user-facing features, new roles, new modules, changed functional requirements             |
   | `docs/frontend-tester.md` | New testing patterns, new provider wrappers, changed test conventions                         |

   If a change is purely internal (bug fix, style tweak, refactor with no behaviour change) and no doc section is factually wrong after it, skip that doc.

3. **Read before writing**
   Read the full content of each doc you plan to update before editing. Never overwrite a section without reading it first.

4. **Make targeted edits**
   - Add new sections or update existing ones.
   - Preserve the existing tone, heading style, and table format.
   - Do not remove content that is still accurate.
   - Do not rewrite sections that are not affected by the recent changes.

5. **Verify docs are consistent with each other**
   After editing, check that `architecture.md` and `project_spec.md` do not contradict each other on shared topics (roles, API paths, auth model).

6. **Stage and commit**
   Stage the updated doc files alongside any still-unstaged code changes, then commit with a message in the form:

   ```
   DOCS: update [doc names] to reflect [brief description of what changed]
   ```

   Example: `DOCS: update architecture.md to reflect new /api/reports route handler`

   Run `npm run lint` before committing. If lint fails, fix the errors first.

> **Scope guard:** Only touch files under `docs/`. Do not refactor code, rename files, or make any non-documentation changes as part of this command.
