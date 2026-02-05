import { apiFetchWithToken } from "../api/api";

export async function listarRegrasPorEmpresa({
  empresaId,
  page = 1,
  limit = 10,
  search = "",
}) {
  const params = new URLSearchParams({
    page,
    limit,
    search,
  });

  const res = await apiFetchWithToken(`/regras-acesso-urls/empresa/${empresaId}?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function listarRegrasPorGrupo(grupoId) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/grupo/${grupoId}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function getRegra(id) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/id/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function createRegra(data) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function createRegraBulk(data) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/bulk`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function updateRegra(id, data) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function toggleRegraAtivo(id) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/${id}/toggle`, {
    method: "PATCH",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function deleteRegra(id) {
  const res = await apiFetchWithToken(`/regras-acesso-urls/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}
