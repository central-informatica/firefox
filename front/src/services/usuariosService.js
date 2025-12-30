import {apiFetchWithToken} from "../api/api";

export async function listarUsuariosPaginado({
  empresa_id,
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

  const res = await apiFetchWithToken(
    `/usuarios/empresas/${empresa_id}/usuarios?${params.toString()}`
  );
  
  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json(); // { data, total }
}

export async function getUsuarioById(id){
   const res = await apiFetchWithToken(`/usuarios/${id}`);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
};

export async function createUsuario(usuario){
  const res = await apiFetchWithToken(`/usuarios/`, {
    method: "POST",
    body: JSON.stringify(usuario),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
};

export async function updateUsuario(empresaId, id, usuario) {
  const params = new URLSearchParams();
  if (empresaId) params.set("empresa_id", empresaId);

  const res = await apiFetchWithToken(`/usuarios/${id}?${params.toString()}`, {
    method: "PUT",
    body: JSON.stringify(usuario),
  });

  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function deletarUsuario(empresaId, usuarioId) {
  const params = new URLSearchParams();
  if (empresaId) params.set("empresa_id", empresaId);

  const res = await apiFetchWithToken(
    `/usuarios/${usuarioId}?${params.toString()}`,
    { method: "DELETE" }
  );

  if (!res.ok) throw new Error(await res.text());
  return true;
}
