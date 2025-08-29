# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Dict, Set, Iterable
import regex as rx
import re
import unicodedata as ud

# ====== REGEX ======
RX_SPACE   = re.compile(r"\s+")
RX_ZWJZWNJ = rx.compile(r"[\u200c\u200d]+")
RX_ZERO_WIDTH = rx.compile(r"[\u200b\u2060]")
RX_WORD    = rx.compile(r"\p{Letter}+(?:['’-]\p{Letter}+)*")
RX_LETTERS = rx.compile(r"\p{Letter}")
RX_MARK    = rx.compile(r"\p{Mark}")

# ====== SENTINEL & BORDI ======
PAD, ST, EN = "\u0002", "\u0001", "\u0003"
SEP = "\u0001" 

# ====== ZWNJ policy ======
KEEP_ZWNJ_LANGS = {'fa', 'ur', 'ps', 'ks', 'ug', 'sd', 'ku'}

# ====== NEUTRAL PER SCRIPT ======
TIBETAN_NEUTRAL   = {"\u0F0B", "\u0F0C"}
DEVANAGARI_NEUTRAL= {"\u0964", "\u0965"}
HEBREW_NEUTRAL    = {"\u05BE"}
ARABIC_NEUTRAL    = {"\u060C", "\u061B", "\u061F", "\u0640"}
JAPANESE_NEUTRAL  = {"\u3001", "\u3002", "\u30FB"}
KHMER_NEUTRAL     = {"\u17D4", "\u17D5"}
THAI_NEUTRAL      = {"\u0E2F", "\u0E46"}
LAO_NEUTRAL       = {"\u0EAF"}
MYANMAR_NEUTRAL   = {"\u104A", "\u104B"}
CJK_NEUTRAL_COMMON= {"\uFF0C", "\uFF0E"}
BASE_NEUTRAL      = {PAD, ST, EN, " ", "\t"}

# ====== PRIOR LINGUE ======
LANG_PRIOR = {
    "en": 3.0, "es": 2.5, "zh": 2.5, "ar": 2.5, "pt": 2.0, "ru": 2.5, "fr": 2.5,
    "de": 2.5, "it": 2.5, "ja": 2.5, "ko": 2.5, "hi": 1.6, "bn": 1.6, "tr": 1.6,
    "uk": 1.6, "pl": 1.6, "nl":1.6,
    "ce": 0.35, "ab": 0.4, "av": 0.2, "os": 0.4, "ba": 0.4, "tt": 0.4, "wa": 0.4,
    "li": 0.3, "kv": 0.3, "an": 0.2, "gl": 0.2,
}

# ====== GRUPPI LINGUE / SCRIPT ======
CYRILLIC  = {'ab', 'av', 'ru', 'uk', 'sr', 'bg', 'mk', 'kk', 'ky', 'kv', 'be', 'mn', 'tt', 'ba', 'tg', 'ce', 'cv'}
GREEK     = {'el'}
ARABIC_G  = {'ar', 'fa', 'ur', 'ps', 'sd', 'ug', 'ks', 'ku'}
DEVANAGARI= {'hi', 'mr', 'ne', 'sa'}
BENGALI   = {'bn', 'as'}
ETHIOPIC  = {'am'}
TIBETAN   = {'dz', 'bo'}
GUJARATI  = {'gu'}
HEBREW    = {'he'}
ARMENIAN  = {'hy'}
GEORGIAN  = {'ka'}
KHMER     = {'km'}
THAI      = {'th'}
LAO       = {'lo'}
MYANMAR   = {'my'}
SINHALA   = {'si'}
TAMIL     = {'ta'}
TELUGU    = {'te'}
KANNADA   = {'kn'}
MALAYALAM = {'ml'}
ORIYA     = {'or'}
GURMUKHI  = {'pa'}
HAN       = {'zh', 'ja', 'ko'}
HIRAGANA  = {'ja'}
KATAKANA  = {'ja'}
HANGUL    = {'ko'}
YI        = {'ii'}      # Sichuan Yi
THAANA    = {'dv'}      # Dhivehi

# lingue multi-script
MULTISCRIPT = {
    'sr': {'Latin', 'Cyrillic'},
    'kk': {'Cyrillic', 'Latin'},
    'uz': {'Latin', 'Cyrillic'},
    'ja': {'Han', 'Hiragana', 'Katakana'},
    'ko': {'Hangul', 'Han'},
    'iu': {'Latin', 'Canadian_Aboriginal'},
    'tt': {'Cyrillic', 'Latin'},
    'kr': {'Latin', 'Arabic'},
    'ks': {'Arabic', 'Devanagari'},
    'ku': {'Latin', 'Arabic'},
}

