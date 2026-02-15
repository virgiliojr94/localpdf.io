"""
Conversor de arquivos PDF
"""

import logging
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
import ghostscript
from pdf2docx import Converter
from pdf2docx.converter import ConversionException
from PIL import Image
from werkzeug.datastructures import FileStorage

from ..config import Config
from ..utils import save_uploaded_file

logger = logging.getLogger(__name__)


class PDFConverter:
    """Classe base para operações de conversão de PDF"""
    
    @staticmethod
    def pdf_to_images(file: FileStorage, temp_dir: str) -> List[str]:
        """
        Converte páginas de PDF em imagens
        
        Args:
            file: Arquivo PDF
            temp_dir: Diretório temporário
            
        Returns:
            Lista de caminhos das imagens geradas
        """
        pdf_path = save_uploaded_file(file, temp_dir)
        output_files = []
        
        try:
            with fitz.open(str(pdf_path)) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(
                        matrix=fitz.Matrix(
                            Config.PDF_RESOLUTION_MULTIPLIER,
                            Config.PDF_RESOLUTION_MULTIPLIER
                        )
                    )
                    img_path = str(Path(temp_dir) / f"page_{page_num + 1}.png")
                    pix.save(img_path)
                    output_files.append(img_path)
                    logger.info(f"Página {page_num + 1} convertida para imagem")
        except Exception as e:
            logger.error(f"Erro ao converter PDF para imagens: {e}")
            raise RuntimeError(f"Erro ao converter PDF para imagens: {e}") from e
        
        return output_files
    
    @staticmethod
    def images_to_pdf(files: List[FileStorage], temp_dir: str) -> List[str]:
        """
        Combina imagens em um único PDF
        
        Args:
            files: Lista de arquivos de imagem
            temp_dir: Diretório temporário
            
        Returns:
            Lista com caminho do PDF gerado
        """
        images = []
        
        try:
            for file in files:
                img_path = save_uploaded_file(file, temp_dir)
                img = Image.open(str(img_path))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)
                logger.info(f"Imagem processada: {file.filename}")
            
            pdf_path = str(Path(temp_dir) / "images_to_pdf.pdf")
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            logger.info(f"PDF criado com {len(images)} imagens")
            
        except Exception as e:
            logger.error(f"Erro ao converter imagens para PDF: {e}")
            raise RuntimeError(f"Erro ao converter imagens para PDF: {e}") from e
        
        return [pdf_path]
    
    @staticmethod
    def merge_pdfs(files: List[FileStorage], temp_dir: str) -> List[str]:
        """
        Mescla múltiplos PDFs em um único arquivo
        
        Args:
            files: Lista de arquivos PDF
            temp_dir: Diretório temporário
            
        Returns:
            Lista com caminho do PDF mesclado
        """
        merged_doc = fitz.open()
        
        try:
            for file in files:
                pdf_path = save_uploaded_file(file, temp_dir)
                with fitz.open(str(pdf_path)) as doc:
                    merged_doc.insert_pdf(doc)
                    logger.info(f"PDF mesclado: {file.filename}")
            
            output_path = str(Path(temp_dir) / "merged.pdf")
            merged_doc.save(output_path)
            logger.info(f"PDFs mesclados com sucesso: {len(files)} arquivos")
            
        except Exception as e:
            logger.error(f"Erro ao mesclar PDFs: {e}")
            raise RuntimeError(f"Erro ao mesclar PDFs: {e}") from e
        finally:
            merged_doc.close()
        
        return [output_path]
    
    @staticmethod
    def split_pdf(file: FileStorage, temp_dir: str) -> List[str]:
        """
        Divide PDF em páginas separadas
        
        Args:
            file: Arquivo PDF
            temp_dir: Diretório temporário
            
        Returns:
            Lista de caminhos dos PDFs individuais
        """
        pdf_path = save_uploaded_file(file, temp_dir)
        output_files = []
        
        try:
            with fitz.open(str(pdf_path)) as doc:
                for page_num in range(len(doc)):
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    output_path = str(Path(temp_dir) / f"page_{page_num + 1}.pdf")
                    new_doc.save(output_path)
                    new_doc.close()
                    output_files.append(output_path)
                    logger.info(f"Página {page_num + 1} extraída")
        except Exception as e:
            logger.error(f"Erro ao dividir PDF: {e}")
            raise RuntimeError(f"Erro ao dividir PDF: {e}") from e
        
        return output_files
    
    @staticmethod
    def compress_pdf(file: FileStorage, temp_dir: str) -> List[str]:
        """
        Comprime arquivo PDF
        
        Args:
            file: Arquivo PDF
            temp_dir: Diretório temporário
            
        Returns:
            Lista com caminho do PDF comprimido
        """
        pdf_path = save_uploaded_file(file, temp_dir)
        output_path = str(Path(temp_dir) / "compressed.pdf")
        
        try:
            with fitz.open(str(pdf_path)) as doc:
                doc.save(
                    output_path,
                    garbage=Config.PDF_COMPRESSION_LEVEL,
                    deflate=True,
                    clean=True
                )
                logger.info("PDF comprimido com sucesso")
        except Exception as e:
            logger.error(f"Erro ao comprimir PDF: {e}")
            raise RuntimeError(f"Erro ao comprimir PDF: {e}") from e
        
        return [output_path]
    
    @staticmethod
    def pdf_to_pdfa(files: List[FileStorage], temp_dir: str) -> List[str]:
        """
        Converte PDFs para formato PDF/A-1b
        
        Args:
            files: Lista de arquivos PDF
            temp_dir: Diretório temporário
            
        Returns:
            Lista de caminhos dos PDFs convertidos
        """
        if not isinstance(files, list):
            files = [files]
        
        output_files = []
        
        for file in files:
            input_path = save_uploaded_file(file, temp_dir)
            base_name = input_path.stem
            output_path = str(Path(temp_dir) / f"{base_name}_pdfa.pdf")
            
            gs_args = Config.GS_PDFA_ARGS + [
                f"-sOutputFile={output_path}",
                str(input_path),
            ]
            gs_args = [
                arg.encode("utf-8") if isinstance(arg, str) else arg
                for arg in gs_args
            ]
            
            try:
                ghostscript.Ghostscript(*gs_args)
                output_files.append(output_path)
                logger.info(f"PDF/A criado: {file.filename}")
            except Exception as e:
                logger.error(f"Erro ao converter {file.filename} para PDF/A: {e}")
                raise RuntimeError(
                    f"Erro ao converter {file.filename} para PDF/A: {e}"
                ) from e
        
        return output_files
    
    @staticmethod
    def pdf_to_word(file: FileStorage, temp_dir: str) -> List[str]:
        """
        Converte PDF para Word (.docx)
        
        Args:
            file: Arquivo PDF
            temp_dir: Diretório temporário
            
        Returns:
            Lista com caminho do arquivo Word
        """
        pdf_path = save_uploaded_file(file, temp_dir)
        docx_filename = pdf_path.stem + ".docx"
        docx_path = str(Path(temp_dir) / docx_filename)
        
        cv = None
        try:
            cv = Converter(str(pdf_path))
            cv.convert(docx_path)
            logger.info(f"PDF convertido para Word: {file.filename}")
        except ValueError as e:
            logger.error(f"Erro no arquivo PDF: {e}")
            raise RuntimeError(f"Erro no arquivo PDF: {e}") from e
        except ConversionException as e:
            logger.error(f"Erro interno na conversão: {e}")
            raise RuntimeError(f"Erro interno na conversão: {e}") from e
        except Exception as e:
            logger.error(f"Erro ao converter para Word: {e}")
            raise RuntimeError(f"Erro ao converter {file.filename} para Word: {e}") from e
        finally:
            if cv:
                cv.close()
        
        return [docx_path]
