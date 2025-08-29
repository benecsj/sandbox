### oAWToRst — Implementation Plan

- [ ] Write `specification.md` describing oAW to RST tool behavior
- [ ] Scaffold project: `oaw_to_rst.py`, `config.json`, `test/` data
- [ ] Implement config loading and CLI overrides (`--component`, `--test_path`, `--spec_path`)
- [ ] Normalize paths to absolute (relative to `config.json` directory)
- [ ] Validate `test_path` and `spec_path` existence
- [ ] Discover `.tsc` files for `<Component>_*.tsc` under `test_path`; build `tsc_files`
- [ ] Group files by second token -> `tsc_file_groups`
- [ ] Locate `<component>_component_test.rst` in `spec_path`; set `toc_rst_path`
- [ ] Clean previous generated files `<Component>_oAW_*.rst` next to TOC
- [ ] Remove lines starting with `<Component>_oAW_` from TOC RST
- [ ] Implement `convert_group_name()` mapping Generate→Generator, Compile→Compiler, Validate→Validator
- [ ] Append group links to TOC for each group using converted names
- [ ] Parse `.tsc` headers (Description, Input, Output, Requirements)
- [ ] Validate header structure; dedupe and normalize tags
- [ ] Generate group RST files per template with ID sequencing and tag wrapping
- [ ] Add sample data under `test/` and demo config
- [ ] Iteratively test and refine
- [ ] Write `README.md` with usage instructions

