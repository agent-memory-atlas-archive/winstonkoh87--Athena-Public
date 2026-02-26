# Skills Directory

This directory contains reusable AI skills that extend agent capabilities. Each skill is a self-contained instruction set that teaches your AI agent a specialized workflow.

## Available Skills

```
skills/
├── coding/
│   ├── diagnostic-refactor/   # Diagnose code issues before editing
│   └── spec-driven-dev/       # Build a design spec before writing code
├── decision/
│   └── mcda-solver/           # Multi-criteria decision matrix calculator
├── quality/
│   └── red-team-review/       # Adversarial QA review for any artifact
├── research/
│   └── deep-research-loop/    # Structured multi-source research workflow
└── workflow/
    └── context-compactor/     # Compress context to stay within token limits
```

## What is a Skill?

A **skill** is a specialized prompt pattern + workflow that teaches an AI agent how to perform a specific task well. Each skill contains:

- `SKILL.md` — Main instruction file with the prompt and execution workflow
- Optional: scripts, examples, templates

## Quick Start

### For Antigravity Users

Skills in `.agent/skills/` are auto-detected. To use these templates:

```bash
# Copy a skill template into your workspace
cp -r examples/skills/coding/spec-driven-dev .agent/skills/

# The skill is now available to your agent automatically
```

### For Other IDEs

1. Read the `SKILL.md` file for the skill you want to use
2. Follow the execution workflow described
3. The AI will produce output in the specified format

## Creating Your Own Skills

Every skill follows this structure:

```yaml
---
name: My Custom Skill
description: One-line description of what this skill does
---

# Skill Title

## When to Use
[Triggers and conditions]

## Execution Workflow
[Step-by-step instructions]

## Output Format
[Expected output structure]
```

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on adding new skills.
