// src/services/planosTrabalhoService.js
let planos = [
  { id: 1, nome: "Plano Suporte 24h", descricao: "Atendimento contínuo" },
  { id: 2, nome: "Plano Comercial", descricao: "Horário comercial" },
];

export function listarPlanosTrabalhoPaginado({
  page = 1,
  limit = 10,
  search = "",
  sort = "",
}) {
  let lista = [...planos];

  if (search && search.trim() !== "") {
    const termo = search.toLowerCase();
    lista = lista.filter(
      (p) =>
        p.nome.toLowerCase().includes(termo) ||
        (p.descricao || "").toLowerCase().includes(termo)
    );
  }

  if (sort) {
    const [campo, direcao] = sort.split(".");
    lista.sort((a, b) => {
      if (a[campo] < b[campo]) return direcao === "asc" ? -1 : 1;
      if (a[campo] > b[campo]) return direcao === "asc" ? 1 : -1;
      return 0;
    });
  }

  const total = lista.length;
  const inicio = (page - 1) * limit;
  const fim = inicio + limit;
  const paginados = lista.slice(inicio, fim);

  return Promise.resolve({ data: paginados, total });
}

export function getPlanoTrabalho(id) {
  const plano = planos.find((p) => p.id === Number(id));
  return Promise.resolve(plano);
}

export function createPlanoTrabalho(data) {
  const novo = { ...data, id: Date.now() };
  planos.push(novo);
  return Promise.resolve(novo);
}

export function updatePlanoTrabalho(id, data) {
  planos = planos.map((p) =>
    p.id === Number(id) ? { ...p, ...data } : p
  );
  return Promise.resolve(true);
}
