<!-- ITO:START -->

# Ito Instructions

These instructions are for AI assistants working in this project.

Always open `@/.ito/AGENTS.md` when the request:

- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/.ito/AGENTS.md` to learn:

- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Note: Files under `.ito/`, `.opencode/`, `.github/`, and `.codex/` are installed/updated by Ito (`ito init`, `ito update`) and may be overwritten.
Add project-specific guidance in `.ito/user-prompts/guidance.md` (shared), `.ito/user-prompts/<artifact>.md` (artifact-specific), and/or below this managed block.

Keep this managed block so 'ito update' can refresh the instructions.

## Path Helpers

Use `ito path ...` to get absolute paths at runtime (do not hardcode absolute paths into committed files):

- `ito path project-root`
- `ito path worktree-root`
- `ito path ito-root`
- `ito path worktrees-root`
- `ito path worktree --main|--branch <name>|--change <id>`

## Worktree Workflow


**Strategy:** `bare_control_siblings`
**Directory name:** `ito-worktrees`
**Default branch:** `main`
**Integration mode:** `merge_parent`


This project uses a bare/control repo layout with worktrees as siblings:

```bash
../                              # bare/control repo
|-- .bare/                              # git object store
|-- .git                                # gitdir pointer
|-- main/               # main branch worktree
`-- ito-worktrees/              # change worktrees
    `-- <change-name>/
```

To create a worktree for a change:

```bash
mkdir -p "../ito-worktrees"
git worktree add "../ito-worktrees/<change-name>" -b <change-name>
```


Do NOT ask the user where to create worktrees. Use the configured locations above.

After the change branch is merged, clean up:

```bash
git worktree remove <worktree-path> 2>/dev/null || true
git branch -d <change-name> 2>/dev/null || true
git worktree prune
```

<!-- ITO:END -->

## Project Guidance

## Makefile Workflow

- Use `make install` to set up dependencies via `uv sync`.
- Use `make check` as the standard quality gate (runs `lint`, `format-check`, and `typecheck`).
- Use `make test` for fast unit tests, and `make test-all` when integration coverage is needed.
- For local app development, use `make dev` to run `uvicorn` with reload.
- Use Docker helpers when required: `make docker-build`, `make docker-up`, `make docker-down`, `make docker-logs`.
- Generate the OpenAPI artifact with `make openapi-spec`.
- Before moving to the next implementation task, prefer running `make check` and `make test`, then fix issues before continuing.


## Docker Workflow

- **Use orbstack** for local development and testing

## External files
Access glean-docker for local development and testing of the Glean API here: 

- .local/glean-docker
