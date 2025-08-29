# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0 - Initial Phase 1 wrapper
- Public API proxy, SDK client, CLI entry points
- Env verifier wrapper and hooks installer wrapper
- Functional hook shims delegating to repo hooks

## 0.1.2 - Phase 2 core migration
- Expose tool registry in package; monorepo loads from package
- Add WebMCP binding descriptor
- Add package-native TaskManagerClient (HTTP ChromaDB)
- Route handlers to TaskManagerClient
- CI: add TestPyPI and PyPI publish jobs
