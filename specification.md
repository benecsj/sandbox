### oAWToRst (oaw_to_rst.py) — Software Specification

#### 1. Purpose and Scope
The `oaw_to_rst.py` tool automates the generation and maintenance of reStructuredText (RST) documentation for oAW tests. It:
- Reads test specifications from oAW `.tsc` files under a configured test directory.
- Updates a component table-of-contents RST file.
- Generates per-group oAW test specification RST files derived from structured headers embedded in `.tsc` files.

This document defines functional and non-functional requirements, configuration, I/O, processing logic, error handling, and acceptance criteria.

#### 2. Definitions
- **Component**: High-level module name (e.g., `Crypto`).
- **.tsc file**: oAW test script. Naming convention: `<Component>_<Group>_<TestName...>.tsc`.
- **Group**: Single-word token in filename indicating test grouping (e.g., `Generate`, `Compile`, `Validate`).
- **TOC RST**: `<component>_component_test.rst` table-of-contents file for the component’s tests.
- **Group RST**: Generated files named `<Component>_oAW_<group_name_converted>_Tests.rst` placed next to the TOC RST file.
- **group_name_converted**: Mapping of group to display variant: `Generate`→`Generator`, `Compile`→`Compiler`, `Validate`→`Validator`; otherwise unchanged.

#### 3. Inputs
- `config.json` (located next to `oaw_to_rst.py`):
  - `component` (string, required): Component name (case-sensitive; used as filename prefix filter)
  - `test_path` (string, required): Path to test sources (absolute or relative to `config.json` directory)
  - `spec_path` (string, required): Path to documentation (absolute or relative to `config.json` directory)

- CLI overrides (optional):
  - `--component <name>`
  - `--test_path <path>`
  - `--spec_path <path>`

Precedence: CLI overrides > values in `config.json`.

#### 4. Outputs
- Updated TOC RST file: `<component>_component_test.rst` with refreshed links to generated group RST files.
- Generated/overwritten group RST files: `<Component>_oAW_<group_name_converted>_Tests.rst` for each discovered group.
- Console logs describing actions, found files, and errors.

#### 5. High-Level Flow
1) Load configuration from `config.json` and apply CLI overrides.
2) Normalize paths: convert relative `test_path` and `spec_path` to absolute using the directory of `config.json`; keep absolute paths unchanged.
3) Validate paths: ensure `test_path` and `spec_path` exist; on failure, log error and exit with non-zero status.
4) Discover `.tsc` files under `test_path` whose basenames start with `<Component>_`. Log absolute paths of all matches.
   - If no `.tsc` files are found: log "No oAW tests found for <Component>." and exit successfully (no changes).
5) Group discovered files into `tsc_file_groups` as `{ GroupName: [absolute_file_paths...] }` where `GroupName` is the second underscore-separated token of the filename.
6) Locate TOC RST file `<component>_component_test.rst` under `spec_path` (non-recursive search of root; optionally allow recursive search — see 9.4). If not found, log `ERROR <component>_component_test.rst not found in <spec_path>` and exit with non-zero status.
7) In the TOC RST directory:
   - Delete any files starting with `<Component>_oAW_` and ending with `.rst` (exclude the TOC file itself).
   - Open the TOC RST and remove any line starting with `<Component>_oAW_`.
   - Append/insert link entries (one per group) for newly generated group RST files.
8) Parse headers of each `.tsc` file to extract `Description`, `Input`, `Output`, and `Requirements` (list of tags). On parse error or missing fields, log error and exit with non-zero status.
9) For each group, generate a single Group RST containing:
   - A section header.
   - A `.. sw_test::` block with aggregated unique tags across the group.
   - For each `.tsc` in the group, two `.. sw_test_step::` blocks (name and step `1`) populated with parsed fields and per-file tags.
   - IDs incrementing from `0001` across the entire group file (two IDs per test file, in order).

#### 6. Detailed Functional Requirements

6.1 Configuration Handling
- Read `config.json` located in the same directory as `oaw_to_rst.py`.
- Apply CLI overrides for `component`, `test_path`, and `spec_path` if provided.
- After merging, convert `test_path` and `spec_path` to absolute paths if they are relative. The base for resolution is the directory of `config.json`.
- Keep absolute paths unchanged. Store the normalized absolute paths back into the in-memory config object for subsequent steps.

6.2 Validation
- Verify `test_path` exists and is a directory.
- Verify `spec_path` exists and is a directory.
- If either check fails, log a clear error and exit with code `1`.

