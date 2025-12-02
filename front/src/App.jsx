// src/App.jsx
import React, { useState } from "react";
import Login from "./login";
import Cadastro from "./pages/Usuarios/Cadastro";
import { useAuth } from "./auth/useAuth";
import AppRoutes from "./AppRoutes";

import { ToastContainer } from "react-toastify";

export default function App() {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (loading) return <div>Carregando...</div>;

  return (
    <>
      <ToastContainer />
      {user ? (
        <AppRoutes />
      ) : showRegister ? (
        <Cadastro onVoltar={() => setShowRegister(false)} />
      ) : (
        <Login onCadastrar={() => setShowRegister(true)} />
      )}
    </>
  );
}
