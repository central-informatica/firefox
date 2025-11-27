// src/api/api.js
import { getCookie } from "./cookies";

const API_URL = "http://127.0.0.1:8000";

let refreshing = false;

async function refresh() {
  if (refreshing) return;
  refreshing = true;

  await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
    headers: {
      "X-CSRF-Token": getCookie("csrf_token") || "",
    },
  });

  refreshing = false;
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

  if (response.status !== 401) return response;

  await refresh();

  return fetch(API_URL + path, {
    credentials: "include",
    ...options,
    headers: {
      "X-CSRF-Token": getCookie("csrf_token") || "",
      ...(options.headers || {}),
    },
  });
}