6.3 Discovery of `.tsc` Files
- Search recursively under `test_path` for files matching glob `**/*.tsc` whose basenames start with `<Component>_` (case-sensitive).
- Log the absolute path of each discovered file.
- Store all matching paths in `tsc_files` (list of absolute paths).
- If `tsc_files` is empty: log `No oAW tests found for <Component>.` and exit with code `0`.

6.4 Grouping Logic (`tsc_file_groups`)
- For each entry in `tsc_files`:
  - Extract filename without extension and split by underscore `_`.
  - Validate there are at least 3 parts: `<Component>_<Group>_<TestName...>`.
  - The second token is the `Group` name; it must be a single word (no underscores). If invalid, log error and exit.
- Build dictionary: `{ Group: [list of absolute paths sorted by filename] }`.
- Sort groups by `Group` name for deterministic output.

6.5 Group Name Conversion
- Define function `convert_group_name(group: str) -> str` mapping using case-insensitive comparison:
  - `Generate` → `Generator`
  - `Compile` → `Compiler`
  - `Validate` → `Validator`
  - Otherwise, return the original `group` unchanged.

6.6 Locating the TOC RST
- Expected filename: `<component>_component_test.rst` (note lowercase component in filename is acceptable only if the repository convention dictates; default is as provided, case-sensitive). The search will look within `spec_path` directory. If multiple matches exist (when searching recursively), prefer the one at the root of `spec_path`.
- On failure: log `ERROR <component>_component_test.rst not found in <spec_path>` and exit with code `1`.

6.7 Cleaning Prior Generated Files
- In the directory of the TOC RST (`toc_dir`):
  - Delete any file with pattern `^<Component>_oAW_.*\.rst$`.
  - Ensure the TOC RST itself is not deleted.
- Open the TOC RST and remove any entire line that starts with `<Component>_oAW_` (anchored at line start, plain text match).
- Save the modified TOC RST in-place.

6.8 Updating TOC with New Links
- For each group in sorted order:
  - Compute `group_name_converted = convert_group_name(Group)`.
  - Compute link filename: `<Component>_oAW_<group_name_converted>_Tests.rst`.
  - Append a line with exactly that filename to the TOC RST. Placement: after existing content; if a toctree directive exists, preferred placement is inside the first toctree; otherwise, append at end of file.
- The TOC update should be idempotent due to prior cleanup.

6.9 Parsing `.tsc` Headers
- The header starts at the beginning of the `.tsc` file and consists of lines prefixed by `// ` in the following structure:
  - `// Description`
  - one or more lines of free text (each starting with `//`)
  - `// Input`
  - one or more lines of free text (each starting with `//`)
  - `// Output`
  - one or more lines of free text (each starting with `//`)
  - `// Requirements`
  - one or more lines of tags separated by commas and/or whitespace (each starting with `//`)
  - a required empty line after the header block (blank or not starting with `//`).
- Parsing rules:
  - Accept `//` followed by optional single space before content.
  - Section headers are matched case-insensitively: `Description`, `Input`, `Output`, `Requirements`.
  - Accumulate multi-line text for `Description`, `Input`, `Output` preserving paragraph line breaks.
  - For `Requirements`, combine all lines, replace commas with spaces, split on whitespace, trim each token, drop empties, deduplicate preserving first occurrence.
  - Stop parsing at the first empty or non-comment line following the `Requirements` content.
- Validation rules:
  - All four sections must be present and non-empty.
  - `Requirements` must result in at least one tag.
  - On violation: log an error indicating file and missing/invalid section; exit with code `1`.

6.10 Generating Group RST Files
- For each group (sorted by name):
  - Output path: `<toc_dir>/<Component>_oAW_<group_name_converted>_Tests.rst`.
  - Structure and content:

```
<group_name_converted> Test Specification - oAW tests
========================================================================================================================

<Component>_oAW_<group_name_converted>_Tests
--------------------------------------------------

.. sw_test:: <Component>_oAW_<group_name_converted>_Tests
   :id: TS_<Component>_oAW_<group_name_converted>_Tests
   :tst_shortdescription: Tests for successful <Group> of <Component>
   :tst_level: Component Requirement Test
   :tst_designdoc: <Component>_VerificationDocumentation.docx
   :tst_envconditions: oAW on PC
   :tst_method: Interface tests/API tests
   :tst_preparation: nothing specific
   :tst_type: Manual
   :tst_env: Generator-Test
   :tests: <space-separated unique tags across all tests in this group; wrap at 120 chars, continuation lines indented 11 spaces>

   See descriptions below

   .. sw_test_step:: <Name of the .tsc file>
      :id: TSS_<Component>_oAW_<group_name_converted>_Tests_<0001+>
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_<Component>_oAW_<group_name_converted>_Tests_<0002+>
      :collapse: true
      :tests: <space-separated tags for this .tsc file; wrap as above>
      
      Description: <Description text of the .tsc file>
      
      Input: <Input text of the .tsc file>

      Output: <Output text of the .tsc file>
```

  - For each additional `.tsc` file in the group, repeat the two `.. sw_test_step::` blocks and continue incrementing the 4-digit IDs globally within this group file (i.e., two IDs per file).
  - Line wrapping of long `:tests:` lines: wrap at 120 characters; continuation lines must be indented with exactly 11 spaces.
  - All content is overwritten on each run (freshly generated after cleanup).

