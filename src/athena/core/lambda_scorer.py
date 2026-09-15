"""
lambda_scorer.py — Deterministic Risk Tier & Compute Allocator
=============================================================

Replaces subjective 'Lambda is vibes' with an objective, feature-based
risk scoring engine (<5ms runtime). Evaluates query complexity, financial stakes,
irreversibility, and existential ruin risks to compute an integer Lambda score (0-100)
and map it strictly to RiskLevel (SNIPER <10, STANDARD 10-30, ULTRA >30).

Part of Phase C1 (Computed Lambda + Hard Pre-Answer Gate).
"""

from __future__ import annotations

import re
from typing import Any

from athena.core.governance import RiskLevel

__all__ = ["compute_lambda", "LambdaResult"]

TRIVIAL_PATTERNS = [
    r"^(hi|hello|hey|yo|morning|afternoon|evening)\b",
    r"^(thanks|thank you|ty|cheers|got it|noted|ok|okay|cool|nice|good)\b",
    r"^(yes|no|proceed|continue|agree|approved|lgtm|looks good)\b",
    r"^(bye|goodbye|cya|see you)\b",
]

FINANCIAL_STAKES_PATTERNS = [
    (r"(s\$|\$|usd|sgd|¥)\s*\d+[\d,]*(\.\d+)?", "currency_amount"),
    (r"\b(margin|liquidation|pnl|deposit|burn rate|pricing|invoice|paynow|capital|drawdown)\b", "financial_concept"),
]

IRREVERSIBILITY_PATTERNS = [
    (r"\b(sign|quit|resign|terminate|terminated|laid off|retrenchment|pip|lawsuit|sue|charged|court|contract)\b", "irreversible_action"),
    (r"\b(marriage|wedding|banquet|ang[\s-]bao)\b", "high_stakes_social"),
    (r"\b(guarantee|indemnification|indemnity|warranties|warranty)\b", "legal_liability"),
]

RUIN_RISK_PATTERNS = [
    (r"\b(ruin|guillotine|wipeout|short[\s-]gamma|circuit breaker|law of ruin|tail risk)\b", "ruin_risk"),
]

STRATEGIC_PATTERNS = [
    (r"\b(strategy|architecture|portfolio|allocation|asymmetry|monte carlo|kelly|audit|deep dive|comprehensive)\b", "strategic_depth"),
    (r"\b(prove me wrong|red team|counter[\s-]argument|cui bono|hidden meaning|substance decode)\b", "adversarial_reasoning"),
]

ENTITY_PATTERNS = [
    (r"\b(a\d+|s\d{2,4}|cs-\d+|pat-\d+|td-\d+|cc\d{4})\b", "athena_entity_code"),
]


class LambdaResult(dict):
    score: int
    tier: str
    risk_level: RiskLevel
    features: list[dict[str, Any]]


def compute_lambda(
    query: str,
    intent: str = "GENERAL",
    web_required: bool = False,
    underspec_opt: bool = False,
) -> dict[str, Any]:
    """Compute an objective risk Lambda score (0-100) and assign RiskLevel.

    Args:
        query: User's raw or cleaned prompt text.
        intent: Classified intent ('GENERAL', 'SYSTEM_KNOWLEDGE', 'PERSONALISED_DECISION', etc.).
        web_required: Whether external web search is triggered.
        underspec_opt: Whether the query is an underspecified optimization problem.

    Returns:
        dict with score (int), tier (str), risk_level (RiskLevel), and features (list).
    """
    cleaned = query.strip()
    if not cleaned:
        return {
            "score": 0,
            "tier": RiskLevel.SNIPER.name,
            "risk_level": RiskLevel.SNIPER,
            "features": [{"name": "empty_query", "weight": 0}],
        }

    query_lower = cleaned.lower()
    words = query_lower.split()
    word_count = len(words)

    # 1. Check for trivial conversational greeting
    if word_count <= 4 and any(re.search(p, query_lower) for p in TRIVIAL_PATTERNS):
        return {
            "score": 2,
            "tier": RiskLevel.SNIPER.name,
            "risk_level": RiskLevel.SNIPER,
            "features": [{"name": "trivial_conversational", "weight": 2}],
        }

    score = 10  # Baseline default is STANDARD (10-30)
    features: list[dict[str, Any]] = [{"name": "base_standard", "weight": 10}]

    # 2. Ruin & Existential Risk (+30)
    for pat, label in RUIN_RISK_PATTERNS:
        if re.search(pat, query_lower):
            score += 30
            features.append({"name": label, "weight": 30})
            break

    # 3. Irreversibility & Legal Liability (+25)
    for pat, label in IRREVERSIBILITY_PATTERNS:
        if re.search(pat, query_lower):
            score += 25
            features.append({"name": label, "weight": 25})
            break

    # 4. Financial Stakes & Capital (+20)
    for pat, label in FINANCIAL_STAKES_PATTERNS:
        if re.search(pat, query_lower):
            score += 20
            features.append({"name": label, "weight": 20})
            break

    # 5. Strategic & Adversarial Markers (+15)
    for pat, label in STRATEGIC_PATTERNS:
        if re.search(pat, query_lower):
            score += 15
            features.append({"name": label, "weight": 15})
            break

    # 6. Entity Codes (+10)
    for pat, label in ENTITY_PATTERNS:
        if re.search(pat, query_lower):
            score += 10
            features.append({"name": label, "weight": 10})
            break

    # 7. Underspecified Optimization (+10)
    if underspec_opt:
        score += 10
        features.append({"name": "underspec_optimization", "weight": 10})

    # 8. Web Search Required (+5)
    if web_required:
        score += 5
        features.append({"name": "web_required", "weight": 5})

    # 9. Query Length Modifiers
    if word_count > 25:
        score += 10
        features.append({"name": "long_query_length", "weight": 10})
    elif word_count <= 5 and intent == "SYSTEM_KNOWLEDGE" and not web_required and not underspec_opt:
        # Factual short system queries demote to SNIPER
        score -= 8
        features.append({"name": "short_system_fact", "weight": -8})

    # Cap score at 100 max, 0 min
    score = max(0, min(100, score))

    # Map to RiskLevel
    if score < 10:
        tier = RiskLevel.SNIPER
    elif score <= 30:
        tier = RiskLevel.STANDARD
    else:
        tier = RiskLevel.ULTRA

    return {
        "score": score,
        "tier": tier.name,
        "risk_level": tier,
        "features": features,
    }
