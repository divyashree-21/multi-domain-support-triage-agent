"""
pipeline.py — Main triage pipeline orchestrator.

Wires together: classifier → retriever → safety_checker → response_generator
Reads from support_issues/support_issues.csv
Writes to support_issues/output.csv
"""

import csv
import os
import sys
import time
from pathlib import Path
import pandas as pd
# ── Local imports ─────────────────────────────────────────────────────────────
from agent.classifier import classify
from agent.retriever import load_corpus, CorpusRetriever
from agent.safety_checker import check_safety
from agent.response_generator import generate_response


# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_CSV = BASE_DIR / "support_issues" / "support_issues.csv"
OUTPUT_CSV = BASE_DIR / "support_issues" / "output.csv"

OUTPUT_FIELDS = [
    "issue",
    "subject",
    "company",
    "response",
    "product_area",
    "status",
    "request_type",
    "justification",
]


# ── Terminal colours (graceful fallback for non-TTY) ───────────────────────────
def _c(code: str, text: str) -> str:
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text


GREEN  = lambda t: _c("92", t)
YELLOW = lambda t: _c("93", t)
RED    = lambda t: _c("91", t)
CYAN   = lambda t: _c("96", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline() -> None:
    print(BOLD("\n╔══════════════════════════════════════════════════╗"))
    print(BOLD("║     Multi-Domain Support Triage Agent v1.0       ║"))
    print(BOLD("╚══════════════════════════════════════════════════╝\n"))

    # 1. Load corpus
    print(CYAN("▶ Loading support corpus..."))
    corpus = load_corpus(str(DATA_DIR))
    retriever = CorpusRetriever(corpus)

    chunk_counts = {k: len(v) for k, v in corpus.items()}
    for company, count in chunk_counts.items():
        print(f"   {company:12s}  {count} chunks loaded")
    print()

    # 2. Read input CSV
    if not INPUT_CSV.exists():
        print(RED(f"✗ Input file not found: {INPUT_CSV}"))
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV, encoding="utf-8")

# normalize column names
    df.columns = [c.lower() for c in df.columns]

    rows = df.to_dict(orient="records")

    print(CYAN(f"▶ Processing {len(rows)} support tickets...\n"))
    print("─" * 70)

    output_rows = []
    stats = {"replied": 0, "escalated": 0}

    for i, row in enumerate(rows, 1):
        issue = str(row.get("issue") or "").strip()
        issue = issue.replace("\n", " ").replace("\r", " ")
        subject = str(row.get("subject") or "").strip()
        if subject.lower() == "nan": subject = ""
        company_raw = str(row.get("company") or "").strip()
        if not issue:
            print(DIM(f"[{i:02d}] Skipping empty row."))
            continue

        # ── Step 1: Classify ──────────────────────────────────────────────
        classification = classify(issue, subject, company_raw)
        company      = classification.company
        request_type = classification.request_type
        product_area = classification.product_area

        # ── Step 2: Retrieve ──────────────────────────────────────────────
        if company != "none":
            retrieval_results = retriever.retrieve(
                query=f"{subject} {issue}",
                company=company,
                top_k=3,
                min_score=0.05,
            )
        else:
            retrieval_results = retriever.retrieve_cross_company(
                query=f"{subject} {issue}",
                top_k=2,
                min_score=0.05,
            )

        # ── Step 3: Safety check ──────────────────────────────────────────
        safety = check_safety(
            issue=issue,
            subject=subject,
            company=company,
            request_type=request_type,
            product_area=product_area,
            retrieval_results=retrieval_results,
        )

        # ── Step 4: Generate response ─────────────────────────────────────
        status, response, justification = generate_response(
            issue=issue,
            company=company,
            product_area=product_area,
            request_type=request_type,
            should_escalate=safety.should_escalate,
            escalation_reason=safety.reason,
            retrieval_results=retrieval_results,
        )

        stats[status] += 1

        # ── Terminal output ───────────────────────────────────────────────
        status_badge = GREEN("✔ REPLIED  ") if status == "replied" else YELLOW("⚠ ESCALATED")
        print(f"[{i:02d}] {status_badge}  {BOLD(subject or issue[:60])}")
        print(f"       company={company}  type={request_type}  area={product_area}")
        print(f"       hits={len(retrieval_results)}  " + DIM(justification[:90]))
        print()

        # ── Collect output ────────────────────────────────────────────────
        output_rows.append({
            "issue":            issue,
            "subject":          subject,
            "company":          company,
            "response":         response.replace("\n", " "),
            "product_area":     product_area,
            "status":           status,
            "request_type":     request_type,
            "justification":    justification,
        })

    # 3. Write output CSV
    print("─" * 70)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    # 4. Summary
    total = stats["replied"] + stats["escalated"]
    print(BOLD("\n╔══════════════════════╗"))
    print(BOLD("║     FINAL SUMMARY    ║"))
    print(BOLD("╚══════════════════════╝"))
    print(f"  Total processed : {total}")
    print(f"  {GREEN('Replied')}          : {stats['replied']}")
    print(f"  {YELLOW('Escalated')}        : {stats['escalated']}")
    print(f"\n  Output saved to  : {OUTPUT_CSV}\n")


if __name__ == "__main__":
    run_pipeline()
