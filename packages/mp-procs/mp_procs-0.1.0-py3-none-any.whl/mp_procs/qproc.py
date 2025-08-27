import re, pandas as pd, pyterrier as pt, pyterrier_alpha as pta

_DEFAULT_STOPWORDS = {
    "the","a","an","and","or","und","oder","der","die","das","of","in","im","to"
}

def weighted_segmentation_boost(
    *,
    seg_col: str = "segmentation",
    boost_weight: float = 1.2,
    stopwords: set[str] | None = None,
):
    """
    Boosts all terms in multi-word segments by a weighting factor:
    query + hubble^1.2 telescope^1.2 achievements
    Single-word segments are added without boosting.
    
    This function is designed to work with the output of a segmentation artifact.
    """
    if stopwords is None:
        stopwords = _DEFAULT_STOPWORDS

    def _to_tokens(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _transform(df: pd.DataFrame) -> pd.DataFrame:
        if seg_col not in df.columns:
            return df

        out = df.copy()

        for i, row in out.iterrows():
            base_q = row["query"]
            
            segs = row.get(seg_col, None)
            if not segs:
                continue

            # Parse segmentations
            if isinstance(segs, str):
                cand = [s.strip() for s in segs.split("||") if s.strip()]
            elif isinstance(segs, (list, tuple)):
                cand = [" ".join(s) if isinstance(s, (list, tuple)) else s
                        for s in segs]
            else:
                cand = []

            # Build boosted terms
            boosted_parts = []
            for seg in cand:
                tokens = _to_tokens(seg)
                filtered_tokens = [t for t in tokens if t not in stopwords]
                
                if len(filtered_tokens) > 1:
                    # Multi-word segment: boost each term
                    boosted_terms = [f"{token}^{boost_weight}" for token in filtered_tokens]
                    boosted_parts.extend(boosted_terms)
                elif len(filtered_tokens) == 1:
                    # Single-word segment: add without boosting
                    boosted_parts.append(filtered_tokens[0])

            if not boosted_parts:
                continue

            # Combine original query with boosted terms
            new_query = f"{base_q} {' '.join(boosted_parts)}"
            out.at[i, "query"] = new_query

        return out

    return pt.apply.generic(_transform)

def append_segmentation_with_or(
    *,
    seg_col: str = "segmentation",
    stopwords: set[str] | None = None,
):
    """
    Appends segmentation phrases to the original query with logical OR:
    query -> #syn(original_query #band(seg1_term1 seg1_term2) seg2_term ...)
    """
    if stopwords is None:
        stopwords = _DEFAULT_STOPWORDS

    def _to_tokens(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _transform(df: pd.DataFrame) -> pd.DataFrame:
        if seg_col not in df.columns:
            return df

        out = df.copy()

        for i, row in out.iterrows():
            base_q = row["query"]
            
            segs = row.get(seg_col, None)
            if not segs:
                continue

            # Parse segmentations
            if isinstance(segs, str):
                cand = [s.strip() for s in segs.split("||") if s.strip()]
            elif isinstance(segs, (list, tuple)):
                cand = [" ".join(s) if isinstance(s, (list, tuple)) else s
                        for s in segs]
            else:
                cand = []

            # Filter and process segments
            seg_parts = []
            for seg in cand:
                tokens = _to_tokens(seg)
                if len(tokens) < 2:
                    # Single term, add directly
                    if tokens and tokens[0] not in stopwords:
                        seg_parts.append(tokens[0])
                else:
                    # Multiple terms, use #band
                    filtered_tokens = [t for t in tokens if t not in stopwords]
                    if len(filtered_tokens) >= 2:
                        seg_parts.append(f"#band({' '.join(filtered_tokens)})")
                    elif len(filtered_tokens) == 1:
                        seg_parts.append(filtered_tokens[0])

            if not seg_parts:
                continue

            all_parts = [base_q] + seg_parts
            new_query = f"#syn({' '.join(all_parts)})"
            out.at[i, "query"] = new_query

        return out

    return pt.apply.generic(_transform)

def synonym_segmentation(
    *,
    seg_col: str = "segmentation",
    stopwords: set[str] | None = None,
):
    """
    Treats segmentation terms as synonyms:
    query -> query {seg1_term1 seg1_term2} {seg2_term1 seg2_term2}
    """
    if stopwords is None:
        stopwords = _DEFAULT_STOPWORDS

    def _to_tokens(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _transform(df: pd.DataFrame) -> pd.DataFrame:
        if seg_col not in df.columns:
            return df

        out = df.copy()

        for i, row in out.iterrows():
            base_q = row["query"]
            segs = row.get(seg_col, None)
            if not segs:
                continue

            # Parse segmentations
            if isinstance(segs, str):
                cand = [s.strip() for s in segs.split("||") if s.strip()]
            elif isinstance(segs, (list, tuple)):
                cand = [" ".join(s) if isinstance(s, (list, tuple)) else s for s in segs]
            else:
                cand = []

            # Build synonym groups
            synonym_parts = []
            for seg in cand:
                tokens = _to_tokens(seg)
                filtered_tokens = [t for t in tokens if t not in stopwords]
                if len(filtered_tokens) >= 2:
                    synonym_group = " ".join(filtered_tokens)
                    synonym_parts.append(f"{{{synonym_group}}}")

            if not synonym_parts:
                continue

            # Combine original query with synonym groups
            new_query = f"{base_q} {' '.join(synonym_parts)}"
            out.at[i, "query"] = new_query

        return out

    return pt.apply.generic(_transform)

def single_rare_term_emphasis_weighted(
    *,
    avg_idf_col: str = "avg-idf",
    max_idf_col: str = "max-idf",
    avg_idf_low: float = 5.0,
    max_minus_avg_gap: float = 2.0,
    emphasis_weight: float = 1.5,
    stopwords: set[str] | None = None,
):
    """
    Emphasizes a single rare term by boosting it as term^weight in the query string.
    """
    if stopwords is None:
        stopwords = _DEFAULT_STOPWORDS

    def _transform(df: pd.DataFrame) -> pd.DataFrame:
        if max_idf_col not in df.columns: 
            return df
        
        out = df.copy()
        for i, row in out.iterrows():
            avg_idf = row.get(avg_idf_col, 0.0)
            max_idf = row.get(max_idf_col, 0.0)
            # Only apply if avg_idf is low and max_idf is significantly higher
            if not (avg_idf < avg_idf_low and (max_idf - avg_idf) >= max_minus_avg_gap):
                continue

            tokens = re.findall(r"\w+", row["query"])
            content = [t for t in tokens if t.lower() not in stopwords]
            if len(content) < 2:
                continue

            content_sorted = sorted(content, key=len, reverse=True)
            candidate = content_sorted[0]

            # Boost the candidate term in the query string
            boosted_tokens = []
            for token in tokens:
                if token.lower() == candidate.lower():
                    boosted_tokens.append(f"{token}^{emphasis_weight}")
                else:
                    boosted_tokens.append(token)
            weighted_query = " ".join(boosted_tokens)
            out.at[i, "query"] = weighted_query

        return out

    return pt.apply.generic(_transform)


def intent_trigger_weighted(
    *,
    intent_col: str = "intent_prediction",
    trigger_weight: float = 1.5,
):
    """
    Appends intent-specific trigger phrases with weights:
    - Instrumental: query "how to"^1.5
    - Factual: query "definition of"^1.5
    - Transactional: query buy^1.5
    - Navigational: query official^1.5
    - Abstain: no modification
    """
    
    INTENT_TRIGGERS = {
        "instrumental": "how to",
        "factual": "definition of",
        "transactional": "buy", 
        "navigational": "official",
        "abstain": ""
    }
    
    def _transform(df: pd.DataFrame) -> pd.DataFrame:
        if intent_col not in df.columns:
            return df

        out = df.copy()

        for i, row in out.iterrows():
            base_q = row["query"]
            intent = row.get(intent_col, "").lower()
            
            trigger = INTENT_TRIGGERS.get(intent, "")
            if not trigger:
                continue
                
            # Boost each word in the trigger phrase individually
            weighted_trigger = " ".join([f"{word}^{trigger_weight}" for word in trigger.split()])
            new_query = f"{base_q} {weighted_trigger}"
            out.at[i, "query"] = new_query

        return out

    return pt.apply.generic(_transform)

def sanitize_column_transform(
    *,
    source_col: str = "query", 
    target_col: str = "query",
):
    """
    Generic transformer to sanitize any column and optionally map it to another column.
    
    Args:
        source_col: Column to read and sanitize from
        target_col: Column to write sanitized content to (default: "query" for PyTerrier compatibility)
    """
    def _sanitize(df: pd.DataFrame) -> pd.DataFrame:
        if source_col not in df.columns:
            return df
        
        out = df.copy()
        
        def sanitize_text(text_str):
            return re.sub(r"['\"\(\)\/\:]", "", str(text_str))
        
        out[target_col] = out[source_col].apply(sanitize_text)
        
        return out
    
    return pt.apply.generic(_sanitize)