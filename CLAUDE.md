# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a digital certificate management backend built with FastAPI. It allows users to securely upload, store, and use .pfx certificates for digital signing operations. The system encrypts certificates using AES-GCM with a master key derived from PBKDF2.

## Architecture

### Core Security Flow

1. **Master Key Generation** (`chave_mestra.py`): Derives a 256-bit AES key from a password stored in `.env` using PBKDF2HMAC with SHA256 (480,000 iterations). The salt is persisted in `storage/salt.bin`.

2. **Certificate Encryption** (`crypto_utils.py`): Uses AES-GCM with the master key to encrypt both the .pfx file and its password. Each encryption generates a unique 12-byte nonce.

3. **Storage**: Encrypted certificates are stored in two places:
   - SQLite database (`storage/db/meu_banco.db`) with metadata
   - JSON files in `storage/certificados/` directory

### Database Schema (db_sqlite.py)

The `getDb()` function auto-creates three tables:
- `usuarios`: User accounts (id, nome, senha)
- `acesso`: Access tokens (id, id_usuario, token, ativo)
- `certificados`: Encrypted certificates (id, id_usuario, nome_arquivo, cert_id, encrypted, secret)

### API Endpoints (main.py)

**Authentication:**
- `POST /cadastro/usuario`: Register new user
- `POST /login`: Login and receive bearer token
- Token validation via `validar_token()` dependency

**Certificate Management:**
- `POST /upload/certificado`: Upload and encrypt .pfx file (requires auth)
- `GET /api/certificates`: List user's certificates with base64-encoded DER format
- `POST /api/sign`: Sign data using stored certificate (RSA-SHA256 with PKCS#1 v1.5)

**Note:** The `/api/certificates` endpoint has a hardcoded password `b"2705"` for loading PFX files (line 120), which should match the actual certificate passwords.

### Frontend

A separate Vite-based frontend exists in `/front` directory using pnpm for package management.

## Development Commands

### Backend

Run the development server:
```bash
fastapi dev main.py
```

Install dependencies:
```bash
poetry install
```

Run with production server:
```bash
fastapi run main.py
```

### Frontend

Navigate to frontend and install:
```bash
cd front
pnpm install
```

Run development server:
```bash
pnpm dev
```

## Environment Setup

Create a `.env` file in the root with:
```
MASTER_KEY=your-secure-master-password
```

The system expects:
- `certificados/private_key.pem`: RSA private key for signing operations
- `storage/salt.bin`: Auto-generated on first run
- `storage/db/`: SQLite database directory

## Key Technical Details

**Cryptography Stack:**
- Uses both `cryptography` and `pycryptodome` libraries
- Certificate handling: `cryptography.hazmat` for PKCS12
- Signing: `Crypto.Signature.pkcs1_15` with SHA256
- Encryption: AES-GCM from `cryptography.hazmat.primitives.ciphers.aead`

**Token Generation:**
Uses `secrets.token_urlsafe(32)` for cryptographically secure tokens (~43 characters).

**CORS Configuration:**
Currently allows only `http://localhost:5173` (Vite default port).

## Known Limitations

1. User ID is hardcoded to `1` in `/api/certificates` and `/api/sign` endpoints
2. Certificate password is hardcoded as `b"2705"` in line 120 of main.py
3. No password hashing for user accounts (passwords stored in plaintext)
4. No token expiration mechanism implemented
5. The `PRIVATE_KEY` loaded at startup (line 41-45) is loaded but never used in the codebase
