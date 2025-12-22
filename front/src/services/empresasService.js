import { ReplaceAll } from "lucide-react";
import { apiFetch } from "../api/api";

export async function listarMinhasEmpresas() {
  const response = await apiFetch("/empresas/minhas");
  const json = await response.json();

  console.log("🟢 JSON da API:", json);

  return json;
}

export async function listarEmpresasPaginado({
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

  const res = await apiFetch(`/empresas/?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json(); // { data, total }
}

export async function getEmpresasDoUsuario(userId) {
  console.log("Id do usuário logado: ", userId);
  const res = await fetch(`http://127.0.0.1:8000/usuarios/${userId}/empresas`, {
    credentials: "include",
  });
  return await res.json();
}

export async function getEmpresa(id) {
  const res = await apiFetch(`/empresas/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * CREATE
 */
export async function createEmpresa(data) {
  data.cnpj = data.cnpj.replace(/\D/g, ""); // Remove formatação
  console.log(data.cnpj)
  const res = await apiFetch(`/empresas/`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * UPDATE
 */
export async function updateEmpresa(id, data) {
  const res = await apiFetch(`/empresas/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}

/**
 * DELETE
 */
export async function deleteEmpresa(id) {
  const res = await apiFetch(`/empresas/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}
