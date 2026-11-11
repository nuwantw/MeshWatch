# ADR-0002: Conventional Commits

**Status:** Exepted   
**Date:** 2026-11-11  
**Author:** Cothi

## Context

MeshWatch is developed by five team members. We need consistent commit messages to keep our Git history clear and understandable.

## Considered Options

- **Free-form messages:** Simple but inconsistent.
- **Conventional Commits:** Standardized and easy to understand. 

## Decision

We will use **Conventional Commits v1.0.0**.

Format: `<type>(optional scope): <description>`

Common types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `chore`: Maintenance

Examples:
- `feat(sensor): add temperature simulation`
- `fix(gossip): prevent duplicate readings`
- `docs: add ADR-0002`

## Consequences

**Positive:**
- Clear and consistent commit history.
- Easier collaboration.

**Negative:**
- Team members must follow the naming convention.
