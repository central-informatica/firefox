import { useState, useEffect } from "react";
import { toast } from "react-toastify";
import {
  FiClock, FiPlus, FiTrash2, FiSettings, FiAlertCircle, FiEdit2, FiX, FiSave, FiWifi, FiUsers, FiCalendar, FiCheck, FiToggleLeft, FiToggleRight
} from "react-icons/fi";
import Label from "../../components/Label/Label";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import {
  listarRegrasPorEmpresa,
  createRegraBulk,
  updateRegra,
  deleteRegra,
  toggleRegraAtivo
} from "../../services/regrasAcessoIpsService";
import { listarGruposPorEmpresa } from "../../services/gruposService";

const TIPO_DIA_OPTIONS = [
  { value: "corridos", label: "Todos os dias" },
  { value: "uteis", label: "Dias úteis (Seg-Sex)" },
  { value: "especificos", label: "Dias específicos" },
];

const DIAS_SEMANA = [
  { value: 1, label: "Segunda" },
  { value: 2, label: "Terça" },
  { value: 3, label: "Quarta" },
  { value: 4, label: "Quinta" },
  { value: 5, label: "Sexta" },
  { value: 6, label: "Sábado" },
  { value: 7, label: "Domingo" },
];

// Regex para validar IPv4, IPv6 e CIDR
const IPV4_REGEX = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
const IPV6_REGEX = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,6}:$|^(?:[0-9a-fA-F]{1,4}:){1,5}:[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,4}:(?:[0-9a-fA-F]{1,4}:)?[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,3}:(?:[0-9a-fA-F]{1,4}:){0,2}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,2}:(?:[0-9a-fA-F]{1,4}:){0,3}[0-9a-fA-F]{1,4}$|^[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,4}[0-9a-fA-F]{1,4}$|^::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,7}:$/;
const CIDR_REGEX = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(?:[12]?[0-9]|3[0-2])$/;

function isValidIPOrCIDR(ip) {
  return IPV4_REGEX.test(ip) || IPV6_REGEX.test(ip) || CIDR_REGEX.test(ip);
}

