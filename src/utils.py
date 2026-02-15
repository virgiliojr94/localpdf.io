"""
Funções utilitárias para manipulação de arquivos e canvas PDF
"""

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import List

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .config import Config


def allowed_file(filename: str) -> bool:
    """Verifica se a extensão do arquivo é permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@contextmanager
def temporary_directory():
    """Context manager para criação e limpeza de diretório temporário"""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def save_uploaded_file(file: FileStorage, directory: str) -> Path:
    """
    Salva arquivo enviado de forma segura
    
    Args:
        file: Arquivo do werkzeug FileStorage
        directory: Diretório de destino
        
    Returns:
        Path do arquivo salvo
    """
    filename = secure_filename(file.filename)
    filepath = Path(directory) / filename
    file.save(str(filepath))
    return filepath


def create_text_pdf_canvas(pdf_path: str) -> tuple:
    """
    Cria canvas PDF para texto com configurações padrão
    
    Returns:
        Tupla com (canvas, width, height, y_position)
    """
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y_position = height - Config.TEXT_MARGIN
    return c, width, height, y_position


def handle_page_break(c: canvas.Canvas, y_position: float, height: float) -> float:
    """
    Gerencia quebra de página se necessário
    
    Returns:
        Nova posição Y
    """
    if y_position < Config.TEXT_MARGIN:
        c.showPage()
        return height - Config.TEXT_MARGIN
    return y_position


def wrap_text(text: str, max_chars: int) -> List[str]:
    """
    Quebra texto em linhas respeitando limite de caracteres
    
    Args:
        text: Texto a ser quebrado
        max_chars: Máximo de caracteres por linha
        
    Returns:
        Lista de linhas
    """
    if len(text) <= max_chars:
        return [text]
    
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        if len(test_line) <= max_chars:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word[:max_chars])
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines
