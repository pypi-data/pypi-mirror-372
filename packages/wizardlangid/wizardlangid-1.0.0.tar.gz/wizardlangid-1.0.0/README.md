<img src="https://raw.githubusercontent.com/textwizard-dev/wizardlangid/main/asset/WizardLangID%20Banner.png"
     alt="WizardLangID Banner" width="800" height="300">

---

# WizardLangID
[![PyPI - Version](https://img.shields.io/pypi/v/wizardlangid)](https://pypi.org/project/wizardlangid/)
[![PyPI - Downloads/month](https://img.shields.io/pypi/dm/wizardlangid?label=PyPI%20downloads)](https://pypistats.org/packages/wizardlangid)
[![License](https://img.shields.io/pypi/l/wizardlangid)](https://github.com/textwizard-dev/wizardlangid/blob/main/LICENSE)


**WizardLangID** is a Python library for Language identification via character n-gram profiles. Candidate gating guided by priors and linguistic cues, then probability estimation for each language. Supports 161 languages. Returns a top-1 ISO code or a probability-ordered list.


---

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Language detection](#language-detection)
- [License](#license)
- [Resources](#resources)

---
## Installation

Requires Python 3.9+.

~~~bash
pip install wizardlangid
~~~

---

## Quick start

~~~python
import wizardlangid as wl

text = "hello world"
lang = wl.lang_detect(text, return_top1=True)
print(lang) 
~~~

---

## Language detection

### Parameters

- `text`: Input string (Unicode).  
- `top_k`: Number of candidates to return (default `3`).  
- `profiles_dir`: Override the bundled profiles directory.  
- `use_mmap`: If `True`, memory-map the profile tries (lower RAM; first access may be slightly slower).  
- `return_top1`: If `True`, return only the best language code; otherwise a list of `(lang, prob)`.


### Examples

**Top-1 (single code)**

```python
import wizardlangid as wl

text = "Ciao, come stai oggi?"
lang = wl.lang_detect(text, return_top1=True)
print(lang) 
```
**Output**  
~~~
it
~~~
**Top-k distribution**

```python
import wizardlangid as wl

text = "The quick brown fox jumps over the lazy dog."
langs = wl.lang_detect(text, top_k=5, return_top1=False)
print(langs) 
```
**Output**  
~~~list
[('en', 0.9999376335362183), ('mg', 4.719212057614953e-05), ('fy', 1.4727973350205069e-05), ('rm', 2.8718519851832537e-07), ('la', 1.5918465665694727e-07)]
~~~
**Batch example**

```python
import wizardlangid as wl

tests = [
    "これは日本語のテスト文です。",
    "Alex parle un peu français, aber nicht so viel.",
    "¿Dónde está la estación de tren?",
]
for s in tests:
    print("TOP1:", wl.lang_detect(s, return_top1=True))
```
**Output**  
~~~
TOP1: ja
TOP1: fr
TOP1: es
~~~

**Custom profiles & mmap**

```python
from pathlib import Path
import wizardlangid as wl

langs = wl.lang_detect(
    "Buongiorno a tutti!",
    profiles_dir=Path("/opt/wizardlangid/profiles"),  # custom profiles
    use_mmap=True,                                   # lower RAM
    top_k=3,
)
print(langs)
```


## License

[AGPL-3.0-or-later](LICENSE).

## RESOURCES

- [GitHub Repository](https://github.com/textwizard-dev/wizardlangid)
- [Documentation](https://wizardlangid.readthedocs.io/en/latest/)
- [PyPI Package](https://pypi.org/project/wizardlangid/)
---

## Contact & Author

**Author:** Mattia Rubino  
**Email:** <textwizard.dev@gmail.com>
