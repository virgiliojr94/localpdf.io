FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de requisitos primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/
COPY static/ ./static/
COPY run.py .

# Criar diretórios necessários para uploads e outputs
RUN mkdir -p uploads outputs

# Expor porta
EXPOSE 5000

# Comando para executar a aplicação
CMD ["python", "run.py"]
