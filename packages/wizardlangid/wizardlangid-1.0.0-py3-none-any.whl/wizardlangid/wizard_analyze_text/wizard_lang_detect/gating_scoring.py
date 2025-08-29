# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
from typing import Dict, Tuple, List
from collections import Counter
import math
import regex as rx

from wizardlangid.wizard_analyze_text.wizard_lang_detect._utils import (
    RX_WORD, RX_LETTERS, PAD, ST, EN,
    LangConfig, DEFAULT_CFG, PER_LANG, scripts_for_lang,
    effective_neutral_for_lang, line_script_share,
    char_ngrams, affix_ngrams, IBERIAN_SET, SOUTH_SLAVIC_LATIN,
    SLAVIC_CONFUSION_SET, TIBETAN_PAIR, ARABIC_GROUP, HARD_DIACRITICS,
    CYR_EXCLUSIVE, letter_hist, is_cyr,
)

from wizardlangid.wizard_analyze_text.wizard_lang_detect.hints import iberian_hints as _iberian_hints
from wizardlangid.wizard_analyze_text.wizard_lang_detect.hints import south_slavic_hints as _south_slavic_hints

ORDERS_TO_USE = (2, 3, 4, 5)
AFFIX_ON_ALPHA = True
USE_SIG_TIEBREAK_DZ_BO = True
SOFTMAX_TEMP = 10.0
OOV_PENALTY = 255
SIG_MIN_HITS = 3
SIG_CAP = 5.0

BIGRAM_WEIGHT_ULTRA = 1.8
SHORT_LEN_THRESHOLD = 60
BIGRAM_WEIGHT_SHORT = 1.35
BIGRAM_WEIGHT_LONG  = 1.10
AFFIX_BONUS_SHORT   = 1.15
AFFIX_BONUS_LONG    = 1.00

HARD_DIAC_BONUS_SHORT = 2.8
HARD_DIAC_BONUS_LONG  = 1.6
EXCL_BONUS_SHORT = 2.2
EXCL_BONUS_LONG  = 1.1

RARE_CYRILLIC = {'ab', 'av', 'ce', 'kv', 'os', 'tt', 'ba'}
RARE_CYRILLIC_PENALTY_SHORT = 1.2
RARE_CYRILLIC_PENALTY_LONG  = 1.6

NEGATIVE_CHARS = {
    "sl": {"ć", "đ"},
    "ty": {"\u0327", "m\u0327", "l\u0304", "n\u0304", "ṃ", "ļ", "ō"},
    "to": {"\u0327", "m\u0327", "l\u0304", "n\u0304", "ṃ", "ļ", "ō"},
    "lv": {"m\u0327", "l\u0304", "n\u0304", "ṃ", "ō", "ḷ"},
}
NEG_CHAR_PEN_SHORT = 2.2
NEG_CHAR_PEN_LONG  = 1.3

UNIQUE_SIG = {
    "kr": {"ƙ", "Ƙ"},
    "kv": {"ӧ"},
    "mh": {"\u004D\u0327","m\u0327","\u0327","ṃ","l\u0304","n\u0304","ō","ḷ"},
    "nv": {"ł", "ʼ", "ą", "į", "ń"},
}

# SEP trie key
SEP = "\u0001"

# VI diacritics set 
VI_DIAC_SET = set("ăâêôơưĂÂÊÔƠƯàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệ"
                  "ìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵđ")

MORPH_SUFFIX = {
    "ro": ("ului","elor","ilor","ate","ele"),
    "pl": ("owie","ami","ego","ych"),
    "pt": ("ções","mente"),
    "tr": ("lar","ler","dır","dir","tır","tir","dur","dür"),
}
MORPH_BONUS_SHORT = {"ro": 0.30, "pl": 0.25, "pt": 0.20, "tr": 0.20}


HIRA_RE   = rx.compile(r"\p{Script=Hiragana}")
KATA_RE   = rx.compile(r"\p{Script=Katakana}")
HANGUL_RE = rx.compile(r"\p{Script=Hangul}")
LATIN_RE  = rx.compile(r"\p{Script=Latin}")
CYR_RE    = rx.compile(r"\p{Script=Cyrillic}")

