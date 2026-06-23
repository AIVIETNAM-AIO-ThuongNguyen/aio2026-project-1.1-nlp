"""Project 1.1: Web and Streamlit for Simple Deployment (Using NLP Libs)

Author : Nguyen Van Thuong
Course : AIO 2026 - Module 01

A two-in-one Streamlit application built for the AIO 2026 Project 1.1 exercise.

* Tab 1 - Translation: auto-detects the source language of the input text and
  translates it into a user-selected target language through Google Translate.
* Tab 2 - Spell checking: auto-detects the language and fixes typos with
  ``pyspellchecker`` (ten languages supported).

Run locally:
    streamlit run project_1_1.py

Dependencies:
    streamlit langdetect pyspellchecker nltk langcodes deep-translator
"""

from __future__ import annotations

import langcodes
import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, LangDetectException, detect
from nltk.tokenize import TreebankWordDetokenizer, wordpunct_tokenize
from spellchecker import SpellChecker

# Make langdetect deterministic so identical input always yields the same guess.
DetectorFactory.seed = 0

# Project metadata shown in the application UI.
AUTHOR: str = "Nguyen Van Thuong"
COURSE: str = "AIO 2026"
MODULE: str = "Module 01"
PROJECT: str = "Project 1.1"

# Reject inputs shorter than this; language detection is unreliable on tiny strings.
MIN_INPUT_LENGTH: int = 3

# Languages for which pyspellchecker ships a built-in frequency dictionary.
SPELL_LANGS: frozenset[str] = frozenset(
    {"en", "es", "fr", "pt", "de", "ru", "ar", "eu", "lv", "nl"}
)

# Friendly language names. Kept locally so the app no longer needs the optional
# ``langcodes[data]`` download and never floods the console with the repeated
# "language_data package" warning when a code is rendered.
LANG_NAMES: dict[str, str] = {
    "en": "Tiếng Anh",
    "vi": "Tiếng Việt",
    "fr": "Tiếng Pháp",
    "es": "Tiếng Tây Ban Nha",
    "de": "Tiếng Đức",
    "pt": "Tiếng Bồ Đào Nha",
    "ru": "Tiếng Nga",
    "ar": "Tiếng Ả Rập",
    "eu": "Tiếng Basque",
    "lv": "Tiếng Latvia",
    "nl": "Tiếng Hà Lan",
    "ja": "Tiếng Nhật",
    "ko": "Tiếng Hàn",
    "zh-cn": "Tiếng Trung (Giản thể)",
}

# Human-readable target languages mapped to ISO codes accepted by GoogleTranslator.
TARGET_LANGS: dict[str, str] = {
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Pháp": "fr",
    "Tiếng Nhật": "ja",
    "Tiếng Trung (Giản thể)": "zh-CN",
    "Tiếng Hàn": "ko",
    "Tiếng Tây Ban Nha": "es",
    "Tiếng Đức": "de",
}

EXAMPLES_TRANSLATE: list[str] = [
    "Every morning, I drink a cup of coffee.",
    "Bonjour, comment allez-vous?",
    "Xin chào, hôm nay trời đẹp quá.",
]
EXAMPLES_SPELL: list[str] = [
    "Yesturday, I recieveed a mesage from my freind.",
    "Definately a great oppurtunity.",
    "Je voudraiis allerr au marchee.",
]


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_spellchecker(code: str) -> SpellChecker:
    """Return a cached SpellChecker for ``code``.

    Building a SpellChecker loads a dictionary from disk, so caching one
    instance per language avoids repeating that work on every rerun.
    """
    return SpellChecker(language=code)


def language_name(code: str) -> str:
    """Convert an ISO code into a readable name (e.g. ``en`` -> Tiếng Anh).

    The local ``LANG_NAMES`` table is consulted first so the app works even when
    the optional ``langcodes[data]`` package is missing; ``langcodes`` is only a
    fallback for codes outside the table.
    """
    if not code:
        return "Unknown"
    if code.lower() in LANG_NAMES:
        return LANG_NAMES[code.lower()]
    try:
        return langcodes.Language.get(code).display_name()
    except Exception:
        return code


