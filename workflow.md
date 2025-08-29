### oAWToRst Development Workflow

#### 1. Analyze
- Clarify the change: bug, feature, or refactor
- Identify impacted behavior (config, parsing, grouping, generation, logging)
- Check existing tests and docs for expectations

#### 2. Plan
- Define acceptance criteria (inputs, outputs, logs, edge cases)
- Decide code touch-points (functions/files) and test coverage
- Update `todo.md` with atomic tasks

#### 3. Create/Update Tests First
- Add/extend `.tsc` samples in `test/tests/` to exercise the change (valid, invalid, edge)
- If TOC or RST structure changes, reflect expectations in `run_test.py`
- For error/warning behavior, assert presence of formatted messages

#### 4. Implement Incrementally
- Make small edits; keep code readable and deterministic
- Prefer pure helpers (parsers/formatters); reuse utilities
- Maintain cross-platform path handling and sorted outputs

#### 5. Run and Iterate
- Run generator: `python oaw_to_rst.py`
- Run tests: `python run_test.py` (or VS Code tasks)
- Fix failures; repeat until green

#### 6. Verify Manually (Spot Checks)
- Inspect updated RST under `test/spec/`
- Confirm tag wrapping, continuation indents (11/14), trailing commas, and multiline value alignment
- Ensure warnings/errors follow the problem matcher format

#### 7. Update Documentation
- `README.md`: usage/behavior changes
- `specification.md`: requirements and behavior details
- `workflow.md`: update process if it evolves
- `todo.md`: check off completed items

#### 8. Commit and Pull Request
- Commit with meaningful message referencing issue/feature
- Ensure CI/lint/tests pass if configured
- In PR, summarize change, testing, and impact

#### Notes
- Keep generation idempotent; never partially write on failure
- Parse-and-validate before any file deletions/modifications
- Prefer stable ordering for reproducible diffs