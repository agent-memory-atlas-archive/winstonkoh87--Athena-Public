---
title: I built a 1000+ session AI agent framework — here's the full starter pack (skills, memory, protocols)
flair: Resources & Guides
subreddit: r/google_antigravity
---

I saw u/MathiRaja's post asking how to actually set up agent skills from scratch. Same struggle here months ago. So I'm sharing the full reference implementation I've been running daily.

**TL;DR**: [github.com/winstonkoh87/Athena-Public](https://github.com/winstonkoh87/Athena-Public) — MIT licensed, clone and go.

---

### What's in the box

| Component | What it does |
|-----------|--------------|
| **63 protocols** | Decision frameworks (not prompts — reusable thinking patterns) |
| **12 reference scripts** | `boot.py`, `quicksave.py`, `smart_search.py` — the actual commands |
| **6 case studies** | Real examples: boot optimization, search quality, protocol enforcement |
| **Hybrid RAG** | Vector search + GraphRAG + RRF fusion (the expensive part cost ~$50, but there's a free workaround in the docs) |
| **Session loop** | `/start` → Work → `/end` — your agent remembers across sessions |

---

### The folder structure everyone asks about

```
Athena-Public/
├── .agent/
│   ├── scripts/       ← boot.py, shutdown.py, search
│   ├── workflows/     ← /start, /end, /think
│   └── skills/        ← Your protocols live here
├── .context/          ← Session logs, memories
├── .framework/        ← Core identity, laws
├── src/athena/        ← pip installable SDK
└── docs/              ← Deep dives (GraphRAG, VectorRAG, etc.)
```

---

### The loop

```
/start → retrieves context from long-term memory
Work → Athena has your history, protocols, decisions
/end → extracts insights, commits to memory, logs session
```

Think Git, but for conversations.

---

### Why I'm sharing

I hit every wall you're hitting: agent amnesia, no persistence, skills that don't compose. After 1000+ sessions, I codified what worked. The private repo has 308 protocols — this starter pack has the best 63.

Not a product. Just a reference implementation. Fork it, break it, make it yours.

---

**Link**: [github.com/winstonkoh87/Athena-Public](https://github.com/winstonkoh87/Athena-Public)

Happy to answer questions. AMA.
