import { useState, useEffect } from "react";
import { toast } from "react-toastify";
import {
  FiCalendar, FiPlus, FiTrash2, FiSettings, FiAlertCircle, FiCheck, FiEdit2, FiX, FiSave, FiRepeat, FiCopy, FiDownload
} from "react-icons/fi";
import Input from "../../components/Input/Input";
import Label from "../../components/Label/Label";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectCustom from "../../components/Select/Select";
import DatePicker from "../../components/DatePicker/DatePicker";
import { useEmpresasUsuario } from "../../hooks/useEmpresasUsuario";
import {
  listarFeriadosPorEmpresa,
  createFeriado,
  updateFeriado,
  deleteFeriado,
  listarFeriadosPadroes,
  replicarFeriados,
  importarFeriadosPadroes
} from "../../services/feriadosService";

export default function FeriadosList() {
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [feriados, setFeriados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    data: "",
    nome: "",
    recorrente: false,
    empresa_id: null
  });

  // Estados para replicacao
  const [selectedFeriados, setSelectedFeriados] = useState([]);
  const [showReplicarModal, setShowReplicarModal] = useState(false);
  const [empresasDestino, setEmpresasDestino] = useState([]);
  const [replicando, setReplicando] = useState(false);

  // Estados para importar padroes
  const [showImportarModal, setShowImportarModal] = useState(false);
  const [feriadosPadroes, setFeriadosPadroes] = useState([]);
  const [anoImportacao, setAnoImportacao] = useState(new Date().getFullYear());
  const [importando, setImportando] = useState(false);

  const { options: empresasOptions = [] } = useEmpresasUsuario();

  const carregarFeriados = async () => {
    if (!empresaSelecionada) {
      setFeriados([]);
      return;
    }

    setLoading(true);
    try {
      const response = await listarFeriadosPorEmpresa({
        empresaId: empresaSelecionada,
        page: 1,
        limit: 100,
      });
      setFeriados(response.data || []);
    } catch (error) {
      console.error("Erro ao carregar feriados:", error);
      let errorMessage = "Erro ao carregar feriados";
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

  useEffect(() => {
    carregarFeriados();
  }, [empresaSelecionada]);

  const handleOpenModal = (item = null) => {
    if (item) {
      setEditingId(item.feriado_id);
      setFormData({
        data: item.data || "",
        nome: item.nome || "",
        recorrente: item.recorrente || false,
        empresa_id: item.empresa_id
      });
    } else {
      setEditingId(null);
      setFormData({
        data: "",
        nome: "",
        recorrente: false,
        empresa_id: empresaSelecionada
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ data: "", nome: "", recorrente: false, empresa_id: null });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.data) {
      toast.error("Informe a data do feriado");
      return;
    }

    if (!formData.nome) {
      toast.error("Informe o nome do feriado");
      return;
    }

    if (!formData.empresa_id) {
      toast.error("Selecione uma empresa");
      return;
    }

    try {
      if (editingId) {
        await updateFeriado(editingId, {
          data: formData.data,
          nome: formData.nome,
          recorrente: formData.recorrente
        });
        toast.success("Feriado atualizado com sucesso!");
      } else {
        await createFeriado({
          data: formData.data,
          nome: formData.nome,
          recorrente: formData.recorrente,
          empresa_id: formData.empresa_id
        });
        toast.success("Feriado adicionado com sucesso!");
      }

      handleCloseModal();
      carregarFeriados();
    } catch (error) {
      console.error("Erro ao salvar feriado:", error);
      let errorMessage = "Erro ao salvar feriado";
      try {
        const parsed = JSON.parse(error.message);
        errorMessage = parsed.detail || errorMessage;
      } catch {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
    }
  };

  const handleDelete = async (id) => {
    if (confirm("Deseja realmente remover este feriado?")) {
      try {
        await deleteFeriado(id);
        toast.success("Feriado removido com sucesso!");
        carregarFeriados();
      } catch (error) {
        console.error("Erro ao remover feriado:", error);
        let errorMessage = "Erro ao remover feriado";
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

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    const date = new Date(dateStr + "T00:00:00");
    return date.toLocaleDateString("pt-BR");
  };

  // Funcoes para selecao de feriados
  const handleSelectFeriado = (feriadoId) => {
    setSelectedFeriados((prev) =>
      prev.includes(feriadoId)
        ? prev.filter((id) => id !== feriadoId)
        : [...prev, feriadoId]
    );
  };

  const handleSelectAll = () => {
    if (selectedFeriados.length === feriados.length) {
      setSelectedFeriados([]);
    } else {
      setSelectedFeriados(feriados.map((f) => f.feriado_id));
    }
  };

  // Funcoes para replicacao
  const handleOpenReplicarModal = () => {
    if (selectedFeriados.length === 0) {
      toast.warning("Selecione ao menos um feriado para replicar");
      return;
    }
    setShowReplicarModal(true);
  };

  const handleReplicar = async () => {
    if (empresasDestino.length === 0) {
      toast.error("Selecione ao menos uma empresa de destino");
      return;
    }

    setReplicando(true);
    try {
      const result = await replicarFeriados({
        feriado_ids: selectedFeriados,
        empresa_ids_destino: empresasDestino.map((e) => e.value),
      });

      if (result.total_criados > 0) {
        toast.success(`${result.total_criados} feriado(s) replicado(s) com sucesso!`);
      }
      if (result.erros && result.erros.length > 0) {
        result.erros.forEach((erro) => toast.warning(erro));
      }

      setShowReplicarModal(false);
      setSelectedFeriados([]);
      setEmpresasDestino([]);
    } catch (error) {
      console.error("Erro ao replicar feriados:", error);
      let errorMessage = "Erro ao replicar feriados";
      try {
        const parsed = JSON.parse(error.message);
        errorMessage = parsed.detail || errorMessage;
      } catch {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
    } finally {
      setReplicando(false);
    }
  };

  // Funcoes para importar padroes
  const handleOpenImportarModal = async () => {
    if (!empresaSelecionada) {
      toast.warning("Selecione uma empresa primeiro");
      return;
    }

    try {
      const padroes = await listarFeriadosPadroes();
      setFeriadosPadroes(padroes);
      setShowImportarModal(true);
    } catch (error) {
      console.error("Erro ao carregar feriados padroes:", error);
      toast.error("Erro ao carregar feriados padroes");
    }
  };

  const handleImportarPadroes = async () => {
    setImportando(true);
    try {
      const result = await importarFeriadosPadroes({
        empresa_id: empresaSelecionada,
        ano: anoImportacao,
      });

      if (result.total_criados > 0) {
        toast.success(`${result.total_criados} feriado(s) importado(s) com sucesso!`);
      } else {
        toast.info("Nenhum feriado novo importado");
      }
      if (result.erros && result.erros.length > 0) {
        result.erros.forEach((erro) => toast.warning(erro));
      }

      setShowImportarModal(false);
      carregarFeriados();
    } catch (error) {
      console.error("Erro ao importar feriados:", error);
      let errorMessage = "Erro ao importar feriados";
      try {
        const parsed = JSON.parse(error.message);
        errorMessage = parsed.detail || errorMessage;
      } catch {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
    } finally {
      setImportando(false);
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-orange-500 to-orange-700 rounded-xl shadow-lg">
              <FiCalendar className="text-white" size={28} />
            </div>
            Feriados
          </h1>
          <p className="text-neutral-400">Gerencie os feriados que bloqueiam o uso de certificados</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleOpenImportarModal}
            disabled={!empresaSelecionada}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-700 text-neutral-100 font-medium rounded-xl border border-neutral-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <FiDownload size={18} />
            Importar Padroes
          </button>
          <button
            onClick={handleOpenReplicarModal}
            disabled={!empresaSelecionada || selectedFeriados.length === 0}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-700 text-neutral-100 font-medium rounded-xl border border-neutral-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <FiCopy size={18} />
            Replicar ({selectedFeriados.length})
          </button>
          <button
            onClick={() => handleOpenModal()}
            disabled={!empresaSelecionada}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-700 hover:from-orange-600 hover:to-orange-800 text-white font-semibold rounded-xl shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <FiPlus size={20} />
            Adicionar Feriado
          </button>
        </div>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5">
        <h3 className="font-semibold text-neutral-100 mb-4 flex items-center gap-2">
          <FiSettings className="text-orange-400" size={18} />
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

      <div className="bg-gradient-to-r from-orange-900/20 to-amber-900/20 border border-orange-800/50 rounded-card p-4">
        <div className="flex gap-3">
          <FiAlertCircle className="text-orange-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-orange-300 mb-1">Como funcionam os feriados</p>
            <p className="text-sm text-orange-400">
              Nos dias marcados como feriado, os certificados que possuem regras de acesso ativas com "bloquear em feriado",
              não poderão ser utilizados.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
        {!empresaSelecionada ? (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-dark-tertiary rounded-full">
                <FiCalendar size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Selecione uma empresa</p>
                <p className="text-sm text-neutral-500">Escolha uma empresa acima para gerenciar os feriados</p>
              </div>
            </div>
          </div>
        ) : loading ? (
          <div className="p-12 text-center">
            <p className="text-neutral-400">Carregando...</p>
          </div>
        ) : feriados.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-dark-tertiary to-neutral-800 border-b border-neutral-800">
                <tr>
                  <th className="px-4 py-4 text-left">
                    <input
                      type="checkbox"
                      checked={selectedFeriados.length === feriados.length && feriados.length > 0}
                      onChange={handleSelectAll}
                      className="w-4 h-4 text-orange-600 bg-dark-tertiary border-neutral-700 rounded focus:ring-orange-500 cursor-pointer"
                    />
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Data
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Acoes
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800">
                {feriados.map((item) => (
                  <tr key={item.feriado_id} className="hover:bg-dark-tertiary transition-colors duration-150">
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedFeriados.includes(item.feriado_id)}
                        onChange={() => handleSelectFeriado(item.feriado_id)}
                        className="w-4 h-4 text-orange-600 bg-dark-tertiary border-neutral-700 rounded focus:ring-orange-500 cursor-pointer"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <FiCalendar className="text-orange-400" size={16} />
                        <span className="text-sm font-medium text-neutral-100">{formatDate(item.data)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-neutral-100">{item.nome}</span>
                    </td>
                    <td className="px-6 py-4">
                      {item.recorrente ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-900/30 text-blue-400">
                          <FiRepeat size={12} />
                          Recorrente
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-neutral-700/50 text-neutral-400">
                          <FiCalendar size={12} />
                          Unico
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenModal(item)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-900/30 hover:bg-blue-900/50 text-blue-400 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                        >
                          <FiEdit2 size={14} />
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(item.feriado_id)}
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
                <FiCalendar size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Nenhum feriado cadastrado</p>
                <p className="text-sm text-neutral-500">Adicione feriados para bloquear o uso de certificados</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-dark-secondary rounded-card shadow-2xl max-w-md w-full animate-[slideUp_0.3s_ease-out] border border-neutral-800">
            <div className="p-6 border-b border-neutral-800">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-neutral-100 flex items-center gap-2">
                  <FiCalendar className="text-orange-400" />
                  {editingId ? "Editar Feriado" : "Adicionar Feriado"}
                </h3>
                <button
                  onClick={handleCloseModal}
                  className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors duration-200"
                >
                  <FiX size={20} className="text-neutral-500" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">Empresa *</Label>
                <SelectEmpresa
                  placeholder="Selecione uma empresa"
                  value={formData.empresa_id}
                  onChange={(val) => setFormData({ ...formData, empresa_id: val })}
                />
              </div>

              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">Data *</Label>
                <DatePicker
                  value={formData.data}
                  onChange={(date) => setFormData({ ...formData, data: date })}
                  placeholder="Selecione uma data"
                />
              </div>

              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">Nome do Feriado *</Label>
                <Input
                  type="text"
                  placeholder="Ex: Natal, Ano Novo, etc."
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  required
                  className="w-full"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="recorrente"
                  checked={formData.recorrente}
                  onChange={(e) => setFormData({ ...formData, recorrente: e.target.checked })}
                  className="w-4 h-4 text-orange-600 bg-dark-tertiary border-neutral-700 rounded focus:ring-orange-500"
                />
                <Label htmlFor="recorrente" className="text-sm font-medium text-neutral-400">
                  Feriado recorrente (repete todo ano)
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
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-700 hover:from-orange-600 hover:to-orange-800 text-white font-medium rounded-xl shadow-lg shadow-orange-500/30 transition-all duration-200 cursor-pointer"
                >
                  <FiSave size={18} />
                  {editingId ? "Atualizar" : "Adicionar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Replicar Feriados */}
      {showReplicarModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-dark-secondary rounded-card shadow-2xl max-w-md w-full animate-[slideUp_0.3s_ease-out] border border-neutral-800">
            <div className="p-6 border-b border-neutral-800">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-neutral-100 flex items-center gap-2">
                  <FiCopy className="text-orange-400" />
                  Replicar Feriados
                </h3>
                <button
                  onClick={() => setShowReplicarModal(false)}
                  className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors duration-200"
                >
                  <FiX size={20} className="text-neutral-500" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="bg-dark-tertiary rounded-lg p-4">
                <p className="text-sm text-neutral-400 mb-2">Feriados selecionados:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedFeriados.map((id) => {
                    const feriado = feriados.find((f) => f.feriado_id === id);
                    return feriado ? (
                      <span
                        key={id}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-orange-900/30 text-orange-400"
                      >
                        <FiCalendar size={12} />
                        {feriado.nome}
                      </span>
                    ) : null;
                  })}
                </div>
              </div>

              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">
                  Empresas de destino *
                </Label>
                <SelectCustom
                  isMulti
                  options={empresasOptions.filter(
                    (e) => e.value !== empresaSelecionada
                  )}
                  value={empresasDestino}
                  onChange={setEmpresasDestino}
                  placeholder="Selecione as empresas"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowReplicarModal(false)}
                  className="flex-1 px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 font-medium rounded-xl transition-all duration-200"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleReplicar}
                  disabled={replicando || empresasDestino.length === 0}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-700 hover:from-orange-600 hover:to-orange-800 text-white font-medium rounded-xl shadow-lg shadow-orange-500/30 transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FiCopy size={18} />
                  {replicando ? "Replicando..." : "Replicar"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Importar Feriados Padroes */}
      {showImportarModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-dark-secondary rounded-card shadow-2xl max-w-lg w-full animate-[slideUp_0.3s_ease-out] border border-neutral-800">
            <div className="p-6 border-b border-neutral-800">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-neutral-100 flex items-center gap-2">
                  <FiDownload className="text-orange-400" />
                  Importar Feriados Nacionais
                </h3>
                <button
                  onClick={() => setShowImportarModal(false)}
                  className="p-2 hover:bg-dark-tertiary rounded-lg transition-colors duration-200"
                >
                  <FiX size={20} className="text-neutral-500" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="bg-gradient-to-r from-blue-900/20 to-cyan-900/20 border border-blue-800/50 rounded-lg p-4">
                <p className="text-sm text-blue-300 mb-3">
                  Os seguintes feriados nacionais serao importados:
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {feriadosPadroes.map((feriado, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 text-sm text-neutral-300"
                    >
                      <FiCheck className="text-green-400" size={14} />
                      <span>
                        {String(feriado.dia).padStart(2, "0")}/
                        {String(feriado.mes).padStart(2, "0")} - {feriado.nome}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">
                  Ano dos feriados
                </Label>
                <Input
                  type="number"
                  value={anoImportacao}
                  onChange={(e) => setAnoImportacao(parseInt(e.target.value) || new Date().getFullYear())}
                  min={2020}
                  max={2100}
                  className="w-full"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowImportarModal(false)}
                  className="flex-1 px-4 py-2.5 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 font-medium rounded-xl transition-all duration-200"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleImportarPadroes}
                  disabled={importando}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-700 hover:from-orange-600 hover:to-orange-800 text-white font-medium rounded-xl shadow-lg shadow-orange-500/30 transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FiDownload size={18} />
                  {importando ? "Importando..." : "Importar"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
