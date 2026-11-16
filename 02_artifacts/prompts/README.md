# Prompts

Prompt files for LLM calls. Each prompt lives in its own folder, versioned with semver.

## Folder structure

```
prompts/
├── <prompt_name>/
│   ├── v<MAJOR>.<MINOR>.<PATCH>.md   ← prompt content
│   └── CHANGELOG.md                  ← version history
└── README.md                         ← this file
```

## Naming conventions

| Element | Rule | Example |
|---|---|---|
| Folder name | `snake_case`, matches the use-case | `search_sheets` |
| Version file | `v<semver>.md` | `v1.0.0.md` |
| Latest symlink | Not used — always load by explicit version | — |

## Versioning rules

- **PATCH** (`v1.0.1`): Typo fixes, rephrasing that does not change behaviour.
- **MINOR** (`v1.1.0`): New instructions added, behaviour extended but backwards compatible.
- **MAJOR** (`v2.0.0`): Breaking change — output format, language or role changes.

## Loading in code

```python
from common.prompts.loader import load_prompt

text, version, hash_ = load_prompt("search_sheets", "v1.0.0")
# Pass version and hash_ to LlmRun for full traceability
```

## Updating a prompt

1. Create the new version file: `cp v1.0.0.md v1.1.0.md`
2. Edit the new file.
3. Update `CHANGELOG.md`.
4. Update the version string in the calling service.
5. Commit — the diff is human-readable.

> **Do not edit existing version files.** They are the historical record.
