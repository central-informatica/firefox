-- Migration: Alterar coluna ip_address para ip_addresses (JSONB)
-- Data: 2024-02-05
-- Descrição: Altera a estrutura da tabela regras_acesso_ips para armazenar
-- múltiplos IPs em formato JSONB ao invés de um único IP por regra.

-- 1. Adicionar nova coluna JSONB
ALTER TABLE regras_acesso_ips ADD COLUMN IF NOT EXISTS ip_addresses JSONB;

-- 2. Migrar dados existentes (wrapping o IP único em array)
UPDATE regras_acesso_ips
SET ip_addresses = jsonb_build_array(ip_address)
WHERE ip_address IS NOT NULL AND ip_addresses IS NULL;

-- 3. Remover a constraint única antiga (grupo_id + ip_address)
ALTER TABLE regras_acesso_ips DROP CONSTRAINT IF EXISTS regras_acesso_ips_grupo_ip_unq;

-- 4. Remover índice do ip_address
DROP INDEX IF EXISTS idx_regras_acesso_ips_ip;

-- 5. Tornar ip_addresses NOT NULL
ALTER TABLE regras_acesso_ips ALTER COLUMN ip_addresses SET NOT NULL;

-- 6. Remover coluna antiga
ALTER TABLE regras_acesso_ips DROP COLUMN IF EXISTS ip_address;

-- 7. Adicionar comentário na nova coluna
COMMENT ON COLUMN regras_acesso_ips.ip_addresses IS 'Lista de enderecos IP (IPv4, IPv6 ou blocos CIDR)';
