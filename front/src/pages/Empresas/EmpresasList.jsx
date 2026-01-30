import {useState} from "react";
import { useNavigate } from "react-router-dom";
import { listarEmpresasPaginado } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";
import {
  FiPlus, FiEdit2, FiClock, FiBriefcase, FiTrendingUp
} from "react-icons/fi";
import DataTable from "../../components/Tables/DataTable";
import formatCNPJ from "../../utils/formatCNPJ"

const EmpresasList = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [totalEmpresas, setTotalEmpresas] = useState(0);

  if (loading || !user) {
    return null;
  }

  const columns = [
    {
      header: "Nome",
      accessorKey: "razao_social",
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
            {row.original.razao_social?.charAt(0).toUpperCase() || "E"}
          </div>
          <div>
            <div className="font-semibold text-neutral-100">{row.original.razao_social}</div>
            <div className="text-xs text-neutral-500">
              {formatCNPJ(row.original.cnpj) || "CNPJ nao informado"}
            </div>
          </div>
        </div>
      ),
    },
    {
      header: "CNPJ",
      accessorKey: "cnpj",
      cell: ({ row }) => (
        <span className="text-sm text-neutral-400 font-mono">
          {formatCNPJ(row.original.cnpj) || "-"}
        </span>
      ),
    },
    {
      header: "Fuso Horario",
      accessorKey: "timezone",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-neutral-400">
          <FiClock size={14} />
          {row.original.timezone || "America/Sao_Paulo"}
        </div>
      ),
    },
    {
      header: "Status",
      cell: () => (
        <span className="badge-permitido">
          <div className="w-1.5 h-1.5 bg-status-permitido rounded-full"></div>
          Ativa
        </span>
      ),
    },
    {
      header: "Acoes",
      cell: ({ row }) => (
        <button
          onClick={() => navigate(`/empresas/editar/${row.original.empresa_id}`)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-xfire-orange/10 hover:bg-xfire-orange/20 text-xfire-orange rounded-lg text-sm font-medium transition-all duration-200"
        >
          <FiEdit2 size={16} />
          Editar
        </button>
      ),
    },
  ];

  const fetchEmpresas = async ({ page, limit, search, sort }) => {
    const res = await listarEmpresasPaginado({ page, limit, search, sort });
    setTotalEmpresas(res.total);
    return res;
  };

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-neutral-100 mb-2 font-montserrat">Empresas</h1>
          <p className="text-neutral-400">Gerencie as empresas cadastradas no sistema</p>
        </div>

        <button
          onClick={() => navigate("/empresas/nova")}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0"
        >
          <FiPlus size={20} />
          Nova Empresa
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dark-secondary rounded-card p-5 border border-neutral-900">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-status-monitorado/10 rounded-xl">
              <FiBriefcase className="text-status-monitorado" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Total de Empresas</p>
              <p className="text-2xl font-bold text-neutral-100">{totalEmpresas}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 border border-neutral-900">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-status-permitido/10 rounded-xl">
              <FiTrendingUp className="text-status-permitido" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Empresas Ativas</p>
              <p className="text-2xl font-bold text-neutral-100">{totalEmpresas}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        total={totalEmpresas}
        fetchData={fetchEmpresas}
        limit={10}
      />
    </div>
  );
};

export default EmpresasList;
