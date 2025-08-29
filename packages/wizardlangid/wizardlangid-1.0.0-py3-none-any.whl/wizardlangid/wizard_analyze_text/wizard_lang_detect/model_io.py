# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
import tempfile
import json
import os

import zstandard as zstd
import marisa_trie
from pathlib import Path

from wizardlangid.wizard_analyze_text.wizard_lang_detect._utils import SEP

_THIS_DIR     = Path(__file__).resolve().parent
PROFILES_DIR  = _THIS_DIR / "profiles_trie_kn"
ADDONS_DIR    = _THIS_DIR / "lang_addons"

DIACRITIC_PATH       = ADDONS_DIR / "diacritic_map.json"
ARABIC_SIG_PATH      = ADDONS_DIR / "arabic_signature_letters.json"
SIG_PROFILES_DIR     = ADDONS_DIR / "profiles_trie_signature"
LETTER_FREQ_PATH     = ADDONS_DIR / "letter_freq.json"
ADDONS_PROFILES_PATH = ADDONS_DIR / "profiles.json"

SIG_ORDERS: Tuple[int, ...] = (2, 3, 4)
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


def _read_json_any(path_like: Any) -> dict:
    try:
        is_file = getattr(path_like, "is_file", None)
        if callable(is_file) and not is_file():
            return {}

        read_bytes = getattr(path_like, "read_bytes", None)
        if not callable(read_bytes):
            with open(os.fspath(path_like), "rb") as fp:
                data = fp.read()
        else:
            data = read_bytes()

        name = getattr(path_like, "name", "")
        if data.startswith(ZSTD_MAGIC) or str(name).endswith(".zst"):
            data = zstd.decompress(data)

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        return json.loads(text)
    except Exception:
        return {}


@dataclass
class LangProfiles:
    profile_dir: Any   # Path | Traversable
    cache_dir: Optional[Any] = None
    use_mmap: bool = False
    _mem: Dict[int, marisa_trie.RecordTrie] = field(default_factory=dict, init=False)

    def load(self, order: int) -> marisa_trie.RecordTrie:
        if order in self._mem:
            return self._mem[order]

        comp_path = self.profile_dir / str(order) / "fused.trie.zst"
        if not comp_path.is_file():
            raise FileNotFoundError(f"Missing profile: {comp_path}")

        if self.use_mmap:
            if self.cache_dir is None:
                raise ValueError("use_mmap=True but cache_dir is None")

            raw_bytes = comp_path.read_bytes()
            raw_path = (self.cache_dir / str(order) / "fused.trie")
            raw_path_parent = os.fspath(raw_path.parent)
            os.makedirs(raw_path_parent, exist_ok=True)
            with open(os.fspath(raw_path), "wb") as fp:
                fp.write(zstd.decompress(raw_bytes))

            trie = marisa_trie.RecordTrie("B")
            trie.mmap(os.fspath(raw_path))
        else:
            raw_bytes = comp_path.read_bytes()
            decomp = zstd.decompress(raw_bytes)
            tmp = tempfile.NamedTemporaryFile(delete=False, prefix=f"marisa_{order}_", suffix=".trie")
            try:
                tmp.write(decomp)
                tmp.flush()
                tmp.close()
                trie = marisa_trie.RecordTrie("B")
                trie.load(tmp.name)
            finally:
                try:
                    os.unlink(tmp.name)
                except PermissionError:
                    pass

        self._mem[order] = trie
        return trie

    def get(self, order: int) -> marisa_trie.RecordTrie:
        return self.load(order)

    def preload(self, orders=(1, 2, 3, 4, 5)) -> None:
        for n in orders:
            try:
                self.load(n)
            except FileNotFoundError:
                continue

    def clear_memory_cache(self) -> None:
        self._mem.clear()


@dataclass
class SigProfiles:
    base_dir: Any
    tries: Dict[int, marisa_trie.RecordTrie] = field(default_factory=dict, init=False)

    def load(self, n: int) -> marisa_trie.RecordTrie:
        if n in self.tries:
            return self.tries[n]

        comp = self.base_dir / str(n) / "fused.sig.trie.zst"
        if not comp.is_file():
            raise FileNotFoundError(f"Signature trie missing: {comp}")

        raw = comp.read_bytes()
        data = zstd.decompress(raw)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".trie")
        try:
            tmp.write(data)
            tmp.flush()
            tmp.close()
            t = marisa_trie.RecordTrie("H")
            t.load(tmp.name)
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

        self.tries[n] = t
        return t


