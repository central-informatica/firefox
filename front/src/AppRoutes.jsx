// src/AppRoutes.jsx
import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard/Dashboard";
import EmpresasList from "./pages/Empresas/EmpresasList";
import EmpresaForm from "./pages/Empresas/EmpresasForm";
import UsuariosList from "./pages/Usuarios/UsuariosList";
import UsuariosForm from "./pages/Usuarios/UsuariosForm";
import CertificadosList from "./pages/Certificados/CertificadosList"
import CertificadosForm from "./pages/Certificados/CertificadosForm"
import PlanosList from "./pages/PlanosTrabalho/PlanosTrabalhoList"
import PlanosForm from "./pages/PlanosTrabalho/PlanosTrabalhoForm"


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

        {/* CRUD de Certificados */}
        <Route path="/certificados" element={<CertificadosList />} />
        <Route path="/certificados/novo" element={<CertificadosForm />} />
        {/*<Route path="/certificados/editar/:id" element={<CertificadosForm />} />*/}
        <Route path="/certificados/excluir" element={<CertificadosForm />} />

        {/* CRUD de planos de trabalho */}
        <Route path="/planos" element={<PlanosList />} />
        <Route path="/planos/novo" element={<PlanosForm />} />
        <Route path="/planos/editar/:id" element={<PlanosForm />} />

        {/* Redirecionamento padrão */}
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </MainLayout>
  );
}
