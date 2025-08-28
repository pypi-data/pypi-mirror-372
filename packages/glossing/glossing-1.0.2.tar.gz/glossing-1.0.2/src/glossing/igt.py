"""Defines IGT model and convenience functions"""

import re
from functools import reduce
from typing import Any, Dict, List, Optional


class IGT:
    """A single line of IGT"""

    def __init__(
        self,
        transcription: str,
        segmentation: Optional[str] = None,
        glosses: Optional[str] = None,
        pos_glosses: Optional[str] = None,
        translation: Optional[str] = None,
    ):
        self.transcription = transcription
        self.segmentation = segmentation
        self.glosses = glosses
        self.pos_glosses = pos_glosses
        self.translation = translation
        self.should_segment = True

    @classmethod
    def from_dict(cls, d: Dict[str, Optional[str]]):
        if "transcription" not in d or not isinstance(d["transcription"], str):
            raise ValueError("Dict must contain `transcription` key at minimum!")
        return cls(
            transcription=d["transcription"],  # type: ignore
            segmentation=d.get("segmentation", None),
            glosses=d.get("glosses", None),
            pos_glosses=d.get("pos_glosses", None),
            translation=d.get("translation", None),
        )

    def as_dict(self) -> dict[str, Any]:
        d = {"transcription": self.transcription, "translation": self.translation}
        if self.segmentation is not None:
            d["segmentation"] = self.segmentation
        if self.glosses is not None:
            d["glosses"] = self.glosses
        if self.pos_glosses is not None:
            d["pos_glosses"] = self.glosses
        return d

    def __repr__(self):
        return f"Trnsc:\t{self.transcription}\nSegm:\t{self.segmentation}\nGloss:\t{self.glosses}\nTrnsl:\t{self.translation}\n\n"

    # region Convenience Properties
    @property
    def word_glosses_list(self) -> List[str]:
        """Returns a list of the glosses, split by words"""
        if self.glosses is None:
            raise ValueError("`glosses` not set on example!")
        return gloss_string_to_word_glosses(self.glosses)

    @property
    def glosses_list(self) -> List[str]:
        """Returns a list of the glosses, split by morphemes and including word boundaries"""
        if self.glosses is None:
            raise ValueError("`glosses` not set on example!")
        return gloss_string_to_morpheme_glosses(self.glosses)

    @property
    def morphemes_list(self) -> List[str]:
        """Returns the segmented list of morphemes, if possible"""
        if self.segmentation is None:
            raise ValueError("Cannot provide morphemes for non-segmented IGT!")
        words = re.findall(DEFAULT_WORD_REGEX, self.segmentation)
        words = [word.split("-") for word in words]
        words = [[morpheme for morpheme in word if morpheme != ""] for word in words]
        words = [word for word in words if word != []]
        morphemes = reduce(lambda a, b: a + ["[SEP]"] + b, words)
        return morphemes

    # endregion


# Helper utils for splitting up glosses

DEFAULT_WORD_REGEX = r"[\w?]+(?:[-=.\w?])*[\w?]+|\w"


def gloss_string_to_word_glosses(gloss_string: str) -> List[str]:
    return re.findall(DEFAULT_WORD_REGEX, gloss_string)


def gloss_string_to_morpheme_glosses(gloss_string: str) -> List[str]:
    word_glosses = gloss_string_to_word_glosses(gloss_string)
    glosses = [re.split("-|=", word) for word in word_glosses]

    # Remove empty glosses introduced by faulty segmentation
    # glosses = [
    #     [gloss for gloss in word_glosses if gloss != ""] for word_glosses in glosses
    # ]
    # glosses = [word_glosses for word_glosses in glosses if word_glosses != []]

    # Add separator for word boundaries
    glosses = (
        reduce(lambda a, b: a + ["[SEP]"] + b, glosses) if len(glosses) > 0 else []
    )

    return glosses
