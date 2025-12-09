import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import {
  listarCertificadosPaginado,
  excluir_certificado,
} from "../../services/certificadosService";
import { toast } from "react-toastify";

import SelectCustom from "../../components/Select/Select";
import DataTable from "../../components/Tables/DataTable";
import ButtonExluir from "../../components/Button/ButtonExcluir";

export default function CertificadosList() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresasDoUsuario, setEmpresasDoUsuario] = useState([]);
  const [empresaFiltro, setEmpresaFiltro] = useState(null);

  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario(user.id).then((empresas) => {
      const opcoes = empresas.map((e) => ({
        value: e.empresa_id,
        label: e.razao_social,
      }));

      setEmpresasDoUsuario(opcoes);

      if (opcoes.length > 0) {
        setEmpresaFiltro(opcoes[0]);
      }
    });
  }, [user]);

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
        <ButtonExluir
          onClick={async () => {
            if (!confirm("Deseja excluir este certificado?")) return;

            try {
              await excluir_certificado(row.original.id);
              toast.success("Certificado excluído com sucesso!");

              setReloadKey((old) => old + 1);
            } catch (err) {
              console.error(err);
              toast.error("Erro ao excluir certificado.");
            }
          }}
        >
          Excluir
        </ButtonExluir>
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

      {/* Recarrega ao trocar empresa ou ao excluir */}
      {empresaFiltro && (
        <DataTable
          key={empresaFiltro.value + "-" + reloadKey} // 👈 recarrega tabela
          columns={columns}
          fetchData={fetchCertificados}
          limit={10}
        />
      )}
    </div>
  );
}
