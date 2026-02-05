// gruposService.js (SEM MOCK)
// Mantém os mesmos exports do arquivo antigo, mas agora chamando a API real.

import { apiFetchWithToken } from "../api/api"; // ajuste o path se no seu projeto estiver diferente

function qs(params = {}) {
  const clean = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ""
    )
  );
  const query = new URLSearchParams(clean).toString();
  return query ? `?${query}` : "";
}


async function parseJsonSafe(res) {
  const text = await res.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return text; // pode vir text/plain em erro
  }
}

async function ensureOk(res) {
  if (res.ok) return res;
  const data = await parseJsonSafe(res);
  const msg =
    (data && data.detail && (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail))) ||
    (typeof data === "string" ? data : "Erro na requisição");
  throw new Error(`${res.status} ${res.statusText} - ${msg}`);
}

// ===============================
// LISTAS / CRUD
// ===============================

// Listar grupos por plano (mantém o mesmo nome do mock)
export async function listarGruposPorPlano(plano_id, params = {}) {
  // A API pode suportar filtro por plano_id
  // Ex.: GET /grupos/?plano_id=1&page=1&limit=10&search=&sort=
  const res = await apiFetchWithToken(`/grupos/${qs({ plano_id, ...params })}`, {
    method: "GET",
  });
  await ensureOk(res);
  return await res.json();
}

// Listar todos os grupos (mantém o mesmo nome do mock)
export async function getGrupos(params = {}) {
  const { empresa_id, plano_id, ...queryParams } = params;

  if (!empresa_id) {
    throw new Error("empresa_id é obrigatório para listar grupos");
  }

  const query = qs({
    ...queryParams,
    plano_id, // ✅ agora entra na query
  });

  const url = `/grupos/empresa/${empresa_id}${query}`;

  const res = await apiFetchWithToken(url);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  const data = await res.json();

  return {
    data: Array.isArray(data) ? data : [],
    total: data.length,
  };
}



// Obter grupo por ID
export async function getGrupoById(id) {
  const res = await apiFetchWithToken(`/grupos/${id}`, {
    method: "GET",
  });
  await ensureOk(res);
  return await res.json();
}

// Criar grupo
export async function criarGrupo(data) {
  const res = await apiFetchWithToken(`/grupos/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
  await ensureOk(res);
  return await res.json();
}

// Atualizar grupo
export async function atualizarGrupo(id, data) {
  const res = await apiFetchWithToken(`/grupos/${id}`, {
    method: "PUT",
    body: JSON.stringify({
        data: data,
        empresa_id: empresaId,
      }),
  });
  //await ensureOk(res);
  return await res.json();
}

// Deletar grupo
export async function deletarGrupo(id) {
  const res = await apiFetchWithToken(`/grupos/${id}`, {
    method: "DELETE",
  });
  await ensureOk(res);
  return await parseJsonSafe(res);
}

// ===============================
// ASSOCIAÇÕES (Usuários)
// ===============================

// Listar usuários de um grupo
export async function getUsuariosByGrupo(grupo_id) {
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/usuarios`, {
    method: "GET",
  });
  await ensureOk(res);
  return await res.json();
}

// Adicionar usuário ao grupo
export async function addUsuarioToGrupo(grupo_id, usuario_id) {
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/usuarios`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ usuario_id }),
  });
  await ensureOk(res);
  return await parseJsonSafe(res);
}

// Remover usuário do grupo
export async function removeUsuarioFromGrupo(grupo_id, usuario_id) {
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/usuarios/${usuario_id}`, {
    method: "DELETE",
  });
  await ensureOk(res);
  return await parseJsonSafe(res);
}

// Adicionar múltiplos usuários ao grupo (bulk)
export async function addUsuariosToGrupoBulk(grupo_id, usuario_ids, empresa_id = null) {
  const payload = { grupo_id, usuario_ids };
  if (empresa_id) payload.empresa_id = empresa_id;
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/usuarios/bulk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await ensureOk(res);
  return await res.json();
}

/**
 * Lista os grupos de uma empresa específica
 * (tenant-safe: backend valida se o usuário pertence à empresa)
 */
export async function listarGruposPorEmpresa(empresaId, planoTrabalhoId = null) {
  if (!empresaId) return [];

  console.log("listarGruposPorEmpresa chamado com empresaId:", empresaId, "planoTrabalhoId:", planoTrabalhoId);

  const params = new URLSearchParams();
  if (planoTrabalhoId) {
    params.append("plano_trabalho_id", String(planoTrabalhoId));
  }

  const query = params.toString();
  const url = query
    ? `/grupos/empresa/${empresaId}?${query}`
    : `/grupos/empresa/${empresaId}`;

  const res = await apiFetchWithToken(url);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  const json = await res.json();
  return Array.isArray(json) ? json : [];
}

// ===============================
// ASSOCIAÇÕES (Certificados)
// ===============================

// Listar certificados de um grupo
export async function getCertificadosByGrupo(grupo_id) {
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/certificados`, {
    method: "GET",
  });
  await ensureOk(res);
  return await res.json();
}

// Adicionar certificado ao grupo
export async function addCertificadoToGrupo(grupo_id, certificado_id) {
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/certificados`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ certificado_id }),
  });
  await ensureOk(res);
  return await parseJsonSafe(res);
}

// Listar associações grupos<->usuarios por empresa
export async function listarGruposUsuariosPorEmpresa(empresaId) {
  if (!empresaId) return [];
  const res = await apiFetchWithToken(`/grupos-usuarios/empresa/${empresaId}`);
  await ensureOk(res);
  return await res.json();
}

// Remover certificado do grupo
export async function removeCertificadoFromGrupo(grupo_id, certificado_id) {
  const res = await apiFetchWithToken(`/grupos/${grupo_id}/certificados/${certificado_id}`, {
    method: "DELETE",
  });
  await ensureOk(res);
  return await parseJsonSafe(res);
}

// Remover usuário do grupo por grupo_usuario_id
export async function removerUsuarioDoGrupo(grupo_usuario_id) {
  const res = await apiFetchWithToken(`/grupos-usuarios/${grupo_usuario_id}`, {
    method: "DELETE",
  });
  await ensureOk(res);
  return await parseJsonSafe(res);
}

