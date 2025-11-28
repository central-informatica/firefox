# Backend Certificado

Sistema de gerenciamento seguro de certificados digitais (.pfx) com API REST construída em FastAPI.

## Visão Geral

Este projeto permite que usuários façam upload, armazenem de forma criptografada e utilizem certificados digitais .pfx para operações de assinatura digital. O sistema garante segurança através de criptografia AES-GCM com chave mestra derivada por PBKDF2.

### Funcionalidades Principais

- **Autenticação de usuários** com sistema de tokens Bearer
- **Upload seguro de certificados .pfx** com criptografia automática
- **Armazenamento criptografado** de certificados e senhas
- **Listagem de certificados** do usuário autenticado
- **Assinatura digital** usando certificados armazenados (RSA-SHA256)
- **Frontend integrado** em React/Vite

### Arquitetura de Segurança

1. **Chave Mestra**: Derivada de senha através de PBKDF2HMAC (SHA256, 480.000 iterações)
2. **Criptografia**: AES-GCM de 256 bits para certificados e senhas
3. **Tokens de Acesso**: Gerados com `secrets.token_urlsafe` para autenticação segura
4. **Armazenamento**: SQLite com dados criptografados + arquivos JSON

## Pré-requisitos

- Python 3.11 ou superior
- Poetry (gerenciador de dependências Python)
- Node.js e pnpm (para o frontend)

## Instalação

### Backend

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd backend_certificado
```

2. **Instale as dependências com Poetry**
#### Instalação do poetry Linux
curl -sSL https://install.python-poetry.org | python3 -

#### Instalação do peoetry Windows
curl -sSL https://install.python-poetry.org | python -

```bash
poetry install
```

3. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```env
MASTER_KEY=sua-senha-mestra-segura
```

4. **Crie os diretórios necessários**

Os diretórios serão criados automaticamente na primeira execução, mas você pode criá-los manualmente:
```bash
mkdir -p storage/db
mkdir -p storage/certificados
mkdir -p certificados
```

5. **Adicione sua chave privada RSA** (se necessário para assinatura)
```bash
# Coloque seu arquivo private_key.pem em:
# certificados/private_key.pem
```

### Frontend

1. **Navegue até o diretório do frontend**
```bash
cd front
```

2. **Instale as dependências**
#### Instalação pnpm  windows
```bash
Invoke-WebRequest https://get.pnpm.io/install.ps1 -UseBasicParsing | Invoke-Expression
```
```bash
pnpm install
```

## Como Executar

### Executar o Backend

**Modo Desenvolvimento:**
```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O servidor estará disponível em: `http://127.0.0.1:8000`

**Modo Produção:**
```bash
poetry run fastapi run main.py
```

**Documentação Automática da API:**
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Executar o Frontend
#### Instalação do do node https://nodejs.org/
```bash
cd front
pnpm dev
```

O frontend estará disponível em: `http://127.0.0.1:5173`

## Estrutura do Projeto

```
backend-certificado/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── certificados.py
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       └── certificados.py
│   │   ├── utils/ (OPCIONAL)
│   ├── __init__.py
│
├── db_sqlite.py           ⟵ pode ficar na raiz ou mover p/ backend/
├── crypto_utils.py
├── chave_mestra.py
├── gerar_token_acesso.py
│
├── storage/
├── front/                 ⟵ seu frontend
├── .env
├── pyproject.toml
└── README.md

backend_certificado/
├── main.py                  # API FastAPI e endpoints
├── chave_mestra.py         # Geração de chave mestra com PBKDF2
├── crypto_utils.py         # Funções de criptografia AES-GCM
├── db_sqlite.py            # Configuração do banco SQLite
├── gerar_token_acesso.py   # Geração de tokens seguros
├── pyproject.toml          # Configuração Poetry e dependências
├── .env                    # Variáveis de ambiente (não versionado)
├── storage/
│   ├── salt.bin           # Salt para derivação de chave
│   ├── db/                # Banco de dados SQLite
│   └── certificados/      # Certificados criptografados (JSON)
├── certificados/
│   └── private_key.pem    # Chave privada RSA
└── front/                 # Frontend React/Vite
    ├── package.json
    ├── pnpm-lock.yaml
    └── src/
```

## Endpoints da API

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/cadastro/usuario` | Cadastrar novo usuário |
| POST | `/login` | Login e obtenção de token |

### Certificados (Requer Autenticação)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/upload/certificado` | Upload de arquivo .pfx |
| GET | `/api/certificates` | Listar certificados do usuário |
| POST | `/api/sign` | Assinar dados com certificado |

### Outros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Health check |

## Exemplo de Uso

### 1. Cadastrar Usuário
```bash
curl -X POST "http://127.0.0.1:8000/cadastro/usuario" \
  -F "nome=joao" \
  -F "senha=senha123"
```

### 2. Fazer Login
```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -F "nome=joao" \
  -F "senha=senha123"
```

Resposta:
```json
{
  "status": "ok",
  "message": "usuario cadastrado",
  "usuario": 1,
  "token": "SEU_TOKEN_AQUI"
}
```

### 3. Upload de Certificado
```bash
curl -X POST "http://127.0.0.1:8000/upload/certificado" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "arquivo=@certificado.pfx" \
  -F "senha=senha_do_certificado"
```

### 4. Listar Certificados
```bash
curl -X GET "http://127.0.0.1:8000/api/certificates"
```

### 5. Assinar Dados
```bash
curl -X POST "http://127.0.0.1:8000/api/sign" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "BASE64_DO_DIGEST",
    "cert_id": "ID_DO_CERTIFICADO",
    "algorithm": "SHA256"
  }'
```

## Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLite**: Banco de dados leve
- **Cryptography**: Biblioteca de criptografia (PKCS12, AES-GCM)
- **PyCryptodome**: Assinatura digital RSA
- **Poetry**: Gerenciamento de dependências
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

### Frontend
- **React**: Biblioteca para UI
- **Vite**: Build tool e dev server
- **pnpm**: Gerenciador de pacotes rápido

## Segurança

⚠️ **Notas Importantes:**

1. **Nunca compartilhe** seu arquivo `.env` ou a `MASTER_KEY`
2. **Mantenha seguro** o arquivo `storage/salt.bin` (necessário para descriptografia)
3. **Use HTTPS** em produção para proteger tokens e dados em trânsito
4. **Faça backup** dos certificados criptografados e do salt
5. **Senha forte**: Use uma senha mestra forte e única para `MASTER_KEY`

## Desenvolvimento

### Adicionar Novas Dependências

```bash
# Backend
poetry add nome-do-pacote

# Frontend
cd front
pnpm add nome-do-pacote
```

### Verificar Dependências

```bash
# Backend
poetry show

# Frontend
cd front
pnpm list
```

