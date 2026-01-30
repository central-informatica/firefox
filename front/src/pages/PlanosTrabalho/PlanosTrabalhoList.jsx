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
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-700 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
            <FiFlag size={20} />
          </div>
          <div>
            <div className="font-semibold text-neutral-100">{row.original.nome}</div>
            <div className="text-xs text-neutral-500">
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
        <span className="text-sm text-neutral-400 line-clamp-2">
          {row.original.descricao || "-"}
        </span>
      ),
    },
    {
      header: "Status",
      cell: () => (
        <span className="badge-permitido">
          <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
          Ativo
        </span>
      ),
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <button
          onClick={() => navigate(`/planos/editar/${row.original.plano_id}`)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-xfire-orange/20 hover:bg-xfire-orange/30 text-xfire-orange rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
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
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2">Planos de Trabalho</h1>
          <p className="text-neutral-400">Organize e gerencie os planos de trabalho da empresa</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/planos/associacoes")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-700 hover:from-purple-600 hover:to-purple-800 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiUsers size={20} />
            Gerenciar Associações
          </button>
          <button
            onClick={() => navigate("/planos/novo")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiPlus size={20} />
            Novo Plano de Trabalho
          </button>
        </div>
      </div>

      {/* Filtro de Empresa */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5">
        <h3 className="font-semibold text-neutral-100 mb-4 flex items-center gap-2">
          <FiFilter className="text-purple-400" size={18} />
          Filtros
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label className="text-sm font-medium text-neutral-400 mb-2">Empresa</Label>
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
        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-900/30 rounded-xl">
              <FiFlag className="text-purple-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Total de Planos</p>
              <p className="text-2xl font-bold text-neutral-100">{totalPlanos}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-900/30 rounded-xl">
              <FiCheckCircle className="text-green-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Planos Ativos</p>
              <p className="text-2xl font-bold text-neutral-100">{totalPlanos}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-900/30 rounded-xl">
              <FiUsers className="text-blue-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Grupos Ativos</p>
              <p className="text-2xl font-bold text-neutral-100">{totalGrupos}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
        <DataTable
          key={tableKey}
          columns={columns}
          fetchData={fetchPlanos}
          limit={10}
        />
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-800/50 rounded-card p-5 flex items-start gap-4">
        <div className="p-3 bg-dark-secondary rounded-xl shadow-sm">
          <FiCalendar className="text-purple-400" size={24} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-neutral-100 mb-1 flex items-center gap-2">
            <span>Dica:</span>
            <span className="text-purple-400">Organize melhor seus recursos</span>
          </h3>
          <p className="text-sm text-neutral-400">
            Os planos de trabalho permitem agrupar usuários e certificados, facilitando a gestão de permissões e o controle de acesso baseado em horários específicos.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PlanosTrabalhoList;
