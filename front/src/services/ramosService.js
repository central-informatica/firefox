import { apiFetchWithToken } from "../api/api";

/**
 * Lista todos os ramos de atuação (para selects)
 */
export async function listarTodosRamos() {
  const res = await apiFetchWithToken("/ramos/");
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return await res.json();
}

/**
 * Lista ramos de atuação com paginação
 */
export async function listarRamosPaginado({
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

  const res = await apiFetchWithToken(`/ramos/paginado?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * Busca um ramo por ID
 */
export async function getRamo(id) {
  const res = await apiFetchWithToken(`/ramos/id/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * Cria um novo ramo
 */
export async function createRamo(data) {
  const res = await apiFetchWithToken("/ramos/", {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * Atualiza um ramo existente
 */
export async function updateRamo(id, data) {
  const res = await apiFetchWithToken(`/ramos/id/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * Deleta um ramo
 */
export async function deleteRamo(id) {
  const res = await apiFetchWithToken(`/ramos/id/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}
