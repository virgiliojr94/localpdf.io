"""
Configurações da aplicação LocalPDF.io
"""


class Config:
    """Configurações da aplicação"""

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = "uploads"
    OUTPUT_FOLDER = "outputs"
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "xlsx", "jpg", "jpeg", "png"}
    
    # Configurações de conversão
    PDF_RESOLUTION_MULTIPLIER = 2
    PDF_COMPRESSION_LEVEL = 4
    
    # Configurações de texto para PDF
    TEXT_FONT = "Helvetica"
    TEXT_FONT_SIZE = 12
    TEXT_MARGIN = 50
    TEXT_LINE_SPACING = 15
    
    # Ghostscript PDF/A
    GS_PDFA_ARGS = [
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
    ]
