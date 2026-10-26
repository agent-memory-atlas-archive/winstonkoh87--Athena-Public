# Athena Examples & Protocols

This directory contains executable examples, protocol specifications, templates, and reference workflows designed for Project Athena.

## 📁 Directory Structure

- [protocols/](protocols/) — Public reference protocols across Decision Science, Workflow Orchestration, Engineering, and Risk Management.
- [workflows/](workflows/) — Domain-specific slash-command execution plans and multi-turn workflows.
- [templates/](templates/) — Structured templates for session logs, task tracking, and decision registers.
- [agents/](agents/) — Sample autonomous agent configurations and persona cards.
- [case_studies/](case_studies/) — Sanitized case studies illustrating real-world application of cognitive protocols.

## 🚀 Usage

Protocols in Athena are declarative markdown files with structured frontmatter that can be ingested by any LLM or IDE agent harness.

```bash
# Verify published examples syntax integrity
ruff check examples/ --select F821,F822,F823,E9
```
