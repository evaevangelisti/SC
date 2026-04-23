import json
from pathlib import Path
from typing import Any

from tqdm import tqdm


class Mapper:
    """ """

    def __init__(
        self,
        input_path: Path,
    ):
        """
        Initialize the Mapper with the path to the input Wiktextract JSONL file.

        Args:
            input_path (Path): Path to the Wiktextract JSONL file containing lemmas and senses.
        """
        self._input_path: Path = input_path

    @staticmethod
    def _safe_load(
        string: str,
    ) -> dict[str, Any]:
        """
        Safely load a JSON string, returning an empty dictionary if parsing fails.

        Args:
            string (str): The JSON string to parse.

        Returns:
            dict[str, Any]: The parsed JSON object, or an empty dictionary if parsing fails.
        """
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            return {}

    def _build_mappings(
        self,
        mappings_path: Path,
    ) -> dict[str, dict[str, str]]:
        """
        Build a mapping dictionary from the mappings JSONL file.

        Args:
            mappings_path (Path): Path to the mappings JSONL file.

        Returns:
            dict[str, dict[str, str]]: A dictionary mapping lemma IDs to their corresponding sense-to-translation mappings.
        """
        mappings: dict[str, dict[str, str]] = {}

        with mappings_path.open(encoding="utf-8") as file:
            for line in file:
                entry = self._safe_load(line)
                if not entry:
                    continue

                entry_id: str = entry.get("id", "")

                if entry_id in mappings:
                    mappings[entry_id] = {}
                    continue

                raw_mapping: dict[str, str] | None = entry.get("mapping")
                if isinstance(raw_mapping, dict):
                    mappings.setdefault(entry_id, raw_mapping)

        return mappings

    def associate_translations(
        self,
        mappings_path: Path,
    ) -> list[dict[str, Any]]:
        """
        Associate translations with senses based on the provided mappings.

        Args:
            mappings_path (Path): Path to the mappings JSONL file.

        Returns:
            list[dict[str, Any]]: A list of lemma entries with associated translations for each sense, based on the provided mappings.
        """
        lemmas: list[dict[str, Any]] = []

        mappings: dict[str, dict[str, str]] = self._build_mappings(
            mappings_path,
        )

        with (
            self._input_path.open(encoding="utf-8") as file,
            tqdm(
                desc="Associating",
                unit=" lines",
            ) as pbar,
        ):
            for line in file:
                lemma_entry: dict[str, Any] = self._safe_load(line)
                if not lemma_entry:
                    pbar.update(1)
                    continue

                lemma_id: str = lemma_entry.get("id", "")
                mapping: dict[str, str] = mappings.get(lemma_id, {}) if mappings else {}

                translation_map: dict[str, dict[str, list[str]]] = lemma_entry.get(
                    "translations",
                    {},
                )

                translation_keys: list[str] = [
                    key for key in translation_map.keys() if isinstance(key, str)
                ]

                senses: list[dict[str, Any]] = []

                for i, sense in enumerate(lemma_entry.get("senses", []), start=1):
                    translations: dict[str, list[str]] = {}

                    mapped: str | None = mapping.get(f"F{i}")

                    raw_translations: dict[str, list[str]] | None = None
                    if mapped and mapped.startswith("S"):
                        try:
                            index: int = int(mapped[1:]) - 1
                            if 0 <= index < len(translation_keys):
                                raw_translations = translation_map.get(
                                    translation_keys[index]
                                )
                        except ValueError:
                            pass

                    if raw_translations:
                        for language, words in raw_translations.items():
                            if not isinstance(words, list):
                                continue

                            translations.setdefault(language, [])
                            for word in words:
                                if word not in translations[language]:
                                    translations[language].append(word)

                    sense_entry: dict[str, Any] = sense

                    if translations:
                        sense_entry["translations"] = translations

                    senses.append(sense_entry)

                lemma_entry["senses"] = senses
                lemmas.append(lemma_entry)

                pbar.update(1)

        return lemmas

    def associate_wordnet_definitions(
        self,
        mappings_path: Path,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
