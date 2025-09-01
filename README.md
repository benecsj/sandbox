### oAWToRst (oaw_to_rst.py)

Generates reStructuredText documentation for oAW tests from `.tsc` sources.

#### Requirements
- Python 3.10+
- Jinja2 (see `requirements.txt`)
  - If Jinja2 is missing, the generator will auto-install it to the user site
    at runtime (with a safe fallback when system packaging constraints apply).

#### Configuration
`config/config.json` (by default; or specify via `--config`):
```
{
  "component": "Crypto",
  "test_path": "./test/tests",
  "spec_path": "./test/spec",
  "group_name_mappings": {
    "Generate": "Generator",
    "Compile": "Compiler",
    "Validate": "Validator"
  }
}
```
- `test_path` and `spec_path` may be absolute or relative to `config.json`.
- CLI can override all except `group_name_mappings` (config-only, mandatory).
- You can point to an alternate config file using `--config <path>` (absolute
  or relative to the script directory). Default is `./config/config.json`.

#### Usage
- Using config only:
```
python3 oaw_to_rst.py
```
- Using an alternate config file:
```
python3 oaw_to_rst.py --config ../my_config.json
```
- With overrides:
```
python3 oaw_to_rst.py --component Crypto --test_path ../tests --spec_path ../docs
```

#### Behavior
1. Loads config and applies CLI overrides.
2. Converts relative paths to absolute (relative to `config.json`).
3. Validates that `test_path` and `spec_path` exist.
4. Recursively finds `.tsc` files under `test_path` starting with `<Component>_`.
   - If none found: logs and exits without changes.
5. Groups tests by the second token in filename `<Component>_<Group>_...`.
6. Finds `<component>_component_test.rst` in `spec_path` (now searched recursively; if multiple, prefers the one at the root of `spec_path`, otherwise the shallowest path).
7. Deletes previously generated `<Component>_oAW_*.rst` in the same directory.
8. Removes lines starting with `<Component>_oAW_` from the TOC file, then appends new group links.
9. Parses `.tsc` headers for DESCRIPTION, INPUT, OUTPUT, REQUIREMENTS.
10. Generates one group RST per group with `.. sw_test::` and per-file `.. sw_test_step::` blocks. `.. sw_test_step::` uses file names without extension.
11. When all headers are invalid/missing, oaw to rst action is skipped (for legacy components)

Formatting specifics:
- Tags are comma-separated and wrapped at 120 characters
  - Group header continuation indent: 11 spaces
  - Per-file `:tests:` continuation indent: 14 spaces
- Multi-line Description/Input/Output values align continuation lines under the value start
- Placeholder header (all four headers present but empty) generates TODO lines referencing the `.tsc` filename for all fields

Group name normalization for filenames and titles:
- `Generate`→`Generator`, `Compile`→`Compiler`, `Validate`→`Validator`.

#### Test file (.tsc) header format
This script expect a specific header to be present in all .tsc header files with uppercase attribute keys.
  - `// DESCRIPTION`
  - one or more lines of free text (each starting with `//`)
  - `// INPUT`
  - one or more lines of free text (each starting with `//`)
  - `// OUTPUT`
  - one or more lines of free text (each starting with `//`)
  - `// REQUIREMENTS`
  - one or more lines of tags separated by commas and/or whitespace (each starting with `//`)
  - a required empty line after the header block (blank or not starting with `//`).

*Important: Always leave an empty line after the last tags line**

<pre>
// DESCRIPTION
// Some description about the test
// Even more lines can be here
// INPUT
// Some description/summary about the configuration
// Even more lines can be here
// OUTPUT
// Some description/summary of the expected output
// Even more lines can be here
// REQUIREMENTS
// TAG_1, TAG2, TAG3,
// TAG_4

 </pre>

#### Demo Data
Sample files are provided under `test/` and a ready config is included. A test harness `run_test.py` validates generated output structure and formatting.

#### Status banners
- Successful run (green):
  - "OAW TO RST WAS SUCCESSFUL"
- Completed with warnings (yellow):
  - "OAW TO RST FINISHED WITH WARNINGS"
- Failed due to errors (red):
  - "OAW TO RST FAILED"
- Skipped run (yellow):
  - "OAW TO RST SKIPPED" (occurs when all discovered `.tsc` files have invalid/missing headers, see skip behavior above)
