# Konecty CLI

Interface de linha de comando para utilitários do Konecty.

## 📑 Sumário

- [🚀 Comandos Principais](#-comandos-principais)
  - [⚙️ Gerenciamento de Configurações](#️-gerenciamento-de-configurações)
  - [🏗️ Gerenciamento de Projetos](#️-gerenciamento-de-projetos)
  - [🤖 Melhorias com IA](#-melhorias-com-ia)
  - [🛠️ Comandos de Desenvolvimento](#️-comandos-de-desenvolvimento)
- [🔧 Desenvolvimento](#-desenvolvimento)

### Usando uvx (Recomendado)

Você pode executar o CLI diretamente usando `uvx`:

```bash
uvx konecty-cli help
```

## 📋 Comandos Disponíveis

### 🚀 Comandos Principais

Comandos básicos para verificar informações do CLI e obter ajuda.

```bash
# Ver versão do CLI
uvx konecty-cli version

# Ver ajuda geral
uvx konecty-cli help
```

### ⚙️ Gerenciamento de Configurações

Gerencie suas configurações de conexão com Konecty, MongoDB e serviços de IA. As configurações são salvas no usuário e podem ser adcionadas a um arquivo de env.

```bash
# Listar todas as configurações
uvx konecty-cli config list

# Criar nova configuração
uvx konecty-cli config create

# Criar configuração com parâmetros
uvx konecty-cli config create --name "minha-config" --type "konecty"

# Editar configuração existente
uvx konecty-cli config edit

# Adicionar configuração ao ambiente
uvx konecty-cli config add-to-env
```

**Tipos de configuração disponíveis:**

- `konecty` - Configurações do Konecty (URL e Token)
- `mongo` - Configurações do MongoDB (URL)
- `ai` - Configurações de IA (OpenAI API Key)

### 🏗️ Gerenciamento de Projetos

Crie novos projetos rapidamente usando templates pré-configurados. Os templates incluem configurações básicas, estrutura de pastas e dependências iniciais para cada stack.

```bash
# Criar novo projeto
uvx konecty-cli project create

# Criar projeto com parâmetros
uvx konecty-cli project create --name "meu-projeto" --stack "Python"
```

**Stacks disponíveis:**

- `Python` - Projeto Python
- `Typescript` - Projeto TypeScript
- `React` - Projeto React

### 🤖 Melhorias com IA

Use inteligência artificial para melhorar seu código automaticamente. O sistema analisa seu código seguindo os padrões de estilo da empresa e sugere melhorias mantendo a funcionalidade original.

```bash
# Melhorar arquivo usando IA
uvx konecty-cli aimprove file

# Melhorar arquivo específico
uvx konecty-cli aimprove file --path "src/main.py"
```

## 🔧 Desenvolvimento

Este projeto usa Make para gerenciar scripts de desenvolvimento. Você pode listar os comandos disponíveis com `make help`

### Configurar Ambiente de Desenvolvimento

Instale as dependências de desenvolvimento:

```bash
make install-dev
```

### Rodar o projeto localmente

```bash
uv run konecty-cli ...
```

### Executar Testes

```bash
# Executar todos os testes
make test

# Executar testes com cobertura
make test-cov
```

### Qualidade do Código

```bash
# Executar todas as verificações de qualidade (formatar, lint, type-check, test)
make check

# Ou execute verificações individuais:
make format    # Formatar código com black e isort
make lint      # Executar linter flake8
make type-check # Executar verificador de tipos mypy
```

#### Build e Publicação

É necessário aumentar o número da versão no arquivo [pyproject](./pyproject.toml).

> [Um arquivo pypirc é necessário](https://packaging.python.org/en/latest/specifications/pypirc/#using-a-pypi-token)

```sh
make build
make publish
```
