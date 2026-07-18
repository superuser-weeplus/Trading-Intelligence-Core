# Configuration Standard Specification

Trading Intelligence Core enforces a strict hierarchical configuration model to guarantee security, environment flexibility, and operational safety.

---

## 1. Configuration Hierarchy

Configurations are resolved using the following order of precedence (highest priority first):

```
1. Secrets Manager / Production KMS (Highest Precedence)
        │
        ▼
2. Environment Variables (.env file / System OS Env Vars)
        │
        ▼
3. settings.yaml (Base Default Configuration File)
```

---

## 2. Hardcoding Prohibition Rule

> [!CAUTION]
> Hardcoding API Keys, Database Passwords, Supabase Service Keys, JWT Tokens, or Broker Credentials directly inside source code files is **STRICTLY FORBIDDEN**.

---

## 3. Configuration Access Pattern in Python

All configuration items MUST be accessed through `app/config/` module wrappers:

```python
import os
from app.config import settings

# Accessing database URL securely
db_url = os.getenv("SUPABASE_DB_URL", settings.database.local_url)
```