def detect_language(raw: str) -> str | None:
    """Detect the language of ``raw`` and return its ISO code, or None on failure."""
    try:
        return detect(raw)
    except LangDetectException:
        return None


def fix_typos(text: str, code: str) -> tuple[str, bool]:
    """Correct spelling token-by-token while preserving the original casing.

    Returns the rebuilt sentence and a flag indicating whether anything changed.
    """
    spell = get_spellchecker(code)
    tokens = wordpunct_tokenize(text)
    fixed: list[str] = []
    for token in tokens:
        # Only correct genuine words; leave punctuation and single letters alone.
        if token.isalpha() and len(token) > 1:
            suggestion = spell.correction(token.lower()) or token
            # Restore the original capitalisation pattern of the token.
            if token.istitle():
                suggestion = suggestion.title()
            elif token.isupper():
                suggestion = suggestion.upper()
            fixed.append(suggestion)
        else:
            fixed.append(token)
    rebuilt = TreebankWordDetokenizer().detokenize(fixed)
    return rebuilt, fixed != tokens


# --------------------------------------------------------------------------- #
# Processing pipelines
# --------------------------------------------------------------------------- #
def run_translation(
    text: str, target_code: str, forced_source: str | None = None
) -> dict:
    """Translate ``text`` into ``target_code``.

    When ``forced_source`` is provided it is trusted directly; otherwise the
    source language is auto-detected. Manual selection is the reliable choice
    for short inputs, where statistical detection is frequently wrong.
    """
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        return {"ok": False, "error": f"Nhập tối thiểu {MIN_INPUT_LENGTH} ký tự."}

    source = forced_source or detect_language(raw)
    if source is None:
        return {"ok": False, "error": "Không nhận diện được ngôn ngữ."}

    # Skip the network call when the text is already in the requested language.
    if source == target_code:
        return {
            "ok": True,
            "source": language_name(source),
            "target": language_name(target_code),
            "translated": raw,
            "note": "Câu đã ở ngôn ngữ đích, không cần dịch.",
        }

    try:
        translated = GoogleTranslator(source=source, target=target_code).translate(raw)
    except Exception as exc:  # Surface network/API failures to the UI.
        return {"ok": False, "error": f"Lỗi dịch: {exc}"}

    return {
        "ok": True,
        "source": language_name(source),
        "target": language_name(target_code),
        "translated": translated,
    }


def run_spellcheck(text: str, forced_code: str | None = None) -> dict:
    """Fix typos for ``text``.

    ``forced_code`` lets the caller pin the dictionary language. This avoids the
    classic failure mode where ``langdetect`` mis-classifies a short sentence
    (for example English read as Spanish) and the wrong dictionary corrupts the
    text. When it is ``None`` the language is auto-detected as before.
    """
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        return {"ok": False, "error": f"Nhập tối thiểu {MIN_INPUT_LENGTH} ký tự."}

    auto_detected = forced_code is None
    code = forced_code or detect_language(raw)
    if code is None:
        return {"ok": False, "error": "Không nhận diện được ngôn ngữ."}

    if code not in SPELL_LANGS:
        return {
            "ok": False,
            "error": f"pyspellchecker chưa hỗ trợ {language_name(code)} ({code}).",
        }

    fixed, changed = fix_typos(raw, code)
    return {
        "ok": True,
        "language": language_name(code),
        "auto_detected": auto_detected,
        "fixed": fixed,
        "changed": changed,
    }


# --------------------------------------------------------------------------- #
# Selectbox options (label -> ISO code; ``None`` means auto-detect)
# --------------------------------------------------------------------------- #
AUTO_LABEL: str = "Tự động nhận diện"

