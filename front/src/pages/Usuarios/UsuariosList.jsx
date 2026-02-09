import { useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  FiPlus, FiEdit2, FiTrash2, FiUsers, FiUserCheck, FiShield, FiAlertCircle, FiMail, FiUserPlus
} from "react-icons/fi";
import { deletarUsuario, listarUsuariosPaginado, toggleUsuarioAtivo } from "../../services/usuariosService";
import { toast } from "react-toastify";

import SelectEmpresa from "../../components/Select/SelectEmpresa";
import DataTable from "../../components/Tables/DataTable";
import VincularUsuarioModal from "../../components/VincularUsuarioModal";
import ConfirmModal from "../../components/ConfirmModal";

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

  // Toggle state management
  const [statusOverride, setStatusOverride] = useState({});
  const [togglingId, setTogglingId] = useState(null);

  // Confirmation modal state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmData, setConfirmData] = useState(null); // { user_id, nome, currentStatus }


  const fetchUsuarios = async ({ page, limit, search, sort }) => {
    if (!empresaId) return { rows: [], total: 0 , total_adm: 0};
    const res = await listarUsuariosPaginado({empresa_id: empresaId,page,limit,search,sort,});
    setTotalUsuarios(res.total);
    setTotalUserAtivos(res.total);
    setTotalUsuariosAdmin(res.total_adm);

    // Clear status overrides on reload
    setStatusOverride({});

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

  const handleToggleClick = (usuario) => {
    // Use override if exists, otherwise use is_active from the user
    const currentStatus = statusOverride[usuario.id] !== undefined
      ? statusOverride[usuario.id]
      : (usuario.is_active !== false);

    setConfirmData({
      user_id: usuario.id,
      nome: usuario.nome,
      currentStatus,
    });
    setConfirmOpen(true);
  };

  const handleConfirmToggle = async () => {
    if (!confirmData) return;

    setTogglingId(confirmData.user_id);
    setConfirmOpen(false);

    try {
      const result = await toggleUsuarioAtivo(confirmData.user_id);
      toast.success(result.message);

      // Update local override
      setStatusOverride(prev => ({
        ...prev,
        [confirmData.user_id]: result.is_active,
      }));

      setRefreshKey(k => k + 1);
    } catch (err) {
      console.error(err);
      toast.error("Erro ao alterar status do usuário");
    } finally {
      setTogglingId(null);
      setConfirmData(null);
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
      size: 140,
      cell: ({ row }) => {
        const u = row.original;
        const isToggling = togglingId === u.id;
        // Use override if exists, otherwise use is_active from user
        const isAtivo = statusOverride[u.id] !== undefined
          ? statusOverride[u.id]
          : (u.is_active !== false);

        return (
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleToggleClick(u)}
              disabled={isToggling}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-xfire-orange focus:ring-offset-2 focus:ring-offset-dark-primary ${
                isAtivo ? 'bg-green-600' : 'bg-neutral-600'
              } ${isToggling ? 'opacity-50 cursor-wait' : 'cursor-pointer'}`}
              title={isAtivo ? 'Clique para desativar' : 'Clique para ativar'}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                  isAtivo ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-xs font-medium ${isAtivo ? 'text-green-400' : 'text-neutral-500'}`}>
              {isAtivo ? 'Ativo' : 'Inativo'}
            </span>
          </div>
        );
      },
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

      {/* Confirmation Modal */}
      <ConfirmModal
        open={confirmOpen}
        title={confirmData?.currentStatus ? "Desativar usuário?" : "Ativar usuário?"}
        description={
          confirmData?.currentStatus
            ? `Ao desativar o usuário "${confirmData?.nome}", ele não poderá mais fazer login no sistema. Deseja continuar?`
            : `Ao ativar o usuário "${confirmData?.nome}", ele poderá fazer login no sistema novamente. Deseja continuar?`
        }
        confirmText={confirmData?.currentStatus ? "Desativar" : "Ativar"}
        cancelText="Cancelar"
        onConfirm={handleConfirmToggle}
        onCancel={() => {
          setConfirmOpen(false);
          setConfirmData(null);
        }}
        variant={confirmData?.currentStatus ? "danger" : "primary"}
      />
    </div>
  );
};

export default UsuariosList;
