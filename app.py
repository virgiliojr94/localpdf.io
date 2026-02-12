import io
import os
import shutil
import tempfile
import zipfile

import fitz  # PyMuPDF
import ghostscript
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
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "outputs"

# Criar diretórios se não existirem
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "xlsx", "jpg", "jpeg", "png"}


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
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 40px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .tool-card { background: white; border-radius: 15px; padding: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s ease; cursor: pointer; }
        .tool-card:hover { transform: translateY(-5px); }
        .tool-card h3 { color: #333; margin-bottom: 15px; font-size: 1.5em; }
        .tool-card p { color: #666; margin-bottom: 20px; }
        .upload-area { border: 2px dashed #ddd; border-radius: 10px; padding: 40px; text-align: center; background: #f9f9f9; margin: 20px 0; transition: all 0.3s ease; }
        .upload-area:hover { border-color: #667eea; background: #f0f4ff; }
        .upload-area.dragover { border-color: #667eea; background: #e8f0ff; }
        .file-input { display: none; }
        .upload-btn { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 25px; cursor: pointer; font-size: 1.1em; transition: background 0.3s ease; }
        .upload-btn:hover { background: #5a6fd8; }
        .convert-btn { background: #28a745; color: white; padding: 15px 40px; border: none; border-radius: 25px; cursor: pointer; font-size: 1.2em; margin-top: 20px; transition: background 0.3s ease; }
        .convert-btn:hover { background: #1e7e34; }
        .convert-btn:disabled { background: #ccc; cursor: not-allowed; }
        .file-list { margin-top: 20px; }
        .file-item { background: #f8f9fa; padding: 10px 15px; margin: 5px 0; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .progress { width: 100%; background: #f0f0f0; border-radius: 10px; margin: 20px 0; }
        .progress-bar { height: 20px; background: #667eea; border-radius: 10px; width: 0%; transition: width 0.3s ease; }
        .result { margin-top: 20px; padding: 20px; background: #d4edda; border-radius: 10px; color: #155724; }
        .error { margin-top: 20px; padding: 20px; background: #f8d7da; border-radius: 10px; color: #721c24; }
        .hidden { display: none; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); }
        .modal-content { background: white; margin: 5% auto; padding: 30px; width: 80%; max-width: 600px; border-radius: 15px; position: relative; }
        .close { position: absolute; right: 20px; top: 15px; font-size: 30px; cursor: pointer; color: #aaa; }
        .close:hover { color: #000; }
        .back-btn { background: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 25px; cursor: pointer; margin-bottom: 20px; }
        .back-btn:hover { background: #545b62; }
        .footer { text-align: center; color: white; margin-top: 40px; padding: 20px 0; border-top: 1px solid #ddd; }
        .footer p { margin-bottom: 10px; }
        .footer a { color: #667eea; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }
        .social-icons { margin-top: 10px; }
        .social-icons a { margin: 0 10px; color: #667eea; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 LocalPDF.io</h1>
            <p>Todas as ferramentas PDF que você precisa em um só lugar</p>
        </div>

        <div id="home-view">
            <div class="tools-grid">
                <div class="tool-card" onclick="showTool('pdf-to-images')">
                    <h3>🖼️ PDF para Imagens</h3>
                    <p>Converta páginas PDF em imagens JPG ou PNG</p>
                </div>
                <div class="tool-card" onclick="showTool('images-to-pdf')">
                    <h3>📄 Imagens para PDF</h3>
                    <p>Combine várias imagens em um único PDF</p>
                </div>
                <div class="tool-card" onclick="showTool('merge-pdf')">
                    <h3>🔗 Mesclar PDFs</h3>
                    <p>Combine vários PDFs em um documento único</p>
                </div>
                <div class="tool-card" onclick="showTool('split-pdf')">
                    <h3>✂️ Dividir PDF</h3>
                    <p>Extraia páginas específicas do seu PDF</p>
                </div>
                <div class="tool-card" onclick="showTool('compress-pdf')">
                    <h3>📦 Comprimir PDF</h3>
                    <p>Reduza o tamanho do seu arquivo PDF</p>
                </div>
                <div class="tool-card" onclick="showTool('pdf-to-pdfa')">
                    <h3>🔒 PDF para PDF/A</h3>
                    <p>Padronize seu PDF para arquivamento (PDF/A)</p>
                </div>
                <div class="tool-card" onclick="showTool('word-to-pdf')">
                    <h3>📝 Word para PDF</h3>
                    <p>Converta um ou mais documentos DOCX para PDF</p>
                </div>
                <div class="tool-card" onclick="showTool('excel-to-pdf')">
                    <h3>📊 Excel para PDF</h3>
                    <p>Converta planilhas XLSX para PDF</p>
                </div>
                <div class="tool-card" onclick="showTool('txt-to-pdf')">
                    <h3>📄 TXT para PDF</h3>
                    <p>Converta arquivos de texto simples para PDF</p>
                </div>
                <div class="tool-card" onclick="showTool('pdf-to-word')">
                    <h3>🔄 PDF para Word</h3>
                    <p>Converta documentos PDF para Word (.docx) editável</p>
                </div>
            </div>
        </div>

        <!-- Tool Views -->
        <div id="tool-views" class="hidden">
            <button class="back-btn" onclick="showHome()">← Voltar</button>
            <div class="tool-card">
                <h3 id="tool-title"></h3>
                <p id="tool-description"></p>

                <div class="upload-area" id="upload-area" onclick="document.getElementById('file-input').click()">
                    <input type="file" id="file-input" class="file-input" multiple accept=".pdf,.docx,.jpg,.jpeg,.png,.txt,.xlsx">
                    <p>📁 Clique aqui ou arraste arquivos para fazer upload</p>
                    <button class="upload-btn">Escolher Arquivos</button>
                </div>

                <div id="file-list" class="file-list"></div>

                <div id="options" class="hidden">
                    <!-- Opções específicas para cada ferramenta -->
                </div>

                <button id="convert-btn" class="convert-btn hidden" onclick="convertFiles()">Converter</button>

                <div id="progress" class="progress hidden">
                    <div id="progress-bar" class="progress-bar"></div>
                </div>

                <div id="result" class="hidden"></div>
            </div>
        </div>

        <div class="footer">
            <p>Desenvolvido por Virgilio Borges</p>
            <div>
                <a href="mailto:virgilio.junior94@gmail.com">✉️ virgilio.junior94@gmail.com</a> |
                <a href="tel:+5595981121572">📱 (95) 98112-1572</a>
            </div>
            <div class="social-icons">
                <a href="https://github.com/virgiliojr94" target="_blank">🔗 GitHub</a>
                <a href="https://www.linkedin.com/in/virgiliojunior94/" target="_blank">🔗 LinkedIn</a>
            </div>
        </div>
    </div>

    <script>
        let currentTool = '';
        let uploadedFiles = [];

        const tools = {
            'pdf-to-images': {
                title: '🖼️ PDF para Imagens',
                description: 'Converta cada página do seu PDF em imagens separadas',
                accept: '.pdf',
                multiple: false
            },
            'images-to-pdf': {
                title: '📄 Imagens para PDF',
                description: 'Combine múltiplas imagens em um único arquivo PDF',
                accept: '.jpg,.jpeg,.png',
                multiple: true
            },
            'merge-pdf': {
                title: '🔗 Mesclar PDFs',
                description: 'Combine vários arquivos PDF em um documento único',
                accept: '.pdf',
                multiple: true
            },
            'split-pdf': {
                title: '✂️ Dividir PDF',
                description: 'Extraia páginas específicas do seu PDF',
                accept: '.pdf',
                multiple: false
            },
            'compress-pdf': {
                title: '📦 Comprimir PDF',
                description: 'Reduza o tamanho do arquivo PDF mantendo a qualidade',
                accept: '.pdf',
                multiple: false
            },
            'pdf-to-pdfa': {
                title: '🔒 PDF para PDF/A',
                description: 'Converta PDFs para o padrão de arquivamento PDF/A-1b',
                accept: '.pdf',
                multiple: true
            },
            'word-to-pdf': {
                title: '📝 Word para PDF',
                description: 'Converta documentos Word (.docx) para PDF - aceita múltiplos arquivos',
                accept: '.docx',
                multiple: true
            },
            'excel-to-pdf': {
                title: '📊 Excel para PDF',
                description: 'Converta planilhas Excel (.xlsx) para PDF',
                accept: '.xlsx',
                multiple: false
            },
            'txt-to-pdf': {
                title: '📄 TXT para PDF',
                description: 'Converta arquivos de texto simples (.txt) para PDF',
                accept: '.txt',
                multiple: false
            },
            'pdf-to-word': {
                title: '🔄 PDF para Word',
                description: 'Converta seus documentos PDF para Word (.docx) editável',
                accept: '.pdf',
                multiple: false
            }
        };

        function showTool(toolName) {
            currentTool = toolName;
            const tool = tools[toolName];

            document.getElementById('home-view').classList.add('hidden');
            document.getElementById('tool-views').classList.remove('hidden');
            document.getElementById('tool-title').innerText = tool.title;
            document.getElementById('tool-description').innerText = tool.description;
            document.getElementById('file-input').accept = tool.accept;
            document.getElementById('file-input').multiple = tool.multiple;

            uploadedFiles = [];
            updateFileList();
            hideResult();
        }

        function showHome() {
            document.getElementById('home-view').classList.remove('hidden');
            document.getElementById('tool-views').classList.add('hidden');
            uploadedFiles = [];
        }

        function updateFileList() {
            const fileList = document.getElementById('file-list');
            const convertBtn = document.getElementById('convert-btn');

            if (uploadedFiles.length === 0) {
                fileList.innerHTML = '';
                convertBtn.classList.add('hidden');
                return;
            }

            fileList.innerHTML = uploadedFiles.map((file, index) => `
                <div class="file-item">
                    <span>📄 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                    <button onclick="removeFile(${index})" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">Remover</button>
                </div>
            `).join('');

            convertBtn.classList.remove('hidden');
        }

        function removeFile(index) {
            uploadedFiles.splice(index, 1);
            updateFileList();
        }

        function hideResult() {
            document.getElementById('result').classList.add('hidden');
            document.getElementById('progress').classList.add('hidden');
        }

        // Upload de arquivos
        document.getElementById('file-input').addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            if (tools[currentTool].multiple) {
                uploadedFiles = uploadedFiles.concat(files);
            } else {
                uploadedFiles = files.slice(0, 1);
            }
            updateFileList();
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

            const files = Array.from(e.dataTransfer.files);
            if (tools[currentTool].multiple) {
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

            document.getElementById('progress').classList.remove('hidden');
            document.getElementById('convert-btn').disabled = true;

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

                    document.getElementById('result').innerHTML = '<h4>✅ Sucesso!</h4><p>Arquivo convertido e baixado com sucesso!</p>';
                    document.getElementById('result').classList.remove('hidden');
                } else {
                    throw new Error('Erro na conversão');
                }
            } catch (error) {
                document.getElementById('result').innerHTML = '<h4>❌ Erro!</h4><p>Ocorreu um erro durante a conversão. Tente novamente.</p>';
                document.getElementById('result').classList.remove('hidden');
            } finally {
                document.getElementById('progress').classList.add('hidden');
                document.getElementById('convert-btn').disabled = false;
            }
        }
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
