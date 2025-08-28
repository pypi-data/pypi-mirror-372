from collections import Counter
from functools import reduce
import math
from statistics import geometric_mean
from typing import cast

def _compute_ngrams(sentence: list[str], n: int):
    for i in range(0, len(sentence) - n + 1):
        yield tuple(sentence[i:i+n])

def bleu_score(
    candidates: list[list[str]],
    references: list[list[list[str]]],
    max_ngram_order: int = 4,
) -> float:
    """Simple implementation of BLEU score following Papineni et al. (2002). Probably not very optimized.

    Args:
        candidates (list[list[str]]): The candidate sentences (tokenized)
        references (list[list[list[str]]]): The references (may have multiple per candidate)
        max_ngram_order: int
    """
    if len(candidates) != len(references):
        raise ValueError(f"Length of candidates ({len(candidates)}) and references ({len(references)}) must match!")

    # 1. Compute modified n-gram precisions
    all_precisions: list[float] = []
    smooth_value = 1.
    for ngram_order in range(1, max_ngram_order + 1):
        # For computing precision
        n_gram_matches = 0
        total_n_grams = 0

        for candidate, reference in zip(candidates, references):
            candidate_grams = Counter(_compute_ngrams(candidate, ngram_order))
            total_n_grams += candidate_grams.total()

            # Compute the reference grams, taking the max count for each ngram across references
            reference_grams = reduce(Counter.__or__, (Counter(_compute_ngrams(r, ngram_order)) for r in reference))

            for gram, candidate_count in candidate_grams.items():
                n_gram_matches += min(candidate_count, reference_grams.get(gram, 0))

        if n_gram_matches == 0:
            smooth_value *= 2
            precision = 100. / (smooth_value * total_n_grams)
        else:
            precision = 100. * n_gram_matches / total_n_grams
        all_precisions.append(precision)
    print(all_precisions)
    mean_precision = geometric_mean(all_precisions)

    # 2. Compute brevity penalty
    candidate_corpus_length = sum((len(c) for c in candidates))
    reference_corpus_length = 0
    for candidate, reference in zip(candidates, references):
        # Compute the "best match length", the closest reference length to the candidate length
        can_len = len(candidate)
        reference_lengths: list[int] = [len(r) for r in reference]
        best_match_length: int = reduce(
            lambda ref_len1, ref_len2: ref_len1 if abs(cast(int, ref_len1) - can_len) < abs(ref_len2 - can_len) else ref_len2,
            reference_lengths[1:],
            reference_lengths[0]
        )
        reference_corpus_length += best_match_length
    brevity_penalty: float = (
        1.0 if candidate_corpus_length > reference_corpus_length
        else math.exp(1 - (reference_corpus_length / candidate_corpus_length))
    )

    return brevity_penalty * mean_precision
