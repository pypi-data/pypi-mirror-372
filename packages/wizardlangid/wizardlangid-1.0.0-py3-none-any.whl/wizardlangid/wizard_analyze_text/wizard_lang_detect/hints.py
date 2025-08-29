# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import regex as rx

from wizardlangid.wizard_analyze_text.wizard_lang_detect._utils import RX_WORD

# Iberico
_RX_GL_XVOW = rx.compile(r"\bx[aeiouáéíóú]\w*", flags=rx.VERSION1)
_RX_GL_HAI  = rx.compile(r"\bhai\b", flags=rx.VERSION1)
# Aragonese 'ye' — evita match da 'oye' con lookbehind negativo
_RX_AN_YE   = rx.compile(r"(?<!o)\bye\b", flags=rx.VERSION1)
_RX_AN_ENOA = rx.compile(r"\b(en\s+(o|a))\b", flags=rx.VERSION1)
_RX_AN_DART = rx.compile(r"\bd['’]\s?(o|a|os|as)\b", flags=rx.VERSION1)
_RX_AN_LU   = rx.compile(r"\bluenga\b", flags=rx.VERSION1)
_RX_AN_ARAG = rx.compile(r"\barag[oó]n(és)?\b", flags=rx.VERSION1)
# Catalano
_RX_CA_NY   = rx.compile(r"\b\p{Letter}+ny(?=[aeiouáéíóúàèìòùäëïöü])\p{Letter}*\b", flags=rx.VERSION1)

_CA_STRONG = {
    "els","les","amb","fins","sóc","ets","és","som","sou","són",
    "aquest","aquesta","aquests","aquestes","això","aquí","dels","als","pels","pel"
}
_ES_STRONG = {
    "del","al","los","las","una","unos","unas","este","esta","estos","estas","está","están","hay"
}
_GL_STRONG = {"unha","xente","xeral","xornal"}
# Diacritici latini comuni in GL 
_GL_DIAC = rx.compile(r"[áéíóúñ]", flags=rx.VERSION1)

# Sud-slavo / ceco
_RX_SL_SCINA   = rx.compile(r"\b\w+ščina\b", flags=rx.VERSION1)
_RX_CS_STINA   = rx.compile(r"\b\w+ština\b", flags=rx.VERSION1)
# Ceco forti 
_RX_CS_STRONG_DIAC = rx.compile(r"[ěřůťďň]", flags=rx.VERSION1)

_RX_HR_AUTONYM = rx.compile(r"\bhrvatsk\w*\b", flags=rx.VERSION1)
_RX_HR_REP     = rx.compile(r"\brepublik[ae]\s+hrvatsk[aeio]\b", flags=rx.VERSION1)
_RX_HR_GEONYM  = rx.compile(r"\b(zagreb|dalmat\w*|dubrova\w*)\b", flags=rx.VERSION1)

_RX_BS_ADJ     = rx.compile(r"\bbosansk\w*\b|\bbošnja\w*\b", flags=rx.VERSION1)
_RX_BS_GEO     = rx.compile(r"\bbosn[aeiouy]\b|\bhercegovin\w*\b", flags=rx.VERSION1)

_RX_SR_CYR     = rx.compile(r"[ђћјљњџ]", flags=rx.VERSION1)
_RX_SR_DALI    = rx.compile(r"\bda\s+li\b", flags=rx.VERSION1)
_RX_SR_EKAV    = rx.compile(r"\b(mleko|lepo|vreme|sreć\w*|beograd\w*)\b", flags=rx.VERSION1)

_SL_DUAL_STRONG = {"sva","sta"}
_SL_AUX         = {"sem","si","je","smo","ste","so"}  

_RX_INDONESIA = rx.compile(r"\bindonesi\w*\b", flags=rx.VERSION1)
_RX_MALAYSIA  = rx.compile(r"\bmalaysi\w*\b", flags=rx.VERSION1)
_RX_SEDANGKAN = rx.compile(r"\bsedangkan\b", flags=rx.VERSION1)
_RX_KARENA    = rx.compile(r"\bkarena\b", flags=rx.VERSION1)
_RX_KERANA    = rx.compile(r"\bkerana\b", flags=rx.VERSION1)

_RX_TAHITI = rx.compile(r"\btahiti\b|\bmā’ohi\b|\bfenua\b", flags=rx.VERSION1)
_RX_MAORI_WH = rx.compile(r"\bwh\w+", flags=rx.VERSION1)

_RX_NYNORSK = rx.compile(r"\bnynorsk\b", flags=rx.VERSION1)
_RX_IKKJE   = rx.compile(r"\bikkje\b|\bikkji\b", flags=rx.VERSION1)
_RX_EIN_DEI = rx.compile(r"\bein\b.*\bdei\b", flags=rx.VERSION1)
_RX_IKKE    = rx.compile(r"\bikke\b", flags=rx.VERSION1)

