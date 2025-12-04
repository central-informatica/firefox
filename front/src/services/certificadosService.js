// certificadosService.js
import { apiFetch } from "../api/api";

// -------------------------
// LISTAGEM PAGINADA
// -------------------------
export async function listarCertificadosPaginado({
  empresa_id,
  page = 1,
  limit = 10,
  search = "",
  sort = "",
}) {
  const params = new URLSearchParams({
    empresa_id,
    page,
    limit,
    search,
    sort,
  });

  const res = await apiFetch(`/certificados?${params.toString()}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Erro ao listar certificados");
  }

  return res.json();
}

// -------------------------
// BUSCAR POR ID
// -------------------------
export async function getCertificado(id) {
  const res = await apiFetch(`/certificados/${id}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Erro ao carregar certificado");
  }

  return res.json();
}

// -------------------------
// CRIAR (UPLOAD DO PFX)
// -------------------------
export async function createCertificado(formData) {
  const res = await apiFetch(`/certificados`, {
    method: "POST",
    body: formData,
  });
  console.log("Form data: ", res)
  if (!res.ok) {
    throw new Error("Erro ao criar certificado");
  }

  return res.json();
}

// -------------------------
// EXCLUIR
// -------------------------
// EXCLUI UM CERTIFICADO
export async function excluir_certificado(id) {
  const res = await apiFetch(`/certificados/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("Erro ao excluir", errorText);
    throw new Error("Erro ao excluir certificado");
  }

  return res.json();
}

