---
name: Deep Research Loop
description: Multi-step web research, compilation, and synthesis workflow. Scrapes multiple sources, cross-references claims, and produces a structured research brief.
created: 2026-02-27
auto-invoke: true
model: default
context_trigger: "research, deep dive, investigate, scrape, compile, multi-source, rabbit hole, comprehensive analysis, literature search"
---

# 🔬 Deep Research Loop

> **Philosophy**: Go deep before going wide. One validated source > ten unverified claims.

## 1. The Prompt

**Role**: Senior Research Analyst.

**Objective**: Execute a structured multi-step research loop on the given topic. Produce a research brief with cited sources, cross-referenced claims, and confidence ratings.

## 2. Execution Workflow

```
STEP 1: SCOPE
  └─ Define the research question in one sentence
  └─ List 3-5 sub-questions that must be answered

STEP 2: GATHER (3+ Sources)
  └─ Search for primary sources (official docs, papers, repos)
  └─ Search for secondary sources (blogs, forums, discussions)
  └─ Search for contrarian views (what disagrees?)

STEP 3: CROSS-REFERENCE
  └─ For each claim: How many independent sources confirm it?
  └─ Flag any claim with only 1 source as [UNVERIFIED]

STEP 4: SYNTHESIZE
  └─ Produce the Research Brief (see Output Format below)
  └─ Highlight conflicts between sources

STEP 5: CONFIDENCE RATING
  └─ Rate overall confidence: HIGH / MEDIUM / LOW
  └─ State what would change your assessment
```

## 3. Output Format

```markdown
# Research Brief: [Topic]

## Key Findings
1. [Finding] — [Source] — Confidence: [H/M/L]
2. [Finding] — [Source] — Confidence: [H/M/L]

## Conflicts & Gaps
- [Source A] says X, but [Source B] says Y

## Recommendations
- [What to do with this information]

## Sources
1. [URL] — [Date accessed]
```

## 4. When to Use

- Before making any decision based on external information
- When the user says "find out everything about X"
- Before building something based on a technology you haven't used

---

# skill #research #synthesis #fact-checking
