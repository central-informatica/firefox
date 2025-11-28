import React, { useState } from "react";
import Login from "./login";
import Cadastro from "./pages/Usuarios/Cadastro";
import Dashboard from "./pages/Dashboard/Dashboard";
import { useAuth } from "./auth/useAuth";

export default function App() {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (loading) return <div>Carregando...</div>;

  if (user) {
    return <Dashboard />;
  }

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