CORE_LATIN = {
    "en", "es", "fr", "de", "it", "pt", "nl", "pl", "ro", "sv", "da", "fi", "no", "tr", "cs", "hu"
}
RARE_LATIN = {
    "ki", "sw", "yo", "zu", "mg", "ht", "gd", "ga", "mt", "fy", "wa", "lb", "rm",
    "tn", "ts", "st", "sn", "ss", "rw", "li", "wa", "lb", "rm"
}

CORE_CYRILLIC = {'ru', 'uk', 'bg', 'sr', 'be', 'mk'}
RARE_CYRILLIC = {'ab', 'av', 'ce', 'kv', 'os', 'tt', 'ba'}

# ISO 639-1
ISO_639_1_CODES = set(
    """aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv
       cy da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he ho hr
       ht hu hy hz ia id ie ig ii ik io is it iu ja jv ka kg ki kj kk kl km kn ko kr ks ku kv kw
       ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms mt my na nb nd ne ng nl nn no nr nv
       ny oc oj om or os pa pi pl ps pt qu rm rn ro rw sa sc sd se sg si sk sl sm sn so sq sr ss st
       su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi yo za zh zu"""
    .split()
)

# ====== SET / GRUPPI PER HINT E CLUSTER ======
IBERIAN_SET = {"es", "gl", "an", "ca"}
SOUTH_SLAVIC_SET = {"bs", "hr", "sr", "sl", "cs"}
SOUTH_SLAVIC_LATIN = frozenset({"bs","hr","sr","sl"})
SLAVIC_CONFUSION_SET = frozenset({"bs","hr","sr","sl","cs"})
TIBETAN_PAIR = frozenset({"bo", "dz"})
ARABIC_GROUP = ARABIC_G  

# ====== DECORATOR ======
DEBUG_ASSERTS = True

def checked(fn):
    def _w(*a, **kw):
        out = fn(*a, **kw)
        if DEBUG_ASSERTS and fn.__name__ == "scripts_for_lang":
            lang = a[0]; s = out
            if lang == "ja":
                assert {"Han", "Hiragana", "Katakana"} <= s, "ja must include Han+Hira+Kata"
            if lang == "ko":
                assert {"Hangul"} <= s, "ko must include Hangul"
        return out
    return _w

# ====== CONFIG ======
@dataclass(frozen=True)
class LangConfig:
    scripts: Set[str] | None = None
    min_line_script_share: float = 0.60
    min_ngram_script_share: float = 0.80
    enable_affixes: bool = True
    neutral_extra: Set[str] = frozenset()

    def with_defaults(self, defaults: "LangConfig") -> "LangConfig":
        return replace(
            defaults,
            scripts=self.scripts or defaults.scripts,
            min_line_script_share=self.min_line_script_share or defaults.min_line_script_share,
            min_ngram_script_share=self.min_ngram_script_share or defaults.min_ngram_script_share,
            enable_affixes=self.enable_affixes if self.enable_affixes is not None else defaults.enable_affixes,
            neutral_extra=(defaults.neutral_extra | self.neutral_extra),
        )

DEFAULT_CFG = LangConfig(
    scripts={'Latin'},
    min_line_script_share=0.60,
    min_ngram_script_share=0.80,
    enable_affixes=True,
    neutral_extra=frozenset()
)


