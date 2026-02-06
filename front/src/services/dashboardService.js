// dashboardService.js

import { apiFetchWithToken } from "../api/api";

/**
 * Get dashboard statistics
 * Returns: { total_usuarios: number, certificados_ativos: number }
 */
export async function getDashboardStats() {
  const res = await apiFetchWithToken("/dashboard/stats", {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return await res.json();
}
