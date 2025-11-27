// src/auth/AuthContext.jsx
import { createContext, useState, useEffect } from "react";
import { apiFetch } from "../api/api";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    const res = await apiFetch("/auth/me");
    if (res.ok) setUser(await res.json());
    else setUser(null);
    setLoading(false);
  }

  useEffect(() => {
    loadUser();
  }, []);

  async function login(email, senha) {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, senha }),
    });

    if (!res.ok) throw new Error("Login inválido");

    const user = await res.json();
    setUser(user);
  }

  async function logout() {
    await apiFetch("/auth/logout", { method: "POST" });
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
