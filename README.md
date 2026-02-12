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

### Com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/virgiliojr94/localpdf.io.git
cd localpdf.io

# Execute com Docker
docker build -t localpdf .
docker run -p 5000:5000 localpdf
```

Acesse: **http://localhost:5000**

### Sem Docker

```bash
# Clone o repositório
git clone https://github.com/virgiliojr94/localpdf.io.git
cd localpdf.io

# Instale as dependências
pip install -r requirements.txt
# Instale o Ghostscript no sistema (ex.: apt-get install ghostscript)

# Execute a aplicação
python app.py
```

Acesse: **http://localhost:5000**

## 🛠️ Tecnologias

- **Flask** - Framework web Python
- **PyMuPDF** - Manipulação de PDFs
- **Pillow** - Processamento de imagens
- **python-docx** - Manipulação de arquivos Word
- **ReportLab** - Geração de PDFs
- **OpenPyXL** - Manipulação de planilhas Excel
- **PDF2Docx** - Conversor de PDF para Docx

## 🔒 Privacidade

Todos os arquivos são processados **localmente** no seu computador. Nenhum dado é enviado para servidores externos.

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Veja o [guia de contribuição](CONTRIBUTING.md) para começar.

## 👥 Contribuidores

Obrigado a todas essas pessoas incríveis que contribuíram para este projeto! ✨

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/virgiliojr94"><img src="https://avatars.githubusercontent.com/u/virgiliojr94?v=4?s=100" width="100px;" alt="Virgilio Borges"/><br /><sub><b>Virgilio Borges</b></sub></a><br /><a href="https://github.com/virgiliojr94/localpdf.io/commits?author=virgiliojr94" title="Code">💻</a> <a href="https://github.com/virgiliojr94/localpdf.io/commits?author=virgiliojr94" title="Documentation">📖</a> <a href="#design-virgiliojr94" title="Design">🎨</a> <a href="#infra-virgiliojr94" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-virgiliojr94" title="Maintenance">🚧</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

Este projeto segue a especificação [all-contributors](https://allcontributors.org). Contribuições de qualquer tipo são bem-vindas!

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
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=virgiliojr94/localpdf.io&type=timeline&legend=top-left)](https://www.star-history.com/#virgiliojr94/localpdf.io&type=timeline&legend=top-left)