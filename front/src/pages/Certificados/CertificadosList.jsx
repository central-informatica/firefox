import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
// REMOVIDO: getEmpresasDoUsuario (SelectEmpresa é autônomo)
// import { getEmpresasDoUsuario } from "../../services/empresasService";

import {
  listarCertificadosPaginado,
  excluir_certificado,
} from "../../services/certificadosService";
import { toast } from "react-toastify";
import {
  FiShield,
  FiPlus,
  FiDownload,
  FiTrash2,
  FiCalendar,
  FiUser,
  FiFile,
  FiClock,
  FiAlertCircle,
  FiCheckCircle,
  FiBriefcase,
  FiFilter,
  FiUsers,
} from "react-icons/fi";

//import SelectCustom from "../../components/Select/SelectEmpresa";
import DataTable from "../../components/Tables/DataTable";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectGrupo from "../../components/Select/SelectGrupo";
import ConfirmModal from "../../components/ConfirmModal";

export default function CertificadosList() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresaId, setEmpresaId] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [stats, setStats] = useState({ total: 0, ativos: 0, expirando: 0, expirados: 0, });
  const [selectedGroup, setSelectedGroup] = useState(null);

  // Confirmation modal state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmData, setConfirmData] = useState(null); // { id, nome }
  const [isDeleting, setIsDeleting] = useState(false);

  const getCertificateStatus = (validoAte) => {
    const hoje = new Date();
    const dataValidade = new Date(validoAte);
    const diasRestantes = Math.ceil((dataValidade - hoje) / (1000 * 60 * 60 * 24));

    if (diasRestantes < 0) {
      return { status: "expirado", label: "Expirado", color: "red", dias: diasRestantes };
    } else if (diasRestantes <= 30) {
      return { status: "expirando", label: "Expirando", color: "orange", dias: diasRestantes };
    } else {
      return { status: "ativo", label: "Ativo", color: "green", dias: diasRestantes };
    }
  };

  useEffect(() => {
  if (!empresaId) {
    setStats({ total: 0, ativos: 0, expirando: 0, expirados: 0});
    return;
  }

  async function carregarStats() {
    try {
      const params = {
        empresa_id: empresaId,
        page: 1,
        limit: 1000, // suficiente para stats
        search: "",
        sort: "",
      };

      if (selectedGroup && selectedGroup.grupo_id) params.grupo_id = selectedGroup.grupo_id;

      const res = await listarCertificadosPaginado(params);

      const certificados = res.data || [];

      let _ativos = 0;
      let _expirando = 0;
      let _expirados = 0;

      certificados.forEach((c) => {
        const statusInfo = getCertificateStatus(c.valido_ate);

        if (statusInfo.status === "ativo") _ativos++;
        else if (statusInfo.status === "expirando") _expirando++;
        else if (statusInfo.status === "expirado") _expirados++;
      });

      setStats({
        total: certificados.length,
        ativos: _ativos,
        expirando: _expirando,
        expirados: _expirados,
      });

      console.log("Contadores:", { _ativos, _expirando, _expirados });

    } catch (err) {
      console.error("Erro ao carregar estatísticas:", err);
      setStats({ total: 0, ativos: 0, expirando: 0, expirados: 0 });
    }
  }

  carregarStats();
}, [empresaId, reloadKey, selectedGroup]);


  const columns = [
    {
      header: "Certificado",
      accessorKey: "nome_arquivo",
      cell: ({ row }) => {
        const cert = row.original;
        const statusInfo = getCertificateStatus(cert.valido_ate);

        return (
          <div className="flex items-center gap-3 py-2">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl flex items-center justify-center shadow-sm">
                <FiFile className="text-emerald-600" size={20} />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-gray-800 truncate">{cert.nome_arquivo || "Certificado.pfx"}</div>
              <div className="flex items-center gap-2 mt-1">
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
                  ${statusInfo.status === 'ativo' ? 'bg-green-50 text-green-700' : ''}
                  ${statusInfo.status === 'expirando' ? 'bg-orange-50 text-orange-700' : ''}
                  ${statusInfo.status === 'expirado' ? 'bg-red-50 text-red-700' : ''}
                `}>
                  {statusInfo.status === 'ativo' && <FiCheckCircle size={10} />}
                  {statusInfo.status !== 'ativo' && <FiAlertCircle size={10} />}
                  {statusInfo.label}
                </span>
              </div>
            </div>
          </div>
        );
      },
    },
    {
      header: "Criado por",
      accessorKey: "criado_por_nome",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-gray-700">
          <FiUser className="text-gray-400" size={14} />
          <span>{row.original.criado_por_nome || "Desconhecido"}</span>
        </div>
      ),
    },
    {
      accessorKey: "validade_inicio",
      header: "Início",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FiCalendar className="text-gray-400" size={14} />
          {new Date(row.original.validade_inicio).toLocaleDateString("pt-BR")}
        </div>
      ),
    },
    {
      accessorKey: "valido_ate",
      header: "Válido até",
      cell: ({ row }) => {
        const statusInfo = getCertificateStatus(row.original.valido_ate);
        return (
          <div>
            <div className="flex items-center gap-2 text-sm text-gray-700 font-medium">
              <FiClock className="text-gray-400" size={14} />
              {new Date(row.original.valido_ate).toLocaleDateString("pt-BR")}
            </div>
            {statusInfo.dias > 0 && statusInfo.dias <= 30 && (
              <div className="text-xs text-orange-600 mt-1">
                {statusInfo.dias} {statusInfo.dias === 1 ? 'dia' : 'dias'} restantes
              </div>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: "criado_em",
      header: "Cadastrado em",
      cell: ({ row }) => (
        <div className="text-sm text-gray-600">
          {new Date(row.original.criado_em).toLocaleDateString("pt-BR")}
        </div>
      ),
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setConfirmData({ id: row.original.certificado_id, nome: row.original.nome_arquivo });
              setConfirmOpen(true);
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer group"
            title="Excluir certificado"
          >
            <FiTrash2 size={14} className="group-hover:scale-110 transition-transform" />
            Excluir
          </button>
        </div>
      ),
    },
  ];

  const fetchCertificados = ({ page, limit, search, sort }) => {
    // 🔧 Correção: usar empresaId e não empresaFiltro
    const params = {
      empresa_id: empresaId,
      page,
      limit,
      search,
      sort,
    };

    if (selectedGroup && selectedGroup.grupo_id) params.grupo_id = selectedGroup.grupo_id;

    return listarCertificadosPaginado(params);
  };

  const handleConfirmDelete = async () => {
    if (!confirmData) return;
    setIsDeleting(true);

    try {
      await excluir_certificado(confirmData.id);
      toast.success("Certificado excluído com sucesso!");
      setReloadKey((old) => old + 1);
      setConfirmOpen(false);
      setConfirmData(null);
    } catch (err) {
      console.error(err);
      toast.error("Erro ao excluir certificado.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl shadow-lg">
              <FiShield className="text-white" size={28} />
            </div>
            Certificados Digitais
          </h1>
          <p className="text-gray-600">Gerencie seus certificados digitais de forma segura</p>
        </div>

        <button
          onClick={() => navigate("/certificados/novo")}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
        >
          <FiPlus size={20} />
          Novo Certificado
        </button>
      </div>

      {/* Filter Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 animate-slideUp">
        <div className="flex items-center gap-3 mb-3">
          <FiFilter className="text-emerald-600" size={18} />
          <h3 className="font-semibold text-gray-800">Filtros</h3>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <FiBriefcase className="text-gray-400" size={14} />
              Empresa
            </label>
            <SelectEmpresa
              value={empresaId}
              onChange={(id) => {
                setEmpresaId(id);
                setSelectedGroup(null);
                setReloadKey((k) => k + 1);
              }}
            />
          </div>

          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <FiUsers className="text-gray-400" size={14} />
              Grupo
            </label>
            <SelectGrupo
              empresaId={empresaId}
              value={selectedGroup?.grupo_id || null}
              onChange={(val) => {
                // value is grupo_id
                if (!val) {
                  setSelectedGroup(null);
                } else {
                  const g = { grupo_id: val };
                  setSelectedGroup(g);
                }
                setReloadKey((k) => k + 1);
              }}
              isDisabled={!empresaId}
            />
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-slideUp">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <FiShield className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Total de Certificados</p>
              <p className="text-2xl font-bold text-gray-800">{stats.total || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-50 rounded-xl">
              <FiCheckCircle className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Certificados Ativos</p>
              <p className="text-2xl font-bold text-gray-800">{stats.ativos || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-50 rounded-xl">
              <FiAlertCircle className="text-orange-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Expirando em breve</p>
              <p className="text-2xl font-bold text-gray-800">{stats.expirando || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-50 rounded-xl">
              <FiAlertCircle className="text-red-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Certificados Expirados</p>
              <p className="text-2xl font-bold text-gray-800">{stats.expirados || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 animate-slideUp">
        <div className="flex gap-3">
          <FiAlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-blue-900 mb-1">Sobre os certificados</p>
            <p className="text-sm text-blue-800">
              Todos os certificados são criptografados com AES-256-GCM. Certificados que expirarem em menos de 30 dias serão destacados com alerta laranja.
            </p>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden animate-slideUp">
        {/* 🔧 Correção: condição e key baseadas em empresaId */}
        {empresaId ? (
          <DataTable
            key={empresaId + "-" + reloadKey}
            columns={columns}
            fetchData={fetchCertificados}
            limit={10}
          />
        ) : (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-gray-100 rounded-full">
                <FiBriefcase size={32} className="text-gray-400" />
              </div>
              <div>
                <p className="text-gray-700 font-medium mb-1">Selecione uma empresa</p>
                <p className="text-sm text-gray-500">Escolha uma empresa acima para visualizar os certificados</p>
              </div>
            </div>
          </div>
        )}

        <ConfirmModal
          open={confirmOpen}
          title={`Excluir certificado?`}
          description={confirmData ? `Deseja realmente excluir o certificado "${confirmData.nome}"? Esta ação não pode ser desfeita.` : ''}
          confirmText="Excluir"
          cancelText="Cancelar"
          onConfirm={handleConfirmDelete}
          onCancel={() => setConfirmOpen(false)}
          loading={isDeleting}
        />
      </div>
    </div>
  );
}
