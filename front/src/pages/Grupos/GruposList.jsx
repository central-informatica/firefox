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
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
            <FiUsers size={20} />
          </div>
          <div>
            <div className="font-semibold text-neutral-100">
              {row.original.nome}
            </div>
            <div className="text-xs text-neutral-500">
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
          onClick={() => navigate(`/grupos/editar/${row.original.grupo_id}`)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-xfire-orange/20 hover:bg-xfire-orange/30 text-xfire-orange rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
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
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2">
            Grupos
          </h1>
          <p className="text-neutral-400">
            Gerencie os grupos de usuários do sistema
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/grupos/novo")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiPlus size={20} />
            Novo Grupo
          </button>

          <button
            onClick={() => navigate("/grupos/associar-usuarios")}
            className="inline-flex items-center gap-2 px-4 py-3 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 font-semibold rounded-xl transition-all duration-200"
          >
            <FiUsers size={18} />
            Associar Usuários
          </button>
        </div>
      </div>
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-900/30 rounded-xl">
              <FiLayers className="text-blue-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">
                Total de Grupos
              </p>
              <p className="text-2xl font-bold text-neutral-100">
                {totalGrupos}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-900/30 rounded-xl">
              <FiCheckCircle className="text-green-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">
                Grupos Ativos
              </p>
              <p className="text-2xl font-bold text-neutral-100">
                {totalGrupos}
              </p>
            </div>
          </div>
        </div>
        {/* Filter Card */}
      </div>
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5 animate-slideUp">
        <div className="flex items-center gap-3 mb-3">
          <FiFilter className="text-xfire-orange" size={18} />
          <h3 className="font-semibold text-neutral-100">Filtros</h3>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          {/* Empresa */}
          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
              <FiBriefcase className="text-neutral-500" size={14} />
              Empresa
            </label>

            <SelectEmpresa
              value={empresaSelecionada}
              onChange={handleEmpresaChange}
            />
          </div>

          {/* Plano de Trabalho */}
          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
              <FiLayers className="text-neutral-500" size={14} />
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
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
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
