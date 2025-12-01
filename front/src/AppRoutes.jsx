// src/AppRoutes.jsx
import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard/Dashboard";
import EmpresasList from "./pages/Empresas/EmpresasList";
import EmpresaForm from "./pages/Empresas/EmpresasForm";
import UsuariosList from "./pages/Usuarios/UsuariosList";
import UsuariosForm from "./pages/Usuarios/UsuariosForm";


export default function AppRoutes() {
  return (
    <MainLayout>
      <Routes>
        {/* Página principal */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* CRUD de empresas */}
        <Route path="/empresas" element={<EmpresasList />} />
        <Route path="/empresas/nova" element={<EmpresaForm />} />
        <Route path="/empresas/editar/:id" element={<EmpresaForm />} />

        {/* CRUD de Usuarios */}
        <Route path="/usuarios" element={<UsuariosList />} />
        <Route path="/usuarios/novo" element={<UsuariosForm />} />
        <Route path="/usuarios/editar/:id" element={<UsuariosForm />} />

        {/* Redirecionamento padrão */}
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </MainLayout>
  );
}
