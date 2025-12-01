let usuarios = [
  {
    id: 1,
    nome: "Fabricio Peruzzolo",
    email: "fabricio@centrnet.com.br",
    telefone: "(69) 98422-6006",
    email_verificado: true,
    atualizado_em: "2025-11-28",
    nivel: 1
  },
  {
    id: 2,
    nome: "Rafaela da Silva",
    email: "rafa@provedor.com.br",
    telefone: "(69) 98422-3421",
    email_verificado: true,
    atualizado_em: "2025-11-29",
    nivel: 2
  },
];

export const getUsuarios = () => {
  return Promise.resolve(usuarios);
};

export const getUsuarioById = (id) => {
  return Promise.resolve(usuarios.find((u) => u.id === Number(id)));
};

export const createUsuario = (data) => {
  const novo = { id: Date.now(), ...data };
  usuarios.push(novo);
  return Promise.resolve(novo);
};

export const updateUsuario = (id, data) => {
  usuarios = usuarios.map((u) => (u.id === Number(id) ? { ...u, ...data } : u));
  return Promise.resolve();
};

export const deleteUsuario = (id) => {
  usuarios = usuarios.filter((u) => u.id !== Number(id));
  return Promise.resolve();
};