6.11 Ordering and Determinism
- Sort groups alphabetically by `Group`.
- Within each group, sort tests by filename (natural/lexicographic) to ensure stable output.
- Aggregate tags in group header in deterministic order: by appearance order across sorted tests, deduplicated.

6.12 Logging and Exit Codes
- INFO: configuration summary, resolved absolute paths, number of files discovered, each file path, TOC path, generated files.
- WARNING: none anticipated.
- ERROR: configuration/validation failures, parse errors, missing TOC RST, grouping errors.
- Exit codes: `0` success (including no tests case), `1` on error.

#### 7. CLI and Usage Examples
- Basic:
  - `python oaw_to_rst.py` (uses `config.json` only)
  - `python oaw_to_rst.py --component Crypto`
  - `python oaw_to_rst.py --component Crypto --test_path "../tests" --spec_path "../docs"`

#### 8. File System Conventions
- `config.json` must be adjacent to `oaw_to_rst.py`.
- `spec_path` contains `<component>_component_test.rst` at its root; generated group RST files are created in the same directory.
- `test_path` contains the `.tsc` files recursively.

#### 9. Non-Functional Requirements
9.1 Reliability
- Fail fast on configuration or parsing errors with clear messages.
- All file writes are atomic where feasible (write to temp then replace) to avoid partial writes.

9.2 Performance
- Handle thousands of `.tsc` files; operations are I/O bound; use efficient directory traversal.

9.3 Portability
- Python 3.10+; standard library only (no external dependencies required).
- Paths handled using platform-native separators; globbing is case-sensitive by default.

9.4 Extensibility
- Conversion mapping is isolated in a function; can extend with additional groups.
- Parsing is section-based; adding new sections should not break existing behavior.

9.5 Idempotence and Safety
- Prior cleanup guarantees idempotent TOC entries.
- Group RST files are regenerated from source of truth (`.tsc` headers) each run.

#### 10. Error Messages (Representative)
- `ERROR config.json not found next to oaw_to_rst.py`
- `ERROR Invalid or missing 'component' in configuration`
- `ERROR 'test_path' does not exist: <path>`
- `ERROR 'spec_path' does not exist: <path>`
- `ERROR <component>_component_test.rst not found in <spec_path>`
- `ERROR No valid group token in filename: <file>`
- `ERROR Missing <Section> in header: <file>`

#### 11. Test Data and Demo Setup
- Create `test/` directory next to `oaw_to_rst.py` containing:
  - `tests/` tree with sample `.tsc` files named `Crypto_Generate_XYZ.tsc`, `Crypto_Compile_ABC.tsc`, etc., each with a conforming header.
  - `spec/` tree containing a sample `Crypto_component_test.rst` TOC file.
  - A `config.json` pointing `test_path` to `./test/tests` and `spec_path` to `./test/spec` and `component` to `Crypto`.

#### 12. Acceptance Criteria
- Paths are normalized to absolute (relative inputs become absolute based on `config.json` location; absolute inputs remain unchanged).
- Validation errors cause exit code `1` with clear messages.
- When no `.tsc` files are found for the component, the tool logs the informational message and exits with code `0` without modifying TOC.
- TOC RST is updated: old `<Component>_oAW_*.rst` lines removed; new group filenames appended; corresponding files are (re)generated.
- Group RST files are produced with correct filenames, sections, aggregated unique tags, and correctly incremented 4-digit IDs across all `.. sw_test_step::` blocks.
- Requirements tags are deduplicated and correctly wrapped at 120 characters with exactly 11-space indentation on continuation lines.

#### 13. Risks and Edge Cases
- Filenames not matching the convention: tool errors out with a helpful message.
- Missing or malformed header sections: tool errors out and does not produce partial outputs.
- Multiple TOC files: tool selects the one in `spec_path` root by default.
- Case sensitivity in component match: enforced as provided; mismatches will result in no files found.

#### 14. Implementation Notes
- Use `argparse` for CLI; `json` for config; `pathlib` for paths; `glob`/`rglob` for discovery; `re` for parsing; `textwrap` for wrapping.
- Ensure deterministic ordering and stable output to facilitate reviews and diffs.