@dataclass
class Model:
    langs: List[str]
    orders: Tuple[int, ...]
    tries: Dict[int, marisa_trie.RecordTrie]
    scale: int
    diacritics: Dict[str, set] | None = None
    letter_freq: Dict[str, Dict[str, float]] | None = None
    stop_pairs: Dict[str, Set[Tuple[str, str]]] | None = None
    char_bigram_stats: Dict[str, Dict[str, float | int]] | None = None
    tfidf_unigram: Dict[str, Dict[str, float]] | None = None
    arabic_signatures: Dict[str, Set[str]] | None = None
    sig_tries: Dict[int, marisa_trie.RecordTrie] | None = None

    def q_of(self, lang: str, gram: str, n: int) -> int:
        trie = self.tries.get(n)
        if trie is None:
            return 255
        key = f"{lang}{SEP}{gram}"
        rec = trie.get(key)
        if not rec:
            return 255
        return int(rec[0][0])


# ====== FACTORY ======
def load_model(
    profiles_dir: Any = PROFILES_DIR,          
    cache_dir: Optional[Any] = None,           
    use_mmap: bool = False,
    *,
    diacritic_path: Any = DIACRITIC_PATH,      
    letter_freq_path: Any = LETTER_FREQ_PATH,  
    addons_profiles_path: Any = ADDONS_PROFILES_PATH,  
    arabic_sig_path: Any = ARABIC_SIG_PATH,   
    sig_profiles_dir: Any = SIG_PROFILES_DIR, 
    sig_orders: Tuple[int, ...] = SIG_ORDERS,
) -> Model:

    meta_path_zst = profiles_dir / "meta.json.zst"
    meta_path_json = profiles_dir / "meta.json"
    meta = _read_json_any(meta_path_zst) or _read_json_any(meta_path_json)
    if not meta:
        raise FileNotFoundError("Meta not found or unreadable in profiles_trie_kn/ (meta.json[.zst])")

    missing = [k for k in ("orders", "SCALE", "langs") if k not in meta]
    if missing:
        raise KeyError(f"Incomplete goals, keys missing: {missing}")

    orders = tuple(int(o) for o in meta["orders"])
    scale  = int(meta["SCALE"])
    langs  = list(meta["langs"])

    profiles = LangProfiles(profile_dir=profiles_dir, cache_dir=cache_dir, use_mmap=use_mmap)
    tries: Dict[int, marisa_trie.RecordTrie] = {}
    for n in orders:
        try:
            tries[n] = profiles.get(n)
        except FileNotFoundError:
            continue

    # add-on
    diacritics_raw = _read_json_any(diacritic_path)
    diacritics = {L: set(diacritics_raw.get(L, "")) for L in langs} if diacritics_raw else None

    letter_freq = _read_json_any(letter_freq_path) or None

    addons = _read_json_any(addons_profiles_path) or {}
    stop_pairs: Dict[str, Set[Tuple[str, str]]] = {}
    char_bigram_stats: Dict[str, Dict[str, float | int]] = {}
    tfidf_unigram: Dict[str, Dict[str, float]] = {}

    for L in langs:
        p = addons.get(L, {}) or {}
        tfidf = p.get("tfidf_unigram", {}) or {}
        tfidf_unigram[L] = {k: float(v) for k, v in tfidf.items()} if tfidf else {}

        sp_list = p.get("stop_pairs", []) or []
        stop_pairs[L] = {
            (it.get("a", ""), it.get("b", ""))
            for it in sp_list
            if it.get("a") and it.get("b")
        }

        cb = p.get("char_bigram", {}) or {}
        char_bigram_stats[L] = {
            "entropy_bits": float(cb.get("entropy_bits", 0.0)),
            "distinct_bigrams": int(cb.get("distinct_bigrams", 0)),
            "n80": int(cb.get("n80", 0)),
        }

    arabic_sigs_raw = _read_json_any(arabic_sig_path) or {}
    arabic_signatures = {L: set(arabic_sigs_raw.get(L, [])) for L in langs if arabic_sigs_raw.get(L)}

    sig_tries: Dict[int, marisa_trie.RecordTrie] = {}
    try:
        sp = SigProfiles(sig_profiles_dir)
        for n in sig_orders:
            try:
                sig_tries[n] = sp.load(n)
            except FileNotFoundError:
                pass
    except Exception:
        sig_tries = {}

    return Model(
        langs=langs,
        orders=orders,
        tries=tries,
        scale=scale,
        diacritics=diacritics,
        letter_freq=letter_freq,
        stop_pairs=stop_pairs or None,
        char_bigram_stats=char_bigram_stats or None,
        tfidf_unigram=tfidf_unigram or None,
        arabic_signatures=arabic_signatures or None,
        sig_tries=sig_tries or None,
    )


__all__ = [
    "PROFILES_DIR","ADDONS_DIR","DIACRITIC_PATH","ARABIC_SIG_PATH","SIG_PROFILES_DIR",
    "LETTER_FREQ_PATH","ADDONS_PROFILES_PATH","SIG_ORDERS",
    "LangProfiles","SigProfiles","Model","load_model","_read_json_any",
]
