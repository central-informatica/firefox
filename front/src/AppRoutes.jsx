import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard/Dashboard";
import EmpresasList from "./pages/Empresas/EmpresasList";
import EmpresaForm from "./pages/Empresas/EmpresasForm";
import UsuariosList from "./pages/Usuarios/UsuariosList";
import UsuariosForm from "./pages/Usuarios/UsuariosForm";
import CertificadosList from "./pages/Certificados/CertificadosList"
import CertificadosForm from "./pages/Certificados/CertificadosForm"
import CertificadosGruposList from "./pages/Certificados/CertificadosGruposList"
import PlanosList from "./pages/PlanosTrabalho/PlanosTrabalhoList"
import PlanosForm from "./pages/PlanosTrabalho/PlanosTrabalhoForm"
import GerenciarAssociacoes from "./pages/PlanosTrabalho/GerenciarAssociacoes"
import GruposList from "./pages/Grupos/GruposList";
import GruposForm from "./pages/Grupos/GruposForm";
import AssociarUsuarios from "./pages/Grupos/AssociarUsuarios";
import GlobalURLs from "./pages/Seguranca/GlobalURLs";
import RegrasAcessoUrlsList from "./pages/Seguranca/RegrasAcessoUrlsList";
import RegrasAcessoIpsList from "./pages/Seguranca/RegrasAcessoIpsList";
import FeriadosList from "./pages/Configuracoes/FeriadosList";


export default function AppRoutes() {
  return (
    <Routes>

      <Route path="/dashboard" element={<Dashboard />} />


      <Route path="/empresas" element={<EmpresasList />} />
      <Route path="/empresas/nova" element={<EmpresaForm />} />
      <Route path="/empresas/editar/:id" element={<EmpresaForm />} />


      <Route path="/usuarios" element={<UsuariosList />} />
      <Route path="/usuarios/novo" element={<UsuariosForm />} />
      <Route path="/usuarios/editar/:id" element={<UsuariosForm />} />


      <Route path="/certificados" element={<CertificadosList />} />
      <Route path="/certificados/novo" element={<CertificadosForm />} />
      <Route path="/certificados/grupos" element={<CertificadosGruposList />} />


      <Route path="/planos" element={<PlanosList />} />
      <Route path="/planos/novo" element={<PlanosForm />} />
      <Route path="/planos/editar/:id" element={<PlanosForm />} />
      <Route path="/planos/associacoes" element={<GerenciarAssociacoes />} />

      <Route path="/grupos" element={<GruposList />} />
      <Route path="/grupos/novo" element={<GruposForm />} />
      <Route path="/grupos/editar/:id" element={<GruposForm />} />
      <Route path="/grupos/associar-usuarios" element={<AssociarUsuarios />} />

      <Route path="/seguranca/enderecos-permitidos" element={<GlobalURLs />} />
      <Route path="/seguranca/regras-acesso-urls" element={<RegrasAcessoUrlsList />} />
      <Route path="/seguranca/regras-acesso-ips" element={<RegrasAcessoIpsList />} />

      <Route path="/configuracoes/feriados" element={<FeriadosList />} />

      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}
