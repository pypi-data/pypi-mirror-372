# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from .wizard_lang_id import WizardLangID
from .wizard_ner.wizard_ner import EntitiesResult, Entity, TokenAnalysis

_wizard = WizardLangID()

lang_detect        = _wizard.lang_detect


__all__ = [
    "WizardLangID",
    'lang_detect'
]
