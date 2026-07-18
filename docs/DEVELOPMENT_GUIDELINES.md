# Development Guidelines Specification

This document outlines the mandatory engineering practices, code quality standards, and Definition of Done (DoD) for all developers and AI coding agents working on Trading Intelligence Core.

---

## 1. Core Principles

1. **Clean Architecture**: Clear boundary separation between Presentation, Service, Domain, and Repository layers.
2. **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
3. **Repository Pattern**: All database and storage operations must pass through repository interfaces.
4. **Dependency Injection**: Pass database sessions and configuration objects via constructor parameter injection.
5. **Type Hinting**: All Python functions must include parameter types and return type hints (`def func(param: int) -> str:`). TypeScript code must avoid `any`.
6. **Structured Logging**: Use `logging.getLogger(__name__)` with standardized log levels (`INFO`, `WARNING`, `ERROR`).
7. **Code Formatting & Linting**: Python code must format cleanly with `Black` and pass `Ruff` linter rules without errors.

---

## 2. Definition of Done (DoD)

A task or pull request is considered **DONE** only when:

- [x] Code passes all automated unit tests and integration tests.
- [x] All functions include full type hints.
- [x] APIs adhere strictly to `/api/v1/` route versioning and Unified Response Envelope.
- [x] Data storage uses UTC timezone explicitly.
- [x] Relevant documentation in `docs/` is updated.
