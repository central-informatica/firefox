import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiShield,
  FiFilter,
  FiBriefcase,
  FiUsers,
  FiFile,
  FiCalendar,
  FiClock,
  FiCheckCircle,
  FiAlertCircle,
  FiLink,
  FiPlus,
  FiX,
  FiTrash2,
  FiLayers,
} from "react-icons/fi";

import DataTable from "../../components/Tables/DataTable";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectPlanoTrabalho from "../../components/Select/SelectPlanoTrabalho";
import SelectGrupo from "../../components/Select/SelectGrupo";
import { apiFetchWithToken } from "../../api/api";
import {
  listarCertificadosDaEmpresa,
  adicionarCertificadoAoGrupo,
  removerCertificadoDoGrupo,
} from "../../services/certificadosService";

export default function CertificadosGruposList() {
  const navigate = useNavigate();
  const [empresaId, setEmpresaId] = useState(null);
  const [filterGrupoId, setFilterGrupoId] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [stats, setStats] = useState({ total: 0, ativos: 0, expirando: 0, expirados: 0 });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedPlanoId, setSelectedPlanoId] = useState(null);
  const [selectedGrupoId, setSelectedGrupoId] = useState(null);
  const [availableCerts, setAvailableCerts] = useState([]);
  const [selectedCerts, setSelectedCerts] = useState([]);
  const [loadingCerts, setLoadingCerts] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const getCertificateStatus = (validoAte) => {
    if (!validoAte) return { status: "desconhecido", label: "Desconhecido", color: "gray", dias: 0 };

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

  const fetchGruposCertificados = async ({ page, limit, search, sort }) => {
    const params = new URLSearchParams({
      page,
      limit,
      search: search || "",
    });

    if (filterGrupoId) {
      params.append("grupo_id", filterGrupoId);
    }

    const res = await apiFetchWithToken(
      `/grupos-certificados/empresa/${empresaId}/detalhado?${params.toString()}`
    );

    if (!res.ok) {
      throw new Error("Erro ao listar grupos de certificados");
    }

    const data = await res.json();

    // Calculate stats
    let ativos = 0, expirando = 0, expirados = 0;
    (data.data || []).forEach((item) => {
      const statusInfo = getCertificateStatus(item.certificado_valido_ate);
      if (statusInfo.status === "ativo") ativos++;
      else if (statusInfo.status === "expirando") expirando++;
      else if (statusInfo.status === "expirado") expirados++;
    });

    setStats({
      total: data.total || 0,
      ativos,
      expirando,
      expirados,
    });

    return data;
  };

  const handleOpenModal = async () => {
    if (!empresaId) {
      toast.error("Selecione uma empresa primeiro");
      return;
    }
    setShowModal(true);
    setSelectedPlanoId(null);
    setSelectedGrupoId(null);
    setSelectedCerts([]);
    setLoadingCerts(true);

    try {
      const certs = await listarCertificadosDaEmpresa(empresaId);
      setAvailableCerts(certs);
    } catch (err) {
      console.error("Erro ao carregar certificados:", err);
      toast.error("Erro ao carregar certificados");
      setAvailableCerts([]);
    } finally {
      setLoadingCerts(false);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedPlanoId(null);
    setSelectedGrupoId(null);
    setSelectedCerts([]);
  };

  const handleToggleCert = (certId) => {
    setSelectedCerts((prev) =>
      prev.includes(certId)
        ? prev.filter((id) => id !== certId)
        : [...prev, certId]
    );
  };

  const handleSubmitLink = async () => {
    if (!selectedGrupoId) {
      toast.error("Selecione um grupo");
      return;
    }
    if (selectedCerts.length === 0) {
      toast.error("Selecione pelo menos um certificado");
      return;
    }

    setSubmitting(true);
    let successCount = 0;
    let errorCount = 0;

    for (const certId of selectedCerts) {
      try {
        await adicionarCertificadoAoGrupo(selectedGrupoId, certId, empresaId);
        successCount++;
      } catch (err) {
        console.error(`Erro ao vincular certificado ${certId}:`, err);
        errorCount++;
      }
    }

    setSubmitting(false);

    if (successCount > 0) {
      toast.success(`${successCount} certificado(s) vinculado(s) com sucesso!`);
      setReloadKey((k) => k + 1);
      handleCloseModal();
    }
    if (errorCount > 0) {
      toast.error(`${errorCount} certificado(s) falharam ao vincular`);
    }
  };

  const handleRemoveLink = async (grupoCertId, grupoId, certificadoId) => {
    if (!confirm("Deseja remover este vínculo?")) return;

    try {
      await removerCertificadoDoGrupo(grupoId, certificadoId, empresaId);
      toast.success("Vínculo removido com sucesso!");
      setReloadKey((k) => k + 1);
    } catch (err) {
      console.error("Erro ao remover vínculo:", err);
      toast.error("Erro ao remover vínculo");
    }
  };

  const columns = [
    {
      header: "Certificado",
      accessorKey: "certificado_nome",
      cell: ({ row }) => {
        const item = row.original;
        const statusInfo = getCertificateStatus(item.certificado_valido_ate);

        return (
          <div className="flex items-center gap-3 py-2">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl flex items-center justify-center shadow-sm">
                <FiFile className="text-white" size={20} />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-neutral-100 truncate">
                {item.certificado_nome || "Certificado.pfx"}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
                    ${statusInfo.status === "ativo" ? "badge-permitido" : ""}
                    ${statusInfo.status === "expirando" ? "bg-orange-900/30 text-orange-400" : ""}
                    ${statusInfo.status === "expirado" ? "badge-bloqueado" : ""}
                  `}
                >
                  {statusInfo.status === "ativo" && <FiCheckCircle size={10} />}
                  {statusInfo.status !== "ativo" && <FiAlertCircle size={10} />}
                  {statusInfo.label}
                </span>
              </div>
            </div>
          </div>
        );
      },
    },
    {
      header: "Grupo",
      accessorKey: "grupo_nome",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-neutral-100">
          <div className="w-8 h-8 bg-blue-900/30 rounded-lg flex items-center justify-center">
            <FiUsers className="text-blue-400" size={14} />
          </div>
          <span className="font-medium">{row.original.grupo_nome || "Sem grupo"}</span>
        </div>
      ),
    },
    {
      header: "Proprietário",
      accessorKey: "certificado_proprietario",
      cell: ({ row }) => (
        <span className="text-sm text-neutral-400">
          {row.original.certificado_proprietario || "-"}
        </span>
      ),
    },
    {
      accessorKey: "certificado_validade_inicio",
      header: "Início",
      cell: ({ row }) => (
        <div className="flex items-center gap-2 text-sm text-neutral-400">
          <FiCalendar className="text-neutral-500" size={14} />
          {row.original.certificado_validade_inicio
            ? new Date(row.original.certificado_validade_inicio).toLocaleDateString("pt-BR")
            : "-"}
        </div>
      ),
    },
    {
      accessorKey: "certificado_valido_ate",
      header: "Válido até",
      cell: ({ row }) => {
        const statusInfo = getCertificateStatus(row.original.certificado_valido_ate);
        return (
          <div>
            <div className="flex items-center gap-2 text-sm text-neutral-100 font-medium">
              <FiClock className="text-neutral-500" size={14} />
              {row.original.certificado_valido_ate
                ? new Date(row.original.certificado_valido_ate).toLocaleDateString("pt-BR")
                : "-"}
            </div>
            {statusInfo.dias > 0 && statusInfo.dias <= 30 && (
              <div className="text-xs text-orange-400 mt-1">
                {statusInfo.dias} {statusInfo.dias === 1 ? "dia" : "dias"} restantes
              </div>
            )}
          </div>
        );
      },
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <button
          onClick={() => handleRemoveLink(
            row.original.grupo_cert_id,
            row.original.grupo_id,
            row.original.certificado_id
          )}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer group"
          title="Remover vínculo"
        >
          <FiTrash2 size={14} className="group-hover:scale-110 transition-transform" />
          Remover
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl shadow-lg">
              <FiLink className="text-white" size={28} />
            </div>
            Grupos de Certificados
          </h1>
          <p className="text-neutral-400">
            Visualize e gerencie os certificados vinculados aos grupos
          </p>
        </div>

        <button
          onClick={handleOpenModal}
          disabled={!empresaId}
          className={`inline-flex items-center gap-2 px-6 py-3 font-semibold rounded-xl shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer
            ${empresaId
              ? "bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40"
              : "bg-neutral-700 text-neutral-500 cursor-not-allowed"
            }
          `}
        >
          <FiPlus size={20} />
          Vincular Certificado
        </button>
      </div>

      {/* Filter Card */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5 animate-slideUp">
        <div className="flex items-center gap-3 mb-3">
          <FiFilter className="text-xfire-orange" size={18} />
          <h3 className="font-semibold text-neutral-100">Filtros</h3>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
              <FiBriefcase className="text-neutral-500" size={14} />
              Empresa
            </label>
            <SelectEmpresa
              value={empresaId}
              onChange={(id) => {
                setEmpresaId(id);
                setFilterGrupoId(null);
                setReloadKey((k) => k + 1);
              }}
            />
          </div>

          <div className="flex-1 max-w-sm">
            <label className="block text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
              <FiUsers className="text-neutral-500" size={14} />
              Grupo
            </label>
            <SelectGrupo
              empresaId={empresaId}
              value={filterGrupoId}
              onChange={(id) => {
                setFilterGrupoId(id);
                setReloadKey((k) => k + 1);
              }}
              placeholder="Todos os grupos"
              isDisabled={!empresaId}
            />
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-slideUp">
        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-900/30 rounded-xl">
              <FiLink className="text-blue-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Total de Vínculos</p>
              <p className="text-2xl font-bold text-neutral-100">{stats.total || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-900/30 rounded-xl">
              <FiCheckCircle className="text-green-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Certificados Ativos</p>
              <p className="text-2xl font-bold text-neutral-100">{stats.ativos || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-900/30 rounded-xl">
              <FiAlertCircle className="text-orange-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Expirando em breve</p>
              <p className="text-2xl font-bold text-neutral-100">{stats.expirando || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-secondary rounded-card p-5 shadow-sm border border-neutral-900 hover:shadow-md transition-all duration-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-900/30 rounded-xl">
              <FiAlertCircle className="text-red-400" size={24} />
            </div>
            <div>
              <p className="text-sm text-neutral-400 font-medium">Expirados</p>
              <p className="text-2xl font-bold text-neutral-100">{stats.expirados || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border border-blue-800/50 rounded-card p-4 animate-slideUp">
        <div className="flex gap-3">
          <FiAlertCircle className="text-blue-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-blue-300 mb-1">Sobre os grupos de certificados</p>
            <p className="text-sm text-blue-400">
              Esta página mostra todos os certificados que estão vinculados a grupos. Os vínculos permitem que usuários do grupo utilizem os certificados para assinatura digital.
            </p>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden animate-slideUp">
        {empresaId ? (
          <DataTable
            key={`${empresaId}-${reloadKey}`}
            columns={columns}
            fetchData={fetchGruposCertificados}
            limit={10}
          />
        ) : (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-dark-tertiary rounded-full">
                <FiBriefcase size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Selecione uma empresa</p>
                <p className="text-sm text-neutral-500">
                  Escolha uma empresa acima para visualizar os grupos de certificados
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Vinculação */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-dark-secondary rounded-2xl shadow-2xl border border-neutral-800 w-full max-w-2xl max-h-[90vh] overflow-hidden animate-slideUp">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-neutral-800">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-xfire-orange to-xfire-red rounded-xl">
                  <FiLink className="text-white" size={20} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-neutral-100">Vincular Certificados ao Grupo</h2>
                  <p className="text-sm text-neutral-400">Selecione um grupo e os certificados para vincular</p>
                </div>
              </div>
              <button
                onClick={handleCloseModal}
                className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors text-neutral-400 hover:text-neutral-100"
              >
                <FiX size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto">
              {/* Seleção de Plano de Trabalho */}
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
                  <FiLayers className="text-neutral-500" size={14} />
                  Plano de Trabalho
                </label>
                <SelectPlanoTrabalho
                  empresaId={empresaId}
                  value={selectedPlanoId}
                  onChange={(id) => {
                    setSelectedPlanoId(id);
                    setSelectedGrupoId(null); // Reset grupo when plano changes
                  }}
                  placeholder="Selecione um plano de trabalho"
                />
                <p className="mt-1 text-xs text-neutral-500">
                  Selecione um plano para poder criar novos grupos
                </p>
              </div>

              {/* Seleção de Grupo */}
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
                  <FiUsers className="text-neutral-500" size={14} />
                  Grupo
                </label>
                <SelectGrupo
                  empresaId={empresaId}
                  planoTrabalhoId={selectedPlanoId}
                  value={selectedGrupoId}
                  onChange={setSelectedGrupoId}
                  placeholder={selectedPlanoId ? "Selecione ou crie um grupo" : "Selecione um plano primeiro"}
                  isDisabled={!selectedPlanoId}
                />
              </div>

              {/* Lista de Certificados */}
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-3 flex items-center gap-2">
                  <FiFile className="text-neutral-500" size={14} />
                  Certificados Disponíveis
                  {selectedCerts.length > 0 && (
                    <span className="ml-2 px-2 py-0.5 bg-xfire-orange/20 text-xfire-orange rounded-full text-xs">
                      {selectedCerts.length} selecionado(s)
                    </span>
                  )}
                </label>

                {loadingCerts ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-2 border-xfire-orange border-t-transparent"></div>
                  </div>
                ) : availableCerts.length === 0 ? (
                  <div className="text-center py-8 text-neutral-500">
                    Nenhum certificado disponível para esta empresa
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {availableCerts.map((cert) => {
                      const isSelected = selectedCerts.includes(cert.certificado_id);
                      const statusInfo = getCertificateStatus(cert.valido_ate);

                      return (
                        <div
                          key={cert.certificado_id}
                          onClick={() => handleToggleCert(cert.certificado_id)}
                          className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all duration-200
                            ${isSelected
                              ? "bg-xfire-orange/20 border-2 border-xfire-orange"
                              : "bg-dark-tertiary border-2 border-transparent hover:border-neutral-700"
                            }
                          `}
                        >
                          {/* Checkbox */}
                          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                            ${isSelected
                              ? "bg-xfire-orange border-xfire-orange"
                              : "border-neutral-600"
                            }
                          `}>
                            {isSelected && <FiCheckCircle className="text-white" size={12} />}
                          </div>

                          {/* Cert Icon */}
                          <div className="w-10 h-10 bg-gradient-to-br from-xfire-orange/30 to-xfire-red/30 rounded-lg flex items-center justify-center">
                            <FiFile className="text-xfire-orange" size={18} />
                          </div>

                          {/* Cert Info */}
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-neutral-100 truncate">
                              {cert.nome_arquivo || "Certificado.pfx"}
                            </div>
                            <div className="flex items-center gap-2 text-xs text-neutral-400">
                              <span>{cert.proprietario || "Sem proprietário"}</span>
                              <span>•</span>
                              <span className={`
                                ${statusInfo.status === "ativo" ? "text-green-400" : ""}
                                ${statusInfo.status === "expirando" ? "text-orange-400" : ""}
                                ${statusInfo.status === "expirado" ? "text-red-400" : ""}
                              `}>
                                {statusInfo.label}
                              </span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-neutral-800">
              <button
                onClick={handleCloseModal}
                className="px-6 py-2.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 font-medium rounded-xl transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmitLink}
                disabled={submitting || !selectedGrupoId || selectedCerts.length === 0}
                className={`px-6 py-2.5 font-medium rounded-xl transition-all flex items-center gap-2
                  ${submitting || !selectedGrupoId || selectedCerts.length === 0
                    ? "bg-neutral-700 text-neutral-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white"
                  }
                `}
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    Vinculando...
                  </>
                ) : (
                  <>
                    <FiLink size={16} />
                    Vincular {selectedCerts.length > 0 ? `(${selectedCerts.length})` : ""}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
