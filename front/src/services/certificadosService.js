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

/* ============================================
   LISTAGEM PAGINADA (SERVER-SIDE MOCK)
============================================ */
export function listarCertificadosPaginado({
  empresa_id,
  page = 1,
  limit = 10,
  search = "",
  sort = "",
}) {
  console.log("🔍 listarCertificadosPaginado()", {
    empresa_id,
    page,
    limit,
    search,
    sort,
  });

  // 1) Filtrar por empresa
  let lista = certificados.filter(
    (c) => Number(c.empresa_id) === Number(empresa_id)
  );

  // 2) Aplicar busca global
  if (search && search.trim() !== "") {
    const termo = search.toLowerCase();
    lista = lista.filter(
      (c) =>
        c.nome_arquivo.toLowerCase().includes(termo) ||
        c.criado_por_nome.toLowerCase().includes(termo)
    );
  }

  // 3) Ordenação (ex: "nome_arquivo.asc" ou "criado_em.desc")
  if (sort) {
    const [campo, direcao] = sort.split(".");
    lista.sort((a, b) => {
      if (a[campo] < b[campo]) return direcao === "asc" ? -1 : 1;
      if (a[campo] > b[campo]) return direcao === "asc" ? 1 : -1;
      return 0;
    });
  }

  // 4) Total antes da paginação
  const total = lista.length;

  // 5) Paginação server-side
  const inicio = (page - 1) * limit;
  const fim = inicio + limit;
  const paginados = lista.slice(inicio, fim);

  // 6) Resposta padrão de APIs reais
  return Promise.resolve({
    data: paginados,
    total,
  });
}

/* ============================================
   OUTROS MÉTODOS (SEM PAGINAÇÃO)
============================================ */

// Lista completa (não será usado mais na lista)
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
  const data = Object.fromEntries(formData.entries());

  const novo = {
    id: Date.now(),
    empresa_id: 1, // mock
    criado_por: 1,
    criado_por_nome: "Fabricio Peruzzolo",
    nome_arquivo:
      data.nome_arquivo instanceof File
        ? data.nome_arquivo.name
        : data.nome_arquivo,
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
