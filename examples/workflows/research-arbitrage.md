---
description: Research Arbitrage Workflow (NotebookLM Method)
created: 2026-01-02
last_updated: 2026-03-17
---
# Research Arbitrage Workflow

> **Source**: CS-200 (Paul James) + Session S34 (Cross-Model Triangulation)
> **Purpose**: Transform raw research into high-value "Structured Intelligence" deliverables.
> **Value**: Turns "reading" (free) into "intelligence" ($$$).

---

## Method A: NotebookLM Method (Single-Source Deep Dive)

**When**: You have 5-10 curated primary sources and need structured comparison.

### Phase 1: Ingest (The Raw Material)

**Trigger**: User asks for "Research on [Topic]" or "Competitor Analysis".

1. **Sourcing**:
    - Use `/research` or `/search` to find 5-10 high-quality URLs/PDFs.
    - *Constraint*: Must be primary sources (Whitepapers, Competitor Homepages, 10k Filings).
2. **Aggregation**:
    - Dump all text/links into a single "Source Context".

### Phase 2: Arbitrage (The Structure)

**Command**: "Structure this into a [Format]."

**High-Value Formats**:

1. **The Comparison Matrix**:
    - Columns: Competitors. Rows: Features, Pricing, Positioning.
2. **The Trend Radar**:
    - Columns: Trend, Impact (High/Med/Low), Timeline (Now/Next/Later).
3. **The Gap Analysis**:
    - Columns: Market Need, Current Solutions, The Gap (Opportunity).

**Prompt**:
> "Act as a McKinsey Analyst. Take these sources.
> Produce a Markdown Table comparing [X] vs [Y].
> Highlight the 'White Space' opportunity in the final column."

### Phase 3: Deliverable (The Asset)

**Packaging**:

1. **Intelligence Brief**:
    - Executive Summary (BLUF).
    - The Structured Table (from Phase 2).
    - Strategic Recommendations (3 bullets).
2. **Export**:
    - Save as `reports/[Topic]_Brief.md`.
    - Offer as PDF.

---

## Method B: Cross-Model Triangulation (Multi-Source Consensus)

> **Source**: Session S34 (Mar 17). CANONICAL §242 (Cross-Model Research Arbitrage).
> **When**: Zero domain knowledge. Need to cover KSA gaps before execution.
> **Why**: Different models have divergent training corpora → independent information sources.

### Phase 1: Generate the Research Prompt

1. Give Athena the project inputs (client brief, assignment spec, rubric).
2. Ask Athena to generate a **deep research prompt** covering all possible KSA gaps.
   - The prompt should be self-contained (no dependencies on Athena context).
   - Include: domain fundamentals, methodology options, common pitfalls, evaluation criteria.

### Phase 2: Run Through ≥3 Models

Run the **identical prompt** through:

| Model | Strength | What It Catches |
|-------|----------|----------------|
| **Gemini** | Structured reasoning, code generation | Systematic gaps, implementation details |
| **Grok** | Real-time data, contrarian angles | Current trends, unconventional approaches |
| **ChatGPT** | Broad coverage, pedagogical clarity | Textbook consensus, beginner pitfalls |

Optional: Add Claude (reasoning depth), Perplexity (citation-heavy), or DeepSeek (code-heavy domains).

### Phase 3: Triangulate

1. **Intersection** (mentioned by ALL models) = **Textbook solution**. High-confidence consensus.
   - This is what the examiner/client expects to see.
   - If all 3 agree on a methodology → use it.

2. **Union minus Intersection** (mentioned by only 1-2 models) = **Novel insights**.
   - These are model-specific training data surfacing unique angles.
   - Evaluate for inclusion: does it strengthen or distract?
   - Often contains the "interesting data points" that differentiate from generic work.

3. **Contradiction** (models disagree) = **Decision point**.
   - Research the specific disagreement manually.
   - Often reveals a genuine domain debate worth addressing in the deliverable.

### Phase 4: Synthesize Back to Athena

Return to Athena with:
- The textbook consensus (confirmed foundation)
- The novel angles (potential differentiators)
- Any contradictions (decision points to resolve)

Ask Athena to lay down the step-by-step execution plan incorporating all of the above.

---

## Tags

# research #consulting #arbitrage #notebooklm #deliverables #cross-model #triangulation
