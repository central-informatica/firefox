import { apiFetch, apiFetchWithToken } from "../api/api";

export async function listarCertificadosPaginado({
  empresa_id,
  grupo_id = undefined,
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

  if (grupo_id !== undefined && grupo_id !== null) params.append('grupo_id', String(grupo_id));

  const res = await apiFetchWithToken(`/certificados?${params.toString()}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Erro ao listar certificados");
  }

  return res.json();
}

export async function getCertificado(id) {
  const res = await apiFetchWithToken(`/certificados/${id}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Erro ao carregar certificado");
  }

  return res.json();
}

export async function createCertificado(formData) {
  const res = await apiFetchWithToken("/certificados/", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let message = "Erro ao criar certificado";

    try {
      const errorBody = await res.json();

      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      } else if (Array.isArray(errorBody.detail)) {
        message = errorBody.detail
          .map((e) => e.msg)
          .join(", ");
      }
    } catch {
      // fallback se não for JSON
      message = await res.text();
    }

    throw new Error(message);
  }

  return await res.json();
}


export async function excluir_certificado(id) {
  const res = await apiFetchWithToken(`/certificados/${id}`, {
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

export async function listarCertificadosPermitidos() {
  const res = await apiFetchWithToken(
    `/certificados/listar_certificados_permitidos/`
  );

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

export async function listarCertificadosDaEmpresa(empresaId) {
  if (!empresaId) return [];
  const res = await apiFetchWithToken(`/certificados/?empresa_id=${empresaId}`);
  if (!res.ok) {
    throw new Error(await res.text());
  }
  const json = await res.json();
  return Array.isArray(json?.items) ? json.items : [];
}


/* Lista certificados já vinculados a um grupo */
export async function listarCertificadosDoGrupo(grupoId) {
  if (!grupoId) return [];
  const res = await apiFetchWithToken(`/grupos/${grupoId}/certificados`);
  if (!res.ok) {
    throw new Error(await res.text());
  }
  const json = await res.json();
  return Array.isArray(json) ? json : [];
}

/* Adiciona certificado a um grupo */
export async function adicionarCertificadoAoGrupo(grupoId, certificadoId, empresaId) {
  const res = await apiFetchWithToken(
    `/grupos/${grupoId}/certificados`,
    {
      method: "POST",
      body: JSON.stringify({
        certificado_id: certificadoId,
        empresa_id: empresaId,
      }),
    }
  );
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return await res.json();
}

/* Remove vínculo de um certificado com o grupo*/
export async function removerCertificadoDoGrupo(grupo_id, certificadoId, empresa_id) {
  const res = await apiFetchWithToken(
    `/grupos/${grupo_id}/remover/certificado`,
    {
      method: "DELETE",
      body: JSON.stringify({
        certificado_id: certificadoId,
        empresa_id: empresa_id,
      }),
    }
  );
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return true;
}