export default function RegrasAcessoIpsList() {
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [regras, setRegras] = useState([]);
  const [grupos, setGrupos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    empresa_id: null,
    grupo_ids: [], // Array para múltiplos grupos na criação
    grupo_id: "",  // String para edição (único grupo)
    ip_addresses_text: "", // Texto para IPs separados por vírgula ou nova linha
    tipo_dia: "corridos",
    dias_especificos: [],
    horarios: [{ inicio: "08:00", fim: "18:00" }],
    bloquear_em_feriado: false,
    ativo: true,
  });

  const carregarRegras = async () => {
    if (!empresaSelecionada) {
      setRegras([]);
      return;
    }

    setLoading(true);
    try {
      const response = await listarRegrasPorEmpresa({
        empresaId: empresaSelecionada,
        page: 1,
        limit: 100,
      });
      setRegras(response.data || []);
    } catch (error) {
      console.error("Erro ao carregar regras:", error);
      let errorMessage = "Erro ao carregar regras de acesso";
      try {
        const parsed = JSON.parse(error.message);
        errorMessage = parsed.detail || errorMessage;
      } catch {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const carregarGrupos = async () => {
    if (!empresaSelecionada) {
      setGrupos([]);
      return;
    }
    try {
      const data = await listarGruposPorEmpresa(empresaSelecionada);
      setGrupos(data || []);
    } catch (error) {
      console.error("Erro ao carregar grupos:", error);
      setGrupos([]);
    }
  };

  useEffect(() => {
    carregarRegras();
    carregarGrupos();
  }, [empresaSelecionada]);

  const handleOpenModal = (item = null) => {
    if (item) {
      setEditingId(item.regra_id);
      // Converte array de IPs para texto
      const ipText = Array.isArray(item.ip_addresses)
        ? item.ip_addresses.join("\n")
        : "";
      setFormData({
        empresa_id: item.empresa_id,
        grupo_ids: [],
        grupo_id: item.grupo_id,
        ip_addresses_text: ipText,
        tipo_dia: item.tipo_dia || "corridos",
        dias_especificos: item.dias_especificos || [],
        horarios: item.horarios || [{ inicio: "08:00", fim: "18:00" }],
        bloquear_em_feriado: item.bloquear_em_feriado || false,
        ativo: item.ativo !== undefined ? item.ativo : true,
      });
    } else {
      setEditingId(null);
      setFormData({
        empresa_id: empresaSelecionada,
        grupo_ids: [],
        grupo_id: "",
        ip_addresses_text: "",
        tipo_dia: "corridos",
        dias_especificos: [],
        horarios: [{ inicio: "08:00", fim: "18:00" }],
        bloquear_em_feriado: false,
        ativo: true,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({
      empresa_id: null,
      grupo_ids: [],
      grupo_id: "",
      ip_addresses_text: "",
      tipo_dia: "corridos",
      dias_especificos: [],
      horarios: [{ inicio: "08:00", fim: "18:00" }],
      bloquear_em_feriado: false,
      ativo: true,
    });
  };

  const handleAddHorario = () => {
    setFormData({
      ...formData,
      horarios: [...formData.horarios, { inicio: "08:00", fim: "18:00" }],
    });
  };

  const handleRemoveHorario = (index) => {
    if (formData.horarios.length > 1) {
      const newHorarios = formData.horarios.filter((_, i) => i !== index);
      setFormData({ ...formData, horarios: newHorarios });
    }
  };

  const handleHorarioChange = (index, field, value) => {
    const newHorarios = [...formData.horarios];
    newHorarios[index] = { ...newHorarios[index], [field]: value };
    setFormData({ ...formData, horarios: newHorarios });
  };

  const handleDiaEspecificoToggle = (dia) => {
    const currentDias = formData.dias_especificos || [];
    if (currentDias.includes(dia)) {
      setFormData({
        ...formData,
        dias_especificos: currentDias.filter((d) => d !== dia),
      });
    } else {
      setFormData({
        ...formData,
        dias_especificos: [...currentDias, dia].sort((a, b) => a - b),
      });
    }
  };

  const handleGrupoToggle = (grupoId) => {
    const currentGrupos = formData.grupo_ids || [];
    if (currentGrupos.includes(grupoId)) {
      setFormData({
        ...formData,
        grupo_ids: currentGrupos.filter((id) => id !== grupoId),
      });
    } else {
      setFormData({
        ...formData,
        grupo_ids: [...currentGrupos, grupoId],
      });
    }
  };

  const handleSelectAllGrupos = () => {
    if (formData.grupo_ids.length === grupos.length) {
      setFormData({ ...formData, grupo_ids: [] });
    } else {
      setFormData({ ...formData, grupo_ids: grupos.map(g => g.grupo_id) });
    }
  };

  // Converte texto de IPs para array, validando cada um
  const parseIpAddresses = (text) => {
    return text
      .split(/[,\n]/)
      .map(ip => ip.trim())
      .filter(ip => ip.length > 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!editingId && (!formData.grupo_ids || formData.grupo_ids.length === 0)) {
      toast.error("Selecione ao menos um grupo");
      return;
    }

    // Validação de IPs
    const ips = parseIpAddresses(formData.ip_addresses_text);
    if (ips.length === 0) {
      toast.error("Informe ao menos um endereço IP ou bloco CIDR");
      return;
    }

    if (ips.length > 256) {
      toast.error("Máximo de 256 IPs por regra");
      return;
    }

    const invalidIps = ips.filter(ip => !isValidIPOrCIDR(ip));
    if (invalidIps.length > 0) {
      toast.error(`IPs/CIDRs inválidos: ${invalidIps.slice(0, 3).join(", ")}${invalidIps.length > 3 ? "..." : ""}`);
      return;
    }

    if (!formData.empresa_id) {
      toast.error("Selecione uma empresa");
      return;
    }

    if (formData.tipo_dia === "especificos" && (!formData.dias_especificos || formData.dias_especificos.length === 0)) {
      toast.error("Selecione ao menos um dia da semana");
      return;
    }

    try {
      if (editingId) {
        await updateRegra(editingId, {
          ip_addresses: ips,
          tipo_dia: formData.tipo_dia,
          dias_especificos: formData.tipo_dia === "especificos" ? formData.dias_especificos : null,
          horarios: formData.horarios,
          bloquear_em_feriado: formData.bloquear_em_feriado,
          ativo: formData.ativo,
        });
        toast.success("Regra atualizada com sucesso!");
      } else {
        const payload = {
          empresa_id: formData.empresa_id,
          grupo_ids: formData.grupo_ids,
          ip_addresses: ips,
          tipo_dia: formData.tipo_dia,
          dias_especificos: formData.tipo_dia === "especificos" ? formData.dias_especificos : null,
          horarios: formData.horarios,
          bloquear_em_feriado: formData.bloquear_em_feriado,
          ativo: formData.ativo,
        };
        const result = await createRegraBulk(payload);

        if (result.erros && result.erros.length > 0) {
          toast.warning(`${result.total_criadas} regra(s) criada(s). Avisos: ${result.erros.slice(0, 3).join(", ")}${result.erros.length > 3 ? "..." : ""}`);
        } else {
          toast.success(`${result.total_criadas} regra(s) criada(s) com sucesso!`);
        }
      }

      handleCloseModal();
      carregarRegras();
    } catch (error) {
      console.error("Erro ao salvar regra:", error);
      let errorMessage = "Erro ao salvar regra";
      try {
        const parsed = JSON.parse(error.message);
        if (Array.isArray(parsed.detail)) {
          const ipError = parsed.detail.find(e => e.loc?.includes("ip_addresses"));
          if (ipError) {
            errorMessage = "Máscara de IP errada";
          } else {
            errorMessage = parsed.detail.map(e => e.msg).join("; ");
          }
        } else {
          errorMessage = parsed.detail || errorMessage;
        }
      } catch {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
    }
  };

  const handleDelete = async (id) => {
    if (confirm("Deseja realmente remover esta regra de acesso?")) {
      try {
        await deleteRegra(id);
        toast.success("Regra removida com sucesso!");
        carregarRegras();
      } catch (error) {
        console.error("Erro ao remover regra:", error);
        let errorMessage = "Erro ao remover regra";
        try {
          const parsed = JSON.parse(error.message);
          errorMessage = parsed.detail || errorMessage;
        } catch {
          errorMessage = error.message || errorMessage;
        }
        toast.error(errorMessage);
      }
    }
  };

  const handleToggleAtivo = async (id) => {
    try {
      await toggleRegraAtivo(id);
      carregarRegras();
    } catch (error) {
      console.error("Erro ao alterar status:", error);
      let errorMessage = "Erro ao alterar status da regra";
      try {
        const parsed = JSON.parse(error.message);
        errorMessage = parsed.detail || errorMessage;
      } catch {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
    }
  };

  const formatTipoDia = (tipo_dia, dias_especificos) => {
    if (tipo_dia === "corridos") return "Todos os dias";
    if (tipo_dia === "uteis") return "Dias úteis";
    if (tipo_dia === "especificos" && dias_especificos) {
      const diasNomes = dias_especificos.map(d => {
        const dia = DIAS_SEMANA.find(ds => ds.value === d);
        return dia ? dia.label.substring(0, 3) : d;
      });
      return diasNomes.join(", ");
    }
    return tipo_dia;
  };

  const formatHorarios = (horarios) => {
    if (!horarios || horarios.length === 0) return "-";
    return horarios.map(h => `${h.inicio} - ${h.fim}`).join(", ");
  };

  const formatIpAddresses = (ip_addresses) => {
    if (!ip_addresses || ip_addresses.length === 0) return "-";
    if (ip_addresses.length === 1) return ip_addresses[0];
    if (ip_addresses.length <= 3) return ip_addresses.join(", ");
    return `${ip_addresses.slice(0, 2).join(", ")} +${ip_addresses.length - 2}`;
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-cyan-700 rounded-xl shadow-lg">
              <FiWifi className="text-white" size={28} />
            </div>
            Regras de Acesso por IP
          </h1>
          <p className="text-neutral-400">Configure horários e dias permitidos para endereços IP por grupo</p>
        </div>

        <button
          onClick={() => handleOpenModal()}
          disabled={!empresaSelecionada}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-cyan-700 hover:from-cyan-600 hover:to-cyan-800 text-white font-semibold rounded-xl shadow-lg shadow-cyan-500/30 hover:shadow-xl hover:shadow-cyan-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <FiPlus size={20} />
          Nova Regra
        </button>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5">
        <h3 className="font-semibold text-neutral-100 mb-4 flex items-center gap-2">
          <FiSettings className="text-cyan-400" size={18} />
          Filtros
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-sm font-medium text-neutral-400 mb-2">Empresa</Label>
            <SelectEmpresa
              placeholder="Selecione uma empresa"
              value={empresaSelecionada}
              onChange={setEmpresaSelecionada}
            />
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-cyan-900/20 to-teal-900/20 border border-cyan-800/50 rounded-card p-4">
        <div className="flex gap-3">
          <FiAlertCircle className="text-cyan-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-cyan-300 mb-1">Como funcionam as regras de acesso por IP</p>
            <p className="text-sm text-cyan-400">
              Defina horários e dias específicos em que cada endereço IP (IPv4, IPv6 ou bloco CIDR) pode ser utilizado por um ou mais grupos.
              Cada regra pode conter múltiplos IPs. Acessos fora dos horários configurados ou com regras inativas serão bloqueados automaticamente.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
        {!empresaSelecionada ? (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-dark-tertiary rounded-full">
                <FiWifi size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Selecione uma empresa</p>
                <p className="text-sm text-neutral-500">Escolha uma empresa acima para gerenciar as regras de acesso</p>
              </div>
            </div>
          </div>
        ) : loading ? (
          <div className="p-12 text-center">
            <p className="text-neutral-400">Carregando...</p>
          </div>
        ) : regras.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-dark-tertiary to-neutral-800 border-b border-neutral-800">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Grupo
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    IPs
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Dias
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Horários
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Feriado
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800">
                {regras.map((item) => (
                  <tr key={item.regra_id} className={`hover:bg-dark-tertiary transition-colors duration-150 ${!item.ativo ? 'opacity-60' : ''}`}>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleToggleAtivo(item.regra_id)}
                        className="cursor-pointer"
                        title={item.ativo ? "Clique para desativar" : "Clique para ativar"}
                      >
                        {item.ativo ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-900/30 text-green-400">
                            <FiToggleRight size={14} />
                            Ativo
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-neutral-700/50 text-neutral-400">
                            <FiToggleLeft size={14} />
                            Inativo
                          </span>
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <FiUsers className="text-cyan-400" size={16} />
                        <span className="text-sm font-medium text-neutral-100">{item.grupo_nome || "-"}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <FiWifi className="text-teal-400" size={16} />
                        <span
                          className="text-sm text-neutral-100 font-mono cursor-help"
                          title={Array.isArray(item.ip_addresses) ? item.ip_addresses.join("\n") : "-"}
                        >
                          {formatIpAddresses(item.ip_addresses)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-neutral-300">{formatTipoDia(item.tipo_dia, item.dias_especificos)}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-neutral-300">{formatHorarios(item.horarios)}</span>
                    </td>
                    <td className="px-6 py-4">
                      {item.bloquear_em_feriado ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-orange-900/30 text-orange-400">
                          <FiCalendar size={12} />
                          Bloqueado
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-neutral-700/50 text-neutral-400">
                          Liberado
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenModal(item)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-cyan-900/30 hover:bg-cyan-900/50 text-cyan-400 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                        >
                          <FiEdit2 size={14} />
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(item.regra_id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                        >
                          <FiTrash2 size={14} />
                          Remover
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-dark-tertiary rounded-full">
                <FiWifi size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Nenhuma regra cadastrada</p>
                <p className="text-sm text-neutral-500">Adicione regras para controlar o acesso por IP</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-dark-secondary rounded-card shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto animate-[slideUp_0.3s_ease-out] border border-neutral-800">
            <div className="p-6 border-b border-neutral-800 sticky top-0 bg-dark-secondary z-10">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-neutral-100 flex items-center gap-2">
                  <FiWifi className="text-cyan-400" />
                  {editingId ? "Editar Regra" : "Nova Regra de Acesso"}
                </h3>
                <button
                  onClick={handleCloseModal}
                  className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors duration-200"
                >
                  <FiX size={20} className="text-neutral-500" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-5">
              {editingId ? (
                // Modo edição: mostra apenas o grupo atual (não editável)
                <div>
                  <Label className="text-sm font-medium text-neutral-400 mb-2">Grupo</Label>
                  <div className="px-4 py-3 bg-dark-tertiary border border-neutral-800 rounded-xl text-neutral-400">
                    {grupos.find(g => g.grupo_id === formData.grupo_id)?.nome || "Grupo não encontrado"}
                  </div>
                </div>
              ) : (
                // Modo criação: multi-select de grupos
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-sm font-medium text-neutral-400">Grupos *</Label>
                    <button
                      type="button"
                      onClick={handleSelectAllGrupos}
                      className="text-sm text-cyan-400 hover:text-cyan-300"
                    >
                      {formData.grupo_ids.length === grupos.length ? "Desmarcar todos" : "Selecionar todos"}
                    </button>
                  </div>
                  <div className="max-h-48 overflow-y-auto border border-neutral-800 rounded-xl bg-dark-tertiary p-2 space-y-1">
                    {grupos.length === 0 ? (
                      <p className="text-sm text-neutral-500 p-2">Nenhum grupo disponível</p>
                    ) : (
                      grupos.map((grupo) => (
                        <div
                          key={grupo.grupo_id}
                          onClick={() => handleGrupoToggle(grupo.grupo_id)}
                          className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                            formData.grupo_ids.includes(grupo.grupo_id)
                              ? "bg-cyan-600/20 text-cyan-300"
                              : "hover:bg-neutral-700 text-neutral-300"
                          }`}
                        >
                          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                            formData.grupo_ids.includes(grupo.grupo_id)
                              ? "bg-cyan-600 border-cyan-600"
                              : "border-neutral-600"
                          }`}>
                            {formData.grupo_ids.includes(grupo.grupo_id) && (
                              <FiCheck size={12} className="text-white" />
                            )}
                          </div>
                          <span className="text-sm">{grupo.nome}</span>
                        </div>
                      ))
                    )}
                  </div>
                  {formData.grupo_ids.length > 0 && (
                    <p className="text-xs text-cyan-400 mt-2">
                      {formData.grupo_ids.length} grupo(s) selecionado(s)
                    </p>
                  )}
                </div>
              )}

              {/* IPs Input - sempre como textarea */}
              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">Endereços IP *</Label>
                <textarea
                  value={formData.ip_addresses_text}
                  onChange={(e) => setFormData({ ...formData, ip_addresses_text: e.target.value })}
                  placeholder="192.168.1.1&#10;192.168.1.0/24&#10;10.0.0.1&#10;&#10;ou separados por vírgula: 192.168.1.1, 10.0.0.1"
                  rows={4}
                  className="w-full px-4 py-3 bg-dark-tertiary border border-neutral-800 rounded-xl text-neutral-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors font-mono resize-none"
                />
                <p className="text-xs text-neutral-500 mt-1">
                  Separe os IPs por vírgula ou nova linha. Suporta IPv4, IPv6 e blocos CIDR (ex: 192.168.1.0/24). Máximo: 256 IPs
                </p>
              </div>

              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">Tipo de Dias *</Label>
                <select
                  value={formData.tipo_dia}
                  onChange={(e) => setFormData({ ...formData, tipo_dia: e.target.value })}
                  className="w-full px-4 py-3 bg-dark-tertiary border border-neutral-800 rounded-xl text-neutral-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors"
                >
                  {TIPO_DIA_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              {formData.tipo_dia === "especificos" && (
                <div>
                  <Label className="text-sm font-medium text-neutral-400 mb-2">Dias da Semana *</Label>
                  <div className="flex flex-wrap gap-2">
                    {DIAS_SEMANA.map((dia) => (
                      <button
                        key={dia.value}
                        type="button"
                        onClick={() => handleDiaEspecificoToggle(dia.value)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          formData.dias_especificos?.includes(dia.value)
                            ? "bg-cyan-600 text-white"
                            : "bg-dark-tertiary text-neutral-400 hover:bg-neutral-700"
                        }`}
                      >
                        {dia.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-medium text-neutral-400">Horários Permitidos *</Label>
                  <button
                    type="button"
                    onClick={handleAddHorario}
                    className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                  >
                    <FiPlus size={14} />
                    Adicionar horário
                  </button>
                </div>
                <div className="space-y-3">
                  {formData.horarios.map((horario, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="flex-1">
                        <input
                          type="time"
                          value={horario.inicio}
                          onChange={(e) => handleHorarioChange(index, "inicio", e.target.value)}
                          className="w-full px-4 py-2.5 bg-dark-tertiary border border-neutral-800 rounded-xl text-neutral-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors"
                        />
                      </div>
                      <span className="text-neutral-500">até</span>
                      <div className="flex-1">
                        <input
                          type="time"
                          value={horario.fim}
                          onChange={(e) => handleHorarioChange(index, "fim", e.target.value)}
                          className="w-full px-4 py-2.5 bg-dark-tertiary border border-neutral-800 rounded-xl text-neutral-100 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-colors"
                        />
                      </div>
                      {formData.horarios.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveHorario(index)}
                          className="p-2 text-red-400 hover:bg-red-900/30 rounded-lg transition-colors"
                        >
                          <FiTrash2 size={16} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="bloquear_em_feriado"
                  checked={formData.bloquear_em_feriado}
                  onChange={(e) => setFormData({ ...formData, bloquear_em_feriado: e.target.checked })}
                  className="w-4 h-4 text-cyan-600 bg-dark-tertiary border-neutral-700 rounded focus:ring-cyan-500"
                />
                <Label htmlFor="bloquear_em_feriado" className="text-sm font-medium text-neutral-400">
                  Bloquear acesso em feriados
                </Label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="ativo"
                  checked={formData.ativo}
                  onChange={(e) => setFormData({ ...formData, ativo: e.target.checked })}
                  className="w-4 h-4 text-cyan-600 bg-dark-tertiary border-neutral-700 rounded focus:ring-cyan-500"
                />
                <Label htmlFor="ativo" className="text-sm font-medium text-neutral-400">
                  Regra ativa
                </Label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="flex-1 px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 font-medium rounded-xl transition-all duration-200"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-cyan-700 hover:from-cyan-600 hover:to-cyan-800 text-white font-medium rounded-xl shadow-lg shadow-cyan-500/30 transition-all duration-200 cursor-pointer"
                >
                  <FiSave size={18} />
                  {editingId ? "Atualizar" : `Criar Regra${formData.grupo_ids.length > 1 ? "s" : ""}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
