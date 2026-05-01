"""
classifier.py — Rule-based + keyword classifier for:
  - request_type: product_issue | feature_request | bug | invalid
  - company normalisation: hackerrank | claude | visa | none
  - product_area: derived from company + issue content
"""

import re
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Classification:
    company: str          # normalised: hackerrank | claude | visa | none
    request_type: str     # product_issue | feature_request | bug | invalid
    product_area: str     # e.g. 'account_access', 'billing', 'assessments', etc.


# ---------------------------------------------------------------------------
# Company normalisation
# ---------------------------------------------------------------------------

_COMPANY_ALIASES = {
    "hackerrank": "hackerrank",
    "hacker rank": "hackerrank",
    "hr": "hackerrank",
    "claude": "claude",
    "anthropic": "claude",
    "visa": "visa",
    "none": "none",
    "": "none",
}

_COMPANY_KEYWORDS = {
    "hackerrank": [
        "hackerrank", "hacker rank", "coding challenge", "assessment", "test case",
        "submission", "plagiarism", "certification", "interview kit", "leaderboard",
        "coding test", "practice problem", "code submission","programming language",
        "help","not working","unable to submit","need help","issue","problem","guide","how to"
    ],
    "claude": [
        "claude", "anthropic", "claude pro", "claude.ai", "claude api",
        "ai assistant", "chatbot", "language model",
        "ai", "assistant", "model response", "hallucinate",
        "refuse", "content policy", "data usage", "privacy"
    ],
    "visa": [
        "visa card", "visa debit", "visa credit", "visa transaction",
        "chargeback", "zero liability", "visa gift card", "my visa",
        "card", "payment", "transaction", "bank", "credit", "debit",
        "refund", "billing", "subscription"
    ],
}


def normalise_company(company_str: str, issue_text: str) -> str:
    """
    Resolve company from the CSV 'company' column, falling back to keyword
    detection in the issue text.
    """
    raw = (company_str or "").strip().lower()
    if raw in _COMPANY_ALIASES:
        resolved = _COMPANY_ALIASES[raw]
        if resolved != "none":
            return resolved

    # Keyword scan on the full issue text
    text_lower = (issue_text or "").lower()
    for company, keywords in _COMPANY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return company

    return "none"


# ---------------------------------------------------------------------------
# Request type classification
# ---------------------------------------------------------------------------

_FEATURE_REQUEST_PATTERNS = [
    r"\bi want\b.{0,40}\bfeature\b",
    r"\bplease add\b",
    r"\bwould be great if\b",
    r"\brequest.{0,20}feature\b",
    r"\bfeature request\b",
    r"\bsupport.{0,30}\blike\b",
    r"\badd support for\b",
    r"\bwish.{0,30}\bhad\b",
    r"\bcould you add\b",
    r"\bwould love\b.{0,40}\bfeature\b",
    r"\bsuggest.{0,20}\bfeature\b",
    r"\bintegration.{0,20}\b(like|similar)\b",
    r"\bdark mode\b",
    r"\bplugin\b",
]

_BUG_PATTERNS = [
    r"\bbug\b",
    r"\bbroken\b",
    r"\bdoesn'?t work\b",
    r"\bstops? working\b",
    r"\bcrash(ed|es|ing)?\b",
    r"\berror message\b",
    r"\bglitch\b",
    r"\bfreezes?\b",
    r"\bnot (loading|displaying|rendering|working|responding)\b",
    r"\bsubmit button.{0,20}grey(d)? out\b",
    r"\bpage (crashes?|breaks?)\b",
]

_INVALID_PATTERNS = [
    r"\bhow (do i|to) (make|cook|bake|prepare)\b",
    r"\bweather\b",
    r"\bnetflix\b",
    r"\bamazon\b(?!.*visa)",
    r"\bspotify\b",
    r"\bprogramming language to learn\b",
    r"\bbest laptop\b",
    r"\bcrypto\b",
    r"\bbitcoin\b",
]


def classify_request_type(issue: str, company: str) -> str:
    """
    Classify the request type using regex patterns.
    Order of precedence: feature_request > bug > invalid > product_issue
    """
    text = issue.lower()

    for pat in _FEATURE_REQUEST_PATTERNS:
        if re.search(pat, text):
            return "feature_request"

    for pat in _BUG_PATTERNS:
        if re.search(pat, text):
            return "bug"

    if company == "none":
        for pat in _INVALID_PATTERNS:
            if re.search(pat, text):
                return "invalid"
        # Unknown company with no bug/feature pattern → likely invalid
        return "invalid"

    for pat in _INVALID_PATTERNS:
        if re.search(pat, text):
            return "invalid"

    return "product_issue"


