import { useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  FiPlus, FiEdit2, FiTrash2, FiUsers, FiUserCheck, FiShield, FiAlertCircle, FiMail, FiUserPlus
} from "react-icons/fi";
import { deletarUsuario, listarUsuariosPaginado } from "../../services/usuariosService";
import { toast } from "react-toastify";

import SelectEmpresa from "../../components/Select/SelectEmpresa";
import DataTable from "../../components/Tables/DataTable";
import VincularUsuarioModal from "../../components/VincularUsuarioModal";

const UsuariosList = () => {
  const navigate = useNavigate();
  const [empresaId, setEmpresaSelecionada] = useState(null);
  const [empresaNome, setEmpresaNome] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [totalUsuariosAtivos, setTotalUserAtivos] = useState(0);
  const [totalUsuarios, setTotalUsuarios] = useState(0);
  const [totalUsuariosAdmin, setTotalUsuariosAdmin] = useState(0);

  // Vincular usuario modal state
  const [vincularModalOpen, setVincularModalOpen] = useState(false);


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
      size: 350,
      cell: ({ row }) => {
        const u = row.original;
        return (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-full flex items-center justify-center text-white font-bold text-sm">
              {u.nome?.charAt(0).toUpperCase() || "U"}
            </div>
            <div>
              <div className="font-semibold text-neutral-100">{u.nome}</div>
            </div>
          </div>
        );
      },
    },
    {
      header: "Email",
      accessorKey: "email",
      size: 250,
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-neutral-400">
          <FiMail size={14} className="text-neutral-500" />
          {row.original.email}
        </div>
      ),
    },
    {
      header: "Nível",
      accessorKey: "nivel",
      size: 120,
      cell: ({ row }) => getNivelBadge(row.original.nivel),
    },
    {
      header: "Status",
      size: 100,
      cell: () => (
        <span className="badge-permitido">
          <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
          Ativo
        </span>
      ),
    },
    {
      header: "Ações",
      size: 200,
      cell: ({ row }) => {
        const u = row.original;
        return (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={()=> handleOnClickEdit(u.id)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-xfire-orange/20 hover:bg-xfire-orange/30 text-xfire-orange rounded-lg text-sm font-medium"
            >
              <FiEdit2 size={14} />
              Editar
            </button>
            <button
              onClick={() => handleDelete(u.id, u.nome)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg text-sm font-medium"
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
      ADMINISTRADOR: { color: "bg-purple-900/30 text-purple-400", icon: <FiShield size={12} />, label: "Admin" },
      USUARIO: { color: "bg-blue-900/30 text-blue-400", icon: <FiUsers size={12} />, label: "Usuário" },
      COMUM: { color: "bg-blue-900/30 text-blue-400", icon: <FiUsers size={12} />, label: "Usuário" }, // backward compat
      MODERADOR: { color: "bg-orange-900/30 text-orange-400", icon: <FiUserCheck size={12} />, label: "Moderador" },
    };

    // Convert nivel to string and uppercase safely
    const nivelKey = String(nivel || 'USUARIO').toUpperCase();
    const badge = badges[nivelKey] || badges.USUARIO;

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
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2">Usuários</h1>
          <p className="text-neutral-400">Gerencie os usuários cadastrados no sistema</p>
        </div>

        <div className="flex items-center gap-3">
          {empresaId && (
            <button
              onClick={() => setVincularModalOpen(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
            >
              <FiUserPlus size={20} />
              Vincular Usuário
            </button>
          )}
          <button
            onClick={() => navigate("/usuarios/novo")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold rounded-xl shadow-lg shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
          >
            <FiPlus size={20} />
            Novo Usuário
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-900/30 rounded-xl">
              <FiUsers className="text-blue-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Total de Usuários</p>
              <p className="text-2xl font-bold text-neutral-100">{totalUsuarios}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-900/30 rounded-xl">
              <FiUserCheck className="text-green-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Usuários Ativos</p>
              <p className="text-2xl font-bold text-neutral-100">{totalUsuariosAtivos}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-900/30 rounded-xl">
              <FiShield className="text-purple-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Administradores</p>
              <p className="text-2xl font-bold text-neutral-100">
                {totalUsuariosAdmin}
              </p>
            </div>
          </div>
        </div>
      </div>
      <SelectEmpresa
        value={empresaId}
        onChange={(empresa) => {
          setEmpresaSelecionada(empresa?.value || empresa);
          setEmpresaNome(empresa?.label || '');
          setRefreshKey((k) => k + 1);
        }}
      />

      {/* Table */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
        {empresaId ? (
          <DataTable
            key={`${empresaId}-${refreshKey}`}
            columns={columns}
            fetchData={fetchUsuarios}
            limit={10}
          />
        ) : (
          <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-12 text-center text-neutral-500">
            Selecione uma empresa para visualizar os usuários
          </div>
        )}
      </div>


      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-800/50 rounded-card p-5 flex items-start gap-4">
        <div className="p-3 bg-dark-secondary rounded-xl shadow-sm">
          <FiAlertCircle className="text-blue-400" size={24} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-neutral-100 mb-1 flex items-center gap-2">
            <span>Importante:</span>
            <span className="text-blue-400">Gerenciamento de Usuários</span>
          </h3>
          <p className="text-sm text-neutral-400">
            Os usuários podem ter diferentes níveis de acesso: Administrador (controle total) ou Usuário (acesso básico). Administradores podem gerenciar empresas, certificados e permissões.
          </p>
        </div>
      </div>

      {/* Vincular Usuario Modal */}
      <VincularUsuarioModal
        open={vincularModalOpen}
        empresaId={empresaId}
        empresaNome={empresaNome}
        onClose={() => setVincularModalOpen(false)}
        onSuccess={() => {
          toast.success("Usuário vinculado à empresa com sucesso!");
          setRefreshKey(k => k + 1);
        }}
      />
    </div>
  );
};

export default UsuariosList;
