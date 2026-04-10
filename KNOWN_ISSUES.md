# Known Issues

## Current Limitations

### Self-Healing
- Healer creates `.healer.bak` backup files — clean these up after verifying fixes
- AttributeError fix uses Levenshtein distance with 0.8 cutoff — may suggest incorrect matches
- AssertionError fix only handles `==` comparisons, not `!=`, `>`, `<`, `in`, etc.
- TypeError fix only adds `None` as dummy argument — may not work for typed parameters

### Migration
- `migrate` command handles basic assertions only (`assertEqual`, `assertTrue`, `assertFalse`)
- Complex unittest patterns (e.g., `assertRaises`, `assertDictEqual`) need manual migration
- Always use `--backup` flag before migration

### Coverage
- Coverage audit requires `pytest-cov` installed in environment
- Reports only show total percentage, not per-file breakdown

### Infrastructure
- `cancel_job` MCP tool is not yet implemented
- Shell adapter and coverage auditor now use `create_subprocess_exec` (safe from shell injection)

## Resolved Issues

- ✅ Migration tool now produces valid Python (regex-based transformation)
- ✅ Self-healing creates backups before file modifications
- ✅ Shell injection vulnerability fixed (subprocess_exec)
- ✅ Missing `__init__.py` in autogenerate module added
- ✅ SKILL.md synchronized with actual code
- ✅ CI/CD pipeline added
- ✅ File system path validation added
- ✅ README placeholder values fixed
