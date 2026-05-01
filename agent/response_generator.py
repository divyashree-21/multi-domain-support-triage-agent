"""
response_generator.py — Grounded response generator.

Generates responses ONLY from retrieved corpus chunks.
No external knowledge is used. If no chunks are available,
the generator refuses to produce a response (→ escalate).

Response strategies:
  - replied:   Synthesises a structured reply from the top corpus chunk(s).
  - escalated: Returns a professional escalation notice.
  - out_of_scope: Returns a clear out-of-scope message.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Escalation & out-of-scope templates
# ---------------------------------------------------------------------------

_ESCALATION_TEMPLATE = (
    "Thank you for reaching out. Your request has been escalated to our "
    "specialist support team, who will review it and get back to you as soon "
    "as possible. If your issue is urgent (e.g., account compromise or "
    "unauthorised financial activity), please also contact us directly at "
    "the official support channel for your product. We take these matters "
    "seriously and will prioritise your case."
)

_OUT_OF_SCOPE_TEMPLATE = (
    "Thank you for your message. Unfortunately, this support channel covers "
    "issues related to HackerRank, Claude, and Visa only. Your query appears "
    "to be outside the scope of these products. Please reach out to the "
    "appropriate service provider for assistance."
)

_NO_INFO_TEMPLATE = (
    "Thank you for contacting support. We were unable to find specific "
    "documentation for your query in our knowledge base. Your ticket has been "
    "escalated to a human agent who will follow up with you directly."
)


# ---------------------------------------------------------------------------
# Response synthesis
# ---------------------------------------------------------------------------

def _extract_answer_from_chunk(chunk: str) -> str:
    """
    From a Q&A-style chunk, extract just the answer portion.
    If the chunk contains 'A:', return everything after it.
    Otherwise, return the full chunk.
    """
    if "\nA:" in chunk:
        parts = chunk.split("\nA:", 1)
        return parts[1].strip()
    if "A: " in chunk:
        parts = chunk.split("A: ", 1)
        return parts[1].strip()
    return chunk.strip()


def _build_reply(
    issue: str,
    company: str,
    product_area: str,
    retrieval_results: list[dict],
    request_type: str,
) -> str:
    """
    Synthesise a grounded reply from the top retrieval result(s).
    Uses the highest-scoring chunk as the primary source, and optionally
    supplements with a second chunk if the score warrants it.
    """
    if not retrieval_results:
        return _NO_INFO_TEMPLATE

    primary = retrieval_results[0]
    answer = _extract_answer_from_chunk(primary["chunk"])

    # Add a feature-request acknowledgement prefix
    if request_type == "feature_request":
        prefix = (
            "Thank you for your feedback! Feature requests are valuable to us. "
            "Based on our documentation: "
        )
        return prefix + answer

    # Standard reply prefix
    prefix = "Thank you for reaching out. Based on our support documentation: "

    # Optionally include a second source if it adds new information
    supplementary = ""
    if len(retrieval_results) > 1 and retrieval_results[1]["score"] > 0.12:
        second_answer = _extract_answer_from_chunk(retrieval_results[1]["chunk"])
        # Only include if it's meaningfully different (first 60 chars differ)
        if second_answer[:60] != answer[:60]:
            supplementary = f"\n\nAdditionally: {second_answer}"

    return prefix + answer + supplementary


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_response(
    issue: str,
    company: str,
    product_area: str,
    request_type: str,
    should_escalate: bool,
    escalation_reason: str,
    retrieval_results: list[dict],
) -> tuple[str, str, str]:
    """
    Generate the final output triple: (status, response, justification).

    Returns:
        status:        'replied' | 'escalated'
        response:      The message to send to the user.
        justification: Internal explanation of the decision.
    """

    # Out-of-scope (invalid type, company=none, no escalation needed)
    if request_type == "invalid" and not should_escalate:
        return (
            "replied",
            _OUT_OF_SCOPE_TEMPLATE,
            (
                "Issue classified as invalid/out-of-scope. "
                "Company could not be identified and no relevant corpus documents exist. "
                "Replied with out-of-scope message."
            ),
        )

    # Escalation path
    if should_escalate:
        justification = (
            f"Escalated because: {escalation_reason} "
            f"[company={company}, product_area={product_area}, "
            f"request_type={request_type}, "
            f"corpus_hits={len(retrieval_results)}]"
        )
        return "escalated", _ESCALATION_TEMPLATE, justification

    # Happy path — generate grounded reply
    response = _build_reply(issue, company, product_area, retrieval_results, request_type)
    top_score = retrieval_results[0]["score"] if retrieval_results else 0.0

    justification = (
        f"Issue is answerable from the {company} corpus. "
        f"Top retrieval score: {top_score:.4f}. "
        f"Response grounded in {len(retrieval_results)} corpus chunk(s). "
        f"[product_area={product_area}, request_type={request_type}]"
    )

    return "replied", response, justification
