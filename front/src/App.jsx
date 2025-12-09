import React, { useState } from "react";
import Login from "./login";
import Cadastro from "./pages/Usuarios/Cadastro";
import { useAuth } from "./auth/useAuth";
import AppRoutes from "./AppRoutes";
import Layout from "./layouts/MainLayout";

import { ToastContainer } from "react-toastify";

export default function App() {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (loading) return <div>Carregando...</div>;

  return (
    <>
      <ToastContainer />
      {user ? (
        <Layout>
          <AppRoutes />
        </Layout>
      ) : showRegister ? (
        <Cadastro onVoltar={() => setShowRegister(false)} />
      ) : (
        <Login onCadastrar={() => setShowRegister(true)} />
      )}
    </>
  );
}
