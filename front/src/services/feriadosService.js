import { apiFetchWithToken } from "../api/api";

export async function listarFeriadosPorEmpresa({
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

  const res = await apiFetchWithToken(`/feriados/empresa/${empresaId}?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function getFeriado(id) {
  const res = await apiFetchWithToken(`/feriados/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function createFeriado(data) {
  const res = await apiFetchWithToken(`/feriados/`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function updateFeriado(id, data) {
  const res = await apiFetchWithToken(`/feriados/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function deleteFeriado(id) {
  const res = await apiFetchWithToken(`/feriados/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}

export async function listarFeriadosPadroes() {
  const res = await apiFetchWithToken(`/feriados/padroes/lista`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function replicarFeriados(data) {
  const res = await apiFetchWithToken(`/feriados/replicar`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

export async function importarFeriadosPadroes(data) {
  const res = await apiFetchWithToken(`/feriados/importar-padroes`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}
