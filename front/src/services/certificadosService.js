import { apiFetch } from "../api/api";

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

export async function getCertificado(id) {
  const res = await apiFetch(`/certificados/${id}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Erro ao carregar certificado");
  }

  return res.json();
}

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

// Mock data para testes de associação
const certificadosMock = [
  {
    id: 1,
    nome_arquivo: "certificado_empresa.pfx",
    proprietario: "Empresa XYZ LTDA",
    valido_ate: "2026-12-31",
  },
  {
    id: 2,
    nome_arquivo: "certificado_comercial.pfx",
    proprietario: "Sistema Comercial",
    valido_ate: "2025-06-30",
  },
  {
    id: 3,
    nome_arquivo: "certificado_fiscal.pfx",
    proprietario: "Sistema Fiscal",
    valido_ate: "2026-03-15",
  },
];

// Listar todos os certificados (mock)
export function getCertificadosSimples() {
  return Promise.resolve(certificadosMock);
}

