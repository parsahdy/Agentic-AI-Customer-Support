# Git Strategy

The project uses a simple branch workflow:

```text
main
  └── develop
        ├── feature/agent
        ├── feature/knowledge-base
        ├── feature/api
        ├── feature/evaluation
        └── feature/docker
```

- **main:** Stable project history.
- **develop:** Integration branch for completed development work.
- **feature branches:** Short-lived branches for focused changes. Merge them into `develop` after review and testing.

## Commit Messages

Use short Conventional Commit-style messages:

```text
feat(agent): add human review flow
fix(api): handle missing agent state
docs(readme): update setup instructions
refactor(kb): simplify retrieval pipeline
chore(docker): add compose configuration
test(agent): cover tool routing
```

Keep commits focused. Avoid mixing unrelated refactoring, documentation, and feature changes in one commit.