_RX_OCCITAN = rx.compile(r"\boccitan\b|\bl[’']occitan\b|\blenga\b|\bdins\b|\bòc\b", flags=rx.VERSION1)
_RX_PT_TELH = rx.compile(r"(?:\b|\w)(?:ção|ções)\b", flags=rx.VERSION1)
_RX_PT_TOK  = rx.compile(r"\b(e|de|que|do|da|dos|das)\b", flags=rx.VERSION1)

_RX_BURUNDI = rx.compile(r"\bburundi\b|\buburundi\b|\bikirundi\b", flags=rx.VERSION1)
_RX_RWANDA  = rx.compile(r"\brwanda\b|\bkinyarwanda\b|\babanyarwanda\b", flags=rx.VERSION1)

_RX_AFAR   = rx.compile(r"\bafar(-ta)?\b|\bqafar\b", flags=rx.VERSION1)
_RX_KIKONGO= rx.compile(r"\bkikongo\b", flags=rx.VERSION1)
_RX_KILUBA = rx.compile(r"\bkiluba\b|\bluba\b", flags=rx.VERSION1)
_RX_DINE   = rx.compile(r"\bdiné\b|\bdiné bizaad\b", flags=rx.VERSION1)


@dataclass(frozen=True, slots=True)
class HintWeights:
    # slavic block
    w_scina: float = 0.9
    w_stina: float = 0.6
    w_dual:  float = 0.8
    w_sto:   float = 0.7
    w_sta:   float = 0.5
    w_cs_diac: float = 1.1
    w_hr_autonym: float = 1.2
    w_sr_dali: float = 0.7
    w_sl_aux: float = 0.3

    # id/ms
    w_id_indonesia: float = 1.0
    w_id_sedangkan: float = 0.6
    w_id_karena:    float = 0.5
    w_ms_malaysia:  float = 1.0
    w_ms_kerana:    float = 0.6

    # ty/mi
    w_ty_tahiti: float = 1.1
    w_mi_wh:     float = 0.7

    # nn/no
    w_nn_nynorsk: float = 1.2
    w_nn_ikkje:   float = 0.9
    w_nn_ein_dei: float = 0.5
    w_no_ikke:    float = 0.8

    # oc/pt
    w_oc_tokens: float = 1.2
    w_pt_pt:     float = 0.6

    # rn/rw
    w_rn_burundi: float = 1.2
    w_rw_rwanda:  float = 1.2

    # autònimi sporadici
    w_aa_aut: float = 1.0
    w_kg_aut: float = 1.0
    w_lu_aut: float = 0.8
    w_nv_aut: float = 1.0


@dataclass(slots=True)
class LogLinearHints:
    W: HintWeights

    def features(self, text: str, L: str, *, flags: Optional[Dict[str, bool]] = None) -> float:

        s = text; w = self.W; score = 0.0
        toks = set(RX_WORD.findall(s))

        def F(name: str, patt: Optional[rx.Pattern]) -> bool:
            if flags is not None and name in flags:
                return flags[name]
            return bool(patt.search(s)) if patt is not None else False

        if L == "sl":
            if F("sl_scina", _RX_SL_SCINA): score += w.w_scina
            if _SL_DUAL_STRONG & toks:      score += w.w_dual
            if "ki" in toks or (_SL_AUX & toks):
                score += w.w_sl_aux
        elif L == "cs":
            if F("cs_stina", _RX_CS_STINA):       score += w.w_stina
            if F("cs_diac_strong", _RX_CS_STRONG_DIAC):  # forti
                score += w.w_cs_diac
        elif L == "hr":
            if F("hr_aut", _RX_HR_AUTONYM): score += w.w_hr_autonym
            if rx.search(r"\bšto\b", s):    score += w.w_sto
        elif L in ("sr", "bs"):
            if rx.search(r"\bšta\b", s):    score += w.w_sta
            if L == "sr" and (F("sr_cyr", _RX_SR_CYR) or F("sr_dali", _RX_SR_DALI)):
                score += w.w_sr_dali
        elif L == "id":
            if F("id_tok_indonesia", _RX_INDONESIA): score += w.w_id_indonesia
            if F("id_tok_sedangkan", _RX_SEDANGKAN): score += w.w_id_sedangkan
            if F("id_tok_karena", _RX_KARENA):       score += w.w_id_karena
        elif L == "ms":
            if F("ms_tok_malaysia", _RX_MALAYSIA): score += w.w_ms_malaysia
            if F("ms_tok_kerana", _RX_KERANA):     score += w.w_ms_kerana
        elif L == "ty":
            if F("ty_tok_tahiti", _RX_TAHITI): score += w.w_ty_tahiti
        elif L == "mi":
            if F("mi_tok_wh", _RX_MAORI_WH):  score += w.w_mi_wh
        elif L == "nn":
            if F("nn_tok_nynorsk", _RX_NYNORSK): score += w.w_nn_nynorsk
            if F("nn_tok_ikkje", _RX_IKKJE):     score += w.w_nn_ikkje
            if F("nn_tok_ein_dei", _RX_EIN_DEI): score += w.w_nn_ein_dei
        elif L == "no":
            if F("no_tok_ikke", _RX_IKKE):       score += w.w_no_ikke
        elif L == "oc":
            if F("oc_tok", _RX_OCCITAN):         score += w.w_oc_tokens
        elif L == "pt":
            if F("pt_tel", _RX_PT_TELH) or F("pt_tok", _RX_PT_TOK):
                score += w.w_pt_pt
        elif L == "rn":
            if F("rn_tok", _RX_BURUNDI):         score += w.w_rn_burundi
        elif L == "rw":
            if F("rw_tok", _RX_RWANDA):          score += w.w_rw_rwanda
        elif L == "aa":
            if F("aa_tok", _RX_AFAR):            score += w.w_aa_aut
        elif L == "kg":
            if F("kg_tok", _RX_KIKONGO):         score += w.w_kg_aut
        elif L == "lu":
            if F("lu_tok", _RX_KILUBA):          score += w.w_lu_aut
        elif L == "nv":
            if F("nv_tok", _RX_DINE):            score += w.w_nv_aut

        return score

    def __call__(self, *,
                 L: str,
                 base_q: float,
                 best_q: float,
                 prior: float,
                 text: str,
                 T: float = 10.0,
                 beta: float = 1.0,
                 flags: Optional[Dict[str, bool]] = None) -> float:
        from math import log
        return -(base_q - best_q)/T + beta*log(prior) + self.features(text, L, flags=flags)


