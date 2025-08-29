# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
from typing import List, Tuple
import math
import regex as rx

from wizardlangid.wizard_analyze_text.wizard_lang_detect._utils import (
    normalize_text, LANG_PRIOR, RARE_LATIN, RARE_CYRILLIC, RX_LETTERS,
    HARD_DIACRITICS, CYR_EXCLUSIVE, IBERIAN_SET
)
from wizardlangid.wizard_analyze_text.wizard_lang_detect.gating_scoring import (
    candidate_langs, score_text, _evidence_strength
)
from wizardlangid.wizard_analyze_text.wizard_lang_detect.hints import (
    HINTS, iberian_hints, precomputed_flags
)

BASE_T = 10.0

def _hard_diacritic_hits(text_norm: str, L: str) -> int:
    S = HARD_DIACRITICS.get(L)
    return sum(text_norm.count(ch) for ch in S) if S else 0

def _exclusive_hits(text_norm: str, L: str) -> int:
    S = CYR_EXCLUSIVE.get(L)
    return sum(text_norm.count(ch) for ch in S) if S else 0


EN_STOPS = {"the","is","of","and","to","in","that","it","for","on"}
def _looks_english_ascii(s: str) -> bool:
    toks = [t for t in rx.findall(r"[a-z]+", s)]
    if any(t in EN_STOPS for t in toks):
        return True
    has_common_bi = any(b in s for b in ("th","he","in","er","an","re"))
    return has_common_bi

def detect_lang(
    model,
    text: str,
    top_k: int = 3,
    hints = HINTS,
) -> List[Tuple[str, float]]:
    text_norm = normalize_text(text, lang=None)
    if not text_norm:
        return []

    # 1) gating + 2) scoring
    cand = candidate_langs(text_norm, model)
    scored = score_text(model, text_norm, cand)
    if not scored:
        return []
    scored.sort(key=lambda kv: kv[1])

    best_q = scored[0][1]
    top1_lang = scored[0][0]
    dq = (scored[1][1] - scored[0][1]) if len(scored) >= 2 else 999.0

    # 3) evidenza
    E, _, _ = _evidence_strength(text_norm, model, top1_lang, dq)

    ih = iberian_hints(text_norm)
    strong_gl = ih.get("gl", 0) >= 2
    strong_an = ih.get("an", 0) >= 2
    strong_ca = ih.get("ca", 0) >= 2 or ("·" in text_norm) or ("l·l" in text_norm) or (" ny " in f" {text_norm} ")
    non_es_signal = strong_gl or strong_an or strong_ca

    T = max(6.0, min(12.0, BASE_T - 3.0*E - 0.08*max(0.0, dq)))
    beta = 2.0 - 1.2 * E
    if non_es_signal:
        beta = min(beta, 0.6)

    def _has_hard(L: str) -> bool:
        return (_hard_diacritic_hits(text_norm, L) > 0) or (_exclusive_hits(text_norm, L) > 0)

    letters_cnt = sum(1 for ch in text_norm if RX_LETTERS.match(ch))
    if E < 0.40 and text_norm.isascii():
        major = {L for L in cand if LANG_PRIOR.get(L, 1.0) >= 1.5}
        keep = [L for L in cand if (L in major) or _has_hard(L)]
        if keep and len(keep) < len(cand):
            cand = keep
            scored = [t for t in scored if t[0] in cand]
            scored.sort(key=lambda kv: kv[1])
            best_q = scored[0][1]
            top1_lang = scored[0][0]
            dq = (scored[1][1] - scored[0][1]) if len(scored) >= 2 else 999.0
            E, _, _ = _evidence_strength(text_norm, model, top1_lang, dq)
            T = max(6.0, min(12.0, BASE_T - 3.0*E - 0.08*max(0.0, dq)))
            beta = 2.0 - 1.2 * E
            if non_es_signal:
                beta = min(beta, 0.6)

    micro_ascii = (text_norm.isascii() and letters_cnt <= 6)

    def _eff_prior(L: str) -> float:
        p = LANG_PRIOR.get(L, 1.0)
        if non_es_signal and L in IBERIAN_SET:
            p = 1.0
        if L in RARE_LATIN and not _has_hard(L):
            if E < 0.25:
                p *= 0.20
            elif E < 0.45:
                p *= 0.35
        if L in RARE_CYRILLIC and not _has_hard(L):
            if E < 0.25:
                p *= 0.30
            elif E < 0.55:
                p *= 0.45

        if micro_ascii and L == 'en':
            has_non_en_marks = any(ch in text_norm for ch in "ñçàèìòùáéíóúäöüßœğşłřńśžčćđțșîâă")
            if not has_non_en_marks and _looks_english_ascii(text_norm):
                p *= 1.8
        return p

    CONFUSION_SETS = (
        frozenset({"bs","hr","sr","sl","cs"}),
        frozenset({"id","ms","su"}),
        frozenset({"oc","pt","fr","ca"}),
        frozenset({"nn","no"}),
        frozenset({"ty","mi","to"}),
        frozenset({"rn","rw"}),
        frozenset({"pl","cs","sk"}),
        frozenset({"tr","az"}),
        frozenset({"vi","id","ms"}),
        frozenset({"af","nl"}),
        frozenset({"tl","id","ms"}),
        frozenset({"hi","mr","ne","sa"}),
    )
    active = any(len(set(cand) & S) >= 2 for S in CONFUSION_SETS)

    use_hints = hints if (hints is not None and active) else None
    flags = precomputed_flags(text_norm) if use_hints is not None else None

    logits: List[Tuple[str, float]] = []
    for L, q in scored:
        prior = _eff_prior(L)
        base = -(q - best_q) / T + beta * math.log(prior)
        if use_hints is not None:
            base += use_hints(
                L=L, base_q=q, best_q=best_q, prior=prior, text=text_norm, T=T, beta=beta, flags=flags
            )
        logits.append((L, base))

    logits.sort(key=lambda kv: kv[1], reverse=True)
    k = min(top_k, len(logits))
    mx = logits[0][1]
    exps = [math.exp(l - mx) for _, l in logits[:k]]
    Z = sum(exps) or 1.0
    probs = [float(e / Z) for e in exps]
    return [(logits[i][0], probs[i]) for i in range(k)]


__all__ = ["detect_lang", "BASE_T"]
