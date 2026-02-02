// src/services/planosTrabalhoService.js
import { apiFetch, apiFetchWithToken } from "../api/api"; // ajuste o caminho conforme seu projeto

export async function listarPlanosTrabalho(params = {}) {
  const {
    page = 1,
    limit = 10,
    search = "",
    sort = "",
    empresa_id,
  } = params;

  const query = new URLSearchParams({
    page: String(page),
    limit: String(limit),
    search: search || "",
    sort: sort || "",
    ...(empresa_id ? { empresa_id: String(empresa_id) } : {})
  }).toString();

  console.log("DEBUG empresa_id enviado:", empresa_id);
  const res = await apiFetchWithToken(`/planos-trabalho/?${query}`);
  
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
  const response = await apiFetchWithToken(`/planos-trabalho/${id}`);
  if (response instanceof Response) {
    return await response.json();
  }
  return response;
}


export async function criarPlanoTrabalho(payload) {
  // payload só: { nome, descricao } (empresa_id vem do usuário logado no backend)
  return apiFetchWithToken("/planos-trabalho/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function atualizarPlanoTrabalho(planoId, payload) {
  console.log("Updating PlanoTrabalho ID:", planoId, "with payload:", payload);
  return apiFetchWithToken(`/planos-trabalho/${planoId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}


export async function deletarPlanoTrabalho(planoId) {
  return apiFetch(`/planos-trabalho/${planoId}`, {
    method: "DELETE",
  });
}
