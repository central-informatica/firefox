// src/App.jsx
import React from "react";
import Login from "./login";
import Dashboard from "./pages/Dashboard/Dashboard";
import { ToastContainer } from "react-toastify";
import { useAuth } from "./auth/useAuth";

function App() {
  const { user, loading } = useAuth();

  // Enquanto carrega, não renderiza login nem dashboard
  if (loading) {
    return <div>Carregando...</div>;
  }

  return (
    <>
      {user ? <Dashboard /> : <Login />}
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  );
}

export default App;
