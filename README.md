<div align="right">

🌐 **Language** | **English** · [Português 🇧🇷](README.pt-br.md)

</div>

<div align="center">

# 🌟 LocalPDF.io

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![All Contributors](https://img.shields.io/github/all-contributors/virgiliojr94/localpdf.io?color=ee8449&style=flat-square)](#-contributors)
[![Website](https://img.shields.io/badge/Website-Online-success.svg)](https://virgiliojr94.github.io/localpdf.io/)

> Every PDF tool you need — 100% local, 100% private.

**🌐 [Visit the Official Website](https://virgiliojr94.github.io/localpdf.io/)**

[Features](#-features) •
[Usage](#-usage) •
[Contributing](CONTRIBUTING.md) •
[License](#-license)

</div>

---

## 📋 What is it?

LocalPDF.io is a self-hosted web app for PDF and document manipulation. Every file is processed on your own machine — nothing is uploaded to any server.

No accounts. No cloud. No data leaving your computer.

## ✨ Features

### 📥 Convert to PDF
- **🖼️ Images → PDF** — Combine multiple images (JPG, PNG) into one PDF
- **📝 Word → PDF** — Convert one or multiple DOCX documents into a single PDF
- **📊 Excel → PDF** — Transform XLSX spreadsheets into PDF
- **📄 Text → PDF** — Convert TXT files to formatted PDF
- **🌐 HTML → PDF** — Convert HTML files (with CSS and images support) to PDF

### 📤 Convert from PDF
- **🖼️ PDF → Images** — Extract each page as a PNG image
- **📝 PDF → Word** — Convert PDF into an editable DOCX document
- **📊 PDF → Excel** — Extract tables into an XLSX spreadsheet
- **📄 PDF → Text** — Extract all text into a TXT file
- **🔒 PDF → PDF/A** — Convert to archival standard (PDF/A-1b)
- **🔍 OCR on PDF** — Extract text from PDFs and scanned images using Tesseract OCR

### 🔄 Manipulate PDF
- **🔗 Merge PDFs** — Combine multiple PDFs into one document
- **✂️ Split PDF** — Separate each page into individual files
- **📦 Compress PDF** — Reduce file size while preserving quality

## 🚀 Usage

### With Docker (Recommended)

#### Pull and run (fastest)

```bash
docker run -p 5000:5000 ghcr.io/virgiliojr94/localpdf.io:latest
```

#### Build locally

```bash
git clone https://github.com/virgiliojr94/localpdf.io.git
cd localpdf.io
docker build -t localpdf .
docker run -p 5000:5000 localpdf
```

Open: **http://localhost:5000**

### Without Docker

```bash
git clone https://github.com/virgiliojr94/localpdf.io.git
cd localpdf.io

pip install -r requirements.txt
# Instale o Ghostscript e Tesseract no sistema
# Debian/Ubuntu:
apt-get install ghostscript tesseract-ocr tesseract-ocr-por tesseract-ocr-eng

python app.py
```

Open: **http://localhost:5000**

## 🛠️ Tech stack

- **Flask** - Framework web Python
- **PyMuPDF** - Manipulação de PDFs
- **Pillow** - Processamento de imagens
- **python-docx** - Manipulação de arquivos Word
- **ReportLab** - Geração de PDFs
- **OpenPyXL** - Manipulação de planilhas Excel
- **PDF2Docx** - Conversor de PDF para Docx
- **Tesseract OCR** - Reconhecimento óptico de caracteres
- **Xhtml2pdf** - HTML to PDF converter

## 🔒 Privacy

All files are processed **locally** on your machine. No data is sent to external servers — ever.

## 🤝 Contributing

Contributions are welcome! See the [contribution guide](CONTRIBUTING.md) to get started.

## 👥 Contributors

Thanks to everyone who has contributed to this project! ✨

<a href="https://github.com/virgiliojr94/localpdf.io/graphs/contributors">
  <img alt="Repository contributors" src="https://contrib.rocks/image?repo=virgiliojr94/localpdf.io" />
</a>

## 📝 License

MIT License — free to use and modify.

---

⭐ If this project was useful to you, consider giving it a star on GitHub!

## :star2: Star History

[![Star History Chart](https://api.star-history.com/svg?repos=virgiliojr94/localpdf.io&type=timeline&legend=top-left)](https://www.star-history.com/#virgiliojr94/localpdf.io&type=timeline&legend=top-left)
