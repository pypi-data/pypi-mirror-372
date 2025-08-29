# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from .wizard_spell import WizardSpell

_wizard = WizardSpell()

spell_checking   = _wizard.spell_checking


__all__ = [
    "WizardSpell",
    'spell_checking',

]
