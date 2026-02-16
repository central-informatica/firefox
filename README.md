# 📄 Certificado Protegido

Sistema para armazenamento seguro de certificados digitais (.pfx), autenticação via cookies HttpOnly, CSRF, assinatura remota e processamento seguro no backend FastAPI.

Este projeto possui dois módulos principais:

- **Backend** — FastAPI + Python 3.13 + Poetry 2.x  
- **Frontend** — React + Vite

---
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

### Backend
- Python **3.13** instalado
- Poetry **2.x** instalado  
  https://python-poetry.org/docs/#installation

### Frontend
- Node.js **18+**
- NPM ou Yarn

---

# 🏗 Estrutura do Projeto

```
backend-certificado/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   └── routes/
│       │       ├── auth.py
│       │       └── certificados.py
│       ├── core/
│       │   ├── config.py
│       │   └── security.py
│       ├── schemas/
│       └── utils/
│
├── front/
│   └── (arquivos do React + Vite)
│
├── storage/
│   └── certificados/  (arquivos .pfx criptografados)
│
├── pyproject.toml
├── README.md
└── .env
```

---

# ⚙️ Configuração do Backend (FastAPI)

O backend usa:

- Cookies HttpOnly (`session_token`)
- Token CSRF (`csrf_token`)
- Autenticação baseada em sessão (não usa localStorage)
- Criptografia forte com `pycryptodome` + `cryptography`
- Banco de dados SQLite

---

# 🔐 Arquivo `.env`

Crie na raiz do projeto:

```
MASTER_KEY=123
FRONTEND_ORIGIN=http://127.0.0.1:5173
```

---

# ▶ Como rodar o Backend

## ✔ 1) Instalar dependências:

#### Instalação do poetry Linux
curl -sSL https://install.python-poetry.org | python3 -

#### Instalação do peoetry Windows
curl -sSL https://install.python-poetry.org | python -
```
poetry install
```

## ✔ 2) Ver o caminho da virtualenv:

```
poetry env info --path
```

## ✔ 3) Ativar a venv manualmente (Windows PowerShell) 
<CAMINHO_DA_VENV> :: É o resultado do comando: poetry env info --path
```
& "<CAMINHO_DA_VENV>\Scripts\Activate.ps1"
```

## ✔ 4) Rodar o servidor FastAPI

```
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

API disponível em:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

---

# ▶ Como rodar o Frontend (React + Vite)

Entre na pasta:

```
cd front
npm install
npm run dev -- --host 127.0.0.1
```

Aplicação em:

**http://127.0.0.1:5173**

---

# 🔐 Fluxo de Autenticação

1. O backend cria cookies:
   - HttpOnly: `session_token`
   - Acessível ao JS: `csrf_token`
2. O frontend deve enviar sempre:
   ```
   credentials: "include"
   X-CSRF-Token: csrf_token
   ```
3. Rotas protegidas dependem de:
   ```
   validar_token
   ```

Exemplo:

```js
fetch("http://127.0.0.1:8000/upload/certificado", {
  method: "POST",
  credentials: "include",
  headers: {
    "X-CSRF-Token": csrf,
  },
  body: formData
});
```

---

# 📁 Upload de Certificados (.pfx)

```
POST /upload/certificado
```

Envia:

- arquivo (.pfx)
- senha
- cookie de sessão
- header CSRF

---

# ✍ Assinatura Digital

```
POST /api/sign
```

Retorna assinatura RSA base64 da hash enviada.
---

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

# 🛠 Desenvolvimento

Backend:

```
uvicorn backend.app.main:app --reload
```

Frontend:

```
npm run dev
```

---

# 🚀 Deploy

- Backend com Uvicorn + Nginx
- Frontend build com Vite
- HTTPS obrigatório (SameSite=None)

---

# 👨‍💻 Contribuição

Mantenha o padrão:

- Rotas → `backend/app/api/routes`
- Segurança → `backend/app/core`
- Utilitários → `backend/app/utils`
- Schemas → `backend/app/schemas`

---

# 📄 Licença

Uso interno.