def _exclusive_hits(text_norm: str, L: str) -> int:
    S = CYR_EXCLUSIVE.get(L)
    return sum(text_norm.count(ch) for ch in S) if S else 0

def _hard_diacritic_hits(text_norm: str, L: str) -> int:
    S = HARD_DIACRITICS.get(L)
    return sum(text_norm.count(ch) for ch in S) if S else 0

def _unique_sig_hits(text: str) -> Dict[str, int]:
    out = {}
    for L, chars in UNIQUE_SIG.items():
        n = sum(text.count(ch) for ch in chars)
        if n:
            out[L] = n
    return out

def _diacritic_hits(text: str, diacritics_map: Dict[str, set] | None) -> Dict[str, int]:
    if not diacritics_map:
        return {}
    present = {ch for ch in text if not ch.isascii()}
    hits = {}
    for L, chars in diacritics_map.items():
        if not chars:
            continue
        n = len(present & chars)
        if n:
            hits[L] = n
    return hits

def _signature_hits(text: str, signatures: Dict[str, set] | None) -> Dict[str, int]:
    if not signatures:
        return {}
    present = set(text)
    return {L: sum(1 for ch in sigs if ch in present) for L, sigs in signatures.items()}

def _char_bigrams_only(text_norm: str) -> Counter:
    c = Counter()
    for g in char_ngrams(text_norm, 2):
        if (PAD in g) or (ST in g) or (EN in g):
            continue
        if sum(1 for ch in g if RX_LETTERS.match(ch)) != 2:
            continue
        c[g] += 1
    return c

def _coverage_ratio_ngrams(model, cnts: Counter, L: str, n: int = 2) -> float:
    seen = hit = 0
    for g, c in cnts.items():
        if (PAD in g) or (ST in g) or (EN in g):
            continue
        if sum(1 for ch in g if RX_LETTERS.match(ch)) != n:
            continue
        seen += c
        if model.q_of(L, g, n) != OOV_PENALTY:
            hit += c
    return hit / max(1, seen)

def _word_pairs(text_norm: str) -> Counter:
    toks = RX_WORD.findall(text_norm)
    c = Counter()
    for a, b in zip(toks, toks[1:]):
        c[(a, b)] += 1
    return c

def _char_bigram_entropy_and_n80(text_norm: str) -> Tuple[float, int, int]:
    s = text_norm
    if len(s) < 2:
        return 0.0, 0, 0
    bcnt = Counter(s[i:i + 2] for i in range(len(s) - 1))
    total = sum(bcnt.values())
    if total == 0:
        return 0.0, 0, 0
    H = 0.0
    for c in bcnt.values():
        p = c / total
        H -= p * math.log(p, 2)
    target = 0.80 * total
    cum = n80_text = 0
    for i, (_, c) in enumerate(bcnt.most_common(), 1):
        cum += c
        if cum >= target:
            n80_text = i
            break
    return H, len(bcnt), n80_text

def _sig_bonus_per_lang(model, text_norm: str, langs: List[str],
                        orders: Tuple[int, ...] = (2, 3, 4)) -> Dict[str, float]:
    if not getattr(model, "sig_tries", None):
        return {}
    grams_by_n: Dict[int, Counter] = {n: Counter() for n in orders}
    for n in orders:
        for g in char_ngrams(text_norm, n):
            if (PAD in g) or (ST in g) or (EN in g):
                continue
            if sum(1 for ch in g if RX_LETTERS.match(ch)) != n:
                continue
            grams_by_n[n][g] += 1

    out = {L: 0.0 for L in langs}
    hits = {L: 0 for L in langs}

    for n in orders:
        trie = model.sig_tries.get(n)
        if not trie:
            continue
        cnts = grams_by_n[n]
        if not cnts:
            continue
        for g, c in cnts.items():
            key_suffix = f"{SEP}{g}"
            for L in langs:
                rec = trie.get(f"{L}{key_suffix}")
                if not rec:
                    continue
                qv = rec[0][0] if isinstance(rec[0], (list, tuple)) else rec[0]
                lo = (qv / 100.0) - 100.0
                if lo > 0:
                    out[L] += lo * c
                    hits[L] += 1

    for L in out.keys():
        if hits[L] < SIG_MIN_HITS:
            out[L] = 0.0
        else:
            out[L] = min(out[L] / hits[L], SIG_CAP)
    return out

