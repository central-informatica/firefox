// services/empresasService.js
// Lista
export function getEmpresas() {
  return Promise.resolve(empresas);
}

export async function getEmpresasDoUsuario(userId) {
  console.log("Id do usuário logado: ", userId);
  const res = await fetch(`http://127.0.0.1:8000/usuarios/${userId}/empresas`, {
    credentials: "include",
  });
  return await res.json();
}

export function getEmpresa(id) {
  const empresa = empresas.find((e) => e.id === Number(id));
  return Promise.resolve(empresa);
}

// Empresas paginado
export async function listarEmpresasPaginado({ page = 1, limit = 10, search = "", sort = "" }) {
  const params = new URLSearchParams();

  params.append("page", page);
  params.append("limit", limit);
  params.append("search", search);
  params.append("sort", sort);

  const res = await fetch(`http://127.0.0.1:8000/empresas?${params.toString()}`, {
    credentials: "include",
  });

  if (!res.ok) throw new Error("Erro ao carregar empresas");

  return await res.json(); // deve retornar { data: [...], total: X }
}

export function createEmpresa(data) {
  const nova = { id: Date.now(), ...data };
  empresas.push(nova);
  return Promise.resolve(nova);
}

export function updateEmpresa(id, data) {
  empresas = empresas.map((e) =>
    e.id === Number(id) ? { ...e, ...data } : e
  );
  return Promise.resolve(true);
}
