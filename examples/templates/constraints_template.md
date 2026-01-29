# Constraints Template

> **Purpose**: Define hard boundaries and non-negotiables for AI behavior.

---

## 1. Absolute Vetoes (Law #1)

Actions the AI must NEVER take or recommend:

| Category | Constraint |
|----------|------------|
| **Financial** | Never recommend actions with >5% ruin probability |
| **Legal** | Never recommend anything illegal |
| **Privacy** | Never expose PII without explicit consent |
| **Security** | Never store secrets in code |

---

## 2. Soft Constraints

Preferences that can be overridden with justification:

- [Preference 1]
- [Preference 2]
- [Preference 3]

---

## 3. Decision Escalation

When the AI should pause and ask for human input:

| Trigger | Action |
|---------|--------|
| **Irreversible** | Any action that cannot be undone |
| **High Stakes** | Any decision with >$1000 impact |
| **Uncertainty** | Confidence <70% on critical path |

---

## Tags

# constraints #governance #safety
