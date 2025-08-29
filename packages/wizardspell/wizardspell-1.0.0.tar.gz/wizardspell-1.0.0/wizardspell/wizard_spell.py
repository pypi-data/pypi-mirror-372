# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from pathlib import Path
from typing import Union, Dict, Any


from wizardspell.wizard_analyze_text.wizard_correctness.correctness import CorrectnessAnalyzer


class WizardSpell:

    @staticmethod
    def spell_checking(
            text: str,
            language: str = "en",
            dict_dir: Union[str, Path, None] = None,
            use_mmap: bool = False,
    ) -> Dict[str, Any]:
        """
          Spell-check text using compressed MARISA dictionaries (40+ languages).

          Parameters
          ----------
          text : str
              Input text to analyze (Unicode, non-empty).
          language : str, default "en"
              ISO-639 code or variant alias (e.g., "en", "it", "de").
              • `zh` requires the optional `jieba` package.
              • `ja` uses a dedicated lexical trie.
              See `LANG_INFO` for the supported set.
          dict_dir : str | pathlib.Path | None, optional
              Directory containing *.marisa.zst / *.marisa dictionaries.
              • If None: use the per-user data directory and **auto-download**
                missing files (no prompt).
              • If set: **no network access** – files must already exist.
          use_mmap : bool, default False
              If True, memory-map the `.marisa` file (lower RAM; slightly slower first access).
              If False, load the trie fully into RAM.

          Returns
          -------
          dict
              {"errors_count": int, "errors": list[str]}
              Note: the error list may contain duplicates if the same misspelling
              appears multiple times.

          Examples
          --------
          >>> ws.spell_checking("Thiss sentense has a typo.", language="en")
          {'errors_count': 2, 'errors': ['thiss', 'sentense']}

          >>> # Offline with local dictionaries + memory-mapping
          >>> ws.spell_checking("color colour", language="en", dict_dir="dictionaries", use_mmap=True)
          """       
        analyzer = CorrectnessAnalyzer(
            language,
            _dict_dir=dict_dir,
            use_mmap=use_mmap,
        )
        return analyzer.run(text)
    
