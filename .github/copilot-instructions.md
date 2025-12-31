# Copilot / AI Agent Instructions for xsecurity-vault

Purpose: give an AI coding agent the essential, actionable context to be productive quickly.

1) Quick start (dev)
- Backend (poetry + uvicorn):
  - `poetry install`
  - `poetry run uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`
- Frontend (Vite):
  - `cd front && npm install`
  - `npm run dev -- --host 127.0.0.1`
- Full stack (docker): `docker-compose up` (postgres, backend runs `alembic upgrade head` then uvicorn)

2) Big picture
- Backend: FastAPI app at `backend/app` (routes under `api/routes`, core logic in `core/`, DB models in `db/`).
- Frontend: React + Vite inside `front/` (API fetches use `credentials: 'include'` + `X-CSRF-Token`).
- Storage: encrypted certificates and salt under `storage/`.
- DB: Postgres preferred (docker-compose); tests use a `DATABASE_URL` in `.env.test`.

3) Security & crypto (critical)
- Master key derivation: `backend/app/utils/chave_mestra.py` (PBKDF2HMAC SHA256, 480000 iterations). Salt file: `storage/salt.bin` (created on first run).
- Envelope encryption for PFX: `backend/app/utils/crypto_utils.py` uses AES-GCM (nonce + ciphertext). Functions: `encrypt_pfx()` and `decrypt_pfx()`.
- Certificates are stored in DB (`Certificados.encrypted`, `Certificados.secret`) as JSONified AES-GCM `{nonce, ciphertext}`.

4) Authentication patterns (important integration points)
- Web flows use HttpOnly cookie `session_token` + JS-accessible cookie `csrf_token`.
- Web clients must send `credentials: 'include'` and header `X-CSRF-Token` with every protected request (see `front/src/api/api.js`).
- Tokens are opaque: format `selector.validator` (see `backend/app/core/token_security.py`). The validator is Argon2-hashed in DB (`access_tokens.validator_hash`). Use `verify_validator()` to check.
- Use the dependency utilities: `validar_token`, `validar_token_universal`, or `validar_token_desktop` (see `backend/app/core/validar_token.py`).

5) Certificate flows (examples)
- Upload: `POST /certificados/` — server extracts certificate info via `cryptography.pkcs12`, encrypts with `encrypt_pfx()` and writes to `Certificados` (see `backend/app/api/routes/certificados.py`).
- List for signing: `GET /certificados/api/certificates` — returns cert DER base64 for UI.
- Sign: `POST /certificados/api/sign` — payload `{data: <base64 digest>, cert_id: <id>, algorithm: 'SHA256'}` returns `{signature_b64}`.

6) Tests & local CI
- Tests live in `backend/tests/` and use `pytest` and FastAPI `TestClient`.
- Create `.env.test` with at least: `DATABASE_URL=sqlite:///./tests.db` (or a Postgres test DB). Run: `poetry run pytest -q`.
- Tests rely on `storage/salt.bin` + `MASTER_KEY` derivation; ensure `MASTER_KEY` present in test environment or generated appropriately.

7) Migrations & DB
- Alembic configs are under `backend/migrations/` and `env.py` reads `DATABASE_URL` from config.
- To run migrations locally: from project root: `alembic -c backend/migrations/alembic.ini upgrade head` or use docker-compose (backend service runs `alembic upgrade head` on start).

8) Project conventions & hotspots (where to look first)
- Routes: `backend/app/api/routes/` (auth, certificados, ...)
- Core auth + CSRF: `backend/app/core/` (see `csrf.py`, `security.py`, `token_security.py`, `validar_token.py`)
- Data layer: `backend/app/db/models.py`, `backend/app/db/session.py`
- Crypto: `backend/app/utils/chave_mestra.py`, `backend/app/utils/crypto_utils.py`
- Tests: `backend/tests/` (use as contract for behavior and examples)

9) Safety & non-goals
- Do NOT expose `MASTER_KEY` or `storage/salt.bin` values in code or test fixtures; treat them as secrets.
- Avoid introducing changes that weaken Argon2 or PBKDF2 configurations without a security review.

10) Helpful searches for patches
- `encrypt_pfx` / `decrypt_pfx` (crypto changes)
- `generate_opaque_token`, `verify_validator` (auth/token logic)
- `session_token`, `csrf_token`, `X-CSRF-Token` (request authorization patterns)
- `Certificados` model and `api/routes/certificados.py` (certificate lifecycle)

If anything important is missing or you want a different level of detail (e.g., example request bodies, code snippets for common tasks), tell me which section to expand and I'll update this file. ✅