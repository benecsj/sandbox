### oAWToRst — Implementation Plan

- [x] Write `specification.md` describing oAW to RST tool behavior
- [x] Scaffold project: `oaw_to_rst.py`, `config.json`, `test/` data
- [x] Implement config loading and CLI overrides (`--component`, `--test_path`, `--spec_path`)
- [x] Normalize paths to absolute (relative to `config.json` directory)
- [x] Validate `test_path` and `spec_path` existence
- [x] Discover `.tsc` files for `<Component>_*.tsc` under `test_path`; build `tsc_files`
- [x] Group files by second token -> `tsc_file_groups`
- [x] Locate `<component>_component_test.rst` in `spec_path`; set `toc_rst_path`
- [x] Clean previous generated files `<Component>_oAW_*.rst` next to TOC
- [x] Remove lines starting with `<Component>_oAW_` from TOC RST
- [x] Implement `convert_group_name()` mapping Generate→Generator, Compile→Compiler, Validate→Validator
- [x] Append group links to TOC for each group using converted names
- [x] Parse `.tsc` headers (Description, Input, Output, Requirements)
- [x] Validate header structure; dedupe and normalize tags
- [x] Generate group RST files per template with ID sequencing and tag wrapping
- [x] Add sample data under `test/` and demo config
- [x] Expand sample test data with multiple `.tsc` per group
- [x] Ensure deterministic ordering (sorted files, groups, per-file tags, aggregated tags)
- [x] Iteratively test and refine
- [x] Write `README.md` with usage instructions
- [ ] Final verification: run end-to-end and review generated RST for formatting/wrapping

