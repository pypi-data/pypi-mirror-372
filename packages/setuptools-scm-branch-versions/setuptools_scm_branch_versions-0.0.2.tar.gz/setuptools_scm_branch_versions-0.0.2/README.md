# setuptools-scm-branch-versions

## Use

### With setuptools

In `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61", "setuptools-scm", "setuptools-scm-branch-versions"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
version_scheme = "branch-versions"
```

### With hatch/hatchling

In `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs", "setuptools-scm-branch-versions"]
build-backend = "hatchling.build"

[tool.hatch.version.raw-options]
version_scheme = "branch-versions"
```
