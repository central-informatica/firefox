import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarCertificadosPaginado } from "../../services/certificadosService";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";
import Select from "react-select";
import DataTable from "../../components/Tables/DataTable";
import ButtonExcluir from "../../components/Button/ButtonExcluir"

const CertificadosList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresasDoUsuario, setEmpresasDoUsuario] = useState([]);
  const [empresaFiltro, setEmpresaFiltro] = useState(null);

  // Carregar empresas do usuário
  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario(user.id).then((empresas) => {
      const opcoes = empresas.map((e) => ({
        value: e.empresa_id,
        label: e.razao_social,
      }));

      setEmpresasDoUsuario(opcoes);

      if (!empresaFiltro && opcoes.length > 0) {
        setEmpresaFiltro(opcoes[0]);
      }
    });
  }, [user]);

  const columns = [
    { header: "Criado por", accessorKey: "criado_por_nome" },
    { header: "Nome do arquivo", accessorKey: "nome_arquivo" },
    { header: "Criado em", accessorKey: "criado_em" },
    {
      header: "Ações",
      cell: ({ row }) => (
        <ButtonExcluir
          onClick={() =>
            navigate(`/certificados/excluir/${row.original.id}`)
          }
        >
          Excluir
        </ButtonExcluir>
      ),
    },
  ];

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
      <h1 className="titulo">Meus certificados</h1>

      <div style={{ width: "280px", marginBottom: "15px" }}>
        <Select
          placeholder="Filtrar por empresa"
          value={empresaFiltro}
          onChange={(v) => setEmpresaFiltro(v)}
          options={empresasDoUsuario}
        />
      </div>

      <button
        className="btn btn-danger"
        onClick={() => navigate("/certificados/novo")}
      >
        + Novo Certificado
      </button>

      {empresaFiltro && (
        <DataTable
          columns={columns}
          fetchData={fetchCertificados}
          limit={10}
        />
      )}
    </div>
  );
};

export default CertificadosList;
