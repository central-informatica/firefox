import { getCookie } from "./cookies";

const API_URL = import.meta.env.VITE_URL_BACKEND || "http://localhost:8000";

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

  // If the body is FormData (multipart), DO NOT set Content-Type so browser sets the boundary automatically
  const isFormData = options && options.body && typeof FormData !== 'undefined' && options.body instanceof FormData;

  const headers = {
    "X-CSRF-Token": csrf, // Send CSRF token in header
    ...(options.headers || {}),
  };

  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(API_URL + path, {
    credentials: "include", // Send session_token cookie
    ...options,
    headers,
  });

  return response;
}
