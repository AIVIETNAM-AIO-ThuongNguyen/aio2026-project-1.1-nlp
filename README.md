<!-- ============================================================ -->
<!--  AIO 2026 - Web and Streamlit for Simple Deployment (Using NLP Libs) -->
<!--  Student: Nguyen Van Thuong                                   -->
<!-- ============================================================ -->

# 🧠 AIO 2026 — Project 1.1: NLP Pipeline (Streamlit)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-3DA639)
![Code style](https://img.shields.io/badge/code%20style-PEP%208-1f6feb)

> 🇬🇧 **EN** — A two-app NLP toolkit built with Streamlit for AIO 2026 (Module 01 — Project 1.1): **Translation + Spell Checking** (`project_1_1.py`) and **Grammar Checking** (`project_1_1_grammar_check.py`).
>
> 🇻🇳 **VI** — Bộ đôi ứng dụng NLP xây bằng Streamlit cho AIO 2026 (Module 01 — Project 1.1): **Dịch + Sửa chính tả** (`project_1_1.py`) và **Kiểm tra ngữ pháp** (`project_1_1_grammar_check.py`).

🔗 **Live demo for Project 1.1:** https://aio2026-project-11-nlp-bvlhsybdbguf7zgmqmdkhp.streamlit.app/

---

## 📑 Table of Contents · Mục lục

- [Features · Tính năng](#-features--tính-năng)
- [Tech Stack · Công nghệ](#️-tech-stack--công-nghệ)
- [Project Structure · Cấu trúc dự án](#-project-structure--cấu-trúc-dự-án)
- [Getting Started · Bắt đầu](#-getting-started--bắt-đầu)
- [Usage · Cách dùng](#-usage--cách-dùng)
- [Deployment · Triển khai](#️-deployment--triển-khai)
- [Author · Tác giả](#-author--tác-giả)
- [License · Giấy phép](#-license--giấy-phép)

---

## ✨ Features · Tính năng

**🇬🇧 English**

- **App 1 — Translation & Spell Check** (`project_1_1.py`): auto-detects the input language (langdetect), translates via Google Translate (deep-translator), and fixes typos with pyspellchecker across 10 languages while preserving capitalisation.
- **App 2 — Grammar Check** (`project_1_1_grammar_check.py`): uses LanguageTool to catch grammar mistakes such as "I lives -> I live" that a spell checker misses, with a per-error explanation and suggestions.
- Manual language override for short or ambiguous inputs.

**🇻🇳 Tiếng Việt**

- **App 1 — Dịch & Sửa chính tả** (`project_1_1.py`): tự nhận diện ngôn ngữ (langdetect), dịch qua Google Translate (deep-translator), sửa lỗi typo bằng pyspellchecker cho 10 ngôn ngữ, giữ nguyên kiểu viết hoa.
- **App 2 — Kiểm tra ngữ pháp** (`project_1_1_grammar_check.py`): dùng LanguageTool bắt lỗi ngữ pháp như "I lives -> I live" mà spell checker bỏ sót, kèm giải thích & gợi ý cho từng lỗi.
- Cho phép chọn ngôn ngữ thủ công với câu ngắn hoặc đa nghĩa.

---

## 🛠️ Tech Stack · Công nghệ

| Layer · Tầng | Tools · Công cụ |
| --- | --- |
| Web framework | Streamlit |
| Language detection · Nhận diện ngôn ngữ | langdetect |
| Translation · Dịch | deep-translator (Google) |
| Spell check · Chính tả | pyspellchecker · nltk |
| Grammar check · Ngữ pháp | language-tool-python (LanguageTool, cần Java) |
| Utilities · Tiện ích | langcodes |

---

## 📁 Project Structure · Cấu trúc dự án

Cấu trúc thư mục của dự án được tổ chức như sau để tối ưu hóa việc phát triển và triển khai ứng dụng:

```text
aio2026-project-1.1-nlp/
├── .streamlit/
│   └── config.toml                  # Cấu hình giao diện (UI) và thiết lập cho Streamlit
├── src/                             # Chứa toàn bộ mã nguồn chính của ứng dụng
│   ├── project_1_1.py               # App 1: Xử lý Dịch thuật (Translation) & Chính tả (Spell check)
│   └── project_1_1_grammar_check.py # App 2: Tính năng mở rộng kiểm tra Ngữ pháp (LanguageTool)
├── .gitignore                       # Cấu hình bỏ qua file/thư mục khi commit lên Git
├── LICENSE                          # Giấy phép mã nguồn mở của dự án
├── README.md                        # Tài liệu hướng dẫn sử dụng và cài đặt
└── requirements.txt                 # Danh sách các thư viện Python (Dependencies)
```

> 🇬🇧 This repository contains only the two Project 1.1 related apps above. Other AIO 2026 exercises live in their own repositories.
> 🇻🇳 Repo này chỉ gồm hai app có liên quan đến Project 1.1 ở trên. Các bài tập AIO 2026 khác nằm ở repo riêng.

---

## 🚀 Getting Started · Bắt đầu

### Prerequisites · Yêu cầu

- 🇬🇧 Python 3.10+ . App 2 (Grammar Check) requires Java 17+. Without Java, App 2 automatically falls back to the public LanguageTool API.
- 🇻🇳 Python 3.10+ . App 2 (Grammar Check) cần Java 17+. Không có Java, App 2 tự chuyển sang API công khai của LanguageTool.

### Installation · Cài đặt

    # 1) Clone the repo · Tải mã nguồn
    git clone https://github.com/<username>/aio2026-project-1.1-nlp.git
    cd aio2026-project-1.1-nlp

    # 2) Create & activate a virtual environment · Tạo & kích hoạt môi trường ảo
    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate

    # 3) Install dependencies · Cài thư viện
    pip install -r requirements.txt

    # 4) Run an app · Chạy ứng dụng
    streamlit run src/project_1_1.py
    streamlit run src/project_1_1_grammar_check.py

### requirements.txt

    streamlit>=1.35
    langdetect==1.0.9
    deep-translator==1.11.4
    pyspellchecker==0.8.1
    nltk==3.9.1
    langcodes==3.4.0
    language-tool-python==2.8

---

## 💡 Usage · Cách dùng

- 🇬🇧 Open http://localhost:8501 , type a sentence, optionally pick the language, then press the action button.
- 🇻🇳 Mở http://localhost:8501 , nhập câu, (tùy chọn) chọn ngôn ngữ, rồi bấm nút thao tác.

---

## ☁️ Deployment · Triển khai

**🇬🇧 Streamlit Community Cloud (free)**

1. Sign in at https://share.streamlit.io with GitHub.
2. New app -> pick this repo -> branch main.
3. Main file path: src/project_1_1.py -> Deploy.

**🇻🇳 Streamlit Community Cloud (miễn phí)**

1. Đăng nhập https://share.streamlit.io bằng GitHub.
2. New app -> chọn repo này -> nhánh main.
3. Main file path: src/project_1_1.py -> Deploy.

---

## 👤 Author · Tác giả

**Nguyen Van Thuong** — AIO 2026 · Module 01 · Project 1.1

---

## 📜 License · Giấy phép

- 🇬🇧 Released under the MIT License — see the LICENSE file.
- 🇻🇳 Phát hành theo giấy phép MIT — xem file LICENSE.

---

## 🙏 Acknowledgements · Lời cảm ơn

- AI VIET NAM — AIO 2026 for the project brief and guidance.
- Open-source libraries: Streamlit, langdetect, deep-translator, pyspellchecker, nltk, LanguageTool, langcodes.
