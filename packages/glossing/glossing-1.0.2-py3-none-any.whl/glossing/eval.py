"""Contains the evaluation scripts for comparing predicted and gold IGT"""

from typing import List

from .bleu import bleu_score
from .igt import gloss_string_to_morpheme_glosses, gloss_string_to_word_glosses


def evaluate_glosses(predicted_glosses: List[str], gold_glosses: List[str]):
    """Runs evaluation over paired lists of glosses.

    Expects all glosses to be in the string format such as

    ```text
    DET.PL cat-PL run-3PL
    ```

    where words are separated with spaces and morphemes are separated with dashes '-' or equals '='
    """
    if len(predicted_glosses) != len(gold_glosses):
        raise ValueError(
            f"Length mismatch, got {len(predicted_glosses)} predicted rows and {len(gold_glosses)} gold rows."
        )

    pred_word_glosses = [gloss_string_to_word_glosses(s) for s in predicted_glosses]
    gold_word_glosses = [gloss_string_to_word_glosses(s) for s in gold_glosses]
    word_eval = _eval_accuracy(pred_word_glosses, gold_word_glosses)

    pred_morphemes = [gloss_string_to_morpheme_glosses(s) for s in predicted_glosses]
    gold_morphemes = [gloss_string_to_morpheme_glosses(s) for s in gold_glosses]

    return {
        "word_level": word_eval,
        **_eval_morpheme_glosses(
            pred_morphemes=pred_morphemes, gold_morphemes=gold_morphemes
        ),
    }


def _eval_morpheme_glosses(
    pred_morphemes: List[List[str]], gold_morphemes: List[List[str]]
):
    """Evaluates the performance at the morpheme level"""
    morpheme_eval = _eval_accuracy(pred_morphemes, gold_morphemes)
    class_eval = _eval_stems_grams(pred_morphemes, gold_morphemes)
    bleu = bleu_score(pred_morphemes, [[line] for line in gold_morphemes])

    return {"morpheme_accuracy": morpheme_eval, "classes": class_eval, "bleu": bleu}


def _eval_accuracy(pred: List[List[str]], gold: List[List[str]]) -> dict:
    """Computes the average and overall accuracy, where predicted labels must be in the correct position in the list."""
    total_correct_predictions = 0
    total_tokens = 0
    summed_accuracies = 0

    for entry_pred, entry_gold, i in zip(pred, gold, range(len(gold))):
        entry_correct_predictions = 0

        entry_gold_len = len([token for token in entry_gold if token != "[SEP]"])

        if entry_gold_len == 0:
            raise ValueError(f"Found empty gold entry at position {i}:", entry_gold)

        for token_index in range(len(entry_gold)):
            # For each token, check if it matches
            if (
                token_index < len(entry_pred)
                and entry_pred[token_index] == entry_gold[token_index]
                and entry_gold[token_index] not in ["[UNK]", "[SEP]"]
            ):
                entry_correct_predictions += 1

        entry_accuracy = entry_correct_predictions / entry_gold_len
        summed_accuracies += entry_accuracy

        total_correct_predictions += entry_correct_predictions
        total_tokens += entry_gold_len

    total_entries = len(gold)
    average_accuracy = summed_accuracies / total_entries
    overall_accuracy = total_correct_predictions / total_tokens
    return {"average_accuracy": average_accuracy, "accuracy": overall_accuracy}


def _eval_stems_grams(pred: List[List[str]], gold: List[List[str]]) -> dict:
    perf = {
        "stem": {"correct": 0, "pred": 0, "gold": 0},
        "gram": {"correct": 0, "pred": 0, "gold": 0},
    }

    for entry_pred, entry_gold in zip(pred, gold):
        for token_index in range(len(entry_gold)):
            # We can determine if a token is a stem or gram by checking if it is all uppercase
            token_type = "gram" if entry_gold[token_index].isupper() else "stem"
            perf[token_type]["gold"] += 1

            if token_index < len(entry_pred):
                pred_token_type = (
                    "gram" if entry_pred[token_index].isupper() else "stem"
                )
                perf[pred_token_type]["pred"] += 1

                if entry_pred[token_index] == entry_gold[token_index]:
                    # Correct prediction
                    perf[token_type]["correct"] += 1

    stem_perf = {
        "prec": 0
        if perf["stem"]["pred"] == 0
        else perf["stem"]["correct"] / perf["stem"]["pred"],
        "rec": 0
        if perf["gram"]["gold"] == 0
        else perf["stem"]["correct"] / perf["stem"]["gold"],
    }
    if (stem_perf["prec"] + stem_perf["rec"]) == 0:
        stem_perf["f1"] = 0
    else:
        stem_perf["f1"] = (
            2
            * (stem_perf["prec"] * stem_perf["rec"])
            / (stem_perf["prec"] + stem_perf["rec"])
        )

    gram_perf = {
        "prec": 0
        if perf["gram"]["pred"] == 0
        else perf["gram"]["correct"] / perf["gram"]["pred"],
        "rec": 0
        if perf["gram"]["gold"] == 0
        else perf["gram"]["correct"] / perf["gram"]["gold"],
    }
    if (gram_perf["prec"] + gram_perf["rec"]) == 0:
        gram_perf["f1"] = 0
    else:
        gram_perf["f1"] = (
            2
            * (gram_perf["prec"] * gram_perf["rec"])
            / (gram_perf["prec"] + gram_perf["rec"])
        )
    return {"stem": stem_perf, "gram": gram_perf}


def _eval_word_glosses(pred_words: List[List[str]], gold_words: List[List[str]]):
    """Evaluates the performance at the morpheme level"""
    word_eval = _eval_accuracy(pred_words, gold_words)
    bleu = bleu_score(pred_words, [[line] for line in gold_words])
    return {"word_level": word_eval, "bleu": bleu}