# ---------------------------------------------------------------------------
# Product area detection
# ---------------------------------------------------------------------------

_PRODUCT_AREA_RULES: dict[str, list[tuple[str, list[str]]]] = {
    "hackerrank": [
        ("account_access", ["log in", "login", "password", "reset", "email", "verification", "account", "credentials", "locked", "suspended"]),
        ("assessments", ["assessment", "test case", "submit", "submission", "code", "challenge", "hidden test", "sample test", "deadline", "greyed out", "plagiarism", "language", "coding","not working", "not submitting", "unable to submit", "test not loading"]),
        ("billing", ["charge", "charged", "billing", "subscription", "pro", "cancel", "refund", "payment", "billed", "invoice"]),
        ("certification", ["certificate", "certification", "badge", "score", "beat the", "pass the"]),
        ("security", ["hacked", "hack", "compromised", "someone else", "unauthorized access", "account taken"]),
        ("scam_fraud", ["scam", "fraud", "fake website", "lost money", "phishing"]),
        ("general", ["help", "support", "issue", "problem", "guide","how to", "unable", "need help"]),
    ],
    "claude": [
        ("account_access", ["log in", "login", "password", "sign in", "reset", "cannot access", "locked out"]),
        ("billing", ["charge", "charged", "subscription", "pro", "cancel", "refund", "payment", "billed", "invoice"]),
        ("response_quality", ["wrong answer", "incorrect", "hallucinate", "hallucination", "bad response", "inaccurate", "mistake", "error"]),
        ("safety_refusal", ["refused", "refuse", "won't answer", "blocked", "restricted", "content policy", "declined"]),
        ("connectivity", ["disconnecting", "slow", "not responding", "unresponsive", "lag", "timeout", "crash"]),
        ("security", ["hacked", "unauthorized", "unknown device", "someone else", "compromised", "security"]),
        ("features", ["feature", "plugin", "integration", "memory", "app", "mobile"]),
         ("privacy", ["data", "privacy", "personal data", "data usage",
        "data retention", "information stored", "how data is used",
        "personal information", "user data", "data policy"
        ]),
        ("general", []),
        
    ],
    "visa": [
        ("fraud_dispute", ["unauthorized", "fraud", "scam", "did not make", "didn't make", "stolen", "compromised", "data breach"]),
        ("card_declined", ["declined", "not accepted", "rejected", "failed"]),
        ("dispute_chargeback", ["dispute", "chargeback", "not delivered", "order", "refund", "merchant"]),
        ("lost_stolen", ["lost", "stolen", "missing card", "never received"]),
        ("unsolicited_card", ["did not apply", "never applied", "received a card", "unsolicited"]),
        ("international_use", ["international", "abroad", "travel", "foreign", "japan", "europe", "overseas"]),
        ("card_management", ["activate", "expiry", "expires", "renewal", "virtual card", "gift card"]),
        ("general", []),
    ],
    "none": [
        ("out_of_scope", []),
    ],
}


def detect_product_area(issue: str, company: str) -> str:
    """
    Match issue text to a product area using keyword scoring.
    Returns the area with the most keyword hits, defaulting to 'general'.
    """
    text = issue.lower()
    rules = _PRODUCT_AREA_RULES.get(company, [("general", [])])

    best_area = rules[-1][0]  # default = last rule (general / out_of_scope)
    best_score = 0

    for area, keywords in rules[:-1]:
        score = sum(2 if kw in text else 0 for kw in keywords)
        if score > best_score:
            best_score = score
            best_area = area

    return best_area


# ---------------------------------------------------------------------------
# Main classifier entry point
# ---------------------------------------------------------------------------

def classify(issue: str, subject: str, company_raw: str) -> Classification:
    """
    Full classification of a support ticket.
    """
    company = normalise_company(company_raw, issue + " " + subject)
    request_type = classify_request_type(issue + " " + subject, company)
    product_area = detect_product_area(issue + " " + subject, company)

    return Classification(
        company=company,
        request_type=request_type,
        product_area=product_area,
    )
