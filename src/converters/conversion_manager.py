"""
Gerenciador de conversões de arquivos
"""

from typing import List
from werkzeug.datastructures import FileStorage

from .pdf_converter import PDFConverter
from .document_converter import DocumentToPDFConverter


class ConversionManager:
    """Gerencia operações de conversão de arquivos"""
    
    # Mapeamento de ferramentas para funções de conversão
    CONVERTERS = {
        "pdf-to-images": PDFConverter.pdf_to_images,
        "images-to-pdf": PDFConverter.images_to_pdf,
        "merge-pdf": PDFConverter.merge_pdfs,
        "split-pdf": PDFConverter.split_pdf,
        "compress-pdf": PDFConverter.compress_pdf,
        "pdf-to-pdfa": PDFConverter.pdf_to_pdfa,
        "pdf-to-word": PDFConverter.pdf_to_word,
        "word-to-pdf": DocumentToPDFConverter.word_to_pdf,
        "excel-to-pdf": DocumentToPDFConverter.excel_to_pdf,
        "txt-to-pdf": DocumentToPDFConverter.txt_to_pdf,
    }
    
    @classmethod
    def convert(cls, tool: str, files: List[FileStorage], temp_dir: str) -> List[str]:
        """
        Executa conversão baseado na ferramenta selecionada
        
        Args:
            tool: Nome da ferramenta de conversão
            files: Lista de arquivos para converter
            temp_dir: Diretório temporário
            
        Returns:
            Lista de caminhos dos arquivos convertidos
            
        Raises:
            ValueError: Se ferramenta não for suportada
        """
        if tool not in cls.CONVERTERS:
            raise ValueError(f"Ferramenta não suportada: {tool}")
        
        converter = cls.CONVERTERS[tool]
        
        # Algumas conversões aceitam lista, outras um único arquivo
        if tool in ["images-to-pdf", "merge-pdf", "pdf-to-pdfa", "word-to-pdf"]:
            return converter(files, temp_dir)
        else:
            return converter(files[0], temp_dir)
