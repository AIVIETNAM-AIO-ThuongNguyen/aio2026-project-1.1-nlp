"""Project 1.1 — Extended for Project 1.1
Grammar Check app (bài làm mở rộng).

Tại sao cần app này?
--------------------
`project_1_1.py` dùng `pyspellchecker` nên chỉ bắt được LỖI CHÍNH TẢ
(từ viết sai, không có trong từ điển) chứ KHÔNG bắt được LỖI NGỮ PHÁP.
Ví dụ "I lives you baby!" — mọi từ đều đúng chính tả nên spell checker
báo "không có lỗi", nhưng thực ra sai chia động từ ("I live").

App này dùng `language_tool_python` (wrapper của LanguageTool) để kiểm tra
CẢ ngữ pháp LẪN chính tả, đồng thời giải thích từng lỗi và gợi ý sửa.

Cài đặt:
    pip install streamlit language-tool-python
Lưu ý: lần chạy đầu, language_tool_python sẽ tự tải LanguageTool
(cần Java + mạng). Muốn chạy hoàn toàn offline có thể dùng
LanguageTool server cục bộ và `language_tool_python.LanguageTool(..., remote_server=...)`.

Tác giả: Nguyen Van Thuong · AIO 2026 · Module 01 · Project 1.1
"""

from __future__ import annotations

import streamlit as st

try:
    import language_tool_python
except ImportError:  # pragma: no cover - friendly message when dependency missing
    language_tool_python = None

# ---------------------------------------------------------------------------
# Thông tin tác giả (hiển thị ở sidebar)
# ---------------------------------------------------------------------------
AUTHOR = "Nguyen Van Thuong"
COURSE = "AIO 2026"
MODULE = "Module 01"
PROJECT = "Extended for Project 1.1"

MIN_INPUT_LENGTH = 2

# Mã LanguageTool -> tên hiển thị (không phụ thuộc gói langcodes[data]).
TOOL_LANGS: dict[str, str] = {
    "en-US": "Tiếng Anh (Mỹ)",
    "en-GB": "Tiếng Anh (Anh)",
    "fr": "Tiếng Pháp",
    "de-DE": "Tiếng Đức",
    "es": "Tiếng Tây Ban Nha",
    "pt": "Tiếng Bồ Đào Nha",
    "nl": "Tiếng Hà Lan",
    "ru": "Tiếng Nga",
}

EXAMPLES = [
    "I lives you baby!",
    "Do you likes me? I does love you.",
    "She go to school every days.",
    "He have a apple and three orange.",
]


# ---------------------------------------------------------------------------
# Logic
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Đang tải LanguageTool...")
def get_tool(lang_code: str):
    """Tạo (và cache) một LanguageTool cho một ngôn ngữ.

    Ưu tiên LanguageTool *cục bộ* (cần Java cài sẵn trong máy). Nếu máy CHƯA
    cài Java, tự động chuyển sang *API công khai* của LanguageTool
    (không cần Java, nhưng cần Internet và có giới hạn tần suất).
    Cache theo `lang_code` để không phải khởi tạo lại mỗi lần bấm nút.

    Returns:
        (tool, mode) - tool là đối tượng LanguageTool, mode là "local"/"public".
    """
    if language_tool_python is None:
        raise RuntimeError(
            "Chưa cài language_tool_python. Chạy: pip install language-tool-python"
        )
    try:
        # Cách 1: chạy LanguageTool cục bộ (cần Java + lần đầu cần mạng để tải).
        return language_tool_python.LanguageTool(lang_code), "local"
    except Exception:
        # Cách 2: không có Java -> dùng API công khai (chỉ cần Internet).
        return language_tool_python.LanguageToolPublicAPI(lang_code), "public"


def _as_dict(value) -> dict:
    """Đưa một giá trị (dict / object) về dạng dict để dễ đọc thuộc tính."""
    if isinstance(value, dict):
        return value
    sub = getattr(value, "__dict__", None)
    return sub if isinstance(sub, dict) else {}


