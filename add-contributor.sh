#!/bin/bash

# Script para adicionar contribuidor manualmente
# Uso: ./add-contributor.sh <github-username> <tipo>
# Tipos: code, doc, design, bug, ideas, review, etc.

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Uso: ./add-contributor.sh <github-username> <tipo>"
    echo ""
    echo "Tipos disponíveis:"
    echo "  code      - Código"
    echo "  doc       - Documentação"
    echo "  design    - Design"
    echo "  bug       - Reportar bugs"
    echo "  ideas     - Ideias/Sugestões"
    echo "  review    - Revisar PRs"
    echo "  infra     - Infraestrutura"
    echo "  test      - Testes"
    echo ""
    echo "Exemplo: ./add-contributor.sh virgiliojr94 code,doc"
    exit 1
fi

USERNAME=$1
CONTRIBUTION=$2

echo "🎉 Adicionando $USERNAME como contribuidor..."

# Instalar all-contributors-cli se não estiver instalado
if ! command -v all-contributors &> /dev/null; then
    echo "📦 Instalando all-contributors-cli..."
    npm install -g all-contributors-cli
fi

# Adicionar contribuidor
all-contributors add "$USERNAME" "$CONTRIBUTION"

# Gerar a lista
all-contributors generate

echo "✅ Contribuidor adicionado! Não esqueça de commitar as mudanças."
echo ""
echo "git add ."
echo "git commit -m \"docs: add @$USERNAME as contributor\""
echo "git push"
