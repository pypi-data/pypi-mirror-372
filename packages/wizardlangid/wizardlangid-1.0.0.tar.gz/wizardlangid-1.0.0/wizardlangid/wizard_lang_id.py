# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path
from typing import Optional


from wizardlangid.wizard_analyze_text.wizard_lang_detect.model_io import load_model, Model

from wizardlangid.wizard_analyze_text.wizard_lang_detect.detect_lang import detect_lang as _detect_lang
import threading


class WizardLangID:
    def __init__(self):
        self._lang_model: Model | None = None
        self._lang_lock = threading.Lock()

    def lang_detect(
        self,
        text: str,
        top_k: int = 3,
        profiles_dir: Optional[Path | str] = None,
        use_mmap: bool = False,
        return_top1: bool = False,
    ):
        """
        Detect the language of *text* using a character n-gram model with gating,
        priors, and linguistic hints. Supports 161 ISO-639-1 languages.

        Parameters
        ----------
        text : str
            Input text (Unicode).
        top_k : int, default 3
            How many candidates to return (softmax-normalised probabilities).
        profiles_dir : Path | str | None
            Optional override for the profiles directory. If None, uses the
            package-bundled defaults.
        use_mmap : bool, default False
            If True, memory-map the profile trie(s) to reduce RAM usage; the very first
            access may be slightly slower. If False, load tries fully into RAM for
            maximum lookup throughput.
        return_top1 : bool, default False
            If True, return only the best language code (str). Otherwise return a list
            of (lang, prob) pairs of length ≤ top_k.

        Returns
        -------
        str | list[tuple[str, float]]
            • If ``return_top1=True`` → best language code (or ``""`` if none).
            • Else → list of ``(lang, prob)`` sorted by probability (desc).

        Notes
        -----
        - The model is loaded lazily on first call and cached on the instance.
        - Pass ``profiles_dir`` if you keep profiles outside the packaged defaults.
        """
        # lazy-load + cache (thread-safe)
        if self._lang_model is None:
            with self._lang_lock:
                if self._lang_model is None:
                    if profiles_dir is not None:
                        profiles_dir = Path(profiles_dir)
                        self._lang_model = load_model(
                            profiles_dir=profiles_dir,
                            use_mmap=use_mmap,
                        )
                    else:
                        # packaged defaults (model_io decides paths)
                        self._lang_model = load_model(use_mmap=use_mmap)

        results = _detect_lang(self._lang_model, text, top_k=top_k) or []
        if return_top1:
            return results[0][0] if results else ""
        return results

    