def _collect_attrs(obj) -> dict:
    """Gom TẤT CẢ thuộc tính của một Match thành dict (kể cả property / __slots__).

    Mỗi phiên bản `language_tool_python` đặt tên thuộc tính khác nhau
    (errorLength / length, ruleId / rule.id ...). Duyệt qua `dir()` rồi
    `getattr` giúp lấy được bất kể cách khai báo nào.
    """
    data: dict = {}
    for name in dir(obj):
        if name.startswith("__"):
            continue
        try:
            value = getattr(obj, name)
        except Exception:
            continue
        if callable(value):
            continue
        data[name] = value
    raw = getattr(obj, "__dict__", None)
    if isinstance(raw, dict):
        for key, value in raw.items():
            data.setdefault(key, value)
    return data


def _find_int(data: dict, *names: str, contains: str | None = None):
    """Tìm một giá trị số nguyên theo tên (ưu tiên khớp chính xác, không phân biệt hoa thường)."""
    lower = {k.lower(): v for k, v in data.items()}
    for name in names:
        value = lower.get(name.lower())
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    if contains:
        for key, value in data.items():
            if contains in key.lower() and isinstance(value, int) and not isinstance(value, bool):
                return value
    return None


def _normalize_match(m, text: str) -> dict:
    """Chuẩn hoá một Match (khác nhau giữa các phiên bản) thành dict ổn định.

    Trả về: {message, bad, suggestions, rule, category}. Mọi trường đều có
    nhiều phương án dự phòng để không bị rỗng do đổi tên thuộc tính.
    """
    data = _collect_attrs(m)
    lower = {k.lower(): v for k, v in data.items()}

    # --- Vị trí & độ dài lỗi -> trích “từ sai” (bad) ---
    offset = _find_int(data, "offset", contains="offset")
    error_len = _find_int(data, "errorLength", "errorlength", "length", "error_length", contains="length")

    bad = ""
    if offset is not None and error_len:
        bad = text[offset : offset + error_len]
    if not bad:
        # Dự phòng: lấy từ đoạn ngữ cảnh (context) mà LanguageTool trả về.
        ctx_raw = data.get("context")
        ctx_text = ctx_raw if isinstance(ctx_raw, str) else _as_dict(ctx_raw).get("text")
        ctx_offset = _find_int(data, "offsetInContext")
        if ctx_offset is None:
            ctx_offset = _find_int(_as_dict(ctx_raw), "offset", contains="offset")
        ctx_len = error_len or _find_int(_as_dict(ctx_raw), "length", contains="length")
        if ctx_text and ctx_offset is not None and ctx_len:
            bad = ctx_text[ctx_offset : ctx_offset + ctx_len]
    bad = (bad or "").strip()

    # --- Rule id ---
    rule_id = ""
    for key in ("ruleid", "rule_id"):
        if lower.get(key):
            rule_id = str(lower[key])
            break
    if not rule_id:
        rule_obj = data.get("rule")
        rule_dict = _as_dict(rule_obj)
        if rule_dict.get("id"):
            rule_id = str(rule_dict["id"])
        elif isinstance(rule_obj, str):
            rule_id = rule_obj

    # --- Loại lỗi (category) ---
    category = ""
    for key in ("category", "ruleissuetype", "issuetype"):
        value = lower.get(key)
        if value:
            cat_dict = _as_dict(value)
            category = str(cat_dict.get("name") or cat_dict.get("id") or value)
            break
    if not category:
        cat_dict = _as_dict(_as_dict(data.get("rule")).get("category"))
        category = str(cat_dict.get("name") or cat_dict.get("id") or "")

    # --- Thông điệp ---
    message = str(lower.get("message") or lower.get("msg") or "")

    # --- Gợi ý sửa (replacements có thể là list[str] hoặc list[dict]) ---
    suggestions: list[str] = []
    for item in (lower.get("replacements") or [])[:8]:
        if isinstance(item, dict):
            val = item.get("value") or item.get("replacement") or ""
        else:
            val = str(item)
        if val:
            suggestions.append(val)
    suggestions = suggestions[:5]

    return {
        "message": message,
        "bad": bad,
        "suggestions": suggestions,
        "rule": rule_id,
        "category": category,
    }


