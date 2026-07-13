"""CodeAI Platform — Search Ranker.

BM25 + fuzzy matching for Knowledge Layer search.
Matches DESIGN §9 exactly.

This is an *internal adapter* — not part of the public API.
"""

import math
import re
from collections import Counter

from scripts.core.types.knowledge import Knowledge


# BM25 constants (DESIGN §9.2)
_K1 = 1.5
_B = 0.75

# Fuzzy threshold (DESIGN §9.3)
_FUZZY_THRESHOLD = 2
_FUZZY_MIN_RESULTS = 5

# Source priority (DESIGN §14.4)
_SOURCE_PRIORITY: dict[str, float] = {
    "docs/": 1.0,
    "vault/architecture/": 0.9,
    "vault/best-practices/": 0.8,
    "vault/references/": 0.7,
    "articles/": 0.6,
}

# Kind priority (DESIGN §14.5)
_KIND_PRIORITY: dict[str, float] = {
    "spec": 1.0,
    "adr": 0.9,
    "code": 0.8,
    "api": 0.8,
    "document": 0.7,
    "article": 0.6,
    "test": 0.5,
    "memory": 0.5,
}

# v1 score weights (DESIGN §9.5)
_BM25_WEIGHT = 0.67
_FUZZY_WEIGHT = 0.33


def _tokenize(text: str) -> list[str]:
    """Lowercase + split on whitespace and punctuation."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(
                curr[j] + 1,
                prev[j + 1] + 1,
                prev[j] + cost,
            ))
        prev = curr
    return prev[len(b)]


def _source_score(source: str) -> float:
    """Compute source priority score (DESIGN §14.4)."""
    for prefix, score in sorted(
        _SOURCE_PRIORITY.items(), key=lambda x: -len(x[0])
    ):
        if prefix in source:
            return score
    return 0.4


def _kind_score(kind: str) -> float:
    """Compute kind priority score (DESIGN §14.5)."""
    return _KIND_PRIORITY.get(kind, 0.5)


class SearchRanker:
    """BM25 + fuzzy search ranker.

    Pipeline (DESIGN §9.1):
    1. BM25 full-text search
    2. Fuzzy matching (Levenshtein)
    3. Merge, deduplicate, combine scores
    4. Normalize to [0.0, 1.0]

    Scoring formula v1 (DESIGN §9.5):
        final = BM25_score * 0.67 + fuzzy_score * 0.33
    """

    def rank(self, query: str, items: list[Knowledge]) -> list[Knowledge]:
        """Rank items by relevance to query.

        Returns items sorted by combined score descending.
        Scores are normalized to [0.0, 1.0] (KINV-4).
        """
        if not items:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        # Phase 1: BM25 scoring
        bm25_scores = self._bm25_score(query_tokens, items)

        # Phase 2: Fuzzy scoring
        fuzzy_scores = self._fuzzy_score(query, items)

        # Phase 3: Combine (DESIGN §9.5 v1)
        scored: list[tuple[Knowledge, float]] = []
        for i, item in enumerate(items):
            bm25 = bm25_scores[i]
            fuzzy = fuzzy_scores[i]
            combined = bm25 * _BM25_WEIGHT + fuzzy * _FUZZY_WEIGHT
            # Skip items with no text match at all
            if combined <= 0:
                continue
            # Add secondary factors only when text matched (DESIGN §14)
            source = _source_score(item.source)
            kind = _kind_score(item.kind.value)
            final = combined * 0.6 + source * 0.2 + kind * 0.2
            # Normalize to [0.0, 1.0] (KINV-4)
            final = max(0.0, min(1.0, final))
            scored.append((item, final))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Attach scores to items (Knowledge is frozen, create new instances)
        result = []
        for item, score in scored:
            result.append(Knowledge(
                id=item.id,
                source=item.source,
                kind=item.kind,
                content=item.content,
                score=round(score, 4),
                metadata=item.metadata,
            ))

        return result

    # ------------------------------------------------------------------
    # BM25 (DESIGN §9.2)
    # ------------------------------------------------------------------

    def _bm25_score(
        self, query_tokens: list[str], items: list[Knowledge]
    ) -> list[float]:
        """Compute BM25 scores for each item."""
        n = len(items)
        if n == 0:
            return []

        # Build document tokens
        doc_tokens_list = [
            _tokenize(self._doc_text(item)) for item in items
        ]

        # Average document length
        avg_dl = (
            sum(len(dt) for dt in doc_tokens_list) / n if n > 0 else 1.0
        )

        # Document frequencies
        df: Counter[str] = Counter()
        for dt in doc_tokens_list:
            unique = set(dt)
            for token in unique:
                df[token] += 1

        scores = []
        for dt in doc_tokens_list:
            dl = len(dt)
            tf_counter = Counter(dt)
            score = 0.0
            for qt in query_tokens:
                if qt not in tf_counter:
                    continue
                tf = tf_counter[qt]
                doc_freq = df.get(qt, 0)
                if doc_freq == 0:
                    continue
                # IDF component
                idf = math.log((n - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
                # TF component
                tf_norm = (tf * (_K1 + 1)) / (
                    tf + _K1 * (1 - _B + _B * dl / max(avg_dl, 1.0))
                )
                score += idf * tf_norm

            scores.append(score)

        # Normalize BM25 scores to [0, 1]
        max_score = max(scores) if scores else 1.0
        if max_score > 0:
            scores = [s / max_score for s in scores]

        return scores

    # ------------------------------------------------------------------
    # Fuzzy matching (DESIGN §9.3)
    # ------------------------------------------------------------------

    def _fuzzy_score(
        self, query: str, items: list[Knowledge]
    ) -> list[float]:
        """Compute fuzzy match scores using Levenshtein distance."""
        query_lower = query.lower()
        scores = []
        for item in items:
            text = self._doc_text(item).lower()
            # Check if query tokens fuzzy-match any word in the document
            doc_words = text.split()
            best_distance = float("inf")
            for word in doc_words:
                dist = _levenshtein(query_lower, word[:len(query_lower) + _FUZZY_THRESHOLD])
                best_distance = min(best_distance, dist)
                # Also check substrings
                if len(word) >= len(query_lower):
                    for start in range(len(word) - len(query_lower) + 1):
                        substr = word[start:start + len(query_lower) + _FUZZY_THRESHOLD]
                        dist2 = _levenshtein(query_lower, substr)
                        best_distance = min(best_distance, dist2)

            # Convert distance to score: 0 distance = 1.0, threshold = 0.0
            if best_distance <= _FUZZY_THRESHOLD:
                score = 1.0 - (best_distance / (_FUZZY_THRESHOLD + 1))
            else:
                score = 0.0
            scores.append(score)

        return scores

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _doc_text(item: Knowledge) -> str:
        """Extract searchable text from a Knowledge item."""
        parts = [
            item.source,
            item.kind.value,
            item.content,
        ]
        # Include metadata tags if present
        tags = item.metadata.get("tags", [])
        if isinstance(tags, list):
            parts.extend(str(t) for t in tags)
        return " ".join(parts)
