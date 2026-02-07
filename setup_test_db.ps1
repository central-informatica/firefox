# Script para configurar o banco de dados de testes
# Execute este script sempre que precisar recriar o banco de testes

Write-Host "Configurando banco de dados de testes..." -ForegroundColor Green

# Salvar DATABASE_URL atual
$originalDbUrl = $env:DATABASE_URL

# Configurar para banco de testes
$env:DATABASE_URL = "postgresql+psycopg2://postgres:seq098@192.168.10.36:5432/xsecurity_test"

Write-Host "Executando migrações no banco de testes..." -ForegroundColor Yellow
alembic upgrade head

# Restaurar DATABASE_URL original
$env:DATABASE_URL = $originalDbUrl

Write-Host "Banco de testes configurado com sucesso!" -ForegroundColor Green
Write-Host "Agora você pode rodar: poetry run pytest backend/tests/ -v" -ForegroundColor Cyan
