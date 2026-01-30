import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./login";
import Cadastro from "./pages/Usuarios/Cadastro";
import { useAuth } from "./auth/useAuth";
import AppRoutes from "./AppRoutes";
import Layout from "./layouts/MainLayout";

import { ToastContainer } from "react-toastify";

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-dark-primary">
        <div className="flex flex-col items-center gap-4">
          <svg className="animate-spin h-12 w-12 text-xfire-orange" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-neutral-400 font-medium">Carregando...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
      <Routes>
        {/* Rotas publicas */}
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/cadastro" element={user ? <Navigate to="/dashboard" /> : <Cadastro />} />

        {/* Rotas privadas */}
        <Route
          path="/*"
          element={
            user ? (
              <Layout>
                <AppRoutes />
              </Layout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </>
  );
}