PER_LANG: Dict[str, LangConfig] = {
    # CJK
    'ja': LangConfig(scripts={'Han', 'Hiragana', 'Katakana'}, min_line_script_share=0.55, min_ngram_script_share=0.80, enable_affixes=False, neutral_extra=frozenset(JAPANESE_NEUTRAL | CJK_NEUTRAL_COMMON)),
    'ko': LangConfig(scripts={'Hangul', 'Han'}, min_line_script_share=0.60, min_ngram_script_share=0.80, enable_affixes=False),
    'zh': LangConfig(scripts={'Han'}, min_line_script_share=0.60, min_ngram_script_share=0.85, enable_affixes=False, neutral_extra=frozenset(CJK_NEUTRAL_COMMON)),

    # Indic
    'hi': LangConfig(scripts={'Devanagari'}, neutral_extra=frozenset(DEVANAGARI_NEUTRAL)),
    'mr': LangConfig(scripts={'Devanagari'}, neutral_extra=frozenset(DEVANAGARI_NEUTRAL)),
    'ne': LangConfig(scripts={'Devanagari'}, neutral_extra=frozenset(DEVANAGARI_NEUTRAL)),
    'sa': LangConfig(scripts={'Devanagari'}, neutral_extra=frozenset(DEVANAGARI_NEUTRAL)),
    'bn': LangConfig(scripts={'Bengali'}),
    'as': LangConfig(scripts={'Bengali'}),
    'gu': LangConfig(scripts={'Gujarati'}),
    'pa': LangConfig(scripts={'Gurmukhi'}),
    'or': LangConfig(scripts={'Oriya'}),
    'ta': LangConfig(scripts={'Tamil'}),
    'te': LangConfig(scripts={'Telugu'}),
    'kn': LangConfig(scripts={'Kannada'}),
    'ml': LangConfig(scripts={'Malayalam'}),
    'si': LangConfig(scripts={'Sinhala'}),

    # Tibetano
    'dz': LangConfig(scripts={'Tibetan'}, min_line_script_share=0.65, min_ngram_script_share=0.85, enable_affixes=False, neutral_extra=frozenset(TIBETAN_NEUTRAL)),
    'bo': LangConfig(scripts={'Tibetan'}, min_line_script_share=0.65, min_ngram_script_share=0.85, enable_affixes=False, neutral_extra=frozenset(TIBETAN_NEUTRAL)),

    # Semitiche
    'he': LangConfig(scripts={'Hebrew'}, min_ngram_script_share=0.75, neutral_extra=frozenset(HEBREW_NEUTRAL)),
    'ar': LangConfig(scripts={'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'fa': LangConfig(scripts={'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'ur': LangConfig(scripts={'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'ps': LangConfig(scripts={'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'sd': LangConfig(scripts={'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'ug': LangConfig(scripts={'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'ks': LangConfig(scripts={'Arabic', 'Devanagari'}, neutral_extra=frozenset(ARABIC_NEUTRAL | DEVANAGARI_NEUTRAL)),
    'ku': LangConfig(scripts={'Latin', 'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),

    # Altri script
    'am': LangConfig(scripts={'Ethiopic'}),
    'hy': LangConfig(scripts={'Armenian'}),
    'ka': LangConfig(scripts={'Georgian'}),
    'km': LangConfig(scripts={'Khmer'}, neutral_extra=frozenset(KHMER_NEUTRAL)),
    'th': LangConfig(scripts={'Thai'}, neutral_extra=frozenset(THAI_NEUTRAL)),
    'lo': LangConfig(scripts={'Lao'}, neutral_extra=frozenset(LAO_NEUTRAL)),
    'my': LangConfig(scripts={'Myanmar'}, neutral_extra=frozenset(MYANMAR_NEUTRAL)),

    # Slavi/greco/misti
    'el': LangConfig(scripts={'Greek'}),
    'sr': LangConfig(scripts={'Latin', 'Cyrillic'}),
    'kk': LangConfig(scripts={'Cyrillic', 'Latin'}),
    'uz': LangConfig(scripts={'Latin', 'Cyrillic'}),

    # Inuit + vari
    'iu': LangConfig(scripts={'Latin', 'Canadian_Aboriginal'}),
    'kr': LangConfig(scripts={'Latin', 'Arabic'}, neutral_extra=frozenset(ARABIC_NEUTRAL)),
    'os': LangConfig(scripts={'Cyrillic'}),
    'ti': LangConfig(scripts={'Ethiopic'}),
    'yi': LangConfig(scripts={'Hebrew'}, neutral_extra=frozenset(HEBREW_NEUTRAL)),
    'tt': LangConfig(scripts={'Cyrillic', 'Latin'}),
    'ii': LangConfig(scripts={'Yi'}, min_line_script_share=0.70, enable_affixes=False),
    'dv': LangConfig(scripts={'Thaana'}, min_line_script_share=0.70, enable_affixes=False),

    'mh': LangConfig(scripts={'Latin'}),
    'na': LangConfig(scripts={'Latin'}),
    'ch': LangConfig(scripts={'Latin'}),
}

# ====== HARD DIACRITICS / ESCLUSIVE CYR (scoring/gating) ======
HARD_DIACRITICS = {
    'bs': {'ć', 'č', 'đ', 'ž', 'š'},
    'hr': {'ć', 'č', 'đ', 'ž', 'š'},
    'ku': {'î', 'û', 'ê', 'Î', 'Û', 'Ê'},
    'mh': {'\u004D\u0327', '\u0327', 'ā', 'ē', 'ī', 'ō', 'ū', 'ļ', 'l̄', 'n̄', 'm̄', 'ṃ', 'ḷ', 'ņ'},
    'kr': {'ƙ', 'Ƙ'},
    'kv': {'ӧ', 'Ӧ', 'ї', 'ӧ̈'},
    'av': {'Ӏ', 'ӏ'},
    'ce': {'Ӏ', 'ӏ'},
    'os': {'ӕ', 'Ӕ'},
    'ab': {'ә', 'ҽ', 'ӡ', 'ҵ', 'қ', 'ҳ', 'ԥ', 'ҭ'},
    'tt': {'ә', 'ө', 'ү', 'җ', 'ң', 'ҥ'},
    'ba': {'ә', 'ө', 'ү', 'ҙ', 'ҫ', 'ғ', 'ҡ', 'ң'},
    'cs': {'ě','ř','ů','ť','ď','ň'},
}
CYR_EXCLUSIVE = {
    'ru': {'ы', 'э', 'ъ', 'ё'},
    'uk': {'і', 'ї', 'є', 'ґ'},
    'be': {'ў', 'і', 'ё', 'э'},
    'bg': {'ъ', 'щ', 'ѝ'},
    'sr': {'ђ', 'ћ', 'ј', 'љ', 'њ', 'џ'},
    'mk': {'ѓ', 'ќ', 'ѕ', 'љ', 'њ', 'ј', 'џ'},
    "kv": {"ӧ"}
}

# ====== CACHE SCRIPT REGEX ======
@lru_cache(maxsize=None)
def _script_re(script: str) -> rx.Pattern:
    return rx.compile(rf"\p{{Script={script}}}")

# ====== MAPPING LINGUA→SCRIPT ======
@checked
def scripts_for_lang(lang: str) -> Set[str]:
    if lang in PER_LANG and PER_LANG[lang].scripts:
        return PER_LANG[lang].scripts
    if lang in MULTISCRIPT:
        return MULTISCRIPT[lang]
    if lang in CYRILLIC:    return {'Cyrillic'}
    if lang in GREEK:       return {'Greek'}
    if lang in ARABIC_G:    return {'Arabic'}
    if lang in DEVANAGARI:  return {'Devanagari'}
    if lang in BENGALI:     return {'Bengali'}
    if lang in ETHIOPIC:    return {'Ethiopic'}
    if lang in TIBETAN:     return {'Tibetan'}
    if lang in GUJARATI:    return {'Gujarati'}
    if lang in HEBREW:      return {'Hebrew'}
    if lang in ARMENIAN:    return {'Armenian'}
    if lang in GEORGIAN:    return {'Georgian'}
    if lang in KHMER:       return {'Khmer'}
    if lang in THAI:        return {'Thai'}
    if lang in LAO:         return {'Lao'}
    if lang in MYANMAR:     return {'Myanmar'}
    if lang in SINHALA:     return {'Sinhala'}
    if lang in TAMIL:       return {'Tamil'}
    if lang in TELUGU:      return {'Telugu'}
    if lang in KANNADA:     return {'Kannada'}
    if lang in MALAYALAM:   return {'Malayalam'}
    if lang in GURMUKHI:    return {'Gurmukhi'}
    if lang in HAN:         return {'Han'}
    if lang in HIRAGANA:    return {'Hiragana'}
    if lang in KATAKANA:    return {'Katakana'}
    if lang in HANGUL:      return {'Hangul'}
    if lang in YI:          return {'Yi'}
    if lang in THAANA:      return {'Thaana'}
    if lang in ISO_639_1_CODES:
        return {'Latin'}
    return set()

# ====== NORMALIZZAZIONE ======
_QUOTE_MAP = str.maketrans({
    "’": "'", "‛": "'", "ʻ": "'", "`": "'", "ʼ": "'"
})

def normalize_text(s: str, lang: str | None) -> str:
    is_ascii = s.isascii()
    if is_ascii:
        s2 = s.translate(_QUOTE_MAP)
        s2 = RX_SPACE.sub(" ", s2).strip().casefold()
        return s2

    s = s.translate(_QUOTE_MAP)
    s = ud.normalize("NFKC", s)
    if "\u200c" in s or "\u200d" in s:
        s = RX_ZWJZWNJ.sub("\u200c", s)
        if lang is None or lang not in KEEP_ZWNJ_LANGS:
            s = s.replace("\u200c", "")
    if "\u200b" in s or "\u2060" in s:
        s = RX_ZERO_WIDTH.sub("", s)
    return RX_SPACE.sub(" ", s).strip().casefold()


# ====== NEUTRAL & SHARE ======
def effective_neutral_for_lang(lang: str, scripts: Set[str], extra: Set[str]) -> Set[str]:
    neutral = set(BASE_NEUTRAL) | set(extra)
    if 'Arabic'    in scripts: neutral |= ARABIC_NEUTRAL
    if 'Tibetan'   in scripts: neutral |= TIBETAN_NEUTRAL
    if 'Devanagari'in scripts: neutral |= DEVANAGARI_NEUTRAL
    if {'Han','Hiragana','Katakana'} & scripts:
        neutral |= JAPANESE_NEUTRAL | CJK_NEUTRAL_COMMON
    if 'Khmer'   in scripts: neutral |= KHMER_NEUTRAL
    if 'Thai'    in scripts: neutral |= THAI_NEUTRAL
    if 'Lao'     in scripts: neutral |= LAO_NEUTRAL
    if 'Myanmar' in scripts: neutral |= MYANMAR_NEUTRAL
    return neutral

def line_script_share(s: str, scripts: Set[str], *, neutral: Set[str]) -> float:
    if not scripts:
        return 1.0
    mats = [_script_re(sc) for sc in scripts] + [_script_re('Inherited')]
    letters = [ch for ch in s if RX_LETTERS.match(ch) and ch not in neutral]
    if not letters:
        return 0.0
    ok = sum(1 for ch in letters if any(m.match(ch) for m in mats))
    return ok / len(letters)

# ====== N-GRAMS ======
def char_ngrams(text: str, n: int) -> Iterable[str]:
    buf = PAD * (n - 1) + text + PAD * (n - 1)
    L = len(buf)
    for i in range(L - n + 1):
        yield buf[i:i + n]

def affix_ngrams(word: str, n: int) -> Iterable[str]:
    w = f"{ST}{word}{EN}"
    buf = PAD * (n - 1) + w + PAD * (n - 1)
    L = len(buf)
    for i in range(L - n + 1):
        yield buf[i:i + n]

# ====== HELPER VARI ======
def letter_hist(text: str) -> Dict[str, int]:
    h: Dict[str, int] = {}
    for ch in text:
        if RX_LETTERS.match(ch):
            h[ch] = h.get(ch, 0) + 1
    return h

def is_cyr(lang: str) -> bool:
    return 'Cyrillic' in scripts_for_lang(lang)

# ====== EXPORT ======
__all__ = [
    # regex & sentinels
    "RX_SPACE","RX_ZWJZWNJ","RX_ZERO_WIDTH","RX_WORD","RX_LETTERS","RX_MARK",
    "PAD","ST","EN","SEP",
    # priors / groups
    "LANG_PRIOR","CYRILLIC","GREEK","ARABIC_G","DEVANAGARI","BENGALI","ETHIOPIC","TIBETAN",
    "GUJARATI","HEBREW","ARMENIAN","GEORGIAN","KHMER","THAI","LAO","MYANMAR","SINHALA",
    "TAMIL","TELUGU","KANNADA","MALAYALAM","ORIYA","GURMUKHI","HAN","HIRAGANA","KATAKANA",
    "HANGUL","YI","THAANA","MULTISCRIPT","CORE_LATIN","RARE_LATIN","CORE_CYRILLIC","RARE_CYRILLIC",
    "ISO_639_1_CODES","IBERIAN_SET","SOUTH_SLAVIC_SET","SOUTH_SLAVIC_LATIN","SLAVIC_CONFUSION_SET",
    "TIBETAN_PAIR","ARABIC_GROUP",
    # configs
    "LangConfig","DEFAULT_CFG","PER_LANG",
    # hard diacritics / esclusivi
    "HARD_DIACRITICS","CYR_EXCLUSIVE",
    # functions
    "scripts_for_lang","normalize_text","effective_neutral_for_lang","line_script_share",
    "char_ngrams","affix_ngrams","letter_hist","is_cyr",
    # misc
    "KEEP_ZWNJ_LANGS","BASE_NEUTRAL","ARABIC_NEUTRAL","TIBETAN_NEUTRAL","DEVANAGARI_NEUTRAL",
    "JAPANESE_NEUTRAL","CJK_NEUTRAL_COMMON","KHMER_NEUTRAL","THAI_NEUTRAL","LAO_NEUTRAL","MYANMAR_NEUTRAL",
    "checked",
]
