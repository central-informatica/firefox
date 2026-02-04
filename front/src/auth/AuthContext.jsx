import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, apiFetchWithToken } from "../api/api";
import { loginWeb, getMe, logout as logoutApi } from "../api/auth/auth";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    try {
      const res = await getMe();

      if (res.ok) {
        const data = await res.json();
        setUser({
          id: data.id,
          nome: `${data.first_name || ""} ${data.last_name || ""}`.trim() || data.email,
          email: data.email,
          organization_id: data.organization_id,
          is_admin: data.is_admin,
        });
        return true;
      } else {
        setUser(null);
        return false;
      }
    } catch (err) {
      console.error("Erro ao carregar usuario:", err);
      setUser(null);
      return false;
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
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Login invalido");
    }

    const data = await response.json();

    // Check if 2FA is required
    if (data.requires_2fa) {
      return {
        requires_2fa: true,
        user_id: data.user_id,
        email: email,
      };
    }

    // Cookies are set by backend automatically
    // Load user data from /auth/me
    await loadUser();
    navigate("/");
    return { requires_2fa: false };
  }

  async function completeLogin() {
    // Called after 2FA verification to load user and navigate
    const success = await loadUser();
    if (success) {
      navigate("/");
    } else {
      throw new Error("Falha ao carregar dados do usuario. Tente fazer login novamente.");
    }
  }

  async function register({
    organization_name,
    cnpj,
    address_street,
    address_city,
    address_state,
    address_country,
    address_postal_code,
    admin_email,
    admin_password,
    admin_first_name,
    admin_last_name,
  }) {
    const response = await apiFetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        organization_name,
        cnpj,
        address_street,
        address_city,
        address_state,
        address_country,
        address_postal_code,
        admin_email,
        admin_password,
        admin_first_name,
        admin_last_name,
      }),
    });

    if (!response.ok) {
      let msg = "Erro ao cadastrar usuario";

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
      await logoutApi(); // Backend clears cookies
    } catch (err) {
      console.error("Erro ao fazer logout:", err);
    }

    setUser(null);
    navigate("/login");
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout, register, completeLogin }}
    >
      {children}
    </AuthContext.Provider>
  );
}
