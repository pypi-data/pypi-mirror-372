# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from .text_wizard import TextWizard
from .wizard_ner.wizard_ner import EntitiesResult, Entity, TokenAnalysis

_wizard = TextWizard()

extract_text       = _wizard.extract_text
extract_text_azure  = _wizard.extract_text_azure
extract_entities   = _wizard.extract_entities
clean_html         = _wizard.clean_html
clean_xml          = _wizard.clean_xml
clean_csv          = _wizard.clean_csv
correctness_text   = _wizard.correctness_text
lang_detect        = _wizard.lang_detect
analyze_text_statistics    = _wizard.analyze_text_statistics
text_similarity    = _wizard.text_similarity
beutifull_html     = _wizard.beutifull_html
html_to_markdown   = _wizard.html_to_markdown


__all__ = [
    "TextWizard",
    "extract_text",
    "extract_text_azure",
    "extract_entities",
    "clean_html",
    "clean_xml",
    "clean_csv",
    "EntitiesResult",
    "Entity",
    "TokenAnalysis",
    'correctness_text',
    'lang_detect',
    'analyze_text_statistics',
    'text_similarity',
    'beutifull_html',
    'html_to_markdown'
]