def check_grammar(text: str, lang_code: str) -> dict:
    """Kiểm tra ngữ pháp + chính tả, trả về kết quả đã chuẩn hoá.

    Returns dict gồm:
        original: câu gốc
        corrected: câu đã sửa
        matches: danh sách lỗi (message, context, suggestions, rule)
    """
    tool, mode = get_tool(lang_code)
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)

    issues = [_normalize_match(m, text) for m in matches]

    return {
        "original": text,
        "corrected": corrected,
        "matches": issues,
        "mode": mode,
    }


# ---------------------------------------------------------------------------
# Giao diện
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Project 1.1 — Grammar Check", page_icon="📝")

with st.sidebar:
    st.markdown("### About this project")
    st.write(f"**Author:** {AUTHOR}")
    st.write(f"**Course:** {COURSE}")
    st.write(f"**Module:** {MODULE}")
    st.write(f"**Project:** {PROJECT}")
    st.divider()
    st.caption(
        "App mở rộng: kiểm tra NGỮ PHÁP (khác với spell check ở project_1_1.py "
        "chỉ sửa chính tả)."
    )

st.title("📝 Project 1.1 — Grammar Check (mở rộng)")
st.caption(f"{AUTHOR} · {COURSE} · {MODULE}")
st.write(
    "Kiểm tra **ngữ pháp + chính tả** bằng LanguageTool. "
    "Bắt được cả lỗi chia động từ như *I lives → I live* mà spell checker bỏ sót."
)

if language_tool_python is None:
    st.error(
        "Chưa cài thư viện `language_tool_python`.\n\n"
        "Chạy lệnh sau rồi khởi động lại app:\n\n"
        "`pip install language-tool-python`\n\n"
        "(Lần chạy đầu cần Java và mạng để tự tải LanguageTool.)"
    )
    st.stop()

with st.expander("Ví dụ"):
    for ex in EXAMPLES:
        st.code(ex, language="text")

lang_label = st.selectbox(
    "Ngôn ngữ",
    options=list(TOOL_LANGS.keys()),
    format_func=lambda code: f"{TOOL_LANGS[code]} ({code})",
    index=0,
    help="Chọn đúng ngôn ngữ của câu để LanguageTool kiểm tra chính xác.",
)

text = st.text_area("Câu cần kiểm tra", value="I lives you baby!", height=120)

if st.button("Kiểm tra", type="primary"):
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        st.warning("Vui lòng nhập câu dài hơn.")
    else:
        try:
            result = check_grammar(raw, lang_label)
        except Exception as err:  # noqa: BLE001 - hiển thị lỗi thân thiện
            st.error(f"Không chạy được LanguageTool: {err}")
        else:
            st.subheader("Kết quả")
            if result.get("mode") == "public":
                st.info(
                    "Không tìm thấy Java nên đang dùng **API công khai** của "
                    "LanguageTool (cần Internet, có giới hạn tần suất). Cài Java "
                    "để chạy nhanh & offline."
                )
            if not result["matches"]:
                st.success("Không phát hiện lỗi ngữ pháp/chính tả. 🎉")
                st.write(result["corrected"])
            else:
                st.markdown("**Câu đã sửa:**")
                st.success(result["corrected"])
                st.markdown(f"**Phát hiện {len(result['matches'])} lỗi:**")
                for i, m in enumerate(result["matches"], start=1):
                    sugg = ", ".join(m["suggestions"]) or "(không có gợi ý)"
                    with st.container(border=True):
                        # Chỉ in từ sai trong ngoặc kép khi lấy được (tránh “” rỗng).
                        if m["bad"]:
                            st.markdown(f"**{i}. “{m['bad']}”** — {m['message']}")
                        else:
                            st.markdown(f"**{i}.** {m['message']}")
                        st.caption(f"Gợi ý: {sugg}")
                        # Gộp Loại/Rule, bỏ qua phần nào trống.
                        meta = f"Loại: {m['category']}" if m["category"] else ""
                        if m["rule"]:
                            meta = f"{meta} · Rule: {m['rule']}" if meta else f"Rule: {m['rule']}"
                        if meta:
                            st.caption(meta)
