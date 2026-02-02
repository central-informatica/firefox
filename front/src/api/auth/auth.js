import { apiFetch, apiFetchWithToken } from "../api";

export async function loginWeb(email, senha) {
  return apiFetch("/auth/login/web", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password: senha }),
  });
}

export async function getMe() {
  return apiFetchWithToken("/auth/me", {
    method: "GET",
  });
}

export async function logout() {
  return apiFetchWithToken("/auth/logout", {
    method: "POST",
  });
}
