"""
retriever.py — Corpus loader + TF-IDF-based document retriever.

Loads all .txt files from data/{company}/ directories and retrieves
the most relevant Q&A chunks for a given query using TF-IDF cosine similarity.
Only operates on local corpus files — no internet access.
"""

import os
import re
from pathlib import Path
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------

COMPANY_DIR_MAP = {
    "hackerrank": "hackerrank",
    "claude": "claude",
    "visa": "visa",
}


def _split_into_chunks(text: str) -> list[str]:
    """
    Split a corpus document into individual Q&A chunks.
    Chunks are separated by blank lines. Each chunk must be non-trivial (>20 chars).
    """
    raw_chunks = re.split(r"\n\s*\n", text.strip())
    return [c.strip() for c in raw_chunks if len(c.strip()) > 20]


def load_corpus(data_dir: str) -> dict[str, list[str]]:
    """
    Load all .txt files from data/{company}/ directories.

    Returns:
        {company_name: [chunk1, chunk2, ...]}
    """
    corpus: dict[str, list[str]] = {}
    data_path = Path(data_dir)

    for company_key, subdir in COMPANY_DIR_MAP.items():
        company_path = data_path / subdir
        chunks: list[str] = []

        if company_path.exists():
            for txt_file in sorted(company_path.glob("*.txt")):
                content = txt_file.read_text(encoding="utf-8")
                file_chunks = _split_into_chunks(content)
                chunks.extend(file_chunks)

        corpus[company_key] = chunks

    return corpus


# ---------------------------------------------------------------------------
# TF-IDF Retriever
# ---------------------------------------------------------------------------

class CorpusRetriever:
    """
    Per-company TF-IDF retriever.
    Builds a vectorizer per company so queries are matched only within
    the relevant company's documents — preventing cross-company leakage.
    """

    def __init__(self, corpus: dict[str, list[str]]):
        self.corpus = corpus
        self._vectorizers: dict[str, TfidfVectorizer] = {}
        self._matrices: dict[str, np.ndarray] = {}
        self._build_indexes()

    def _build_indexes(self) -> None:
        for company, chunks in self.corpus.items():
            if not chunks:
                continue
            vec = TfidfVectorizer(
                ngram_range=(1, 2),       # unigrams + bigrams for richer matching
                stop_words="english",
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,        # log-scale TF dampens frequent terms
            )
            matrix = vec.fit_transform(chunks)
            self._vectorizers[company] = vec
            self._matrices[company] = matrix

    def retrieve(
        self,
        query: str,
        company: str,
        top_k: int = 3,
        min_score: float = 0.08,
    ) -> list[dict]:
        """
        Retrieve the top-k most relevant chunks for a query from the given company's corpus.

        Args:
            query:     The support issue text.
            company:   Normalised company key ('hackerrank', 'claude', 'visa').
            top_k:     Number of results to return.
            min_score: Minimum cosine similarity threshold; below this → no results.

        Returns:
            List of {"chunk": str, "score": float} dicts, sorted by descending score.
        """
        company = company.lower().strip()

        if company not in self._vectorizers:
            return []

        vec = self._vectorizers[company]
        matrix = self._matrices[company]
        chunks = self.corpus[company]

        query_vec = vec.transform([query])
        scores = cosine_similarity(query_vec, matrix).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score >= min_score:
                results.append({"chunk": chunks[idx], "score": round(score, 4)})

        return results

    def retrieve_cross_company(
        self,
        query: str,
        top_k: int = 2,
        min_score: float = 0.10,
    ) -> list[dict]:
        """
        Search ALL company corpora (used when company=None or 'none').
        Returns top results across all companies.
        """
        all_results = []
        for company in self._vectorizers:
            results = self.retrieve(query, company, top_k=top_k, min_score=min_score)
            for r in results:
                r["company"] = company
            all_results.extend(results)

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]