SOURCE_OPTIONS: dict[str, str | None] = {AUTO_LABEL: None}
SOURCE_OPTIONS.update({name: code for name, code in TARGET_LANGS.items()})

SPELL_OPTIONS: dict[str, str | None] = {AUTO_LABEL: None}
SPELL_OPTIONS.update(
    {f"{language_name(code)} ({code})": code for code in sorted(SPELL_LANGS)}
)


# --------------------------------------------------------------------------- #
# User interface
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Project 1.1: Web and Streamlit for Simple Deployment (Using NLP Libs)", layout="centered")

with st.sidebar:
    st.subheader("About this project")
    st.markdown(f"**Author:** {AUTHOR}")
    st.markdown(f"**Course:** {COURSE}")
    st.markdown(f"**Module:** {MODULE}")
    st.markdown(f"**Project:** {PROJECT}")

st.title("Project 1.1: Web and Streamlit for Simple Deployment (Using NLP Libs)")
st.caption(f"{AUTHOR} · {COURSE} · {MODULE}")
st.caption("Hai hướng ứng dụng trang này: Dịch văn bản · Sửa lỗi chính tả")

tab_translate, tab_spell = st.tabs(["Dịch văn bản", "Sửa lỗi chính tả"])

# ----- Tab 1: Translation ----- #
with tab_translate:
    st.session_state.setdefault("res_t", None)

    with st.expander("Ví dụ"):
        for example in EXAMPLES_TRANSLATE:
            st.markdown(f"- {example}")

    with st.form("form_translate"):
        text_t = st.text_area(
            "Câu cần dịch",
            height=90,
            placeholder="Nhập câu ở bất kỳ ngôn ngữ nào...",
        )
        source_label = st.selectbox("Ngôn ngữ nguồn", list(SOURCE_OPTIONS.keys()))
        target = st.selectbox("Dịch sang", list(TARGET_LANGS.keys()))
        submitted_t = st.form_submit_button("Dịch", type="primary")

    if submitted_t:
        # Persist the latest result so it survives Streamlit reruns.
        st.session_state.res_t = run_translation(
            text_t, TARGET_LANGS[target], SOURCE_OPTIONS[source_label]
        )

    res = st.session_state.res_t
    if res:
        if res["ok"]:
            st.caption(f"Nguồn: {res['source']}  →  Đích: {res['target']}")
            st.success(res["translated"])
            if res.get("note"):
                st.info(res["note"])
        else:
            st.warning(res["error"])

# ----- Tab 2: Spell checking ----- #
with tab_spell:
    st.session_state.setdefault("res_s", None)

    with st.expander("Ví dụ"):
        for example in EXAMPLES_SPELL:
            st.markdown(f"- {example}")
    st.caption(f"Hỗ trợ: {', '.join(sorted(SPELL_LANGS))}")

    with st.form("form_spell"):
        text_s = st.text_area(
            "Câu cần kiểm tra",
            height=90,
            placeholder="Nhập câu để kiểm tra chính tả...",
        )
        spell_label = st.selectbox(
            "Ngôn ngữ",
            list(SPELL_OPTIONS.keys()),
            help="Câu ngắn dễ bị nhận diện sai; hãy chọn đúng ngôn ngữ để có kết quả chuẩn.",
        )
        submitted_s = st.form_submit_button("Kiểm tra", type="primary")

    if submitted_s:
        st.session_state.res_s = run_spellcheck(text_s, SPELL_OPTIONS[spell_label])

    res = st.session_state.res_s
    if res:
        if res["ok"]:
            mode = "tự động nhận diện" if res["auto_detected"] else "bạn chọn"
            st.caption(f"Ngôn ngữ: {res['language']} ({mode})")
            st.success(res["fixed"])
            st.caption(
                "Có sửa lỗi chính tả" if res["changed"] else "Không phát hiện lỗi"
            )
        else:
            st.warning(res["error"])
