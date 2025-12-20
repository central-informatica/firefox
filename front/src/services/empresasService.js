// services/empresasService.js

import { apiFetch } from "../api/api";

// Lista
function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrf_token="))
    ?.split("=")[1];
}

export function getEmpresas() {
  return Promise.resolve(empresas);
}

export async function getEmpresasDoUsuario(userId) {
  console.log("Id do usuário logado: ", userId);
  const res = await apiFetch(`/usuarios/${userId}/empresas`, {
    credentials: "include",
  });
  return await res.json();
}

export function getEmpresa(id) {
  const empresa = empresas.find((e) => e.id === Number(id));
  return Promise.resolve(empresa);
}

// Empresas paginado
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

  const csrfToken = getCsrfToken();

  const res = await apiFetch(
    `/empresas/?${params.toString()}`,
    {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text);
  }

  return await res.json();
}


export function createEmpresa(data) {
  const nova = { id: Date.now(), ...data };
  empresas.push(nova);
  return Promise.resolve(nova);
}

export function updateEmpresa(id, data) {
  empresas = empresas.map((e) =>
    e.id === Number(id) ? { ...e, ...data } : e
  );
  return Promise.resolve(true);
}
