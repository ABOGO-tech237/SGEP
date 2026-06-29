# /test

Run the Vitest test suite, diagnose every failure, and fix the broken tests or the code under test — whichever is wrong.

## Steps

1. **Run tests** from `frontend/`:
   ```
   npm test -- --run
   ```

2. **If all tests pass**, report "All tests passed." and stop.

3. **If tests fail**:
   a. Read the full failure output carefully.
   b. For each failing test:
      - Read the test file and the file it's testing.
      - Decide whether the **test** is wrong (bad expectation, stale snapshot, wrong mock) or the **implementation** is wrong (genuine bug, missing case).
      - Apply the correct fix — never delete a test or change an assertion just to make it green if the implementation is at fault.
   c. Re-run `npm test -- --run` after fixes.
   d. Repeat until the suite is fully green.

4. **Report** a summary: which tests failed, root cause for each, and what was changed.

## Rules
- Fix the source of truth, not the symptom. If the implementation is broken, fix the implementation.
- Don't mock away real behaviour just to silence a test.
- If a test itself is genuinely wrong (e.g. tests a removed feature), remove or update it with a comment explaining why.
- Run with `--run` (non-watch) so the command exits cleanly.
