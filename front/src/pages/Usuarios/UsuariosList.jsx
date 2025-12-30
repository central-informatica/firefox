import { useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  FiPlus, FiEdit2, FiTrash2, FiUsers, FiUserCheck, FiShield, FiAlertCircle, FiMail
} from "react-icons/fi";
import { deletarUsuario, listarUsuariosPaginado } from "../../services/usuariosService";

import SelectEmpresa from "../../components/Select/SelectEmpresa";
import DataTable from "../../components/Tables/DataTable";

const UsuariosList = () => {
  const navigate = useNavigate();
  const [empresaId, setEmpresaSelecionada] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [totalUsuariosAtivos, setTotalUserAtivos] = useState(0);
  const [totalUsuarios, setTotalUsuarios] = useState(0);
  const [totalUsuariosAdmin, setTotalUsuariosAdmin] = useState(0);


  const fetchUsuarios = async ({ page, limit, search, sort }) => {
    if (!empresaId) return { rows: [], total: 0 , total_adm: 0};
    const res = await listarUsuariosPaginado({empresa_id: empresaId,page,limit,search,sort,});
    setTotalUsuarios(res.total);
    setTotalUserAtivos(res.total);
    setTotalUsuariosAdmin(res.total_adm);
    return res;
  };

  const handleOnClickEdit = (usuario_id)=>{
    console.log(usuario_id)
    navigate(`/usuarios/editar/${usuario_id}`, {
        state: {
          empresa_id: empresaId, // empresa selecionada na lista
        },
    });
  }

  const handleDelete = async (usuario_id, nome) => {
    if (!confirm(`Deseja realmente excluir o usuário "${nome}"?\n\nEsta ação não pode ser desfeita.`)) return;

    try {
      await deletarUsuario(empresaId, usuario_id);
    } catch (error) {
      console.error(error);
      alert("Erro ao excluir usuário");
    }
  };

  const columns = [
  {
      header: "Usuário",
      accessorKey: "nome",
      cell: ({ row }) => {
        const u = row.original;
        return (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              {u.nome?.charAt(0).toUpperCase() || "U"}
            </div>
            <div>
              <div className="font-semibold text-gray-800">{u.nome}</div>
            </div>
          </div>
        );
      },
    },
    {
      header: "Email",
      accessorKey: "email",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FiMail size={14} className="text-gray-400" />
          {row.original.email}
        </div>
      ),
    },
    {
      header: "Nível",
      accessorKey: "nivel",
      cell: ({ row }) => getNivelBadge(row.original.nivel),
    },
    {
      header: "Status",
      cell: () => (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium">
          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
          Ativo
        </span>
      ),
    },
    {
      header: "Ações",
      cell: ({ row }) => {
        const u = row.original;
        return (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={()=> handleOnClickEdit(u.usuario_id)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg text-sm font-medium"
            >
              <FiEdit2 size={14} />
              Editar
            </button>
            <button
              onClick={() => handleDelete(u.id, u.nome)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg text-sm font-medium"
            >
              <FiTrash2 size={14} />
              Excluir
            </button>
          </div>
        );
      },
    },
  ];

  const getNivelBadge = (nivel) => {
    const badges = {
      ADMINISTRADOR: { color: "bg-purple-50 text-purple-700", icon: <FiShield size={12} />, label: "Admin" },
      COMUM: { color: "bg-blue-50 text-blue-700", icon: <FiUsers size={12} />, label: "Usuário" },
      MODERADOR: { color: "bg-orange-50 text-orange-700", icon: <FiUserCheck size={12} />, label: "Moderador" },
    };

    // Convert nivel to string and uppercase safely
    const nivelKey = String(nivel || 'COMUM').toUpperCase();
    const badge = badges[nivelKey] || badges.COMUM;

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 ${badge.color} rounded-full text-xs font-medium`}>
        {badge.icon}
        {badge.label}
      </span>
    );
  };

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Usuários</h1>
          <p className="text-gray-600">Gerencie os usuários cadastrados no sistema</p>
        </div>

        <button
          onClick={() => navigate("/usuarios/novo")}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
        >
          <FiPlus size={20} />
          Novo Usuário
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <FiUsers className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Total de Usuários</p>
              <p className="text-2xl font-bold text-gray-800">{totalUsuarios}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-50 rounded-xl">
              <FiUserCheck className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Usuários Ativos</p>
              <p className="text-2xl font-bold text-gray-800">{totalUsuariosAtivos}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-xl">
              <FiShield className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Administradores</p>
              <p className="text-2xl font-bold text-gray-800">
                {totalUsuariosAdmin}
              </p>
            </div>
          </div>
        </div>
      </div>
      <SelectEmpresa
        value={empresaId}
        onChange={(empresa) => {
          setEmpresaSelecionada(empresa);
          setRefreshKey((k) => k + 1);
        }}
      />

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {empresaId ? (
          <DataTable
            key={`${empresaId}-${refreshKey}`}
            columns={columns}
            fetchData={fetchUsuarios}
            limit={10}
          />
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center text-gray-500">
            Selecione uma empresa para visualizar os usuários
          </div>
        )}
      </div>


      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-100 rounded-xl p-5 flex items-start gap-4">
        <div className="p-3 bg-white rounded-xl shadow-sm">
          <FiAlertCircle className="text-blue-600" size={24} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
            <span>Importante:</span>
            <span className="text-blue-600">Gerenciamento de Usuários</span>
          </h3>
          <p className="text-sm text-gray-700">
            Os usuários podem ter diferentes níveis de acesso: Administrador (controle total), Moderador (gerenciamento limitado) ou Usuário (acesso básico). Administradores podem gerenciar empresas, certificados e permissões.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UsuariosList;
