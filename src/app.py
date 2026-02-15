"""
LocalPDF.io - Aplicação web para manipulação de arquivos PDF
Author: Virgilio Borges

Flask application com rotas e endpoints
"""

import io
import logging
import os
import zipfile
from pathlib import Path
from typing import List, Union

from flask import Flask, Response, jsonify, request, send_file, send_from_directory

from .config import Config
from .utils import allowed_file, temporary_directory
from .converters import ConversionManager


# ========== CONFIGURAÇÃO DE LOGGING ==========

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ========== INICIALIZAÇÃO DA APLICAÇÃO ==========

def create_app():
    """Factory function para criar e configurar a aplicação Flask"""
    
    # Definir caminho para pasta static na raiz do projeto
    static_folder = Path(__file__).parent.parent / "static"
    
    app = Flask(__name__, static_folder=str(static_folder), static_url_path="")
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER
    app.config["OUTPUT_FOLDER"] = Config.OUTPUT_FOLDER
    
    # Criar diretórios necessários
    Path(app.config["UPLOAD_FOLDER"]).mkdir(exist_ok=True)
    Path(app.config["OUTPUT_FOLDER"]).mkdir(exist_ok=True)
    
    # Registrar rotas
    register_routes(app)
    register_error_handlers(app)
    
    return app


# ========== ROTAS ==========

def register_routes(app: Flask):
    """Registra todas as rotas da aplicação"""
    
    @app.route("/")
    def index() -> str:
        """Rota principal - serve página estática"""
        return send_from_directory(app.static_folder, "index.html")
    
    @app.route("/convert", methods=["POST"])
    def convert() -> Union[Response, tuple]:
        """
        Endpoint de conversão de arquivos
        
        Returns:
            Arquivo convertido ou mensagem de erro
        """
        # Validação de entrada
        if "files" not in request.files:
            logger.warning("Nenhum arquivo enviado")
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        files = request.files.getlist("files")
        tool = request.form.get("tool")
        
        if not files or files[0].filename == "":
            logger.warning("Nenhum arquivo selecionado")
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
        # Validação de extensões
        for file in files:
            if not allowed_file(file.filename):
                logger.warning(f"Extensão não permitida: {file.filename}")
                return jsonify({"error": f"Extensão não permitida: {file.filename}"}), 400
        
        # Processamento com diretório temporário
        try:
            with temporary_directory() as temp_dir:
                logger.info(f"Iniciando conversão: {tool} com {len(files)} arquivo(s)")
                output_files = ConversionManager.convert(tool, files, temp_dir)
                return build_response(output_files)
                
        except ValueError as e:
            logger.error(f"Ferramenta inválida: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Erro na conversão: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500


def build_response(output_files: List[str]) -> Response:
    """
    Constrói resposta HTTP com arquivo(s) convertido(s)
    
    Args:
        output_files: Lista de caminhos dos arquivos de saída
        
    Returns:
        Response do Flask com arquivo para download
    """
    if len(output_files) == 1:
        # Arquivo único
        file_path = output_files[0]
        filename = os.path.basename(file_path)
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        logger.info(f"Enviando arquivo: {filename}")
        return send_file(
            io.BytesIO(data),
            as_attachment=True,
            download_name=filename
        )
    else:
        # Múltiplos arquivos - criar ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in output_files:
                zipf.write(file_path, os.path.basename(file_path))
        
        zip_buffer.seek(0)
        logger.info(f"Enviando ZIP com {len(output_files)} arquivo(s)")
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="converted_files.zip",
            mimetype="application/zip"
        )


# ========== TRATAMENTO DE ERROS ==========

def register_error_handlers(app: Flask):
    """Registra handlers de erro da aplicação"""
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handler para arquivos muito grandes"""
        logger.warning("Arquivo muito grande enviado")
        return jsonify({"error": "Arquivo muito grande. Limite: 100MB"}), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handler para erros internos"""
        logger.error(f"Erro interno do servidor: {error}")
        return jsonify({"error": "Erro interno do servidor"}), 500


# ========== CRIAÇÃO DA APLICAÇÃO ==========

app = create_app()


if __name__ == "__main__":
    logger.info("Iniciando aplicação LocalPDF.io")
    app.run(host="0.0.0.0", port=5000, debug=False)