def _evidence_strength(text_norm: str, model, top1_lang: str, dq_top2: float) -> Tuple[float, int, float]:
    letters = sum(1 for ch in text_norm if RX_LETTERS.match(ch))
    bi = _char_bigrams_only(text_norm)
    cov2 = _coverage_ratio_ngrams(model, bi, top1_lang, n=2) if bi else 0.0
    uniq_bi = len(bi)
    e_len    = min(1.0, letters / 24.0)
    e_margin = 1.0 - math.exp(-max(0.0, dq_top2) / 12.0)
    e_cov    = cov2
    e_uniq   = min(1.0, uniq_bi / 28.0)
    E = 0.30*e_len + 0.30*e_margin + 0.25*e_cov + 0.15*e_uniq
    return float(max(0.0, min(1.0, E))), letters, cov2

def _vi_diac_density(text_norm: str) -> float:
    letters = [ch for ch in text_norm if RX_LETTERS.match(ch)]
    if not letters:
        return 0.0
    vi = sum(1 for ch in letters if ch in VI_DIAC_SET)
    return vi / max(1, len(letters))

def _morph_hits(tokens: List[str]) -> Dict[str, int]:
    hits = {"ro": 0, "pl": 0, "pt": 0, "tr": 0}
    for w in tokens:
        for L, suffs in MORPH_SUFFIX.items():
            if any(w.endswith(s) for s in suffs):
                hits[L] += 1
    return hits

