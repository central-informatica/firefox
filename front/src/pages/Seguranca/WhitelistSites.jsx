import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiGlobe, FiPlus, FiTrash2, FiShield, FiAlertCircle, FiCheck, FiEdit2, FiX, FiSave
} from "react-icons/fi";
import Input from "../../components/Input/Input";
import Label from "../../components/Label/Label";
import SelectCustom from "../../components/Select/Select";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";

export default function WhitelistSites() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresas, setEmpresas] = useState([]);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [certificados, setCertificados] = useState([]);
  const [certificadoSelecionado, setCertificadoSelecionado] = useState(null);
  const [whitelist, setWhitelist] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    url: "",
    descricao: ""
  });

  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario().then((lista) => {
      const opcoes = lista.map((e) => ({
        value: e.id,
        label: e.razao_social,
      }));
      setEmpresas(opcoes);

      if (opcoes.length > 0) {
        setEmpresaSelecionada(opcoes[0]);
      }
    });
  }, [user]);

  useEffect(() => {
    if (empresaSelecionada) {
      setCertificados([
        { value: 1, label: "Certificado A1 - Empresa XYZ" },
        { value: 2, label: "Certificado A3 - NF-e" },
      ]);
      setCertificadoSelecionado({ value: 1, label: "Certificado A1 - Empresa XYZ" });
    }
  }, [empresaSelecionada]);

  useEffect(() => {
    if (certificadoSelecionado) {
      setWhitelist([
        { id: 1, url: "https://nfe.fazenda.gov.br", descricao: "Portal NF-e" },
        { id: 2, url: "https://www.sefaz.rs.gov.br", descricao: "SEFAZ RS" },
      ]);
    }
  }, [certificadoSelecionado]);

  const handleOpenModal = (item = null) => {
    if (item) {
      setEditingId(item.id);
      setFormData({
        url: item.url,
        descricao: item.descricao
      });
    } else {
      setEditingId(null);
      setFormData({ url: "", descricao: "" });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ url: "", descricao: "" });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (editingId) {
      setWhitelist(prev => prev.map(item =>
        item.id === editingId ? { ...item, ...formData } : item
      ));
      toast.success("Site atualizado com sucesso!");
    } else {
      setWhitelist(prev => [...prev, { id: Date.now(), ...formData }]);
      toast.success("Site adicionado à whitelist!");
    }

    handleCloseModal();
  };

  const handleDelete = (id) => {
    if (confirm("Deseja realmente remover este site da whitelist?")) {
      setWhitelist(prev => prev.filter(item => item.id !== id));
      toast.success("Site removido da whitelist!");
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg">
              <FiGlobe className="text-white" size={28} />
            </div>
            Whitelist de Sites
          </h1>
          <p className="text-gray-600">Controle quais sites podem usar cada certificado digital</p>
        </div>

        <button
          onClick={() => handleOpenModal()}
          disabled={!certificadoSelecionado}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <FiPlus size={20} />
          Adicionar Site
        </button>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <FiShield className="text-blue-600" size={18} />
          Filtros
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-sm font-medium text-gray-700 mb-2">Empresa</Label>
            <SelectCustom
              placeholder="Selecione uma empresa"
              value={empresaSelecionada}
              onChange={setEmpresaSelecionada}
              options={empresas}
            />
          </div>

          <div>
            <Label className="text-sm font-medium text-gray-700 mb-2">Certificado</Label>
            <SelectCustom
              placeholder="Selecione um certificado"
              value={certificadoSelecionado}
              onChange={setCertificadoSelecionado}
              options={certificados}
              isDisabled={!empresaSelecionada}
            />
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
        <div className="flex gap-3">
          <FiAlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-blue-900 mb-1">Como funciona a whitelist</p>
            <p className="text-sm text-blue-800">
              Apenas os sites cadastrados aqui poderão usar o certificado selecionado. Sites não listados serão bloqueados automaticamente.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {certificadoSelecionado ? (
          whitelist.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      URL do Site
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Descrição
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {whitelist.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50 transition-colors duration-150">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <FiGlobe className="text-blue-500" size={16} />
                          <span className="text-sm font-medium text-gray-800">{item.url}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-600">{item.descricao}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium">
                          <FiCheck size={12} />
                          Ativo
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenModal(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                          >
                            <FiEdit2 size={14} />
                            Editar
                          </button>
                          <button
                            onClick={() => handleDelete(item.id)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
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
                <div className="p-4 bg-gray-100 rounded-full">
                  <FiGlobe size={32} className="text-gray-400" />
                </div>
                <div>
                  <p className="text-gray-700 font-medium mb-1">Nenhum site cadastrado</p>
                  <p className="text-sm text-gray-500">Adicione sites à whitelist para restringir o uso do certificado</p>
                </div>
              </div>
            </div>
          )
        ) : (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-gray-100 rounded-full">
                <FiShield size={32} className="text-gray-400" />
              </div>
              <div>
                <p className="text-gray-700 font-medium mb-1">Selecione um certificado</p>
                <p className="text-sm text-gray-500">Escolha um certificado acima para gerenciar sua whitelist</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-[slideUp_0.3s_ease-out]">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <FiGlobe className="text-blue-600" />
                  {editingId ? "Editar Site" : "Adicionar Site"}
                </h3>
                <button
                  onClick={handleCloseModal}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                >
                  <FiX size={20} className="text-gray-500" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <Label className="text-sm font-medium text-gray-700 mb-2">URL do Site *</Label>
                <Input
                  type="url"
                  placeholder="https://exemplo.com.br"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">Digite a URL completa do site (com https://)</p>
              </div>

              <div>
                <Label className="text-sm font-medium text-gray-700 mb-2">Descrição</Label>
                <Input
                  type="text"
                  placeholder="Ex: Portal NF-e, Sistema contábil..."
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  className="w-full"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="flex-1 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-xl transition-all duration-200"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-200 cursor-pointer"
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
