from dataclasses import dataclass
from enum import Enum


@dataclass
class Sentence:
    """
    A sentence illustrating a sense of a lemma.
    """

    sentence: str
    word_offsets: list[tuple[int, int]]


@dataclass
class Example(Sentence):
    """
    An example sentence illustrating a sense of a lemma.
    """

    pass


@dataclass
class Quotation(Sentence):
    """
    A quotation sentence illustrating a sense of a lemma.
    """

    reference: str


@dataclass
class WiktionarySense:
    """
    A sense of a lemma extracted from Wiktionary.
    """

    sense_order: int
    definition: str
    sentences: list[Sentence]


@dataclass
class WordNetSense:
    """
    A sense of a lemma extracted from WordNet.
    """

    id: str
    definition: str
    synonyms: list[str]


class POS(Enum):
    """
    Part of speech tags.
    """

    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adj"
    ADVERB = "adv"

    @classmethod
    def from_wiktionary(
        cls,
        code: str,
    ) -> "POS | None":
        """
        Convert a Wiktionary POS code to a POS enum member.

        Args:
            code (str): A Wiktionary POS code.

        Returns:
            POS | None: The corresponding POS enum member.
        """
        return {
            "noun": cls.NOUN,
            "verb": cls.VERB,
            "adj": cls.ADJECTIVE,
            "adv": cls.ADVERB,
        }.get(code)

    @classmethod
    def from_wordnet(
        cls,
        code: str,
    ) -> "POS | None":
        """
        Convert a WordNet POS code to a POS enum member.

        Args:
            code (str): A WordNet POS code.

        Returns:
            POS | None: The corresponding POS enum member.
        """
        return {
            "n": cls.NOUN,
            "v": cls.VERB,
            "a": cls.ADJECTIVE,
            "r": cls.ADVERB,
            "s": cls.ADJECTIVE,
        }.get(code)
