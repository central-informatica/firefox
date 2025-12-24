import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiWifi, FiPlus, FiTrash2, FiShield, FiAlertCircle, FiCheck, FiEdit2, FiX, FiSave, FiUser, FiLock
} from "react-icons/fi";
import Input from "../../components/Input/Input";
import InputMask from "../../components/Input/InputMask";
import Label from "../../components/Label/Label";
import SelectCustom from "../../components/Select/Select";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { getUsuarios } from "../../services/usuariosService";
import { useAuth } from "../../auth/useAuth";

export default function IpFixoUsuario() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresas, setEmpresas] = useState([]);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [usuarios, setUsuarios] = useState([]);
  const [restricoes, setRestricoes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    usuario_id: null,
    ip_fixo: "",
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

    getUsuarios().then((lista) => {
      setUsuarios(lista);
    });
  }, [user]);

  useEffect(() => {
    if (empresaSelecionada) {
      setRestricoes([
        {
          id: 1,
          usuario_id: 1,
          usuario_nome: "Fabricio Peruzzolo",
          usuario_email: "fabricio@centrnet.com.br",
          ip_fixo: "192.168.1.100",
          descricao: "Computador escritório"
        },
        {
          id: 2,
          usuario_id: 2,
          usuario_nome: "Rafaela da Silva",
          usuario_email: "rafa@provedor.com.br",
          ip_fixo: "192.168.1.101",
          descricao: "Notebook pessoal"
        },
      ]);
    }
  }, [empresaSelecionada]);

  const handleOpenModal = (item = null) => {
    if (item) {
      setEditingId(item.id);
      setFormData({
        usuario_id: item.usuario_id,
        ip_fixo: item.ip_fixo,
        descricao: item.descricao
      });
    } else {
      setEditingId(null);
      setFormData({
        usuario_id: null,
        ip_fixo: "",
        descricao: ""
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.usuario_id) {
      toast.error("Selecione um usuário");
      return;
    }

    const usuario = usuarios.find(u => u.id === formData.usuario_id);

    if (editingId) {
      setRestricoes(prev => prev.map(item =>
        item.id === editingId ? {
          ...item,
          ...formData,
          usuario_nome: usuario.nome,
          usuario_email: usuario.email
        } : item
      ));
      toast.success("Restrição atualizada com sucesso!");
    } else {
      const jaExiste = restricoes.some(r => r.usuario_id === formData.usuario_id);
      if (jaExiste) {
        toast.error("Este usuário já possui uma restrição de IP!");
        return;
      }

      setRestricoes(prev => [...prev, {
        id: Date.now(),
        ...formData,
        usuario_nome: usuario.nome,
        usuario_email: usuario.email
      }]);
      toast.success("Restrição criada com sucesso!");
    }

    handleCloseModal();
  };

  const handleDelete = (id) => {
    if (confirm("Deseja realmente remover esta restrição de IP?")) {
      setRestricoes(prev => prev.filter(item => item.id !== id));
      toast.success("Restrição removida com sucesso!");
    }
  };

  const usuariosOptions = usuarios.map(u => ({
    value: u.id,
    label: `${u.nome} (${u.email})`
  }));

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg">
              <FiWifi className="text-white" size={28} />
            </div>
            IP Fixo por Usuário
          </h1>
          <p className="text-gray-600">Restrinja o acesso aos certificados por endereço IP</p>
        </div>

        <button
          onClick={() => handleOpenModal()}
          disabled={!empresaSelecionada}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold rounded-xl shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <FiPlus size={20} />
          Nova Restrição
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <FiShield className="text-orange-600" size={18} />
          Filtros
        </h3>

        <div className="max-w-md">
          <Label className="text-sm font-medium text-gray-700 mb-2">Empresa</Label>
          <SelectCustom
            placeholder="Selecione uma empresa"
            value={empresaSelecionada}
            onChange={setEmpresaSelecionada}
            options={empresas}
          />
        </div>
      </div>

      <div className="bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-xl p-4">
        <div className="flex gap-3">
          <FiAlertCircle className="text-orange-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-orange-900 mb-1">Como funciona a restrição por IP</p>
            <p className="text-sm text-orange-800">
              Quando um usuário possui IP fixo configurado, ele só poderá acessar certificados a partir desse endereço IP. Tentativas de outros IPs serão bloqueadas.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {empresaSelecionada ? (
          restricoes.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Usuário
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      IP Fixo
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
                  {restricoes.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50 transition-colors duration-150">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                            {item.usuario_nome.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-800">{item.usuario_nome}</div>
                            <div className="text-xs text-gray-500">{item.usuario_email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <FiWifi className="text-orange-500" size={16} />
                          <span className="text-sm font-mono font-medium text-gray-800">{item.ip_fixo}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-600">{item.descricao || "-"}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 px-3 py-1 bg-orange-50 text-orange-700 rounded-full text-xs font-medium">
                          <FiLock size={12} />
                          Restrito
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenModal(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 hover:bg-orange-100 text-orange-700 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
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
                  <FiWifi size={32} className="text-gray-400" />
                </div>
                <div>
                  <p className="text-gray-700 font-medium mb-1">Nenhuma restrição cadastrada</p>
                  <p className="text-sm text-gray-500">Configure IPs fixos para aumentar a segurança</p>
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
                <p className="text-gray-700 font-medium mb-1">Selecione uma empresa</p>
                <p className="text-sm text-gray-500">Escolha uma empresa acima para gerenciar restrições de IP</p>
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
                  <FiWifi className="text-orange-600" />
                  {editingId ? "Editar Restrição" : "Nova Restrição"}
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
                <Label className="text-sm font-medium text-gray-700 mb-2">Usuário *</Label>
                <SelectCustom
                  placeholder="Selecione um usuário"
                  value={usuariosOptions.find(opt => opt.value === formData.usuario_id)}
                  onChange={(opt) => setFormData({ ...formData, usuario_id: opt.value })}
                  options={usuariosOptions}
                  isDisabled={!!editingId}
                />
                {editingId && (
                  <p className="text-xs text-gray-500 mt-1">Não é possível alterar o usuário após criar a restrição</p>
                )}
              </div>

              <div>
                <Label className="text-sm font-medium text-gray-700 mb-2">Endereço IP *</Label>
                <InputMask
                  name="ip_fixo"
                  mask="000.000.000.000"
                  placeholder="192.168.1.100"
                  value={formData.ip_fixo}
                  onChange={(e) => setFormData({ ...formData, ip_fixo: e.target.value })}
                  required
                  className="w-full font-mono"
                />
                <p className="text-xs text-gray-500 mt-1">Digite o endereço IP v4 (ex: 192.168.1.100)</p>
              </div>

              <div>
                <Label className="text-sm font-medium text-gray-700 mb-2">Descrição</Label>
                <Input
                  type="text"
                  placeholder="Ex: Computador do escritório, Notebook..."
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
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium rounded-xl shadow-lg shadow-orange-500/30 transition-all duration-200 cursor-pointer"
                >
                  <FiSave size={18} />
                  {editingId ? "Atualizar" : "Criar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
