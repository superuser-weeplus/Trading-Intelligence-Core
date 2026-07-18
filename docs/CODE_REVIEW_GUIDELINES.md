# Code Review Guidelines Specification

This document details the code review criteria enforced by the **Code Review Agent** prior to merging code changes into Trading Intelligence Core.

---

## Code Review Criteria Checklist

### 1. Architectural & Structural Compliance
- [ ] Code follows Layered Clean Architecture (`app/api/v1/`, `app/services/`, `app/repositories/`).
- [ ] No direct SQL queries, raw CSV reads, or JSON parsing inside Service or API layers.
- [ ] Modules do not create cyclic imports.

### 2. Code Quality & Type Safety
- [ ] All Python functions include parameter types and return type annotations (`def func(a: int) -> str:`).
- [ ] TypeScript code does not use `any`. All interfaces are explicitly typed in `types/` or `services/`.
- [ ] Variable and function names strictly follow `NAMING_CONVENTIONS.md`.

### 3. Timezone & Data Policy
- [ ] All datetime operations use explicit UTC (`datetime.now(timezone.utc)`). Naive datetimes are rejected.
- [ ] ISO8601 formatting is preserved for API outputs.

### 4. Security & Hardcoding
- [ ] Zero API keys, database URLs, passwords, or tokens hardcoded in code files.
- [ ] Configuration parameters loaded via `app/config/` module.

### 5. Formatting & Linting
- [ ] Code formatted cleanly with `Black`.
- [ ] `Ruff` linter passes without warnings or errors.
