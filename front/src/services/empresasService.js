// services/empresasService.js

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

// Lista
export function getEmpresas() {
  return Promise.resolve(empresas);
}

// Busca por ID
export function getEmpresa(id) {
  const empresa = empresas.find((e) => e.id === Number(id));
  return Promise.resolve(empresa);
}

// Criar
export function createEmpresa(data) {
  const nova = { id: Date.now(), ...data };
  empresas.push(nova);
  return Promise.resolve(nova);
}

// Atualizar
export function updateEmpresa(id, data) {
  empresas = empresas.map((e) =>
    e.id === Number(id) ? { ...e, ...data } : e
  );
  return Promise.resolve(true);
}
