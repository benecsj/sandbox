### oAWToRst (oaw_to_rst.py)

Generates reStructuredText documentation for oAW tests from `.tsc` sources.

#### Requirements
- Python 3.10+

#### Configuration
`config.json` (by default next to `oaw_to_rst.py`; or specify via `--config`):
```
{
  "component": "Crypto",
  "test_path": "./test/tests",
  "spec_path": "./test/spec"
}
```
- `test_path` and `spec_path` may be absolute or relative to `config.json`.
- CLI can override any of the above.
- You can point to an alternate config file using `--config <path>` (absolute
  or relative to the script directory).

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
6. Finds `<component>_component_test.rst` in `spec_path`.
7. Deletes previously generated `<Component>_oAW_*.rst` in the same directory.
8. Removes lines starting with `<Component>_oAW_` from the TOC file, then appends new group links.
9. Parses `.tsc` headers for Description, Input, Output, Requirements.
10. Generates one group RST per group with `.. sw_test::` and per-file `.. sw_test_step::` blocks. `.. sw_test_step::` uses file names without extension.

Formatting specifics:
- Tags are comma-separated and wrapped at 120 characters
  - Group header continuation indent: 11 spaces
  - Per-file `:tests:` continuation indent: 14 spaces
- Multi-line Description/Input/Output values align continuation lines under the value start
- Placeholder header (all four headers present but empty) generates TODO lines referencing the `.tsc` filename for all fields

Group name normalization for filenames and titles:
- `Generate`→`Generator`, `Compile`→`Compiler`, `Validate`→`Validator`.

#### Demo Data
Sample files are provided under `test/` and a ready config is included. A test harness `run_test.py` validates generated output structure and formatting.

