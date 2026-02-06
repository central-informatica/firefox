import {apiFetchWithToken} from "../api/api";

export async function listarUsuariosPaginado({
  empresa_id,
  page = 1,
  limit = 10,
  search = "",
  sort = "",
}) {
  const params = new URLSearchParams({
    page,
    limit,
    search,
    sort,
  });

  const res = await apiFetchWithToken(
    `/usuarios/empresas/${empresa_id}/usuarios?${params.toString()}`
  );

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json(); // { data, total }
}

export async function listarTodosUsuarios({
  limit = 100,
  offset = 0,
}) {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  const res = await apiFetchWithToken(`/usuarios/?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json(); // { users, total }
}

export async function getUsuarioById(id){
   const res = await apiFetchWithToken(`/usuarios/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
};

export async function createUsuario(usuario){
  const res = await apiFetchWithToken(`/usuarios/`, {
    method: "POST",
    body: JSON.stringify(usuario),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
};

export async function updateUsuario(empresaId, id, usuario) {
  const params = new URLSearchParams();
  if (empresaId) params.set("empresa_id", empresaId);

  const res = await apiFetchWithToken(`/usuarios/${id}?${params.toString()}`, {
    method: "PUT",
    body: JSON.stringify(usuario),
  });

  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function deletarUsuario(empresaId, usuarioId) {
  const params = new URLSearchParams();
  if (empresaId) params.set("empresa_id", empresaId);

  const res = await apiFetchWithToken(
    `/usuarios/${usuarioId}?${params.toString()}`,
    { method: "DELETE" }
  );

  if (!res.ok) throw new Error(await res.text());
  return true;
}

/**
 * TOGGLE user active status (organization-level)
 */
export async function toggleUsuarioAtivo(userId) {
  const res = await apiFetchWithToken(`/usuarios/${userId}/toggle-active`, {
    method: "PATCH",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

/**
 * Get all grupos for a specific user
 */
export async function getUsuarioGrupos(userId) {
  const res = await apiFetchWithToken(`/usuarios/${userId}/grupos`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

/**
 * Get all companies a user has access to
 */
export async function getUsuarioCompanies(userId) {
  const res = await apiFetchWithToken(`/usuarios/${userId}/companies`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

/**
 * Remove user from a grupo
 */
export async function removeUsuarioFromGrupo(grupoUsuarioId) {
  const res = await apiFetchWithToken(`/grupos-usuarios/${grupoUsuarioId}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}

/**
 * Remove user from a company
 */
export async function removeUsuarioFromCompany(companyId, userId) {
  const res = await apiFetchWithToken(`/companies/${companyId}/users/${userId}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}
