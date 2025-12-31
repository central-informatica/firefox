import {useState} from "react";
import { useNavigate } from "react-router-dom";
import { listarEmpresasPaginado } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";
import {
  FiPlus, FiEdit2, FiClock, FiBriefcase, FiTrendingUp, FiMapPin
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
          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
            {row.original.razao_social?.charAt(0).toUpperCase() || "E"}
          </div>
          <div>
            <div className="font-semibold text-gray-800">{row.original.razao_social}</div>
            <div className="text-xs text-gray-500">
              {formatCNPJ(row.original.cnpj) || "CNPJ não informado"}
            </div>
          </div>
        </div>
      ),
    },
    {
      header: "CNPJ",
      accessorKey: "cnpj",
      cell: ({ row }) => (
        <span className="text-sm text-gray-600 font-mono">
          {formatCNPJ(row.original.cnpj) || "-"}
        </span>
      ),
    },
    {
      header: "Fuso Horário",
      accessorKey: "timezone",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FiClock size={14} />
          {row.original.timezone || "America/Sao_Paulo"}
        </div>
      ),
    },
    {
      header: "Status",
      cell: () => (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
          Ativa
        </span>
      ),
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <button
          onClick={() => navigate(`/empresas/editar/${row.original.empresa_id}`)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium transition-all duration-200"
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
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Empresas</h1>
          <p className="text-gray-600">Gerencie as empresas cadastradas no sistema</p>
        </div>

        <button
          onClick={() => navigate("/empresas/nova")}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0"
        >
          <FiPlus size={20} />
          Nova Empresa
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <FiBriefcase className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Total de Empresas</p>
              <p className="text-2xl font-bold text-gray-800">{totalEmpresas}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-50 rounded-xl">
              <FiTrendingUp className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Empresas Ativas</p>
              <p className="text-2xl font-bold text-gray-800">{totalEmpresas}</p>
            </div>
          </div>
        </div>

        {/* <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-xl">
              <FiMapPin className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Localizações</p>
              <p className="text-2xl font-bold text-gray-800">8</p>
            </div>
          </div>
        </div> */}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <DataTable
          columns={columns}
          total={totalEmpresas}
          fetchData={fetchEmpresas}
          limit={10}
        />
      </div>
    </div>
  );
};

export default EmpresasList;
