# /lint

Run ESLint across the frontend, diagnose every failure, and fix all auto-fixable issues. For issues that can't be auto-fixed, explain each one and apply manual fixes.

## Steps

1. **Run lint** from `frontend/`:
   ```
   npm run lint
   ```

2. **If there are no errors**, report "Lint passed — no issues found." and stop.

3. **If there are errors**:
   a. Run `npm run lint -- --fix` to auto-fix everything ESLint can handle.
   b. Re-run `npm run lint` to see what's left.
   c. For each remaining error, read the relevant file, understand the issue, and apply a manual fix.
   d. After all manual fixes, run `npm run lint` one final time to confirm zero errors.

4. **Report** a summary: how many issues were auto-fixed, how many were manually fixed, and what they were.

## Rules
- Never use `// eslint-disable` comments to suppress errors — fix the root cause.
- If a fix would change runtime behaviour, explain the trade-off before applying it.
- Work in the `frontend/` subdirectory unless the error path clearly points elsewhere.
