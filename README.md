<div align="center">

# 🌟 LocalPDF.io

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![All Contributors](https://img.shields.io/github/all-contributors/virgiliojr94/localpdf.io?color=ee8449&style=flat-square)](#-contribuidores)
[![Website](https://img.shields.io/badge/Website-Online-success.svg)](https://virgiliojr94.github.io/localpdf.io/)

> Todas as ferramentas PDF que você precisa, 100% local e privado

**🌐 [Visite o Site Oficial](https://virgiliojr94.github.io/localpdf.io/)**

[Funcionalidades](#-funcionalidades) •
[Como Usar](#-como-usar) •
[Contribuir](CONTRIBUTING.md) •
[Licença](#-licença)

</div>

---

## 📋 O que é?

LocalPDF.io é uma aplicação web local para manipulação de arquivos PDF e documentos. Todos os arquivos são processados no seu próprio computador - nada é enviado para a nuvem.

## ✨ Funcionalidades

### 📥 Converter para PDF
- **🖼️ Imagens → PDF** - Combine múltiplas imagens (JPG, PNG) em um PDF
- **📝 Word → PDF** - Converta um ou vários documentos DOCX em PDF único
- **📊 Excel → PDF** - Transforme planilhas XLSX em PDF
- **📄 Texto → PDF** - Converta arquivos TXT em PDF formatado

### 📤 Converter de PDF
- **🖼️ PDF → Imagens** - Extraia cada página como imagem PNG
- **📝 PDF → Word** - Converta PDF em documento DOCX editável
- **📊 PDF → Excel** - Extraia tabelas para planilhas XLSX
- **📄 PDF → Texto** - Extraia todo o texto em arquivo TXT
- **🔒 PDF → PDF/A** - Converta para o padrão de arquivamento (PDF/A-1b)

### 🔄 Manipular PDF
- **🔗 Mesclar PDFs** - Una vários PDFs em um único documento
- **✂️ Dividir PDF** - Separe cada página em arquivo individual
- **📦 Comprimir PDF** - Reduza o tamanho mantendo a qualidade

## 🚀 Como usar

### 🐳 Opção 1: Com Docker (Recomendado)

O jeito mais fácil e rápido de rodar o projeto:

#### 1. Usar imagem pronta (Mais rápido)
Você pode rodar a aplicação diretamente do GitHub Container Registry sem precisar clonar o código:

```bash
docker run -p 5000:5000 ghcr.io/virgiliojr94/localpdf.io:latest
```

#### 2. Build local
Se preferir buildar manualmente ou fazer modificações:

```bash
# Clone o repositório
git clone https://github.com/virgiliojr94/localpdf.io.git
cd localpdf.io

# Execute com Docker
docker build -t localpdf .
docker run -p 5000:5000 localpdf
```

**Acesse:** http://localhost:5000

### 💻 Opção 2: Localmente (Desenvolvimento)

#### Pré-requisitos
- Python 3.11+
- Ghostscript (para conversão PDF/A)

#### Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/virgiliojr94/localpdf.io.git
cd localpdf.io
```

**2. Crie um ambiente virtual (recomendado)**
```bash
# Com venv
python -m venv .venv

# Ative o ambiente virtual
# Windows (Git Bash/PowerShell)
source .venv/Scripts/activate
# Linux/macOS
source .venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Instale o Ghostscript**
```bash
# Ubuntu/Debian
sudo apt-get install ghostscript

# macOS
brew install ghostscript

# Windows
# Baixe em: https://www.ghostscript.com/download/gsdnld.html
```

**5. Execute a aplicação**
```bash
python run.py
```

**Acesse:** http://localhost:5000

## 📁 Estrutura do Projeto

```
localpdf.io/
├── run.py                 # Ponto de entrada da aplicação
├── requirements.txt       # Dependências Python
├── dockerfile            # Configuração Docker
├── static/               # Frontend (HTML, CSS, JS)
│   └── index.html       # Interface do usuário
└── src/                  # Código fonte Python
    ├── app.py           # Flask app e rotas
    ├── config.py        # Configurações
    ├── utils.py         # Funções utilitárias
    └── converters/      # Módulos de conversão
        ├── pdf_converter.py
        ├── document_converter.py
        └── conversion_manager.py
```

## 🛠️ Tecnologias

### Backend
- **Flask** - Framework web Python minimalista e poderoso
- **PyMuPDF (fitz)** - Manipulação e renderização de PDFs
- **Ghostscript** - Conversão para PDF/A e otimização
- **PDF2Docx** - Conversão de PDF para Word com preservação de layout
- **Pillow (PIL)** - Processamento e manipulação de imagens
- **python-docx** - Criação e leitura de arquivos Word (.docx)
- **OpenPyXL** - Manipulação de planilhas Excel (.xlsx)
- **ReportLab** - Geração de PDFs programaticamente

### Frontend
- **HTML5/CSS3/JavaScript** - Interface web moderna e responsiva
- **Vanilla JS** - Sem dependências de frameworks frontend

## 🔒 Privacidade

Todos os arquivos são processados **localmente** no seu computador. Nenhum dado é enviado para servidores externos.

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Veja o [guia de contribuição](CONTRIBUTING.md) para começar.

## 👥 Contribuidores

Obrigado a todas essas pessoas incríveis que contribuíram para este projeto! ✨

<a href="https://github.com/virgiliojr94/localpdf.io/graphs/contributors">
  <img alt="Contribuidores do repositório" src="https://contrib.rocks/image?repo=virgiliojr94/localpdf.io" />
</a>

Contribuições de qualquer tipo são bem-vindas!

## 📝 Licença

MIT License - Sinta-se livre para usar e modificar!

## 👨‍💻 Desenvolvedor

**Virgilio Borges**

- 📧 Email: virgilio.junior94@gmail.com
- 📱 WhatsApp: (95) 98112-1572
- 🔗 GitHub: [@virgiliojr94](https://github.com/virgiliojr94)
- 💼 LinkedIn: [virgiliojunior94](https://www.linkedin.com/in/virgiliojunior94/)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!

## :star2: Star History

[![Star History Chart](https://api.star-history.com/svg?repos=virgiliojr94/localpdf.io&type=timeline&legend=top-left)](https://www.star-history.com/#virgiliojr94/localpdf.io&type=timeline&legend=top-left)
