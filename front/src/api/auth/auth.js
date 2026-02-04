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

export async function verifyEmail(token) {
  return apiFetch("/auth/verify-email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  });
}

export async function forgotPassword(email) {
  return apiFetch("/auth/forgot-password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(token, newPassword) {
  return apiFetch("/auth/reset-password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

export async function verify2FA(userId, code) {
  return apiFetch("/auth/verify-2fa", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: userId, code }),
  });
}
