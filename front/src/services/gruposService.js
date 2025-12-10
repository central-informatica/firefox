// Mock data para grupos e suas associações
let grupos = [
  {
    id: 1,
    plano_id: 1,
    nome: "Equipe Técnica",
    empresa_id: 1,
    criado_em: "2025-11-01",
  },
  {
    id: 2,
    plano_id: 1,
    nome: "Equipe Comercial",
    empresa_id: 1,
    criado_em: "2025-11-02",
  },
  {
    id: 3,
    plano_id: 2,
    nome: "Vendedores",
    empresa_id: 1,
    criado_em: "2025-11-03",
  },
];

// Associações grupo-usuário
let gruposUsuarios = [
  { grupo_id: 1, usuario_id: 1 },
  { grupo_id: 1, usuario_id: 2 },
  { grupo_id: 2, usuario_id: 2 },
];

// Associações grupo-certificado
let gruposCertificados = [
  { grupo_id: 1, certificado_id: 1 },
  { grupo_id: 2, certificado_id: 2 },
];

// Listar grupos por plano
export function getGruposByPlano(plano_id) {
  const filtrados = grupos.filter((g) => g.plano_id === Number(plano_id));
  return Promise.resolve(filtrados);
}

// Listar todos os grupos
export function getGrupos() {
  return Promise.resolve(grupos);
}

// Obter grupo por ID
export function getGrupoById(id) {
  const grupo = grupos.find((g) => g.id === Number(id));
  return Promise.resolve(grupo);
}

// Criar grupo
export function createGrupo(data) {
  const novo = { ...data, id: Date.now() };
  grupos.push(novo);
  return Promise.resolve(novo);
}

// Atualizar grupo
export function updateGrupo(id, data) {
  grupos = grupos.map((g) => (g.id === Number(id) ? { ...g, ...data } : g));
  return Promise.resolve(true);
}

// ========== Associações de Usuários ==========

// Listar usuários de um grupo
export function getUsuariosByGrupo(grupo_id) {
  const associacoes = gruposUsuarios.filter(
    (gu) => gu.grupo_id === Number(grupo_id)
  );
  return Promise.resolve(associacoes.map((a) => a.usuario_id));
}

// Adicionar usuário ao grupo
export function addUsuarioToGrupo(grupo_id, usuario_id) {
  const existe = gruposUsuarios.find(
    (gu) => gu.grupo_id === Number(grupo_id) && gu.usuario_id === Number(usuario_id)
  );
  if (!existe) {
    gruposUsuarios.push({
      grupo_id: Number(grupo_id),
      usuario_id: Number(usuario_id),
    });
  }
  return Promise.resolve(true);
}

// Remover usuário do grupo
export function removeUsuarioFromGrupo(grupo_id, usuario_id) {
  gruposUsuarios = gruposUsuarios.filter(
    (gu) =>
      !(gu.grupo_id === Number(grupo_id) && gu.usuario_id === Number(usuario_id))
  );
  return Promise.resolve(true);
}

// ========== Associações de Certificados ==========

// Listar certificados de um grupo
export function getCertificadosByGrupo(grupo_id) {
  const associacoes = gruposCertificados.filter(
    (gc) => gc.grupo_id === Number(grupo_id)
  );
  return Promise.resolve(associacoes.map((a) => a.certificado_id));
}

// Adicionar certificado ao grupo
export function addCertificadoToGrupo(grupo_id, certificado_id) {
  const existe = gruposCertificados.find(
    (gc) =>
      gc.grupo_id === Number(grupo_id) &&
      gc.certificado_id === Number(certificado_id)
  );
  if (!existe) {
    gruposCertificados.push({
      grupo_id: Number(grupo_id),
      certificado_id: Number(certificado_id),
    });
  }
  return Promise.resolve(true);
}

// Remover certificado do grupo
export function removeCertificadoFromGrupo(grupo_id, certificado_id) {
  gruposCertificados = gruposCertificados.filter(
    (gc) =>
      !(
        gc.grupo_id === Number(grupo_id) &&
        gc.certificado_id === Number(certificado_id)
      )
  );
  return Promise.resolve(true);
}
