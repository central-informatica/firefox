import { createContext, useState, useEffect } from "react";
import { apiFetch } from "../api/api";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // carrega usuário logado ao iniciar o app
  async function loadUser() {
    try {
      const res = await apiFetch("/auth/me");

      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        // 401 aqui é normal se não estiver logado
        setUser(null);
      }
    } catch (err) {
      console.error("Erro ao carregar usuário:", err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUser();
  }, []);

  // LOGIN
  async function login(email, senha) {
    const response = await apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, senha }),
    });

    if (!response.ok) {
      throw new Error("Login inválido");
    }

    const data = await response.json();
    setUser(data);
  }

  // REGISTER (cadastro de usuário)
 async function register({ nome, email, senha, telefone }) {
    const response = await apiFetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, email, senha, telefone }),
    });

    if (!response.ok) {
      let msg = "Erro ao cadastrar usuário";

      try {
        const data = await response.json();

        if (typeof data.detail === "string") {
          msg = data.detail;
        } else if (Array.isArray(data.detail) && data.detail.length > 0) {
          // Erro de validação Pydantic
          msg = data.detail[0].msg || msg;
        }
      } catch {
        // ignore erro ao ler json
      }

      throw new Error(msg);
    }

    return response.json();
  }

  // LOGOUT
  async function logout() {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch (err) {
      console.error("Erro ao fazer logout:", err);
    }
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, register }}
    >
      {children}
    </AuthContext.Provider>
  );
}
