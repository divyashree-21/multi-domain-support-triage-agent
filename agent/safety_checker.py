"""
safety_checker.py — Multi-layer safety checker.

Determines whether a support ticket should be ESCALATED before a response
is attempted. Escalation is conservative — when in doubt, escalate.

Escalation triggers:
  1. HIGH-SENSITIVITY TOPICS: fraud, hacked accounts, payment disputes, scams,
     identity theft, unauthorized access.
  2. UNKNOWN COMPANY: ticket cannot be matched to a supported company.
  3. OUT-OF-SCOPE: issue is unrelated to supported products.
  4. NO CORPUS MATCH: retriever returned no relevant documents.
  5. INVALID REQUEST TYPE: classified as 'invalid'.
"""

import re
from dataclasses import dataclass


@dataclass
class SafetyDecision:
    should_escalate: bool
    reason: str


# ---------------------------------------------------------------------------
# Sensitive topic patterns — these ALWAYS escalate regardless of corpus match
# ---------------------------------------------------------------------------

_ESCALATION_PATTERNS = [
    # Account compromise / hacking
    (r"\b(hacked?|hack(ed|ing)?|compromised|account taken over|someone (changed|took|stole))\b", "account_compromise"),
    (r"\b(unauthorized (access|login|device|sign.?in))\b", "unauthorized_access"),
    (r"\bunknown device\b", "unauthorized_access"),

    # Financial fraud / payment disputes
    (r"\b(fraud|fraudulent|unauthorized (charge|transaction|payment))\b", "financial_fraud"),
    (r"\b(scam(med)?|phishing|fake (website|site|email))\b", "scam_report"),
    (r"\b(lost money|money stolen|transfer.{0,20}(without|not) (my )?consent)\b", "financial_loss"),
    (r"\bdispute.{0,20}(charge|transaction|payment)\b", "payment_dispute"),
    (r"\bchargeback\b", "payment_dispute"),
    (r"\bi did(n'?t| not) (make|authorize|approve|request) (that |this )?(charge|transaction|payment|order)\b", "payment_dispute"),

    # Identity theft
    (r"\b(identity theft|someone (opened|applied for|got) (a )?(card|account|loan) (in my name|using my))\b", "identity_theft"),
    (r"\breceived (a )?card.{0,30}(never|did not|didn'?t) apply\b", "unsolicited_card"),
    (r"\bnever applied\b.{0,30}\bcard\b", "unsolicited_card"),

    # Physical safety / legal
    (r"\b(police|legal action|lawyer|attorney|lawsuit|court)\b", "legal_matter"),
    (r"\bdata breach\b", "data_breach"),
    (r"\bstolen.{0,20}(card|data|information|details)\b", "theft"),
    (r"\blost.{0,20}(card|wallet)\b", "lost_card"),

    # Password / security urgency
    (r"\b(changed my (password|email|phone).{0,20}(without|not) me)\b", "account_takeover"),
]


def _check_sensitive_patterns(text: str) -> tuple[bool, str]:
    """Returns (is_sensitive, matched_category)."""
    text_lower = text.lower()
    for pattern, category in _ESCALATION_PATTERNS:
        if re.search(pattern, text_lower):
            return True, category
    return False, ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_safety(
    issue: str,
    subject: str,
    company: str,
    request_type: str,
    product_area: str,
    retrieval_results: list[dict],
) -> SafetyDecision:
    """
    Evaluate whether the ticket should be escalated.

    Args:
        issue:             Raw issue text.
        subject:           Raw subject text.
        company:           Normalised company key.
        request_type:      Classified request type.
        product_area:      Classified product area.
        retrieval_results: Output of CorpusRetriever.retrieve().

    Returns:
        SafetyDecision with should_escalate flag and human-readable reason.
    """
    combined_text = f"{subject} {issue}"

    # 1. Sensitive topic check (always escalate)
    is_sensitive, category = _check_sensitive_patterns(combined_text)
    if is_sensitive:
        return SafetyDecision(
            should_escalate=True,
            reason=f"Sensitive topic detected ({category}). Requires human review.",
        )

    # 2. Invalid or out-of-scope request type
    if request_type == "invalid":
        return SafetyDecision(
            should_escalate=False,  # reply with out-of-scope message, not escalate
            reason="Request is out of scope for this support system.",
        )

    # 3. Unknown company — cannot retrieve relevant docs
    if company == "none":
        return SafetyDecision(
            should_escalate=True,
            reason="Unable to determine the relevant company/product. Escalating for human triage.",
        )

    # 4. No relevant corpus documents found
    if not retrieval_results:
        return SafetyDecision(
            should_escalate=True,
            reason=(
                f"No relevant documentation found in the {company} corpus for this query. "
                "Escalating to avoid hallucination."
            ),
        )

    # 5. Product areas that should always escalate (even with corpus match)
    ALWAYS_ESCALATE_AREAS = {
        "fraud_dispute",
        "security",
        "scam_fraud",
        "lost_stolen",
        "unsolicited_card",
        "data_breach",
    }
    if product_area in ALWAYS_ESCALATE_AREAS:
        return SafetyDecision(
            should_escalate=True,
            reason=(
                f"Product area '{product_area}' requires human handling. "
                "Automated responses are not appropriate for this issue type."
            ),
        )

    # All checks passed — safe to reply
    return SafetyDecision(
        should_escalate=False,
        reason="Issue is within scope and relevant corpus documents were found.",
    )
