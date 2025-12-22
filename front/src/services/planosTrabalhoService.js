// src/services/planosTrabalhoService.js
import { apiFetch } from "../api/api"; // ajuste o caminho conforme seu projeto

export async function listarPlanosTrabalho(params = {}) {
  const {
    page = 1,
    limit = 10,
    search = "",
    sort = "",
  } = params;

  const query = new URLSearchParams({
    page: String(page),
    limit: String(limit),
    search: search || "",
    sort: sort || "",
  }).toString();
  
  const res = await apiFetch(`/planos-trabalho/?${query}`);
  
  // apiFetch retorna Response (fetch). Então precisa parsear JSON.
  if (!res.ok) {
    throw new Error(await res.text());
  }
  
  const json = await res.json(); // <- aqui está o { items: [...], total: ... }
  
  return {
    data: Array.isArray(json?.items) ? json.items : [],
    total: Number(json?.total) || 0,
  };
}

export async function getPlanoTrabalho(id) {
  const response = await apiFetch(`/planos-trabalho/${id}`);
  if (response instanceof Response) {
    return await response.json();
  }
  return response;
}


export async function criarPlanoTrabalho(payload) {
  // payload só: { nome, descricao } (empresa_id vem do usuário logado no backend)
  return apiFetch("/planos-trabalho/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function atualizarPlanoTrabalho(planoId, payload) {
  return apiFetch(`/planos-trabalho/${planoId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deletarPlanoTrabalho(planoId) {
  return apiFetch(`/planos-trabalho/${planoId}`, {
    method: "DELETE",
  });
}
