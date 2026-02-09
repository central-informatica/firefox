import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarEmpresasPaginado, toggleEmpresaAtivo } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";
import { toast } from "react-toastify";
import {
  FiPlus, FiEdit2, FiClock, FiBriefcase, FiTrendingUp, FiUserPlus
} from "react-icons/fi";
import DataTable from "../../components/Tables/DataTable";
import ConfirmModal from "../../components/ConfirmModal";
import VincularUsuarioModal from "../../components/VincularUsuarioModal";
import formatCNPJ from "../../utils/formatCNPJ"

const EmpresasList = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [totalEmpresas, setTotalEmpresas] = useState(0);
  const [reloadKey, setReloadKey] = useState(0);

  // Local status override (used during toggle before reload)
  const [statusOverride, setStatusOverride] = useState({});
  const [togglingId, setTogglingId] = useState(null);
  const [activeCount, setActiveCount] = useState(0);

  // Confirmation modal state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmData, setConfirmData] = useState(null); // { empresa_id, razao_social, currentStatus }

  // Vincular usuario modal state
  const [vincularModalOpen, setVincularModalOpen] = useState(false);
  const [selectedEmpresa, setSelectedEmpresa] = useState(null);

  if (loading || !user) {
    return null;
  }

  const handleToggleClick = (empresa) => {
    // Use override if exists, otherwise use the ativo from the empresa
    const currentStatus = statusOverride[empresa.empresa_id] !== undefined
      ? statusOverride[empresa.empresa_id]
      : (empresa.ativo !== false);
    setConfirmData({
      empresa_id: empresa.empresa_id,
      razao_social: empresa.razao_social,
      currentStatus,
    });
    setConfirmOpen(true);
  };

  const handleConfirmToggle = async () => {
    if (!confirmData) return;

    setTogglingId(confirmData.empresa_id);
    setConfirmOpen(false);

    try {
      const result = await toggleEmpresaAtivo(confirmData.empresa_id);
      toast.success(result.message);

      // Update local override
      setStatusOverride(prev => ({
        ...prev,
        [confirmData.empresa_id]: result.ativo,
      }));

      // Update active count
      setActiveCount(prev => result.ativo ? prev + 1 : prev - 1);

      setReloadKey(k => k + 1);
    } catch (err) {
      console.error(err);
      toast.error("Erro ao alterar status da empresa");
    } finally {
      setTogglingId(null);
      setConfirmData(null);
    }
  };

  const columns = [
    {
      header: "Nome",
      accessorKey: "razao_social",
      size: 300,
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
      header: "Fuso Horário",
      accessorKey: "timezone",
      size: 180,
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-neutral-400">
          <FiClock size={14} />
          {row.original.timezone || "America/Sao_Paulo"}
        </div>
      ),
    },
    {
      header: "Status",
      size: 120,
      cell: ({ row }) => {
        const empresa = row.original;
        const isToggling = togglingId === empresa.empresa_id;
        // Use override if exists, otherwise use ativo from empresa
        const isAtivo = statusOverride[empresa.empresa_id] !== undefined
          ? statusOverride[empresa.empresa_id]
          : (empresa.ativo !== false);

        return (
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleToggleClick(empresa)}
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
              {isAtivo ? 'Ativa' : 'Inativa'}
            </span>
          </div>
        );
      },
    },
    {
      header: "Ações",
      size: 180,
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setSelectedEmpresa(row.original);
              setVincularModalOpen(true);
            }}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg text-sm font-medium transition-all duration-200"
            title="Vincular usuário"
          >
            <FiUserPlus size={14} />
            Usuários
          </button>
          <button
            onClick={() => navigate(`/empresas/editar/${row.original.empresa_id}`)}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-xfire-orange/10 hover:bg-xfire-orange/20 text-xfire-orange rounded-lg text-sm font-medium transition-all duration-200"
          >
            <FiEdit2 size={14} />
            Editar
          </button>
        </div>
      ),
    },
  ];

  const fetchEmpresas = async ({ page, limit, search, sort }) => {
    const res = await listarEmpresasPaginado({ page, limit, search, sort });
    setTotalEmpresas(res.total);

    // Calculate active count from the data (ativo comes from the listing now)
    const active = res.data.filter(e => e.ativo !== false).length;
    setActiveCount(active);

    // Clear overrides on reload
    setStatusOverride({});

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
              <p className="text-2xl font-bold text-neutral-100">{activeCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <DataTable
        key={reloadKey}
        columns={columns}
        total={totalEmpresas}
        fetchData={fetchEmpresas}
        limit={10}
      />

      {/* Confirmation Modal */}
      <ConfirmModal
        open={confirmOpen}
        title={confirmData?.currentStatus ? "Desativar empresa?" : "Ativar empresa?"}
        description={
          confirmData?.currentStatus
            ? `Ao desativar a empresa "${confirmData?.razao_social}", todos os certificados vinculados a ela também serão desativados. Deseja continuar?`
            : `Ao ativar a empresa "${confirmData?.razao_social}", todos os certificados vinculados a ela também serão ativados. Deseja continuar?`
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

      {/* Vincular Usuario Modal */}
      <VincularUsuarioModal
        open={vincularModalOpen}
        empresaId={selectedEmpresa?.empresa_id}
        empresaNome={selectedEmpresa?.razao_social}
        onClose={() => {
          setVincularModalOpen(false);
          setSelectedEmpresa(null);
        }}
        onSuccess={() => {
          toast.success("Usuário vinculado à empresa com sucesso!");
          setReloadKey(k => k + 1);
        }}
      />
    </div>
  );
};

export default EmpresasList;
