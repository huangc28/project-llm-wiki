# Project LLM Wiki

## What This Builds

Project LLM Wiki creates a git-tracked .llm-wiki/ knowledge layer inside each actual project repository.

It is a reusable repo-local skill package for durable architecture notes, decisions, domain concepts, runbooks, feature summaries, and validated implementation learnings. The wiki is meant to travel with the code and remain reviewable in git.

Volatile task state stays in .planning/, Linear, OMX, workflow files, or pull requests.

## Skill Package

This repository is the working source of truth for the reusable skill package during Phase 1.

The package lives at `skills/project-llm-wiki/`. Start with `skills/project-llm-wiki/SKILL.md`, then inspect the package references for the command surface and package boundary.

Phase 1 documents the package shape and mode names. Later phases add deterministic init, lint, query, ingest, and agent-instruction behavior.

## Current GSD Phase

Current phase: Phase 1, Skill Package Foundation.

The phase establishes the reusable package boundary before implementation work begins, so future phases add behavior inside a stable folder structure instead of inventing new entrypoints.

## Validation

Run python3 -m unittest discover -s skills/project-llm-wiki/tests after package changes.

Phase 1 validation proves the package is inspectable and documents the intended repo-local command surface without installing new third-party dependencies.
