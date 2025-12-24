import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, apiFetchWithToken } from "../api/api";
import { loginWeb, getMe, logout as logoutApi } from "../api/auth/auth";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Carrega usuário ativo da sessão
  async function loadUser() {
    try {
      const res = await getMe();

      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
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

  async function login(email, senha) {
    const response = await loginWeb(email, senha);

    if (!response.ok) {
      throw new Error("Login inválido");
    }

    // Backend retorna dados completos do usuário
    const data = await response.json();
    setUser(data);

    navigate("/"); // redireciona após login
  }

  // REGISTER
  async function register({ nome, email, senha, telefone }) {
    const response = await apiFetchWithToken("/auth/register", {
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
          msg = data.detail[0].msg || msg;
        }
      } catch {}

      throw new Error(msg);
    }

    return response.json();
  }

  async function logout() {
    try {
      await logoutApi();
    } catch (err) {
      console.error("Erro ao fazer logout:", err);
    }

    setUser(null);
    navigate("/login"); // ✔ redireciona
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, register }}
    >
      {children}
    </AuthContext.Provider>
  );
}
