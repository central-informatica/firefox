import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiClock, FiPlus, FiTrash2, FiShield, FiAlertCircle, FiCheck, FiEdit2, FiX, FiSave, FiCalendar
} from "react-icons/fi";
import Input from "../../components/Input/Input";
import Label from "../../components/Label/Label";
import SelectCustom from "../../components/Select/Select";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";

const diasSemana = [
  { value: 0, label: "Domingo" },
  { value: 1, label: "Segunda-feira" },
  { value: 2, label: "Terça-feira" },
  { value: 3, label: "Quarta-feira" },
  { value: 4, label: "Quinta-feira" },
  { value: 5, label: "Sexta-feira" },
  { value: 6, label: "Sábado" },
];

export default function DisponibilidadeCertificado() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [empresas, setEmpresas] = useState([]);
  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [grupos, setGrupos] = useState([]);
  const [grupoSelecionado, setGrupoSelecionado] = useState(null);
  const [regras, setRegras] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    dias_permitidos: [],
    hora_inicio: "08:00",
    hora_fim: "18:00"
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
      setGrupos([
        { value: 1, label: "Equipe Fiscal" },
        { value: 2, label: "Equipe Contábil" },
      ]);
      setGrupoSelecionado({ value: 1, label: "Equipe Fiscal" });
    }
  }, [empresaSelecionada]);

  useEffect(() => {
    if (grupoSelecionado) {
      setRegras([
        {
          id: 1,
          nome: "Horário Comercial",
          dias_permitidos: [1, 2, 3, 4, 5],
          hora_inicio: "08:00",
          hora_fim: "18:00"
        },
        {
          id: 2,
          nome: "Plantão Sábado",
          dias_permitidos: [6],
          hora_inicio: "09:00",
          hora_fim: "13:00"
        },
      ]);
    }
  }, [grupoSelecionado]);

  const getDiasLabel = (dias) => {
    if (dias.length === 7) return "Todos os dias";
    if (dias.length === 0) return "Nenhum dia";

    return dias
      .sort((a, b) => a - b)
      .map(d => diasSemana.find(dia => dia.value === d)?.label.substring(0, 3))
      .join(", ");
  };

  const handleOpenModal = (item = null) => {
    if (item) {
      setEditingId(item.id);
      setFormData({
        nome: item.nome,
        dias_permitidos: item.dias_permitidos,
        hora_inicio: item.hora_inicio,
        hora_fim: item.hora_fim
      });
    } else {
      setEditingId(null);
      setFormData({
        nome: "",
        dias_permitidos: [1, 2, 3, 4, 5],
        hora_inicio: "08:00",
        hora_fim: "18:00"
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
  };

  const toggleDia = (diaValue) => {
    setFormData(prev => ({
      ...prev,
      dias_permitidos: prev.dias_permitidos.includes(diaValue)
        ? prev.dias_permitidos.filter(d => d !== diaValue)
        : [...prev.dias_permitidos, diaValue]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (formData.dias_permitidos.length === 0) {
      toast.error("Selecione pelo menos um dia da semana");
      return;
    }

    if (editingId) {
      setRegras(prev => prev.map(item =>
        item.id === editingId ? { ...item, ...formData } : item
      ));
      toast.success("Regra atualizada com sucesso!");
    } else {
      setRegras(prev => [...prev, { id: Date.now(), ...formData }]);
      toast.success("Regra criada com sucesso!");
    }

    handleCloseModal();
  };

  const handleDelete = (id) => {
    if (confirm("Deseja realmente excluir esta regra de horário?")) {
      setRegras(prev => prev.filter(item => item.id !== id));
      toast.success("Regra excluída com sucesso!");
    }
  };

  return (
    <div className="space-y-6 w-full animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 mb-2 flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-purple-700 rounded-xl shadow-lg">
              <FiClock className="text-white" size={28} />
            </div>
            Horários de Acesso
          </h1>
          <p className="text-neutral-400">Defina quando os certificados podem ser utilizados</p>
        </div>

        <button
          onClick={() => handleOpenModal()}
          disabled={!grupoSelecionado}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-700 hover:from-purple-600 hover:to-purple-800 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <FiPlus size={20} />
          Nova Regra
        </button>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-5">
        <h3 className="font-semibold text-neutral-100 mb-4 flex items-center gap-2">
          <FiShield className="text-purple-400" size={18} />
          Filtros
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-sm font-medium text-neutral-400 mb-2">Empresa</Label>
            <SelectCustom
              placeholder="Selecione uma empresa"
              value={empresaSelecionada}
              onChange={setEmpresaSelecionada}
              options={empresas}
            />
          </div>

          <div>
            <Label className="text-sm font-medium text-neutral-400 mb-2">Grupo de Usuários</Label>
            <SelectCustom
              placeholder="Selecione um grupo"
              value={grupoSelecionado}
              onChange={setGrupoSelecionado}
              options={grupos}
              isDisabled={!empresaSelecionada}
            />
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 border border-purple-800/50 rounded-card p-4">
        <div className="flex gap-3">
          <FiAlertCircle className="text-purple-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-purple-300 mb-1">Como funcionam as regras de horário</p>
            <p className="text-sm text-purple-400">
              Os certificados só poderão ser usados nos dias e horários definidos. Tentativas fora do horário serão automaticamente bloqueadas.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
        {grupoSelecionado ? (
          regras.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-dark-tertiary to-neutral-800 border-b border-neutral-800">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Nome da Regra
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Dias Permitidos
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Horário
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
                  {regras.map((item) => (
                    <tr key={item.id} className="hover:bg-dark-tertiary transition-colors duration-150">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <FiCalendar className="text-purple-400" size={16} />
                          <span className="text-sm font-medium text-neutral-100">{item.nome}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-neutral-400">{getDiasLabel(item.dias_permitidos)}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <FiClock className="text-neutral-500" size={14} />
                          <span className="text-sm text-neutral-400">
                            {item.hora_inicio} às {item.hora_fim}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="badge-permitido">
                          <FiCheck size={12} />
                          Ativa
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenModal(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-purple-900/30 hover:bg-purple-900/50 text-purple-400 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                          >
                            <FiEdit2 size={14} />
                            Editar
                          </button>
                          <button
                            onClick={() => handleDelete(item.id)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer"
                          >
                            <FiTrash2 size={14} />
                            Excluir
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
                  <FiClock size={32} className="text-neutral-500" />
                </div>
                <div>
                  <p className="text-neutral-100 font-medium mb-1">Nenhuma regra cadastrada</p>
                  <p className="text-sm text-neutral-500">Crie regras de horário para restringir o uso dos certificados</p>
                </div>
              </div>
            </div>
          )
        ) : (
          <div className="p-12 text-center">
            <div className="flex flex-col items-center gap-3">
              <div className="p-4 bg-dark-tertiary rounded-full">
                <FiShield size={32} className="text-neutral-500" />
              </div>
              <div>
                <p className="text-neutral-100 font-medium mb-1">Selecione um grupo</p>
                <p className="text-sm text-neutral-500">Escolha um grupo acima para gerenciar horários de acesso</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-dark-secondary rounded-card shadow-2xl max-w-lg w-full animate-[slideUp_0.3s_ease-out] border border-neutral-800">
            <div className="p-6 border-b border-neutral-800">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-neutral-100 flex items-center gap-2">
                  <FiClock className="text-purple-400" />
                  {editingId ? "Editar Regra" : "Nova Regra"}
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
              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-2">Nome da Regra *</Label>
                <Input
                  type="text"
                  placeholder="Ex: Horário Comercial"
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  required
                  className="w-full"
                />
              </div>

              <div>
                <Label className="text-sm font-medium text-neutral-400 mb-3">Dias Permitidos *</Label>
                <div className="grid grid-cols-2 gap-2">
                  {diasSemana.map((dia) => (
                    <button
                      key={dia.value}
                      type="button"
                      onClick={() => toggleDia(dia.value)}
                      className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
                        formData.dias_permitidos.includes(dia.value)
                          ? "bg-purple-600 text-white shadow-md shadow-purple-500/30"
                          : "bg-dark-tertiary text-neutral-400 hover:bg-neutral-700"
                      }`}
                    >
                      {dia.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-neutral-400 mb-2">Hora Início *</Label>
                  <Input
                    type="time"
                    value={formData.hora_inicio}
                    onChange={(e) => setFormData({ ...formData, hora_inicio: e.target.value })}
                    required
                    className="w-full"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium text-neutral-400 mb-2">Hora Fim *</Label>
                  <Input
                    type="time"
                    value={formData.hora_fim}
                    onChange={(e) => setFormData({ ...formData, hora_fim: e.target.value })}
                    required
                    className="w-full"
                  />
                </div>
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
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-500 to-purple-700 hover:from-purple-600 hover:to-purple-800 text-white font-medium rounded-xl shadow-lg shadow-purple-500/30 transition-all duration-200 cursor-pointer"
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
