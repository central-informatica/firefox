
let empresas = [
  {
    id: 1,
    nome: "TechMaster",
    cnpj: "12.345.678/0001-90",
    timezone: "America/Recife",
  },
  {
    id: 2,
    nome: "FarmaCorp",
    cnpj: "98.765.432/0001-00",
    timezone: "America/Sao_Paulo",
  },
];

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

export function listarEmpresasPaginado({
  page = 1,
  limit = 10,
  search = "",
  sort = "",
}) {
  console.log("🔍 listarEmpresasPaginado()", { page, limit, search, sort });

  let lista = [...empresas];

  if (search && search.trim() !== "") {
    const termo = search.toLowerCase();
    lista = lista.filter(
      (e) =>
        e.nome.toLowerCase().includes(termo) ||
        e.cnpj.toLowerCase().includes(termo)
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
  const paginadas = lista.slice(inicio, fim);

  return Promise.resolve({
    data: paginadas,
    total,
  });
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