# ── candidate gating (unchanged logic, micro-opt) ─────────────────────────────
def candidate_langs(text_norm: str, model) -> List[str]:
    letters = [ch for ch in text_norm if RX_LETTERS.match(ch)]
    base = model.langs[:]

    if len(letters) < 20:
        latin_cnt = sum(1 for ch in letters if LATIN_RE.match(ch))
        cyr_cnt   = sum(1 for ch in letters if CYR_RE.match(ch))
        thr = max(1, int(0.6 * len(letters)))
        if latin_cnt >= thr:
            base = [L for L in model.langs if L in {
                "en","es","fr","de","it","pt","nl","pl","ro","sv","da","fi","no","tr","cs","hu"
            }] or model.langs
        elif cyr_cnt >= thr:
            base = [L for L in model.langs if L in {'ru','uk','bg','sr','be','mk'}] or model.langs

    cand: List[str] = []
    for L in base:
        cfg = PER_LANG.get(L, LangConfig()).with_defaults(DEFAULT_CFG)
        scr = scripts_for_lang(L)
        neutral = effective_neutral_for_lang(L, scr, cfg.neutral_extra)
        share = line_script_share(text_norm, scr, neutral=neutral)
        if share >= cfg.min_line_script_share:
            cand.append(L)

    u_hits = _unique_sig_hits(text_norm)
    for L, n in u_hits.items():
        if L in model.langs and L not in cand:
            cand.append(L)

    if len(letters) < 30:
        if "·" in text_norm and "ca" in model.langs and "ca" not in cand:
            cand.append("ca")
        if "ñ" in text_norm and "es" in model.langs and "es" not in cand:
            cand.append("es")

        ih = _iberian_hints(text_norm)
        for L in ("es", "gl", "an", "ca"):
            if ih.get(L, 0) > 0 and L in model.langs and L not in cand:
                cand.append(L)

        slh = _south_slavic_hints(text_norm)
        for L in ("bs", "hr", "sr", "sl", "cs"):
            if slh.get(L, 0) > 0 and L in model.langs and L not in cand:
                cand.append(L)

    hits = _diacritic_hits(text_norm, getattr(model, "diacritics", None))
    if hits:
        for Lx in ("mh", "kr", "kv", "nv"):
            hh = _hard_diacritic_hits(text_norm, Lx)
            if hh:
                hits[Lx] = hits.get(Lx, 0) + hh
        protected = set(u_hits.keys())
        diac_cand = [L for L in cand if hits.get(L, 0) >= 2 or L in protected]
        if diac_cand:
            ARABIC_G = {'ar', 'fa', 'ur', 'ps', 'sd', 'ug', 'ks', 'ku'}
            if any(L in ARABIC_G for L in cand):
                if len(diac_cand) <= 2 and 'ar' not in diac_cand and 'ar' in cand:
                    pass
                else:
                    if len(diac_cand) < len(cand):
                        cand = diac_cand
            else:
                if 0 < len(diac_cand) <= max(5, len(cand) // 3):
                    cand = diac_cand

    mh_u = u_hits.get("mh", 0)
    mh_strong = (mh_u >= 2) or ("ṃ" in text_norm) or ("n\u0304" in text_norm) or ("m\u0327" in text_norm) or ("ō" in text_norm)
    if mh_strong:
        cand = [L for L in cand if L not in ("lv", "ty", "to")] or cand

    if USE_SIG_TIEBREAK_DZ_BO and getattr(model, "sig_tries", None) and {'dz', 'bo'}.issubset(cand):
        sig = _sig_bonus_per_lang(model, text_norm, ['dz', 'bo'], orders=(2, 3, 4))
        dz_b, bo_b = sig.get('dz', 0.0), sig.get('bo', 0.0)
        if dz_b >= 0.12 or bo_b >= 0.12:
            if dz_b - bo_b >= 0.08:
                cand = [L for L in cand if L != 'bo']
            elif bo_b - dz_b >= 0.08:
                cand = [L for L in cand if L != 'dz']

    return cand or base


def score_text(model, text_norm: str, langs: List[str]) -> List[Tuple[str, float]]:
    diacritics       = getattr(model, "diacritics", None)
    letter_freq_map  = getattr(model, "letter_freq", None)
    stop_pairs_map   = getattr(model, "stop_pairs", None)
    char_bigram_stats= getattr(model, "char_bigram_stats", None)
    tfidf_unigram    = getattr(model, "tfidf_unigram", None)
    arabic_signatures= getattr(model, "arabic_signatures", None)
    sig_tries        = getattr(model, "sig_tries", None)
    tries_by_n       = model.tries  # più corto

    char_suf_by_n: Dict[int, List[Tuple[str, int]]]  = {n: [] for n in ORDERS_TO_USE}
    affx_suf_by_n: Dict[int, List[Tuple[str, int]]]  = {n: [] for n in ORDERS_TO_USE}

    for n in ORDERS_TO_USE:
        cnts = Counter()
        for g in char_ngrams(text_norm, n):
            cnts[g] += 1
        if cnts:
            char_suf_by_n[n] = [(f"{SEP}{g}", c) for g, c in cnts.items()]

    tokens = RX_WORD.findall(text_norm)
    single_short_token = (len(tokens) == 1 and len(tokens[0]) <= 6)
    use_affixes = AFFIX_ON_ALPHA and not single_short_token
    if use_affixes:
        for n in ORDERS_TO_USE:
            cnts = Counter()
            for w in tokens:
                if len(w) < 2:
                    continue
                if len(w) + 2 < n:
                    continue
                for g in affix_ngrams(w, n):
                    cnts[g] += 1
            if cnts:
                affx_suf_by_n[n] = [(f"{SEP}{g}", c) for g, c in cnts.items()]

    short = len(text_norm) < SHORT_LEN_THRESHOLD
    letters_cnt = sum(1 for ch in text_norm if RX_LETTERS.match(ch))
    ultra_short = (letters_cnt <= 8)

    diac_hits    = _diacritic_hits(text_norm, diacritics)
    text_letters = letter_hist(text_norm)
    Ltot_letters = sum(text_letters.values())
    sp_counts    = _word_pairs(text_norm)
    H_text, _, n80_text = _char_bigram_entropy_and_n80(text_norm)
    sig_hits     = _signature_hits(text_norm, arabic_signatures) if arabic_signatures else {}
    any_sig_hit  = any(sig_hits.values()) if sig_hits else False
    sig_bonus_map= _sig_bonus_per_lang(model, text_norm, langs, orders=(2,3,4)) if sig_tries else {}
    ss_cluster   = len(set(langs) & SOUTH_SLAVIC_LATIN) >= 2
    u_hits       = _unique_sig_hits(text_norm)

    ib_hints = _iberian_hints(text_norm) if any(Lx in IBERIAN_SET for Lx in langs) else {}
    sl_hints = _south_slavic_hints(text_norm) if any(Lx in SLAVIC_CONFUSION_SET for Lx in langs) else {}

    letters = [ch for ch in text_norm if RX_LETTERS.match(ch)]
    L_letters = max(1, len(letters))
    share_hira = sum(1 for ch in letters if HIRA_RE.match(ch)) / L_letters
    share_kata = sum(1 for ch in letters if KATA_RE.match(ch)) / L_letters
    share_hang = sum(1 for ch in letters if HANGUL_RE.match(ch)) / L_letters

    morph_hits = _morph_hits(tokens) if short else {"ro":0,"pl":0,"pt":0,"tr":0}

    diac_bonus_unit = 0.7 if short else 0.4
    chi2_lambda     = 0.002 if short else 0.005
    stop_pair_bonus = 1.2 if short else 0.8
    stop_pair_norm  = max(1, sum(sp_counts.values()))
    entropy_lambda  = 0.08 if short else 0.12
    n80_lambda      = 0.002 if short else 0.003
    tfidf_lambda    = 0.15 if short else 0.5
    sig_bonus_unit  = 0.9 if short else 0.6

    scored: List[Tuple[str, float]] = []

    for L in langs:
        total_q = 0.0
        tot_cnt = 0.0

        for n in ORDERS_TO_USE:
            base2 = (BIGRAM_WEIGHT_ULTRA if (ultra_short and n == 2)
                     else (BIGRAM_WEIGHT_SHORT if (short and n == 2)
                           else (BIGRAM_WEIGHT_LONG if n == 2 else 1.0)))
            # char
            if char_suf_by_n[n]:
                t = tries_by_n[n]; prefix = L
                for suf, c in char_suf_by_n[n]:
                    rec = t.get(prefix + suf)
                    q = rec[0][0] if rec else OOV_PENALTY
                    total_q += base2 * (q * c); tot_cnt += c
            # affissi
            if affx_suf_by_n[n]:
                affix_mult = AFFIX_BONUS_SHORT if short else AFFIX_BONUS_LONG
                if ss_cluster and n in (4, 5):
                    affix_mult *= (1.20 if short else 1.10)
                t = tries_by_n[n]; prefix = L
                for suf, c in affx_suf_by_n[n]:
                    rec = t.get(prefix + suf)
                    q = rec[0][0] if rec else OOV_PENALTY
                    total_q += base2 * affix_mult * (q * c); tot_cnt += c

        avg_q = (total_q / tot_cnt) if tot_cnt else float("inf")

        if u_hits.get(L, 0) > 0:
            avg_q += - (2.6 if short else 1.4) * u_hits[L]

        if ib_hints and L in IBERIAN_SET:
            avg_q += - ((0.75 if short else 0.45) * ib_hints.get(L, 0))

        if sl_hints and L in SLAVIC_CONFUSION_SET:
            avg_q += - ((0.80 if short else 0.50) * sl_hints.get(L, 0))

        if is_cyr(L) and char_suf_by_n.get(2):
            cov2 = _coverage_ratio_ngrams(model, _char_bigrams_only(text_norm), L, n=2)
            thr = 0.50 if short else 0.62
            if cov2 < thr:
                avg_q += (0.8 if short else 1.8) * (thr - cov2) + 0.3

        h_hits = _hard_diacritic_hits(text_norm, L)
        if h_hits:
            avg_q += - (HARD_DIAC_BONUS_SHORT if short else HARD_DIAC_BONUS_LONG) * h_hits

        if L in NEGATIVE_CHARS:
            neg = sum(text_norm.count(ch) for ch in NEGATIVE_CHARS[L])
            if neg:
                avg_q += (NEG_CHAR_PEN_SHORT if short else NEG_CHAR_PEN_LONG) * neg

        if diac_hits and diac_hits.get(L, 0) > 0:
            avg_q += - diac_bonus_unit * diac_hits[L]

        ex_hits = _exclusive_hits(text_norm, L)
        if ex_hits:
            avg_q += - (EXCL_BONUS_SHORT if short else EXCL_BONUS_LONG) * ex_hits

        if L in ARABIC_GROUP and sig_hits:
            if sig_hits.get(L, 0) > 0:
                avg_q += - sig_bonus_unit * sig_hits[L]
            elif any_sig_hit:
                avg_q += +0.2

        if sig_bonus_map and TIBETAN_PAIR.issubset(set(langs)) and L in TIBETAN_PAIR:
            lam = 0.08 if short else 0.16
            avg_q += - lam * sig_bonus_map.get(L, 0.0)

        if L == "ja":
            avg_q += -0.6 * max(0.0, (share_hira + share_kata) - 0.10)
        elif L == "ko":
            avg_q += -0.8 * max(0.0, share_hang - 0.08)

        if L == "vi":
            dens = _vi_diac_density(text_norm)
            if dens >= 0.12:
                avg_q += - (1.2 if short else 0.8) * (dens - 0.12) * 5.0

        if letter_freq_map and L in letter_freq_map and Ltot_letters >= 8:
            chi2 = _chi2_penalty(text_letters, letter_freq_map[L])
            avg_q += chi2_lambda * chi2

        if stop_pairs_map and sp_counts:
            S = stop_pairs_map.get(L, set())
            if S:
                sp_hits = sum(sp_counts.get(p, 0) for p in S)
                dens = sp_hits / stop_pair_norm
                if dens > 0:
                    avg_q += - stop_pair_bonus * dens

        if char_bigram_stats:
            st = char_bigram_stats.get(L, {})
            H_L = float(st.get("entropy_bits", 0.0))
            n80_L = int(st.get("n80", 0))
            if H_L:
                avg_q += entropy_lambda * abs(H_text - H_L)
            if n80_text and n80_L:
                avg_q += n80_lambda * abs(n80_text - n80_L)

        if tfidf_unigram:
            cov_map = tfidf_unigram.get(L, {})
            cov = float(cov_map.get("cov@5000", 0.0)) if cov_map else 0.0
            avg_q += tfidf_lambda * (1.0 - cov)

        if L in RARE_CYRILLIC and _hard_diacritic_hits(text_norm, L) == 0:
            avg_q += (RARE_CYRILLIC_PENALTY_SHORT if short else RARE_CYRILLIC_PENALTY_LONG)

        if short and L in morph_hits and morph_hits[L] > 0:
            avg_q += - MORPH_BONUS_SHORT[L] * morph_hits[L]

        scored.append((L, float(avg_q)))

    scored.sort(key=lambda kv: kv[1])
    return scored

def _chi2_penalty(text_hist: Dict[str, int], lang_freq: Dict[str, float]) -> float:
    N = sum(text_hist.values()) or 1
    pen = 0.0
    for ch, obs in text_hist.items():
        exp = N * lang_freq.get(ch, 0.0)
        if exp > 0:
            d = obs - exp
            pen += (d * d) / exp
        else:
            pen += 0.4
    return pen

__all__ = [
    "candidate_langs","score_text",
    "_evidence_strength","_sig_bonus_per_lang",
    "_coverage_ratio_ngrams","_char_bigram_entropy_and_n80",
]
