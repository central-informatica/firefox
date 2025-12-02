let certificados = [
  {
    id: 1,
    empresa_id: 1,
    criado_por: 1,
    criado_por_nome: "Fabricio Peruzzolo",
    nome_arquivo: "Certificado.pfx",
    criado_em: "2025-12-01 21:32",
  },
  {
    id: 2,
    empresa_id: 1,
    criado_por: 1,
    criado_por_nome: "Fabricio Peruzzolo",
    nome_arquivo: "Certificado 2.pfx",
    criado_em: "2025-12-01 21:33",
  },
];

// Lista
export function getCertificados() {
  return Promise.resolve(certificados);
}

// Busca por ID
export function getCertificado(id) {
  const certificado = certificados.find((e) => e.id === Number(id));
  return Promise.resolve(certificado);
}

// Criar
export function createCertificado(data) {
  const novo = { id: Date.now(), ...data };
  certificados.push(novo);
  return Promise.resolve(novo);
}

// Atualizar
/*export function updateCertificado(id, data) {
  certificados = certificados.map((e) =>
    e.id === Number(id) ? { ...e, ...data } : e
  );
  return Promise.resolve(true);
}*/
