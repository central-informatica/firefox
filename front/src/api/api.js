import { getCookie } from "./cookies";

const API_URL = "http://127.0.0.1:8000";

let refreshing = false;
let refreshPromise = null;

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

export async function apiFetch(path, options = {}) {
  const csrf = getCookie("csrf_token") || "";

  const response = await fetch(API_URL + path, {
    credentials: "include",
    ...options,
    headers: {
      "X-CSRF-Token": csrf,
      ...(options.headers || {}),
    },
  });

  if (response.status !== 401) {
    return response;
  }

  if (!csrf) {
    return response;
  }

  if (path === "/auth/refresh") {
    return response;
  }

  try {
    await refreshTokens();
  } catch (err) {
    return response;
  }

  return fetch(API_URL + path, {
    credentials: "include",
    ...options,
    headers: {
      "X-CSRF-Token": getCookie("csrf_token") || "",
      ...(options.headers || {}),
    },
  });
}
