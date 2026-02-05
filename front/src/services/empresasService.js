import { apiFetchWithToken } from "../api/api";

/**
 * Mapeia campos do Auth service para o formato do frontend
 */
function mapAuthToFrontend(empresa) {
  if (!empresa) return empresa;
  return {
    ...empresa,
    // id ou company_id no Auth service, empresa_id no frontend legado
    empresa_id: empresa.id || empresa.company_id || empresa.empresa_id,
    razao_social: empresa.name || empresa.razao_social,
    fantasia: empresa.name || empresa.fantasia,
    // company_category_id no Auth service, ramos_id no frontend legado
    ramos_id: empresa.company_category_id || empresa.category_id || empresa.ramos_id,
  };
}

/**
 * Mapeia campos do frontend para o formato do Auth service
 */
function mapFrontendToAuth(data) {
  const mapped = { ...data };

  // razao_social -> name
  if (mapped.razao_social) {
    mapped.name = mapped.razao_social;
    delete mapped.razao_social;
  }

  // ramos_id -> category_id
  if (mapped.ramos_id) {
    mapped.category_id = mapped.ramos_id;
    delete mapped.ramos_id;
  }

  // Remove formatação do CNPJ
  if (mapped.cnpj) {
    mapped.cnpj = mapped.cnpj.replace(/\D/g, "");
  }

  return mapped;
}

export async function listarMinhasEmpresas() {
  const response = await apiFetchWithToken("/empresas/minhas");
  const json = await response.json();

  console.log("[listarMinhasEmpresas] raw response:", json);

  // Mapeia a lista para o formato do frontend
  // Pode vir como array direto, {data: []}, ou {companies: []}
  let empresas = [];
  if (Array.isArray(json)) {
    empresas = json;
  } else if (json && Array.isArray(json.data)) {
    empresas = json.data;
  } else if (json && Array.isArray(json.companies)) {
    empresas = json.companies;
  }

  return { data: empresas.map(mapAuthToFrontend) };
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

  const res = await apiFetchWithToken(`/empresas/?${params.toString()}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  const result = await res.json();

  // Mapeia a lista para o formato do frontend
  return {
    data: (result.data || []).map(mapAuthToFrontend),
    total: result.total || 0,
  };
}

export async function getEmpresasDoUsuario(userId) {
  const res = await apiFetchWithToken(`/usuarios/${userId}/empresas`);
  const json = await res.json();

  if (Array.isArray(json)) {
    return json.map(mapAuthToFrontend);
  }
  return json;
}

export async function getEmpresa(id) {
  const res = await apiFetchWithToken(`/empresas/id/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  const empresa = await res.json();
  return mapAuthToFrontend(empresa);
}

/**
 * CREATE
 */
export async function createEmpresa(data) {
  const authData = mapFrontendToAuth(data);

  const res = await apiFetchWithToken(`/empresas/`, {
    method: "POST",
    body: JSON.stringify(authData),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  const empresa = await res.json();
  return mapAuthToFrontend(empresa);
}

/**
 * UPDATE
 */
export async function updateEmpresa(id, data) {
  const authData = mapFrontendToAuth(data);

  const res = await apiFetchWithToken(`/empresas/id/${id}`, {
    method: "PUT",
    body: JSON.stringify(authData),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  const empresa = await res.json();
  return mapAuthToFrontend(empresa);
}

/**
 * DELETE
 */
export async function deleteEmpresa(id) {
  const res = await apiFetchWithToken(`/empresas/id/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return true;
}
