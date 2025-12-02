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
export function createCertificado(formData) {
  // Converte FormData em objeto normal
  const data = Object.fromEntries(formData.entries());

  const novo = {
    id: Date.now(),
    empresa_id: 1, // mock — ajuste se quiser
    criado_por: 1,
    criado_por_nome: "Fabricio Peruzzolo",
    nome_arquivo: data.nome_arquivo instanceof File ? data.nome_arquivo.name : data.nome_arquivo,
    senha: data.senha || null,
    criado_em: new Date().toISOString().slice(0, 19).replace("T", " "),
  };

  certificados.push(novo);

  console.log("📄 Novo certificado salvo (mock):", novo);

  return Promise.resolve(novo);
}

// Atualizar
export function updateCertificado(id, data) {
  certificados = certificados.map((e) =>
    e.id === Number(id) ? { ...e, ...data } : e
  );
  return Promise.resolve(true);
}
