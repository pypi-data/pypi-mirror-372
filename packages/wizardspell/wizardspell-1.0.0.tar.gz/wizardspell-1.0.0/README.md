<img src="https://raw.githubusercontent.com/textwizard-dev/WizardSpell/main/asset/WizardSpell%20Banner.png"
     alt="WizardSpell Banner" width="800" height="300">

---
# WizardSpell

[![PyPI - Version](https://img.shields.io/pypi/v/wizardspell.svg)](https://pypi.org/project/wizardspell/)
[![PyPI - Downloads/month](https://img.shields.io/pypi/dm/wizardspell.svg?label=PyPI%20downloads)](https://pypistats.org/packages/wizardspell)
[![License](https://img.shields.io/pypi/l/wizardspell.svg)](https://github.com/textwizard-dev/wizardspell/blob/main/LICENSE)

**WizardSpell** is a Python library for Dictionary-based spell checking with Unicode-aware tokenization and light text normalization. Supports 62 languages via compressed Marisa-Trie dictionaries. Returns a compact report with the total number of misspellings and the list of offending tokens.

---

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Spell Checking](#spell-checking)
  - [Behavior](#behavior)
  - [Parameters](#parameters)
  - [Return value](#return-value)
  - [Examples](#examples)
  - [Custom dictionary directory & mmap](#custom-dictionary-directory--mmap)
  - [Operational notes](#operational-notes)
  - [Available dictionaries](#available-dictionaries)
- [License](#license)
- [Resources](#resources)
- [Contact & Author](#contact--author)

---

## Installation

Requires Python 3.9+.

```bash
pip install wizardspell
```

---

## Quick start

```python
import wizardspell as ws

res = ws.spell_checking("Thiss sentense has a typo.", language="en")
print(res)
```

---

## Spell Checking

### Behavior

- Normalizes common Unicode quirks (e.g., smart quotes, zero-width joiners).
- Ignores numbers and leading/trailing punctuation when deciding correctness.
- Treats `'` / `’` variants as equivalent.
- Looks up each token against the selected language dictionary.

### Parameters

| **Parameter** | **Description** |
|---|---|
| `text` | (*str*) Raw input text. |
| `language` | (*str*, default `"en"`) ISO-639 code. |
| `dict_dir` | (*str \| Path \| None*) Directory containing one or more `*.marisa.zst` (or decompressed `*.marisa`) dictionaries. If `None`: uses a per-user cache directory and **auto-downloads** the required dictionary if missing. |
| `use_mmap` | (*bool*, default `False`) **True** → memory-map the on-disk `.marisa` file (lowest RAM; fastest startup). **False** → load the entire trie into RAM (higher RAM; highest steady-state throughput). |

### Return value

`dict` with:

- `errors_count` – `int` total misspellings  
- `errors` – `list[str]` of misspelled tokens (normalized/case-folded)

```python
import wizardspell as ws

check = ws.spell_checking("Thiss sentense has a typo.", language="en")
print(check)
```

**Output**
```json
{"errors_count": 2, "errors": ["thiss", "sentense"]}
```

### Examples

**Basic**
```python
import wizardspell as ws

res = ws.spell_checking("Thiss sentense has a typo.", language="en")
print(res)
```

**Output**
```json
{"errors_count": 2, "errors": ["thiss", "sentense"]}
```

**Italian example**
```python
import wizardspell as ws
print(ws.spell_checking("Queso è un tes , di preva.", language="it"))
```

**Output**
```json
{"errors_count": 3, "errors": ["queso", "tes", "preva."]}
```

### Custom dictionary directory & mmap

```python
import wizardspell as ws
from pathlib import Path

res = ws.spell_checking(
    "Coloar centre thetre",
    language="en",
    dict_dir=Path("~/WizardSpell_dicts"),
    use_mmap=True,
)
print(res)
```

**Output**
```json
{"errors_count": 2, "errors": ["coloar", "thetre"]}
```

### Operational notes

- **Cache location** (when `dict_dir=None`): a per-user data directory is used. You can override it via the first existing of:
  `WIZARDSPELL_DATA_DIR` / `WIZARDSPELL_DICT_DIR` / `WIZARDSPELL_HOME` (environment variables).
- **Auto-download**: when a dictionary is missing and `dict_dir` is not set, WizardSpell downloads the compressed `*.marisa.zst` once and reuses it subsequently.
- **File formats**:
  - `*.marisa.zst` files are decompressed on the fly (into memory) or to an adjacent `*.marisa` file when `use_mmap=True`.
  - If you already have an uncompressed `*.marisa` file in `dict_dir`, it is used directly.
- **Performance**:
  - `use_mmap=True` → minimal RAM, fastest startup; excellent for large dictionaries or constrained environments.
  - `use_mmap=False` → maximal throughput once loaded; best when RAM is plentiful.
- **Chinese** requires `jieba`; all other languages work out-of-the-box.
- Output tokens in `errors` are **normalized/case-folded**; they may differ in casing from the original text.

### Available dictionaries

| **Code** | **Language** | **Code** | **Language** |
|---|---|---|---|
| `af` | Afrikaans | `an` | Aragonese |
| `ar` | Arabic | `as` | Assamese |
| `be` | Belarusian | `bg` | Bulgarian |
| `bn` | Bengali | `bo` | Tibetan |
| `br` | Breton | `bs` | Bosnian |
| `ca` | Catalan | `cs` | Czech |
| `da` | Danish | `de` | German |
| `el` | Greek | `en` | English |
| `eo` | Esperanto | `es` | Spanish |
| `fa` | Persian | `fr` | French |
| `gd` | Scottish Gaelic | `gn` | Guarani |
| `gu` | Gujarati (`gu_IN`) | `he` | Hebrew |
| `hi` | Hindi | `hr` | Croatian |
| `id` | Indonesian | `is` | Icelandic |
| `it` | Italian | `ja` | Japanese |
| `kmr` | Kurmanji Kurdish | `kn` | Kannada |
| `ku` | Central Kurdish | `lo` | Lao |
| `lt` | Lithuanian | `lv` | Latvian |
| `mr` | Marathi | `nb` | Norwegian Bokmål |
| `ne` | Nepali | `nl` | Dutch |
| `nn` | Norwegian Nynorsk | `oc` | Occitan |
| `or` | Odia | `pa` | Punjabi |
| `pl` | Polish | `pt` | Portuguese (EU) |
| `ro` | Romanian | `ru` | Russian |
| `sa` | Sanskrit | `si` | Sinhala |
| `sk` | Slovak | `sl` | Slovenian |
| `sq` | Albanian | `sr` | Serbian |
| `sv` | Swedish | `sw` | Swahili |
| `ta` | Tamil | `te` | Telugu |
| `th` | Thai | `tr` | Turkish |
| `uk` | Ukrainian | `vi` | Vietnamese |

---

## License

[AGPL-3.0-or-later](LICENSE)

## Resources

- [PyPI Package](https://pypi.org/project/wizardspell/)
- [Documentation](https://wizardspell.readthedocs.io/en/latest/)
- [GitHub Repository](https://github.com/textwizard-dev/wizardspell)

## Contact & Author

**Author:** Mattia Rubino  
**Email:** <textwizard.dev@gmail.com>
