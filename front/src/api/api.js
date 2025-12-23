import { getCookie } from "./cookies";

const API_URL = "http://127.0.0.1:8000";

let refreshing = false;
let refreshPromise = null;

/**
 * Faz refresh da sessão quando o backend retornar 401.
 * Usa cookies + CSRF corretamente.
 */
async function refreshTokens() {
  if (refreshing) return refreshPromise;

  refreshing = true;

  refreshPromise = fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include", 
    headers: {
      "X-CSRF-Token": getCookie("csrf_token") || "",
    },
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error("Refresh falhou");
      }
    })
    .finally(() => {
      refreshing = false;
    });

  return refreshPromise;
}

/**
 * Fetch centralizado da aplicação.
 * - Envia cookies
 * - Envia CSRF
 * - Tenta refresh automático em 401
 */
export async function apiFetch(path, options = {}) {
  const csrf = getCookie("csrf_token") || "";
  const isFormData = options.body instanceof FormData;

  const response = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      "X-CSRF-Token": csrf,
      ...(options.headers || {}),
    },
  });

  if (response.status !== 401) {
    return response;
  }

  // Não tenta refresh se:
  // - não tem CSRF
  // - já está tentando refresh
  // - a rota já é refresh
  if (!csrf || path === "/auth/refresh") {
    return response;
  }

  // Tenta refresh
  try {
    await refreshTokens();
  } catch {
    return response;
  }

  // Reexecuta a request original após refresh
  return fetch(`${API_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": getCookie("csrf_token") || "",
      ...(options.headers || {}),
    },
  });
}
