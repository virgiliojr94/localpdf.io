# Contribuindo para o LocalPDF.io

Obrigado por considerar contribuir! 🎉

## Como Contribuir

### 1. Fork o Projeto

- Faça um fork do repositório
- Clone o fork para sua máquina

#### Configure o Ambiente

Para garantir a qualidade do código, utilizamos ferramentas como `ruff` e `pre-commit`.

1. **Crie um ambiente virtual (Recomendado)**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2. **Instale as dependências**

    ```bash
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```

3. **Instale os hooks do pre-commit**

    Isso garantirá que verificações automáticas rodem antes de cada commit.

    ```bash
    pre-commit install
    ```

### 2. Crie uma Branch

```bash
git checkout -b feature/minha-contribuicao
```

### 3. Faça suas Alterações

- Escreva código limpo e comentado
- Teste suas mudanças localmente
- Certifique-se de que tudo funciona

### 4. Commit suas Mudanças

```bash
git add .
git commit -m "Adiciona: descrição da sua contribuição"
```

Use mensagens de commit descritivas:

- `Adiciona: nova funcionalidade X`
- `Corrige: bug na conversão Y`
- `Melhora: performance da função Z`
- `Documenta: atualiza README`

### 5. Push para o GitHub

```bash
git push origin feature/minha-contribuicao
```

### 6. Abra um Pull Request

- Vá até o repositório original
- Clique em "New Pull Request"
- Descreva suas mudanças claramente

## O que Contribuir?

### 🐛 Bugs

Encontrou um bug? Abra uma issue descrevendo:

- O que você esperava que acontecesse
- O que aconteceu
- Passos para reproduzir
- Prints/logs se possível

### ✨ Novas Funcionalidades

Ideias de novas funcionalidades:

- Novos formatos de conversão
- Melhorias na interface
- Otimizações de performance
- Testes automatizados
- Internacionalização (i18n)

### 📚 Documentação

- Melhorar o README
- Adicionar exemplos de uso
- Corrigir typos
- Traduzir documentação

### 🎨 Design

- Melhorar a interface
- Adicionar tema escuro
- Tornar responsivo
- Melhorar UX

## Diretrizes de Código

- Mantenha o código Python seguindo PEP 8
- Comente código complexo
- Teste suas mudanças antes de enviar
- Mantenha a simplicidade

## 🎖️ Reconhecimento de Contribuidores

Usamos o [All Contributors Bot](https://allcontributors.org/) para reconhecer todas as contribuições!

### Como ser adicionado como contribuidor

Após sua contribuição ser aceita, você ou um mantenedor pode comentar:

```
@all-contributors please add @seu-username for code
```

**Tipos de contribuição reconhecidos:**

- `code` - Código
- `doc` - Documentação
- `design` - Design
- `bug` - Reportar bugs
- `ideas` - Ideias
- `review` - Revisar PRs
- E muitos mais! (veja [docs/BOT_USAGE.md](docs/BOT_USAGE.md))

O bot criará automaticamente um PR adicionando você à lista de contribuidores! ✨

## Dúvidas?

Entre em contato:

- Email: <virgilio.junior94@gmail.com>
- Abra uma issue no GitHub

---

**Toda contribuição é bem-vinda, não importa o tamanho!** ⭐
