
# ADR-0001: GitHub Flow Branching Strategy

## Context

Our team is developing MeshWatch, an IoT platform.
We need a simple way to work together, manage changes,
and review each other's work.

We considered Git Flow, GitHub Flow, and Trunk-Based
Development.

## Decision

We will use GitHub Flow because it is simple and
suitable for our small team.

We will follow these rules:

- The `main` branch contains approved changes.
- Branch names use `feature/`, `docs/`, or `fix/`.
- Every change requires a Pull Request.
- At least one other team member must approve it.
- Direct pushes to `main` are not allowed.

## Status

Accepted.

## Consequences

GitHub Flow makes teamwork easier and ensures changes
are reviewed at least once before merging.

However, reviews can take time.
