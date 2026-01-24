import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiPlus, FiEdit2, FiFlag, FiCheckCircle, FiUsers, FiCalendar, FiFilter
} from "react-icons/fi";
import DataTable from "../../components/Tables/DataTable";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import Label from "../../components/Label/Label";
import { listarPlanosTrabalho } from "../../services/planosTrabalhoService";

const PlanosTrabalhoList = () => {
  const navigate = useNavigate();
  const [totalPlanos, setTotalPlanos] = useState(0);
  const [totalGrupos, setTotalGrupos] = useState(0);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [tableKey, setTableKey] = useState(0);

  const columns = [
    {
      header: "Nome do Plano",
      accessorKey: "nome",
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
            <FiFlag size={20} />
          </div>
          <div>
            <div className="font-semibold text-gray-800">{row.original.nome}</div>
            <div className="text-xs text-gray-500">
              {row.original.descricao
                ? row.original.descricao.substring(0, 50) + (row.original.descricao.length > 50 ? '...' : '')
                : 'Sem descrição'}
            </div>
          </div>
        </div>
      ),
    },
    {
      header: "Descrição",
      accessorKey: "descricao",
      cell: ({ row }) => (
        <span className="text-sm text-gray-600 line-clamp-2">
          {row.original.descricao || "-"}
        </span>
      ),
    },
    {
      header: "Status",
      cell: () => (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
          Ativo
        </span>
      ),
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <button
          onClick={() => navigate(`/planos/editar/${row.original.plano_id}`)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
        >
          <FiEdit2 size={16} />
          Editar
        </button>
      ),
    },
  ];

  const handleEmpresaChange = (value) => {
    setEmpresaSelecionada(value);
    setTableKey(prev => prev + 1);
  };

  const fetchPlanos = useCallback(async (params) => {
    const res = await listarPlanosTrabalho({
      ...params,
      empresa_id: empresaSelecionada
    });
    setTotalPlanos(res.total);
    return res;
  }, [empresaSelecionada]);


  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Planos de Trabalho</h1>
          <p className="text-gray-600">Organize e gerencie os planos de trabalho da empresa</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/planos/associacoes")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiUsers size={20} />
            Gerenciar Associações
          </button>
          <button
            onClick={() => navigate("/planos/novo")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiPlus size={20} />
            Novo Plano de Trabalho
          </button>
        </div>
      </div>

      {/* Filtro de Empresa */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <FiFilter className="text-purple-600" size={18} />
          Filtros
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label className="text-sm font-medium text-gray-700 mb-2">Empresa</Label>
            <SelectEmpresa
              placeholder="Todas as empresas"
              value={empresaSelecionada}
              onChange={handleEmpresaChange}
            />
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-xl">
              <FiFlag className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Total de Planos</p>
              <p className="text-2xl font-bold text-gray-800">{totalPlanos}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-50 rounded-xl">
              <FiCheckCircle className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Planos Ativos</p>
              <p className="text-2xl font-bold text-gray-800">{totalPlanos}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <FiUsers className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Grupos Ativos</p>
              <p className="text-2xl font-bold text-gray-800">{totalGrupos}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <DataTable
          key={tableKey}
          columns={columns}
          fetchData={fetchPlanos}
          limit={10}
        />
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-100 rounded-xl p-5 flex items-start gap-4">
        <div className="p-3 bg-white rounded-xl shadow-sm">
          <FiCalendar className="text-purple-600" size={24} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
            <span>Dica:</span>
            <span className="text-purple-600">Organize melhor seus recursos</span>
          </h3>
          <p className="text-sm text-gray-700">
            Os planos de trabalho permitem agrupar usuários e certificados, facilitando a gestão de permissões e o controle de acesso baseado em horários específicos.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PlanosTrabalhoList;
