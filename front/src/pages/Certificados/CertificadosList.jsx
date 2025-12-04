//import { useEffect, useState } from "react";
//import { useNavigate } from "react-router-dom";
//import { listarCertificadosPaginado } from "../../services/certificadosService";
//import { getEmpresasDoUsuario } from "../../services/empresasService";
//import { useAuth } from "../../auth/useAuth";
//import Select from "../../components/Select/Select" //"react-select";
//import DataTable from "../../components/Tables/DataTable";
//import ButtonExcluir from "../../components/Button/ButtonExcluir"

// -------------


import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import SelectCustom from "../../components/Select/Select";
import DataTable from "../../components/Tables/DataTable";

import { useAuth } from "../../auth/useAuth";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { listarCertificadosPaginado } from "../../services/certificadosService";

export default function CertificadosList() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresasDoUsuario, setEmpresasDoUsuario] = useState([]);
  const [empresaFiltro, setEmpresaFiltro] = useState(null);

  // -----------------------------
  // Carrega empresas do usuário
  // -----------------------------
  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario(user.id).then((empresas) => {
      const opcoes = empresas.map((e) => ({
        value: e.empresa_id,
        label: e.razao_social,
      }));

      setEmpresasDoUsuario(opcoes);

      // Seleciona automaticamente a primeira empresa
      if (!empresaFiltro && opcoes.length > 0) {
        setEmpresaFiltro(opcoes[0]);
      }
    });
  }, [user]);

  // -----------------------------
  // Tabela de certificados
  // -----------------------------
  const columns = [
    { header: "Criado por", accessorKey: "criado_por_nome" },
    { header: "Nome do arquivo", accessorKey: "nome_arquivo" },
    {
      accessorKey: "validade_inicio",
      header: "Início da validade",
      cell: ({ row }) =>
        new Date(row.original.validade_inicio).toLocaleDateString("pt-BR"),
    },
    {
      accessorKey: "valido_ate",
      header: "Válido até",
      cell: ({ row }) =>
        new Date(row.original.valido_ate).toLocaleDateString("pt-BR"),
    },
    {
      accessorKey: "criado_em",
      header: "Criado em",
      cell: ({ row }) =>
        new Date(row.original.criado_em).toLocaleDateString("pt-BR"),
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <button
          className="btn btn-danger"
          onClick={() => navigate(`/certificados/excluir/${row.original.id}`)}
        >
          Excluir
        </button>
      ),
    },
  ];

  // Função que será passada para o DataTable
  const fetchCertificados = ({ page, limit, search, sort }) => {
    return listarCertificadosPaginado({
      empresa_id: empresaFiltro?.value,
      page,
      limit,
      search,
      sort,
    });
  };

  return (
    <div>
      <h1 className="titulo">Certificados</h1>

      {/* Select de empresas */}
      <div style={{ width: "280px", marginBottom: "15px" }}>
        <SelectCustom
          placeholder="Filtrar por empresa"
          value={empresaFiltro}
          onChange={(value) => setEmpresaFiltro(value)}
          options={empresasDoUsuario}
        />
      </div>

      <button
        className="btn btn-danger"
        onClick={() => navigate("/certificados/novo")}
      >
        + Novo Certificado
      </button>

      {/* 
        IMPORTANTE:
        key={empresaFiltro?.value} força o DataTable a recarregar quando trocar empresa
      */}
      {empresaFiltro && (
        <DataTable
          key={empresaFiltro.value}
          columns={columns}
          fetchData={fetchCertificados}
          limit={10}
        />
      )}
    </div>
  );
}
