import { apiFetchWithToken } from "../api/api";

export async function listarGlobalUrlsPaginado({
  empresaId,
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

  const res = await apiFetchWithToken(`/global-urls/empresa/${empresaId}?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function getGlobalUrl(id) {
  const res = await apiFetchWithToken(`/global-urls/id/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function createGlobalUrl(data) {
  const res = await apiFetchWithToken(`/global-urls/`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function updateGlobalUrl(id, data) {
  const res = await apiFetchWithToken(`/global-urls/id/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function deleteGlobalUrl(id) {
  const res = await apiFetchWithToken(`/global-urls/id/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}
