import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiPlus,
  FiFilter,
  FiBriefcase,
  FiEdit2,
  FiUsers,
  FiCheckCircle,
  FiLayers,
} from "react-icons/fi";

import DataTable from "../../components/Tables/DataTable";
import { getGrupos } from "../../services/gruposService";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectPlanoTrabalho from "../../components/Select/SelectPlanoTrabalho";

const GruposList = () => {
  const navigate = useNavigate();
  const [totalGrupos, setTotalGrupos] = useState(0);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [planoIdSelecionado, setPlanoId] = useState(null);
  
  const handlePlanoChange = (planoId) => {
    setPlanoId(planoId);
  }

  const handleEmpresaChange = (empresaId) => {
    setEmpresaSelecionada(empresaId);
    console.log("Empresa selecionada:", empresaSelecionada, empresaId);
  }

  const fetchGrupos = async (params) => {
    const res = await getGrupos({
      ...params,
      empresa_id: empresaSelecionada,
      plano_id: planoIdSelecionado,
    });

    setTotalGrupos(res.total);
    return res;
  };

  const columns = [
    {
      header: "Nome do Grupo",
      accessorKey: "nome",
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
            <FiUsers size={20} />
          </div>
          <div>
            <div className="font-semibold text-gray-800">
              {row.original.nome}
            </div>
            <div className="text-xs text-gray-500">
              {row.original.descricao
                ? row.original.descricao.substring(0, 50) +
                  (row.original.descricao.length > 50 ? "..." : "")
                : "Sem descrição"}
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
          onClick={() => navigate(`/grupos/editar/${row.original.grupo_id}`)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
        >
          <FiEdit2 size={16} />
          Editar
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Grupos
          </h1>
          <p className="text-gray-600">
            Gerencie os grupos de usuários do sistema
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/grupos/novo")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiPlus size={20} />
            Novo Grupo
          </button>

          <button
            onClick={() => navigate("/grupos/associar-usuarios")}
            className="inline-flex items-center gap-2 px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all duration-200"
          >
            <FiUsers size={18} />
            Associar Usuários
          </button>
        </div>
      </div>
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <FiLayers className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">
                Total de Grupos
              </p>
              <p className="text-2xl font-bold text-gray-800">
                {totalGrupos}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-50 rounded-xl">
              <FiCheckCircle className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">
                Grupos Ativos
              </p>
              <p className="text-2xl font-bold text-gray-800">
                {totalGrupos}
              </p>
            </div>
          </div>
        </div>
        {/* Filter Card */}
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 animate-slideUp">
        <div className="flex items-center gap-3 mb-3">
          <FiFilter className="text-emerald-600" size={18} />
          <h3 className="font-semibold text-gray-800">Filtros</h3>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          {/* Empresa */}
          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <FiBriefcase className="text-gray-400" size={14} />
              Empresa
            </label>

            <SelectEmpresa
              value={empresaSelecionada}
              onChange={handleEmpresaChange}
            />
          </div>

          {/* Plano de Trabalho */}
          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <FiLayers className="text-gray-400" size={14} />
              Plano de Trabalho
            </label>

            <SelectPlanoTrabalho
          empresaId={empresaSelecionada}
          value={planoIdSelecionado}
          onChange={handlePlanoChange}
          isDisabled={!empresaSelecionada}
          />
          </div>
        </div>
      </div>
      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <DataTable 
          key={`${empresaSelecionada ?? "all"}-${planoIdSelecionado ?? "all"}`}
          columns={columns} 
          fetchData={fetchGrupos} limit={10} 
        />
      </div>
    </div>
  );
};

export default GruposList;
