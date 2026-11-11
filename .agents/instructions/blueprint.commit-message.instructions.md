---
name: "Commit Message Conventions"
description: "Conventional Commits types, scopes, and rules enforced by commitlint"
applyTo: "**"
---

# Commit Message Conventions

**Procedure:** [`ha-release`](../skills/ha-release/SKILL.md) — load it when cutting a version, or when the choice of
type decides whether a change reaches users. This file is the rule set commitlint enforces; the skill is how
release-please turns those commits into a version and a changelog.

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Format

```text
type(scope): short summary (max 100 chars)
```

**Commit messages are a single subject line.** No body, no footers, no blank lines, no trailers, and a single `-m`
flag. The commit guardrail in this project rejects anything else. Analyze the full staged diff before writing the
subject, so it names the change that matters most.

## Types

| Type       | When to use                                                        |
| ---------- | ------------------------------------------------------------------ |
| `feat`     | User-facing new functionality (new sensor, service, config option) |
| `fix`      | Bug fix for user-facing issues                                     |
| `chore`    | Dev tooling, dependencies, devcontainer — NOT visible to users     |
| `refactor` | Code restructuring without functional change                       |
| `docs`     | Documentation only                                                 |
| `test`     | Adding or fixing tests                                             |
| `ci`       | CI/CD pipeline changes                                             |
| `perf`     | Performance improvements                                           |

Mark a breaking change with `!` after the type: `feat!:` or `fix!:`. There is no `BREAKING CHANGE:` footer, because commits carry no footers.

## Scopes

Scope is optional but clarifies the affected component. Use the name of the affected layer or platform:

- **Platforms:** `sensor`, `switch`, `fan`, `binary_sensor`, `button`, `number`, `select`, `light`, `climate`, …
- **Layers:** `coordinator`, `api`, `entity`, `config-flow`, `service-actions`, `entity-utils`
- **System:** `diagnostics`, `repairs`, `manifest`, `translations`, `deps`, `devcontainer`, `tests`

A scope names the affected _component_, never a change _category_. Using a type
name as a scope is rejected by commitlint (`scope-enum`), because it publishes
the change in the wrong changelog section: `feat(ci): …` lands under "Features"
as if it were user-facing, while the `ci` **type** is `hidden` in
`release-please-config.json`. Pipeline and tooling work takes the `ci` or
`chore` type — `ci: enable brands validation`, not
`feat(ci): enable brands validation`.

## Rules

1. **Subject line only**: one line, no body, no footers
2. **Always include a scope** when the change is clearly scoped to one component or layer
3. Subject line: ≤ 100 chars, no capital after colon, no trailing period
4. Plain ASCII and plain language only
5. Breaking changes: mark them with `!` **and** warn the developer before implementing
6. Multiple unrelated changes → separate commits, not one large commit
7. **A pull request title is a commit subject.** Pull requests are squash-merged by default, with the title as the
   commit on `main`, so it follows rule 3 and the types above; the `PR title` check enforces it. A pull request
   rebase-merged instead keeps each commit, so each one must follow these rules

## Example

The breaking-change shape, which the rules above do not show:

```text
feat!: redesign config entry data structure
```