def _postprocess_hint_scores(h: Dict[str,int], *, cap:int = 6) -> Dict[str,int]:
    for L in list(h.keys()):
        if h[L] > cap:
            h[L] = cap
    return h

def _evidence_mix_bonus(s: str, buckets: Dict[str, List[bool]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for L, flags in buckets.items():
        kinds = sum(1 for b in flags if b)
        out[L] = 0.0
        if kinds >= 2:
            out[L] = 0.5 if len(s) < 60 else 0.8
    return out


def iberian_hints(text: str) -> Dict[str, int]:
    
    s = text
    toks = set(RX_WORD.findall(s))
    h: Dict[str,int] = {"es": 0, "gl": 0, "an": 0, "ca": 0}

    # ES
    if toks & _ES_STRONG:
        h["es"] += 1

    # GL
    if toks & _GL_STRONG:
        h["gl"] += 2
    if _RX_GL_XVOW.search(s):
        h["gl"] += 1
    if _RX_GL_HAI.search(s):
        h["gl"] += 1
    if _GL_DIAC.search(s):
        h["gl"] += 1

    # AN
    if _RX_AN_YE.search(s):
        h["an"] += 3
    if _RX_AN_ENOA.search(s):
        h["an"] += 2
    if _RX_AN_DART.search(s):
        h["an"] += 2
    if _RX_AN_LU.search(s):
        h["an"] += 1
    if _RX_AN_ARAG.search(s):
        h["an"] += 1

    # CA
    if toks & _CA_STRONG:
        h["ca"] += 2
    if _RX_CA_NY.search(s):
        h["ca"] += 1

    buckets = {
        "es": [bool(toks & _ES_STRONG)],
        "gl": [bool(toks & _GL_STRONG), bool(_RX_GL_XVOW.search(s)), bool(_GL_DIAC.search(s)), bool(_RX_GL_HAI.search(s))],
        "an": [bool(_RX_AN_YE.search(s)), bool(_RX_AN_ENOA.search(s) or _RX_AN_DART.search(s)), bool(_RX_AN_LU.search(s) or _RX_AN_ARAG.search(s))],
        "ca": [bool(toks & _CA_STRONG), bool(_RX_CA_NY.search(s))],
    }
    mix = _evidence_mix_bonus(s, buckets)
    for L, bonus in mix.items():
        h[L] += int(round(bonus))

    return _postprocess_hint_scores(h, cap=6)


def south_slavic_hints(text: str) -> Dict[str, int]:

    s = text
    toks = set(RX_WORD.findall(s))
    h: Dict[str,int] = {L: 0 for L in ("bs","hr","sr","sl","cs")}

    # CS
    if _RX_CS_STINA.search(s):
        h["cs"] += 2
    if _RX_CS_STRONG_DIAC.search(s):
        h["cs"] += 3
    if toks & {"český","čeština","praha","praze","který","protože","neboť"}:
        h["cs"] += 1

    # SL
    if _RX_SL_SCINA.search(s):
        h["sl"] += 4
    if _SL_DUAL_STRONG & toks:
        h["sl"] += 3
    if _SL_AUX & toks:
        h["sl"] += 1
    if rx.search(r"\bslovenij[aeo]\b|\bslovensk\w*", s):
        h["sl"] += 2
    if rx.search(r"\bki\b", s):
        h["sl"] += 1

    # HR
    if _RX_HR_AUTONYM.search(s):
        h["hr"] += 5
    if _RX_HR_REP.search(s):
        h["hr"] += 2
    if _RX_HR_GEONYM.search(s):
        h["hr"] += 1
    if rx.search(r"\bšto\b", s):
        h["hr"] += 2

    # BS
    if _RX_BS_ADJ.search(s):
        h["bs"] += 4
    if _RX_BS_GEO.search(s):
        h["bs"] += 1
    if rx.search(r"\bšta\b", s):
        h["bs"] += 1

    # SR
    if _RX_SR_CYR.search(s):
        h["sr"] += 3
    if _RX_SR_DALI.search(s):
        h["sr"] += 2
    if _RX_SR_EKAV.search(s):
        h["sr"] += 2
    if rx.search(r"\bšta\b", s):
        h["sr"] += 1

    buckets = {
        "cs": [bool(_RX_CS_STINA.search(s)), bool(_RX_CS_STRONG_DIAC.search(s))],
        "sl": [bool(_RX_SL_SCINA.search(s)), bool(_SL_DUAL_STRONG & toks), bool(_SL_AUX & toks)],
        "hr": [bool(_RX_HR_AUTONYM.search(s)), bool(_RX_HR_REP.search(s) or _RX_HR_GEONYM.search(s)), bool(rx.search(r"\bšto\b", s))],
        "bs": [bool(_RX_BS_ADJ.search(s)), bool(_RX_BS_GEO.search(s)), bool(rx.search(r"\bšta\b", s))],
        "sr": [bool(_RX_SR_CYR.search(s)), bool(_RX_SR_DALI.search(s)), bool(_RX_SR_EKAV.search(s))],
    }
    mix = _evidence_mix_bonus(s, buckets)
    for L, bonus in mix.items():
        h[L] += int(round(bonus))

    if h["hr"] >= 5 and _RX_BS_GEO.search(s):
        h["bs"] = max(0, h["bs"] - 2)
    if _RX_SL_SCINA.search(s) and h["cs"] >= 2:
        h["cs"] -= 1

    return _postprocess_hint_scores(h, cap=6)


# ───────────────────────────── Flags precomputabili ───────────────────────────
def precomputed_flags(text: str) -> Dict[str, bool]:
    
    s = text
    return {
        # sl/cs/hr/sr
        "sl_scina": bool(_RX_SL_SCINA.search(s)),
        "cs_stina": bool(_RX_CS_STINA.search(s)),
        "cs_diac_strong": bool(_RX_CS_STRONG_DIAC.search(s)),
        "hr_aut":   bool(_RX_HR_AUTONYM.search(s)),
        "sr_cyr":   bool(_RX_SR_CYR.search(s)),
        "sr_dali":  bool(_RX_SR_DALI.search(s)),

        # id/ms
        "id_tok_indonesia": bool(_RX_INDONESIA.search(s)),
        "id_tok_sedangkan": bool(_RX_SEDANGKAN.search(s)),
        "id_tok_karena":    bool(_RX_KARENA.search(s)),
        "ms_tok_malaysia":  bool(_RX_MALAYSIA.search(s)),
        "ms_tok_kerana":    bool(_RX_KERANA.search(s)),

        # ty/mi
        "ty_tok_tahiti": bool(_RX_TAHITI.search(s)),
        "mi_tok_wh":     bool(_RX_MAORI_WH.search(s)),

        # nn/no
        "nn_tok_nynorsk": bool(_RX_NYNORSK.search(s)),
        "nn_tok_ikkje":   bool(_RX_IKKJE.search(s)),
        "nn_tok_ein_dei": bool(_RX_EIN_DEI.search(s)),
        "no_tok_ikke":    bool(_RX_IKKE.search(s)),

        # oc/pt
        "oc_tok": bool(_RX_OCCITAN.search(s)),
        "pt_tel": bool(_RX_PT_TELH.search(s)),
        "pt_tok": bool(_RX_PT_TOK.search(s)),

        # rn/rw
        "rn_tok": bool(_RX_BURUNDI.search(s)),
        "rw_tok": bool(_RX_RWANDA.search(s)),
    }


HINTS = LogLinearHints(HintWeights())

__all__ = [
    "HintWeights",
    "LogLinearHints",
    "iberian_hints",
    "south_slavic_hints",
    "precomputed_flags",
    "HINTS",
]
