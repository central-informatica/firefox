import { useState, useEffect } from "react";
import { toast } from "react-toastify";
import {
  FiGlobe, FiPlus, FiTrash2, FiShield, FiAlertCircle, FiCheck, FiEdit2, FiX, FiSave, FiXCircle
} from "react-icons/fi";
import Input from "../../components/Input/Input";
import Label from "../../components/Label/Label";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import {
  listarGlobalUrlsPaginado,
  createGlobalUrl,
  updateGlobalUrl,
  deleteGlobalUrl
} from "../../services/globalUrlsService";

export default function GlobalURLs() {
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    url: "",
    inativo: false,
    empresa_id: null
  });

  const carregarSites = async () => {
    if (!empresaSelecionada) {
      setSites([]);
      return;
    }

    setLoading(true);
    try {
      const response = await listarGlobalUrlsPaginado({
        empresaId: empresaSelecionada,
        page: 1,
        limit: 100,
      });
      setSites(response.data || []);
    } catch (error) {
      console.error("Erro ao carregar sites:", error);
      toast.error("Erro ao carregar sites");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarSites();
  }, [empresaSelecionada]);

  const handleOpenModal = (item = null) => {
    if (item) {
      setEditingId(item.global_urls_id);
      setFormData({
        url: item.url || "",
        inativo: item.inativo || false,
        empresa_id: item.empresa_id
      });
    } else {
      setEditingId(null);
      setFormData({
        url: "",
        inativo: false,
        empresa_id: empresaSelecionada
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ url: "", inativo: false, empresa_id: null });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.url) {
      toast.error("Informe a URL do site");
      return;
    }

    if (!formData.empresa_id) {
      toast.error("Selecione uma empresa");
      return;
    }

    try {
      if (editingId) {
        await updateGlobalUrl(editingId, {
          url: formData.url,
          inativo: formData.inativo
        });
        toast.success("Site atualizado com sucesso!");
      } else {
        await createGlobalUrl({
          url: formData.url,
          inativo: formData.inativo,
          empresa_id: formData.empresa_id
        });
        toast.success("Site adicionado com sucesso!");
      }

      handleCloseModal();
      carregarSites();
    } catch (error) {
      console.error("Erro ao salvar site:", error);
      toast.error("Erro ao salvar site");
    }
  };

  const handleDelete = async (id) => {
    if (confirm("Deseja realmente remover este site?")) {
      try {
        await deleteGlobalUrl(id);
        toast.success("Site removido com sucesso!");
        carregarSites();
      } catch (error) {
        console.error("Erro ao remover site:", error);
        toast.error("Erro ao remover site");
      }
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl shadow-lg">
              <FiGlobe className="text-white" size={28} />
            </div>
            Gerência de Sites
          </h1>
          <p className="text-neutral-400">Controle quais sites podem usar cada certificado digital</p>
        </div>

        <button
          onClick={() => handleOpenModal()}
          disabled={!empresaSelecionada}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <FiPlus size={20} />
          Adicionar Site
        </button>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5">
        <h3 className="font-semibold text-neutral-100 mb-4 flex items-center gap-2">
          <FiShield className="text-blue-400" size={18} />
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

      <div className="bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border border-blue-800/50 rounded-card p-4">
        <div className="flex gap-3">
          <FiAlertCircle className="text-blue-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-blue-300 mb-1">Como funciona a gerência de sites</p>
            <p className="text-sm text-blue-400">
              Apenas os sites cadastrados aqui poderão usar o certificado selecionado. Sites não listados serão bloqueados automaticamente.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
        {!empresaSelecionada ? (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-dark-tertiary rounded-full">
                <FiShield size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Selecione uma empresa</p>
                <p className="text-sm text-neutral-500">Escolha uma empresa acima para gerenciar os sites</p>
              </div>
            </div>
          </div>
        ) : loading ? (
          <div className="p-12 text-center">
            <p className="text-neutral-400">Carregando...</p>
          </div>
        ) : sites.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-dark-tertiary to-neutral-800 border-b border-neutral-800">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    URL do Site
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800">
                {sites.map((item) => (
                  <tr key={item.global_urls_id} className="hover:bg-dark-tertiary transition-colors duration-150">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <FiGlobe className="text-blue-400" size={16} />
                        <span className="text-sm font-medium text-neutral-100">{item.url}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {item.inativo ? (
                        <span className="badge-bloqueado">
                          <FiXCircle size={12} />
                          Inativo
                        </span>
                      ) : (
                        <span className="badge-permitido">
                          <FiCheck size={12} />
                          Ativo
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
                          onClick={() => handleDelete(item.global_urls_id)}
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
                <FiGlobe size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Nenhum site cadastrado</p>
                <p className="text-sm text-neutral-500">Adicione sites para restringir o uso do certificado</p>
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
                  <FiGlobe className="text-blue-400" />
                  {editingId ? "Editar Site" : "Adicionar Site"}
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
                <Label className="text-sm font-medium text-neutral-400 mb-2">URL do Site *</Label>
                <Input
                  type="url"
                  placeholder="https://exemplo.com.br"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                  className="w-full"
                />
                <p className="text-xs text-neutral-500 mt-1">Digite a URL completa do site (com https://)</p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="inativo"
                  checked={formData.inativo}
                  onChange={(e) => setFormData({ ...formData, inativo: e.target.checked })}
                  className="w-4 h-4 text-blue-600 bg-dark-tertiary border-neutral-700 rounded focus:ring-blue-500"
                />
                <Label htmlFor="inativo" className="text-sm font-medium text-neutral-400">
                  Inativo
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
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white font-medium rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-200 cursor-pointer"
                >
                  <FiSave size={18} />
                  {editingId ? "Atualizar" : "Adicionar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
