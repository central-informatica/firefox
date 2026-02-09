-- Criar banco de testes se não existir
SELECT 'CREATE DATABASE xsecurity_test' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'xsecurity_test')\gexec

-- Conectar ao banco principal e recriar schema
\c xsecur-orquestra
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
