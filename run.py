"""
LocalPDF.io - Script de entrada
Inicia a aplicação Flask
"""

from src.app import app, logger

if __name__ == "__main__":
    logger.info("Iniciando LocalPDF.io via run.py")
    app.run(host="0.0.0.0", port=5000, debug=False)
