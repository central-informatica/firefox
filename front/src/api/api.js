import { getCookie } from "./cookies";

const API_URL = import.meta.env.VITE_URL_BACKEND || "http://127.0.0.1:8000";

/**
 * Basic API fetch without authentication
 * Use this for public endpoints (login, register, etc.)
 */
export async function apiFetch(path, options = {}) {
  console.log("apiFetch called with path:", path, "and options:", options);
  console.log("API_URL:", API_URL);
  const response = await fetch(API_URL + path, {
    credentials: "include", // Send cookies
    ...options,
    headers: {
      ...(options.headers || {}),
    },
  });
  console.log(response);
  console.log("apiFetch response:", response);
  return response;
}

/**
 * API fetch with CSRF token authentication
 * Use this for protected endpoints that require authentication
 */
export async function apiFetchWithToken(path, options = {}) {
  const csrf = getCookie("csrf_token");

  if (!csrf) {
    console.error("CSRF token not found in cookies. User may not be authenticated.");
    throw new Error("Authentication token missing. Please log in again.");
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
    credentials: "include", // Send auth_token cookie
    ...options,
    headers,
  });

  return response;
}
