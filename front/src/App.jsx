// src/App.jsx
import React, { useState } from "react";
import Login from "./login";
import Cadastro from "./pages/Usuarios/Cadastro";
import { useAuth } from "./auth/useAuth";
import AppRoutes from "./AppRoutes";

export default function App() {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (loading) return <div>Carregando...</div>;

  // Se estiver logado → cai nas rotas com layout e sidebar
  if (user) {
    return <AppRoutes />;
  }

  // Se não estiver logado → Login ou Cadastro
  return (
    <>
      {showRegister ? (
        <Cadastro onVoltar={() => setShowRegister(false)} />
      ) : (
        <Login onCadastrar={() => setShowRegister(true)} />
      )}
    </>
  );
}
