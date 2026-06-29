# /commit-message

Generate a focused, conventional commit message for the current staged (or all) changes, then create the commit.

## Steps

1. **Inspect the diff**:
   ```
   git diff --staged
   ```
   If nothing is staged, fall back to:
   ```
   git diff HEAD
   ```

2. **Analyse the changes**:
   - What is the intent? (new feature, bug fix, refactor, style, docs, chore, test)
   - What is the scope? (which module, component, or area changed)
   - Are there any breaking changes?

3. **Draft the commit message** following Conventional Commits:
   ```
   <type>(<scope>): <short imperative summary>

   <optional body — only if the why isn't obvious from the title>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```

   Type options: `feat`, `fix`, `refactor`, `style`, `test`, `docs`, `chore`, `perf`, `ci`

   Rules:
   - Title ≤ 72 characters, imperative mood ("add", "fix", "remove" — not "added" or "adds")
   - No period at the end of the title
   - Body only when the title can't capture the why (e.g. a non-obvious constraint, a workaround)
   - Never mention file names in the title — the diff already shows them

4. **Show the message** to the user and ask: "Commit with this message? (yes / edit)"

5. **On approval**, run:
   ```
   git add -p   # if nothing staged yet
   git commit -m "<message>"
   ```

## Example output

```
feat(students): add enrol modal with Django API integration

Wires up the create-student form to POST /api/students, which proxies
to the Django backend with the HttpOnly JWT cookie — browser never
touches Django directly.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
