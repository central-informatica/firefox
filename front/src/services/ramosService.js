import { apiFetchWithToken } from "../api/api";

/**
 * Lista todas as categorias de empresa (ramos de atuação) do Auth service
 */
export async function listarTodosRamos() {
  const res = await apiFetchWithToken("/company-categories/");
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return await res.json();
}
