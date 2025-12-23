import { getCookie } from "./cookies";

const API_URL = "http://127.0.0.1:8000";

/**
 * Basic API fetch without authentication
 * Use this for public endpoints (login, register, etc.)
 */
export async function apiFetch(path, options = {}) {
  const response = await fetch(API_URL + path, {
    credentials: "include", // Send cookies
    ...options,
    headers: {
      ...(options.headers || {}),
    },
  });

  return response;
}

/**
 * API fetch with CSRF token authentication
 * Use this for protected endpoints that require authentication
 */
export async function apiFetchWithToken(path, options = {}) {
  const csrf = getCookie("csrf_token") || "";

  if (!csrf) {
    console.warn("CSRF token not found. User may not be authenticated.");
  }

  const response = await fetch(API_URL + path, {
    credentials: "include", // Send session_token cookie
    ...options,
    headers: {
      "X-CSRF-Token": csrf, // Send CSRF token in header
      ...(options.headers || {}),
    },
  });

  return response;
}
