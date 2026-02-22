# Your First Session with Athena

> **Last Updated**: 22 February 2026

> This guide walks you through your very first session. By the end, Athena will know who you are, how you think, and what you're building — and every future session will compound on this foundation.

---

## Why This Matters

Athena is an operating system that becomes **yours**. Unlike generic AI tools, Athena compounds over time — but only if it has the right foundation. Your first session is where you lay that foundation.

Think of it like giving a new executive assistant their first day briefing. The more context they have about you — your goals, preferences, communication style, domain expertise — the faster they become invaluable.

> [!TIP]
> **Everything stays on your machine.** Athena stores all data as local Markdown files. Nothing leaves your device unless you explicitly configure cloud sync. Be as candid as you want — this is your private operating system.

---

## Step 1: Boot Up

Open your workspace in your agentic IDE (Antigravity, Cursor, VS Code) and type:

```
/start
```

Athena loads its core identity and initializes your workspace. On the first run, it creates the directory structure and workspace marker file (`.athena_root`).

---

## Step 2: Take the Guided Tour

Now type:

```
/tutorial
```

This activates Athena's **Guided Walkthrough** — a 7-stage interactive tour that teaches you how Athena works, builds your personal profile, and demos the key tools.

### What the Tutorial Covers

| Stage | What Happens | Duration |
|:------|:------------|:---------|
| **1. Welcome** | What's in the box — the full starter kit | ~1 min |
| **2. Core Loop** | How `/start` → Work → `/end` compounds over time | ~2 min |
| **3. Profile Interview** | Interactive Q&A to build your personal profile | ~15–25 min |
| **4. Search Demo** | See Athena's hybrid RAG search in action | ~2 min |
| **5. Save Demo** | Learn mid-session checkpointing | ~1 min |
| **6. Key Commands** | Your essential toolkit (`/think`, `/research`, `/save`) | ~2 min |
| **7. Graduation** | Summary + next steps | ~30 sec |

> [!TIP]
> **You can skip any stage.** Say "skip" to jump ahead, or "I'm done" to exit early. Athena ships with a working default profile, so you can use it immediately without the interview.

### The Profile Interview (Stage 3)

This is the most important stage. Athena asks you questions (up to 10 per turn) and builds a comprehensive profile of who you are.

| Category | Why It Matters | Examples |
|:---------|:-------------|:---------|
| **Identity** | Name, age, nationality, languages | Shapes communication style and cultural context |
| **Professional** | Occupation, industry, role, salary range | Defines domain expertise and decision-making context |
| **Technical** | Tech stack, tools, skill levels | Determines code style, framework choices, explanation depth |
| **Goals** | Short-term (3 months), medium-term (1 year), long-term (5+ years) | Aligns every response to what you're actually building toward |
| **Decision Style** | Risk appetite, speed vs quality preference, delegation comfort | Calibrates how Athena frames options and tradeoffs |
| **Communication** | Preferred tone (direct, formal, casual), verbosity preference | Sets the default voice for all interactions |
| **Values** | Core principles, non-negotiables, ethical boundaries | Creates guardrails Athena will respect and reinforce |
| **Strengths** | What you're excellent at, your unique edges | Athena leans into these rather than duplicating them |
| **Weaknesses** | Blind spots, recurring mistakes, areas of insecurity | Athena actively watches for these and flags them proactively |
| **Life Context** | Family, health, hobbies, stressors | Helps Athena understand your full context, not just work |

> [!IMPORTANT]
> **The more you share, the better Athena gets.** A one-line answer gives you a generic chatbot. A paragraph gives you a calibrated co-pilot. This is a one-time investment that pays compounding returns across hundreds of sessions.

> [!TIP]
> **Alternative**: If you want to skip the full tutorial and jump straight to profile building, you can use `/brief interview` instead. This runs just the interview without the guided tour.

---

## Step 3: Review Your Profile

After the interview, Athena writes your profile to `.context/memories/user_profile.md`. **Read it.** Edit anything that's wrong or incomplete. This file is the single source of truth that Athena loads on every `/start`.

Your profile will look something like this:

```markdown
# User Profile

## Identity
- **Name**: [Your name]
- **Location**: [City, Country]
- **Languages**: [Languages you speak]

## Professional
- **Role**: [Your role]
- **Industry**: [Your industry]
- **Focus Areas**: [What you work on]

## Goals
- **Short-term**: [3-month targets]
- **Long-term**: [Vision]

## Decision Style
- **Risk**: [Conservative / Calculated / Aggressive]
- **Speed**: [Move fast / Measure twice]

## Communication Preferences
- **Tone**: [Direct / Collaborative / Formal]
- **Verbosity**: [Concise / Detailed]

## Strengths & Blind Spots
- **Strengths**: [What you're great at]
- **Blind Spots**: [What to watch for]
```

---

## Step 4: Work Naturally

Now just work. Talk to Athena like a colleague:

- Ask questions
- Make decisions together
- Let it draft documents, review code, analyze data

Every exchange is automatically saved. Every decision is logged. Every insight compounds.

---

## Step 5: Close the Session

When you're done:

```
/end
```

Athena finalizes the session log, extracts key decisions, and commits everything to memory. Next time you `/start`, it picks up exactly where you left off — with full context.

---

## What Happens Over Time

| Sessions | What Changes |
|:---------|:------------|
| **1** | Athena knows your name, role, and goals |
| **10** | It starts anticipating your preferences |
| **50** | It knows your decision frameworks and communication style |
| **200** | It catches your blind spots before they become problems |
| **500+** | It thinks like a colleague who's been with you for years |

The first session takes ~30 minutes. Every session after that takes ~1–2 minutes to boot.

---

## Tips for a Great First Session

1. **Be honest about weaknesses.** The blind spots you share are the ones Athena will actively monitor.
2. **Share your actual goals, not aspirational ones.** Athena optimizes for where you're going, not where you think you should be going.
3. **Include personal context.** Athena isn't just for work. The more it understands your full life, the better it calibrates priorities.
4. **Edit the profile after.** The interview is a draft. You can always refine `.context/memories/user_profile.md` directly.
5. **Don't worry about over-sharing.** Everything is local. No cloud. No tracking. Your machine, your data.

---

## Next Steps After Your First Session

- **Add more workflows**: Check out the [48 available workflows](../examples/workflows/) — `/think`, `/research`, `/ultrathink`
- **Explore protocols**: Browse [200+ decision frameworks](../examples/protocols/) for inspiration — then write your own
- **Build your knowledge base**: Drop important documents into `.context/memories/` and they'll be indexed on next `/start`
- **Customize the identity**: Edit `.framework/modules/Core_Identity.md` to tune how Athena responds to you

---

> *Your first session is the most important one. After that, Athena handles the rest.*

**[Back to README](../README.md)** · **[Getting Started](GETTING_STARTED.md)** · **[Glossary](GLOSSARY.md)**
