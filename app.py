import io
import os
import shutil
import tempfile
import zipfile

import fitz  # PyMuPDF
try:
    import ghostscript
except (ImportError, RuntimeError) as e:
    ghostscript = None
    print(f"Aviso: Ghostscript não está instalado no sistema ({e}). A funcionalidade PDF/A não funcionará localmente.")
import openpyxl
from flask import (
    Flask,
    jsonify,
    render_template_string,
    request,
    send_file,
)
from pdf2docx import Converter
from pdf2docx.converter import ConversionException
import pytesseract
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
from xhtml2pdf import pisa

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "outputs"

# Criar diretórios se não existirem
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "xlsx", "jpg", "jpeg", "png", "html"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Template HTML
HTML_TEMPLATE = """



<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalPDF.io</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Navbar */
        .navbar { background: rgba(255, 255, 255, 0.1); padding: 15px 30px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); backdrop-filter: blur(10px); color: white; }
        .navbar-brand { font-size: 1.5em; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 10px; justify-self: start; }
        
        .tool-select-wrapper { justify-self: center; position: relative; width: 100%; min-width: 300px; max-width: 500px; }
        .tool-select { appearance: none; background: white; color: #333; padding: 12px 40px 12px 20px; border: none; border-radius: 25px; font-size: 1em; cursor: pointer; outline: none; box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-weight: bold; width: 100%; transition: box-shadow 0.3s; }
        .tool-select:hover { box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .tool-select-wrapper::after { content: '▼'; position: absolute; right: 20px; top: 50%; transform: translateY(-50%); color: #666; pointer-events: none; font-size: 0.8em; }
        
        .lang-switch { justify-self: end; display: flex; background: rgba(255, 255, 255, 0.2); border-radius: 20px; overflow: hidden; }
        .lang-btn { background: none; border: none; color: white; padding: 8px 15px; cursor: pointer; font-size: 0.9em; font-weight: bold; transition: background 0.3s; }
        .lang-btn.active { background: white; color: #667eea; }
        
        /* Acessibility / Focus */
        .tool-select:focus, .lang-btn:focus, .upload-btn:focus, .convert-btn:focus, .remove-btn:focus, #pages-input:focus, #rotation-angle:focus { outline: 3px solid #f6ad55; outline-offset: 2px; }

        .container { max-width: 800px; margin: 40px auto; padding: 20px; flex-grow: 1; display: flex; flex-direction: column; align-items: center; width: 100%; }
        
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        
        .tool-card { background: white; border-radius: 15px; padding: 40px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 100%; }
        .tool-card h3 { color: #333; margin-bottom: 15px; font-size: 1.8em; }
        .tool-card p { color: #666; margin-bottom: 30px; font-size: 1.1em; }
        
        .upload-area { border: 2px dashed #ddd; border-radius: 10px; padding: 50px 20px; text-align: center; background: #f9f9f9; margin: 20px 0; transition: all 0.3s ease; cursor: pointer; position: relative; overflow: hidden; }
        .upload-area:hover { border-color: #667eea; background: #f0f4ff; transform: scale(1.02); }
        .upload-area.dragover { border-color: #667eea; background: #e8f0ff; transform: scale(1.05); }
        .file-input { display: none; }
        .upload-btn { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 25px; cursor: pointer; font-size: 1.1em; transition: background 0.3s ease, transform 0.3s; pointer-events: none; display: inline-block; }
        .upload-btn:hover { background: #5a6fd8; }
        
        /* Pulse Animation */
        @keyframes pulse-soft {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.5); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(102, 126, 234, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
        }
        .pulse-anim { animation: pulse-soft 2s infinite; }

        .convert-btn { background: #28a745; color: white; padding: 15px 40px; border: none; border-radius: 25px; cursor: pointer; font-size: 1.2em; margin-top: 30px; transition: background 0.3s ease; width: 100%; font-weight: bold; }
        .convert-btn:hover { background: #1e7e34; }
        .convert-btn:disabled { background: #6c757d; cursor: not-allowed; opacity: 0.8; }
        
        .file-list { margin-top: 20px; text-align: left; max-height: 250px; overflow-y: auto; padding-right: 10px; }
        .file-item { background: #f8f9fa; padding: 12px 15px; margin: 8px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #eee; transition: background 0.2s; }
        .file-item:hover { background: #f1f3f5; }
        .file-item-name { display: flex; align-items: center; gap: 10px; font-weight: 500; color: #444; word-break: break-all; }
        .remove-btn { background: #ff4757; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; transition: background 0.2s; font-size: 0.9em; flex-shrink: 0; }
        .remove-btn:hover { background: #ff6b81; }
        
        .progress { width: 100%; background: #f0f0f0; border-radius: 10px; margin: 30px 0; overflow: hidden; }
        .progress-bar { height: 20px; background: #667eea; border-radius: 10px; width: 0%; transition: width 0.3s ease; }
        
        /* Toast Notifications */
        .toast-container { position: fixed; bottom: 30px; right: 30px; z-index: 1000; display: flex; flex-direction: column; gap: 15px; }
        .toast { background: white; border-radius: 10px; padding: 15px 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 15px; transform: translateX(120%); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); border-left: 6px solid #ccc; max-width: 350px; }
        .toast.show { transform: translateX(0); }
        .toast.success { border-left-color: #28a745; }
        .toast.error { border-left-color: #dc3545; }
        .toast-icon { font-size: 1.8em; }
        .toast-content h4 { margin: 0 0 5px 0; color: #333; font-size: 1.1em; }
        .toast-content p { margin: 0; color: #666; font-size: 0.95em; line-height: 1.4; }

        .hidden { display: none !important; }
        
        .footer { text-align: center; color: white; padding: 20px 0; background: rgba(0,0,0,0.1); margin-top: auto; }
        .footer p { margin-bottom: 10px; }
        .footer a { color: #e2e8f0; text-decoration: none; transition: color 0.2s; }
        .footer a:hover { color: white; text-decoration: underline; }
        .social-icons { margin-top: 15px; }
        .social-icons a { margin: 0 10px; font-size: 1.2em; }
        
        /* Options specific styles */
        .tool-options { text-align: left; margin-top: 25px; padding: 20px; background: #f8f9fa; border-radius: 10px; border: 1px solid #eee; }
        .tool-options label { display: block; margin-bottom: 8px; font-weight: bold; color: #444; }
        .tool-options input, .tool-options select { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; font-size: 1em; margin-bottom: 15px; transition: border-color 0.2s; }
        .tool-options input:focus, .tool-options select:focus { border-color: #667eea; outline: none; }

        /* Responsive Design */
        @media (max-width: 768px) {
            .navbar { display: flex; flex-direction: column; gap: 15px; text-align: center; padding: 15px; }
            .navbar-brand { justify-self: center; align-self: center; justify-content: center; width: 100%; }
            .tool-select-wrapper { width: 100%; min-width: 100%; }
            .lang-switch { align-self: center; justify-self: center; }
            .container { margin: 20px auto; padding: 15px; }
            .tool-card { padding: 25px 15px; }
            .header h1 { font-size: 2em; }
            .toast-container { bottom: 20px; right: 20px; left: 20px; align-items: center; }
            .toast { max-width: 100%; width: 100%; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-brand" onclick="resetTool()">
            🌟 LocalPDF.io
        </div>
        <div class="tool-select-wrapper">
            <select id="tool-select" class="tool-select" onchange="onToolSelectChange(this.value)" aria-label="Selecione a ferramenta">
                <option value="" disabled selected data-i18n="select_tool">Selecione uma ferramenta...</option>
            </select>
        </div>
        <div class="lang-switch">
            <button class="lang-btn active" onclick="setLanguage('pt-BR')" id="btn-pt-BR" aria-label="Mudar para Português">PT-BR</button>
            <button class="lang-btn" onclick="setLanguage('en')" id="btn-en" aria-label="Mudar para Inglês">EN</button>
        </div>
    </nav>

    <div class="container">
        <div class="header" id="welcome-header">
            <h1 data-i18n="welcome_title">🌟 Bem-vindo ao LocalPDF.io</h1>
            <p data-i18n="welcome_subtitle">Escolha uma ferramenta no menu acima para começar</p>
        </div>

        <!-- Tool Views -->
        <div id="tool-views" class="tool-card hidden">
            <h3 id="tool-title"></h3>
            <p id="tool-description"></p>

            <div class="upload-area" id="upload-area" onclick="document.getElementById('file-input').click()">
                <input type="file" id="file-input" class="file-input" multiple accept=".pdf,.docx,.jpg,.jpeg,.png,.txt,.xlsx,.html">
                <p id="upload-text" data-i18n="upload_text" style="margin-bottom:15px; font-size:1.1em; color:#555;">📁 Clique aqui ou arraste arquivos para fazer upload</p>
                <button class="upload-btn pulse-anim" id="upload-btn" data-i18n="choose_files">Escolher Arquivos</button>
            </div>

            <div id="file-list" class="file-list"></div>

            <div id="options" class="hidden tool-options">
                <!-- Opções específicas para cada ferramenta -->
            </div>

            <button id="convert-btn" class="convert-btn hidden" onclick="convertFiles()" data-i18n="convert_btn">Converter</button>

            <div id="progress" class="progress hidden">
                <div id="progress-bar" class="progress-bar"></div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p data-i18n="developed_by">Desenvolvido por Virgilio Borges e contribuidores.</p>
        <div>
            <a href="mailto:virgilio.junior94@gmail.com">✉️ virgilio.junior94@gmail.com</a> |
            <a href="tel:+5595981121572">📱 (95) 98112-1572</a>
        </div>
        <div class="social-icons">
            <a href="https://github.com/virgiliojr94/localpdf.io" target="_blank">🔗 GitHub</a>
            <a href="https://www.linkedin.com/in/virgiliojunior94/" target="_blank">🔗 LinkedIn</a>
        </div>
    </div>

    <!-- Toast Container -->
    <div id="toast-container" class="toast-container"></div>

    <script>
        // --- i18n ---
        const i18n = {
            'pt-BR': {
                'select_tool': 'Selecione uma ferramenta...',
                'welcome_title': '🌟 Bem-vindo ao LocalPDF.io',
                'welcome_subtitle': 'Escolha uma ferramenta no menu acima para começar',
                'upload_text': '📁 Clique aqui ou arraste arquivos para fazer upload',
                'choose_files': 'Escolher Arquivos',
                'convert_btn': 'Converter',
                'converting': 'Convertendo... ⏳',
                'developed_by': 'Desenvolvido por Virgilio Borges e contribuidores.',
                'success_title': '✅ Sucesso!',
                'success_msg': 'Arquivo convertido e baixado com sucesso!',
                'error_title': '❌ Erro!',
                'error_msg': 'Ocorreu um erro durante a conversão. Tente novamente.',
                'remove_btn': 'Remover',
                'options_delete_pages_label': 'Páginas a excluir (ex: 1, 3, 5-7):',
                'options_delete_pages_placeholder': 'Ex: 1, 3, 5-7',
                'options_rotate_pages_label': 'Páginas (vazio para todas, ex: 1, 3, 5-7):',
                'options_rotate_pages_placeholder': 'Ex: 1, 3, 5-7 ou deixe vazio',
                'options_rotate_angle_label': 'Ângulo de rotação:',
                'angle_90': '90° (Sentido horário)',
                'angle_180': '180°',
                'angle_270': '270° (Sentido anti-horário)',
                'tools': {
                    'pdf-to-images': { title: '🖼️ PDF para Imagens', desc: 'Converta páginas PDF em imagens JPG ou PNG' },
                    'images-to-pdf': { title: '📄 Imagens para PDF', desc: 'Combine várias imagens em um único PDF' },
                    'merge-pdf': { title: '🔗 Mesclar PDFs', desc: 'Combine vários PDFs em um documento único' },
                    'split-pdf': { title: '✂️ Dividir PDF', desc: 'Extraia páginas específicas do seu PDF' },
                    'delete-pages-pdf': { title: '🗑️ Excluir Páginas', desc: 'Exclua páginas específicas do seu PDF (ex: 1, 3, 5-7)' },
                    'rotate-pages-pdf': { title: '🔃 Rotacionar Páginas', desc: 'Rotacione as páginas do seu PDF' },
                    'compress-pdf': { title: '📦 Comprimir PDF', desc: 'Reduza o tamanho do seu arquivo PDF' },
                    'pdf-to-pdfa': { title: '🔒 PDF para PDF/A', desc: 'Padronize seu PDF para arquivamento (PDF/A)' },
                    'word-to-pdf': { title: '📝 Word para PDF', desc: 'Converta um ou mais documentos DOCX para PDF' },
                    'excel-to-pdf': { title: '📊 Excel para PDF', desc: 'Converta planilhas XLSX para PDF' },
                    'txt-to-pdf': { title: '📄 TXT para PDF', desc: 'Converta arquivos de texto simples para PDF' },
                    'pdf-to-word': { title: '🔄 PDF para Word', desc: 'Converta documentos PDF para Word (.docx) editável' },
                    'ocr-pdf': { title: '🔍 OCR em PDF', desc: 'Extraia texto de PDFs e imagens escaneadas com OCR' },
                    'html-to-pdf': { title: '🌐 HTML para PDF', desc: 'Converta arquivos HTML para PDF formatado' }
                }
            },
            'en': {
                'select_tool': 'Select a tool...',
                'welcome_title': '🌟 Welcome to LocalPDF.io',
                'welcome_subtitle': 'Choose a tool from the menu above to get started',
                'upload_text': '📁 Click here or drag files to upload',
                'choose_files': 'Choose Files',
                'convert_btn': 'Convert',
                'converting': 'Converting... ⏳',
                'developed_by': 'Developed by Virgilio Borges and contributors.',
                'success_title': '✅ Success!',
                'success_msg': 'File successfully converted and downloaded!',
                'error_title': '❌ Error!',
                'error_msg': 'An error occurred during conversion. Please try again.',
                'remove_btn': 'Remove',
                'options_delete_pages_label': 'Pages to delete (e.g. 1, 3, 5-7):',
                'options_delete_pages_placeholder': 'e.g. 1, 3, 5-7',
                'options_rotate_pages_label': 'Pages (empty for all, e.g. 1, 3, 5-7):',
                'options_rotate_pages_placeholder': 'e.g. 1, 3, 5-7 or leave empty',
                'options_rotate_angle_label': 'Rotation angle:',
                'angle_90': '90° (Clockwise)',
                'angle_180': '180°',
                'angle_270': '270° (Counter-clockwise)',
                'tools': {
                    'pdf-to-images': { title: '🖼️ PDF to Images', desc: 'Convert each page of your PDF into separate images' },
                    'images-to-pdf': { title: '📄 Images to PDF', desc: 'Combine multiple images into a single PDF file' },
                    'merge-pdf': { title: '🔗 Merge PDFs', desc: 'Combine multiple PDF files into a single document' },
                    'split-pdf': { title: '✂️ Split PDF', desc: 'Extract specific pages from your PDF' },
                    'delete-pages-pdf': { title: '🗑️ Delete Pages', desc: 'Delete specific pages from your PDF (e.g. 1, 3, 5-7)' },
                    'rotate-pages-pdf': { title: '🔃 Rotate Pages', desc: 'Rotate the pages of your PDF' },
                    'compress-pdf': { title: '📦 Compress PDF', desc: 'Reduce the PDF file size while maintaining quality' },
                    'pdf-to-pdfa': { title: '🔒 PDF to PDF/A', desc: 'Convert PDFs to the PDF/A-1b archiving standard' },
                    'word-to-pdf': { title: '📝 Word to PDF', desc: 'Convert Word (.docx) documents to PDF - accepts multiple files' },
                    'excel-to-pdf': { title: '📊 Excel to PDF', desc: 'Convert Excel (.xlsx) spreadsheets to PDF' },
                    'txt-to-pdf': { title: '📄 TXT to PDF', desc: 'Convert plain text (.txt) files to PDF' },
                    'pdf-to-word': { title: '🔄 PDF to Word', desc: 'Convert your PDF documents to editable Word (.docx)' },
                    'ocr-pdf': { title: '🔍 PDF OCR', desc: 'Extract text from PDFs and scanned images using Optical Character Recognition (Tesseract)' },
                    'html-to-pdf': { title: '🌐 HTML to PDF', desc: 'Convert HTML files to formatted PDF' }
                }
            }
        };

        let currentLang = 'pt-BR';
        let currentTool = '';
        let uploadedFiles = [];

        const toolConfigs = {
            'pdf-to-images': { accept: '.pdf', multiple: false },
            'images-to-pdf': { accept: '.jpg,.jpeg,.png', multiple: true },
            'merge-pdf': { accept: '.pdf', multiple: true },
            'split-pdf': { accept: '.pdf', multiple: false },
            'delete-pages-pdf': { accept: '.pdf', multiple: false },
            'rotate-pages-pdf': { accept: '.pdf', multiple: false },
            'compress-pdf': { accept: '.pdf', multiple: false },
            'pdf-to-pdfa': { accept: '.pdf', multiple: true },
            'word-to-pdf': { accept: '.docx', multiple: true },
            'excel-to-pdf': { accept: '.xlsx', multiple: false },
            'txt-to-pdf': { accept: '.txt', multiple: false },
            'pdf-to-word': { accept: '.pdf', multiple: false },
            'ocr-pdf': { accept: '.pdf,.jpg,.jpeg,.png', multiple: false },
            'html-to-pdf': { accept: '.html', multiple: false }
        };

        function setLanguage(lang) {
            currentLang = lang;
            
            // Update buttons
            document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`btn-${lang}`).classList.add('active');
            
            // Update static translations
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[lang][key]) {
                    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                        el.placeholder = i18n[lang][key];
                    } else {
                        el.innerText = i18n[lang][key];
                    }
                }
            });

            // Update Dropdown options
            updateDropdown();

            // Update current tool if selected
            if (currentTool) {
                showTool(currentTool);
            }
            
            // Update file list
            updateFileList();
        }

        function updateDropdown() {
            const select = document.getElementById('tool-select');
            select.innerHTML = `<option value="" disabled ${!currentTool ? 'selected' : ''} data-i18n="select_tool">${i18n[currentLang]['select_tool']}</option>`;
            
            const sortedKeys = Object.keys(toolConfigs).sort((a, b) => {
                const titleA = i18n[currentLang].tools[a].title;
                const titleB = i18n[currentLang].tools[b].title;
                const textA = titleA.split(' ').slice(1).join(' ').toLowerCase();
                const textB = titleB.split(' ').slice(1).join(' ').toLowerCase();
                return textA.localeCompare(textB);
            });

            for (const key of sortedKeys) {
                const option = document.createElement('option');
                option.value = key;
                option.innerText = i18n[currentLang].tools[key].title;
                if (key === currentTool) {
                    option.selected = true;
                }
                select.appendChild(option);
            }
        }

        function resetTool() {
            currentTool = '';
            document.getElementById('tool-select').value = '';
            document.getElementById('welcome-header').classList.remove('hidden');
            document.getElementById('tool-views').classList.add('hidden');
            uploadedFiles = [];
            updateFileList();
        }

        function onToolSelectChange(toolName) {
            if (toolName) {
                showTool(toolName);
            }
        }

        function showTool(toolName) {
            currentTool = toolName;
            const config = toolConfigs[toolName];
            const trans = i18n[currentLang].tools[toolName];

            document.getElementById('welcome-header').classList.add('hidden');
            document.getElementById('tool-views').classList.remove('hidden');
            
            document.getElementById('tool-title').innerText = trans.title;
            document.getElementById('tool-description').innerText = trans.desc;
            document.getElementById('file-input').accept = config.accept;
            document.getElementById('file-input').multiple = config.multiple;

            const optionsDiv = document.getElementById('options');
            optionsDiv.innerHTML = '';
            optionsDiv.classList.add('hidden');
            
            const t = i18n[currentLang];
            
            if (toolName === 'delete-pages-pdf') {
                optionsDiv.innerHTML = `
                    <label>${t.options_delete_pages_label}</label>
                    <input type="text" id="pages-input" placeholder="${t.options_delete_pages_placeholder}">
                `;
                optionsDiv.classList.remove('hidden');
            } else if (toolName === 'rotate-pages-pdf') {
                optionsDiv.innerHTML = `
                    <label>${t.options_rotate_pages_label}</label>
                    <input type="text" id="pages-input" placeholder="${t.options_rotate_pages_placeholder}">
                    
                    <label>${t.options_rotate_angle_label}</label>
                    <select id="rotation-angle">
                        <option value="90">${t.angle_90}</option>
                        <option value="180">${t.angle_180}</option>
                        <option value="270">${t.angle_270}</option>
                    </select>
                `;
                optionsDiv.classList.remove('hidden');
            }

            uploadedFiles = [];
            updateFileList();
        }

        function updateFileList() {
            const fileList = document.getElementById('file-list');
            const convertBtn = document.getElementById('convert-btn');
            const uploadBtn = document.getElementById('upload-btn');
            const t = i18n[currentLang];

            if (uploadedFiles.length === 0) {
                fileList.innerHTML = '';
                convertBtn.classList.add('hidden');
                uploadBtn.classList.add('pulse-anim'); // Add animation when empty
                return;
            }

            uploadBtn.classList.remove('pulse-anim'); // Remove animation when has files

            fileList.innerHTML = uploadedFiles.map((file, index) => `
                <div class="file-item">
                    <span class="file-item-name">📄 ${file.name} <small style="color:#888;">(${(file.size / 1024 / 1024).toFixed(2)} MB)</small></span>
                    <button class="remove-btn" onclick="removeFile(${index})">${t.remove_btn}</button>
                </div>
            `).join('');

            convertBtn.classList.remove('hidden');
        }

        function removeFile(index) {
            uploadedFiles.splice(index, 1);
            updateFileList();
        }

        // Toasts
        function showToast(type, title, message) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            const icon = type === 'success' ? '✅' : '❌';
            toast.innerHTML = `
                <div class="toast-icon">${icon}</div>
                <div class="toast-content">
                    <h4>${title}</h4>
                    <p>${message}</p>
                </div>
            `;
            container.appendChild(toast);
            
            // Trigger animation
            setTimeout(() => toast.classList.add('show'), 10);
            
            // Remove after 5 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 400);
            }, 5000);
        }

        // Upload de arquivos
        document.getElementById('file-input').addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            if (toolConfigs[currentTool].multiple) {
                uploadedFiles = uploadedFiles.concat(files);
            } else {
                uploadedFiles = files.slice(0, 1);
            }
            updateFileList();
            this.value = ''; // reset input
        });

        // Drag and drop
        const uploadArea = document.getElementById('upload-area');
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            if (!currentTool) return; // do nothing if no tool is selected

            const files = Array.from(e.dataTransfer.files);
            if (toolConfigs[currentTool].multiple) {
                uploadedFiles = uploadedFiles.concat(files);
            } else {
                uploadedFiles = files.slice(0, 1);
            }
            updateFileList();
        });

        async function convertFiles() {
            if (uploadedFiles.length === 0) return;

            const formData = new FormData();
            uploadedFiles.forEach(file => {
                formData.append('files', file);
            });
            formData.append('tool', currentTool);

            const pagesInput = document.getElementById('pages-input');
            if (pagesInput) {
                formData.append('pages', pagesInput.value);
            }
            const rotationAngle = document.getElementById('rotation-angle');
            if (rotationAngle) {
                formData.append('angle', rotationAngle.value);
            }

            const t = i18n[currentLang];
            const btn = document.getElementById('convert-btn');
            
            document.getElementById('progress').classList.remove('hidden');
            btn.disabled = true;
            btn.innerText = t.converting;

            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'converted_file.zip';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);

                    showToast('success', t.success_title, t.success_msg);
                } else {
                    throw new Error('Erro na conversão');
                }
            } catch (error) {
                showToast('error', t.error_title, t.error_msg);
            } finally {
                document.getElementById('progress').classList.add('hidden');
                btn.disabled = false;
                btn.innerText = t.convert_btn;
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            updateDropdown();
            setLanguage('pt-BR');
        });
    </script>
</body>
</html>



"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


def excel_to_pdf(file, temp_dir):
    xlsx_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(xlsx_path)

    pdf_path = os.path.join(temp_dir, "excel_to_pdf.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y_position = height - 50

    try:
        workbook = openpyxl.load_workbook(xlsx_path)
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            c.setFont("Helvetica", 10)
            c.drawString(50, y_position, f"--- Planilha: {sheet_name} ---")
            y_position -= 20

            for row_idx, row in enumerate(sheet.iter_rows()):
                row_data = [
                    str(cell.value) if cell.value is not None else "" for cell in row
                ]
                line_text = " | ".join(row_data)

                # Simples quebra de linha para caber na página
                max_line_width = int(
                    (width - 100) / 6
                )  # Estimativa de caracteres por linha
                if len(line_text) > max_line_width:
                    # Implementação mais robusta de quebra de linha seria necessária
                    line_text = line_text[:max_line_width] + "..."

                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 10)  # Reset font after new page

                c.drawString(50, y_position, line_text)
                y_position -= 15  # Espaçamento menor para linhas de planilha

            y_position -= 30  # Espaçamento entre planilhas
            if (
                y_position < 50 and sheet_name != workbook.sheetnames[-1]
            ):  # Only show new page if not last sheet
                c.showPage()
                y_position = height - 50

    except Exception as e:
        # Handle potential errors with Excel files
        c.drawString(50, y_position - 20, f"Erro ao ler planilha: {e}")
        print(f"Erro ao ler planilha Excel: {e}")

    c.save()
    return [pdf_path]


def txt_to_pdf(file, temp_dir):
    txt_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(txt_path)

    pdf_path = os.path.join(temp_dir, "text_to_pdf.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y_position = height - 50

    c.setFont("Helvetica", 12)

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                # Simples quebra de linha para caber na página
                text_line = line.strip()
                max_width_px = width - 100  # Margens de 50px de cada lado

                # Estimar a largura do texto para quebrar linhas
                # ReportLab não tem quebra automática de texto complexa por default
                # Esta é uma estimativa MUITO simples; para algo robusto, precisaria de TextObject
                approx_char_width_px = 7  # Média para Helvetica 12
                chars_per_line = int(max_width_px / approx_char_width_px)

                if len(text_line) > chars_per_line:
                    # Quebra simples da linha
                    chunks = [
                        text_line[i : i + chars_per_line]
                        for i in range(0, len(text_line), chars_per_line)
                    ]
                else:
                    chunks = [text_line]

                for chunk in chunks:
                    if y_position < 50:  # Margem inferior
                        c.showPage()
                        y_position = height - 50
                        c.setFont("Helvetica", 12)  # Reset font after new page

                    c.drawString(50, y_position, chunk)
                    y_position -= 15  # Espaçamento entre linhas

    except Exception as e:
        c.drawString(50, y_position - 20, f"Erro ao ler arquivo de texto: {e}")
        print(f"Erro ao ler arquivo de texto: {e}")

    c.save()
    return [pdf_path]


@app.route("/convert", methods=["POST"])
def convert():
    if "files" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    files = request.files.getlist("files")
    tool = request.form.get("tool")

    if not files or files[0].filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # Validação de extensão dos arquivos enviados
    for f in files:
        if not allowed_file(f.filename):
            return jsonify({"error": f"Extensão não permitida: {f.filename}"}), 400

    # Criar diretório temporário
    temp_dir = tempfile.mkdtemp()
    response = None
    try:
        if tool == "pdf-to-images":
            output_files = pdf_to_images(files[0], temp_dir)
        elif tool == "images-to-pdf":
            output_files = images_to_pdf(files, temp_dir)
        elif tool == "merge-pdf":
            output_files = merge_pdfs(files, temp_dir)
        elif tool == "split-pdf":
            output_files = split_pdf(files[0], temp_dir)
        elif tool == "delete-pages-pdf":
            pages_str = request.form.get("pages", "")
            output_files = delete_pages_pdf(files[0], pages_str, temp_dir)
        elif tool == "rotate-pages-pdf":
            pages_str = request.form.get("pages", "")
            angle_str = request.form.get("angle", "90")
            output_files = rotate_pages_pdf(files[0], pages_str, angle_str, temp_dir)
        elif tool == "compress-pdf":
            output_files = compress_pdf(files[0], temp_dir)
        elif tool == "pdf-to-pdfa":
            output_files = pdf_to_pdfa(files, temp_dir)
        elif tool == "word-to-pdf":
            output_files = word_to_pdf(files, temp_dir)
        elif tool == "excel-to-pdf":
            output_files = excel_to_pdf(files[0], temp_dir)
        elif tool == "txt-to-pdf":
            output_files = txt_to_pdf(files[0], temp_dir)
        elif tool == "pdf-to-word":
            output_files = pdf_to_word(files[0], temp_dir)
        elif tool == "ocr-pdf":
            output_files = ocr_pdf(files[0], temp_dir)
        elif tool == "html-to-pdf":
            output_files = html_to_pdf(files[0], temp_dir)
        else:
            return jsonify({"error": "Ferramenta não suportada"}), 400

        response = build_response(output_files, temp_dir)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Diretório temporário limpo após preparar resposta (BytesIO) evitando remoção antecipada
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def pdf_to_images(file, temp_dir):
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)

    doc = fitz.open(pdf_path)
    output_files = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolution
        img_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
        pix.save(img_path)
        output_files.append(img_path)

    doc.close()
    return output_files


def images_to_pdf(files, temp_dir):
    images = []
    for file in files:
        img_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(img_path)
        img = Image.open(img_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    pdf_path = os.path.join(temp_dir, "images_to_pdf.pdf")
    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    return [pdf_path]


def merge_pdfs(files, temp_dir):
    merged_doc = fitz.open()

    for file in files:
        pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(pdf_path)
        doc = fitz.open(pdf_path)
        merged_doc.insert_pdf(doc)
        doc.close()

    output_path = os.path.join(temp_dir, "merged.pdf")
    merged_doc.save(output_path)
    merged_doc.close()

    return [output_path]


def split_pdf(file, temp_dir):
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)

    doc = fitz.open(pdf_path)
    output_files = []

    for page_num in range(len(doc)):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        output_path = os.path.join(temp_dir, f"page_{page_num + 1}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        output_files.append(output_path)

    doc.close()
    return output_files


def parse_pages(pages_str, max_pages):
    if not pages_str or not pages_str.strip():
        return set(range(max_pages))
    
    pages = set()
    parts = pages_str.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start_idx = int(start) - 1
                end_idx = int(end) - 1
                if start_idx >= 0 and end_idx < max_pages and start_idx <= end_idx:
                    pages.update(range(start_idx, end_idx + 1))
            except ValueError:
                pass
        else:
            try:
                idx = int(part) - 1
                if 0 <= idx < max_pages:
                    pages.add(idx)
            except ValueError:
                pass
    return pages


def delete_pages_pdf(file, pages_str, temp_dir):
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)

    doc = fitz.open(pdf_path)
    max_pages = len(doc)
    pages_to_delete = parse_pages(pages_str, max_pages)

    if not pages_to_delete:
        doc.close()
        return [pdf_path]
    
    pages_to_keep = [i for i in range(max_pages) if i not in pages_to_delete]
    
    if not pages_to_keep:
        doc.close()
        raise ValueError("Não é possível excluir todas as páginas do documento.")
        
    doc.select(pages_to_keep)

    output_path = os.path.join(temp_dir, "deleted_pages.pdf")
    doc.save(output_path)
    doc.close()

    return [output_path]


def rotate_pages_pdf(file, pages_str, angle_str, temp_dir):
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)

    doc = fitz.open(pdf_path)
    max_pages = len(doc)
    pages_to_rotate = parse_pages(pages_str, max_pages)

    try:
        angle = int(angle_str)
    except ValueError:
        angle = 90

    for page_num in pages_to_rotate:
        page = doc[page_num]
        page.set_rotation((page.rotation + angle) % 360)

    output_path = os.path.join(temp_dir, "rotated_pages.pdf")
    doc.save(output_path)
    doc.close()

    return [output_path]


def compress_pdf(file, temp_dir):
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)

    doc = fitz.open(pdf_path)
    output_path = os.path.join(temp_dir, "compressed.pdf")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    return [output_path]


def pdf_to_pdfa(files, temp_dir):
    """Converte um ou mais PDFs para PDF/A-1b usando Ghostscript."""
    if not isinstance(files, list):
        files = [files]

    output_files = []

    for file in files:
        input_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(input_path)

        base_name, _ = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.join(temp_dir, f"{base_name}_pdfa.pdf")

        gs_args = [
            "gs",
            "-dPDFA=1",
            "-dBATCH",
            "-dNOPAUSE",
            "-dNOOUTERSAVE",
            "-dUseCIEColor",
            "-sProcessColorModel=DeviceRGB",
            "-sDEVICE=pdfwrite",
            "-sColorConversionStrategy=UseDeviceIndependentColor",
            "-dPDFACompatibilityPolicy=1",
            f"-sOutputFile={output_path}",
            input_path,
        ]
        gs_args = [
            arg.encode("utf-8") if isinstance(arg, str) else arg for arg in gs_args
        ]

        try:
            ghostscript.Ghostscript(*gs_args)
        except Exception as e:
            raise RuntimeError(
                f"Erro ao converter {file.filename} para PDF/A: {e}"
            ) from e

        output_files.append(output_path)

    return output_files


def word_to_pdf(files, temp_dir):
    """
    Converte um ou múltiplos arquivos DOCX para PDF
    Se houver múltiplos arquivos, mescla todos em um único PDF
    """
    from docx import Document
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    # Criar PDF de saída
    pdf_path = os.path.join(temp_dir, "word_to_pdf.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y_position = height - 50

    # Se for apenas um arquivo (compatibilidade)
    if not isinstance(files, list):
        files = [files]

    # Processar cada arquivo DOCX
    for file_idx, file in enumerate(files):
        docx_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(docx_path)

        # Lê o documento Word
        doc = Document(docx_path)

        # Adicionar separador visual (exceto no primeiro documento)
        if file_idx > 0:
            # Quebra de página
            c.showPage()
            y_position = height - 50

            # Adicionar cabeçalho com nome do arquivo
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"{'=' * 60}")
            y_position -= 20
            c.drawString(50, y_position, f"Documento: {file.filename}")
            y_position -= 20
            c.drawString(50, y_position, f"{'=' * 60}")
            y_position -= 30
            c.setFont("Helvetica", 11)

        # Processar parágrafos
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                # Quebra texto longo em múltiplas linhas
                text = paragraph.text
                max_width = width - 100

                # Estimativa simples de largura de texto
                approx_char_width = 6
                chars_per_line = int(max_width / approx_char_width)

                words = text.split()
                lines = []
                current_line = []

                for word in words:
                    if len(" ".join(current_line + [word])) <= chars_per_line:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)

                if current_line:
                    lines.append(" ".join(current_line))

                for line in lines:
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50

                    c.drawString(50, y_position, line)
                    y_position -= 20

        # Processar tabelas (se houver)
        for table in doc.tables:
            # Adicionar espaçamento antes da tabela
            y_position -= 10

            if y_position < 100:
                c.showPage()
                y_position = height - 50

            # Desenhar linhas da tabela
            c.setFont("Helvetica", 9)
            for row in table.rows:
                row_text = " | ".join([cell.text for cell in row.cells])

                # Quebrar texto da linha se necessário
                if len(row_text) > 100:
                    row_text = row_text[:97] + "..."

                if y_position < 50:
                    c.showPage()
                    y_position = height - 50

                c.drawString(50, y_position, row_text)
                y_position -= 15

            # Espaçamento após tabela
            y_position -= 10
            c.setFont("Helvetica", 11)

    c.save()
    return [pdf_path]


def pdf_to_word(file, temp_dir):
    """
    Convert PDF to Word (.docx) format.
    """
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)

    docx_filename = os.path.splitext(secure_filename(file.filename))[0] + ".docx"
    docx_path = os.path.join(temp_dir, docx_filename)

    cv = None
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
    except ValueError as e:
        raise RuntimeError(f"Erro no arquivo PDF: {e}") from e
    except ConversionException as e:
        raise RuntimeError(f"Erro interno na conversão: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Erro ao converter {file.filename} para Word: {e}") from e
    finally:
        if cv:
            cv.close()

    return [docx_path]


def ocr_pdf(file, temp_dir):
    """
    Extrai texto de um PDF ou imagem usando Tesseract OCR.
    Retorna um arquivo TXT com o texto extraído.
    """
    filename = secure_filename(file.filename)
    input_path = os.path.join(temp_dir, filename)
    file.save(input_path)

    ext = filename.rsplit(".", 1)[1].lower()
    extracted_text = []

    if ext == "pdf":
        with fitz.open(input_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolução
                img_path = os.path.join(temp_dir, f"ocr_page_{page_num + 1}.png")
                pix.save(img_path)

                with Image.open(img_path) as img:
                    text = pytesseract.image_to_string(img, lang="por+eng")
                extracted_text.append(f"--- Página {page_num + 1} ---\n{text}")
    elif ext in ("jpg", "jpeg", "png"):
        # Aplicar OCR diretamente na imagem
        with Image.open(input_path) as img:
            text = pytesseract.image_to_string(img, lang="por+eng")
        extracted_text.append(text)
    else:
        raise RuntimeError(f"Formato não suportado para OCR: {ext}")

    # Salvar texto extraído em arquivo TXT
    base_name = os.path.splitext(filename)[0]
    txt_path = os.path.join(temp_dir, f"{base_name}_ocr.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(extracted_text))

    return [txt_path]


def html_to_pdf(file, temp_dir):
    """
    Convert HTML file to PDF format.
    """
    html_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(html_path)

    pdf_path = os.path.join(temp_dir, "html_to_pdf.pdf")
    
    with open(html_path, "r", encoding="utf-8") as html_file:
        source_html = html_file.read()
        
    with open(pdf_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(source_html, dest=result_file)
        
    if pisa_status.err:
        raise RuntimeError(f"Erro ao converter {file.filename} para PDF.")
        
    return [pdf_path]


def build_response(output_files, temp_dir):
    """Monta resposta enviando arquivos como attachment sem risco de remoção prematura do diretório temporário."""
    if len(output_files) == 1:
        file_path = output_files[0]
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            data = f.read()
        return send_file(io.BytesIO(data), as_attachment=True, download_name=filename)
    else:
        zip_path = os.path.join(temp_dir, "converted_files.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in output_files:
                zipf.write(file_path, os.path.basename(file_path))
        with open(zip_path, "rb") as f:
            data = f.read()
        return send_file(
            io.BytesIO(data), as_attachment=True, download_name="converted_files.zip"
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
