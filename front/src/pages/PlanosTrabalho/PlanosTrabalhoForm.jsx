import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FiFlag, FiFileText, FiAlignLeft, FiSave, FiArrowLeft, FiCheck, FiInfo, FiBriefcase
} from "react-icons/fi";

import Input from "../../components/Input/Input";
import TextArea from "../../components/TextArea/TextArea";
import Label from "../../components/Label/Label";
import SelectEmpresa from "../../components/Select/SelectEmpresa";

import {
  getPlanoTrabalho,
  criarPlanoTrabalho,
  atualizarPlanoTrabalho,
} from "../../services/planosTrabalhoService";

const PlanosTrabalhoForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const [form, setForm] = useState({
    empresa_id: null,
    nome: "",
    descricao: "",
  });

  useEffect(() => {
    if (!isEdit) return;

    getPlanoTrabalho(id).then((data) => {
      setForm({
        empresa_id: data.empresa_id ?? null,
        nome: data.nome ?? "",
        descricao: data.descricao ?? "",
      });
    });
  }, [id, isEdit]);


  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.nome || form.nome.trim() === "") {
      toast.warning("Informe o nome do plano.");
      return;
    }

    if (!isEdit && !form.empresa_id) {
      toast.warning("Selecione uma empresa.");
      return;
    }

    setIsLoading(true);

    try {
      const payload = {
        nome: form.nome.trim(),
        descricao: form.descricao?.trim() || "",
      };

      let response;
      if (isEdit) {
        response = await atualizarPlanoTrabalho(id, payload);
      } else {
        response = await criarPlanoTrabalho({
          ...payload,
          empresa_id: form.empresa_id,
        });
      }

      if (response.ok) {
        setIsSaved(true);
        toast.success(isEdit ? "Plano atualizado com sucesso!" : "Plano criado com sucesso!");
        setTimeout(() => navigate("/planos"), 1000);
      } else {
        const errorText = await response.text();
        toast.error(errorText || "Erro ao salvar plano.");
      }
    } catch (error) {
      console.error("Erro ao salvar plano:", error);
      toast.error("Erro ao salvar plano.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6 animate-[fadeInUp_0.6s_ease-out]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => navigate("/planos")}
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-800 transition-all duration-200 cursor-pointer group"
            title="Voltar"
          >
            <FiArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform duration-200" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
              {isEdit ? (
                <>
                  <FiFlag className="text-blue-600" />
                  Editar Plano de Trabalho
                </>
              ) : (
                <>
                  <FiFlag className="text-emerald-600" />
                  Novo Plano de Trabalho
                </>
              )}
            </h1>
            <p className="text-gray-600 text-sm mt-1">
              {isEdit ? "Atualize as informações do plano de trabalho" : "Crie um novo plano de trabalho para organizar suas atividades"}
            </p>
          </div>
        </div>
      </div>

      {/* Form Card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Empresa */}
            {!isEdit && (
              <div className="group">
                <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <FiBriefcase className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                  Empresa *
                </Label>
                <SelectEmpresa
                  placeholder="Selecione uma empresa"
                  value={form.empresa_id}
                  onChange={(val) => setForm(prev => ({ ...prev, empresa_id: val }))}
                />
                <p className="text-xs text-gray-500 mt-1">Selecione a empresa para este plano de trabalho</p>
              </div>
            )}

            {/* Nome do Plano */}
            <div className="group">
              <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FiFileText className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                Nome do Plano *
              </Label>
              <div className="relative">
                <Input
                  name="nome"
                  placeholder="Digite o nome do plano de trabalho"
                  value={form.nome}
                  onChange={handleChange}
                  required
                  className="w-full transition-all duration-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Escolha um nome descritivo e fácil de identificar</p>
            </div>

            {/* Descrição */}
            <div className="group">
              <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FiAlignLeft className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                Descrição
              </Label>
              <div className="relative">
                <TextArea
                  name="descricao"
                  placeholder="Descreva os objetivos e atividades do plano de trabalho..."
                  value={form.descricao}
                  onChange={handleChange}
                  className="w-full transition-all duration-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 min-h-[120px] resize-y"
                  rows={5}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Adicione detalhes sobre o que este plano de trabalho irá gerenciar</p>
            </div>

            {/* Character Counter */}
            {form.descricao && (
              <div className="flex items-center gap-2 text-xs text-gray-500 animate-[fadeIn_0.3s_ease-out]">
                <FiInfo size={14} />
                <span>{form.descricao.length} caracteres</span>
              </div>
            )}

            {/* Divider */}
            <div className="border-t border-gray-100"></div>

            {/* Actions */}
            <div className="flex items-center justify-between gap-4 pt-2">
              <button
                type="button"
                onClick={() => navigate("/planos")}
                className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all duration-200 cursor-pointer"
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={isLoading || isSaved}
                className={`
                  inline-flex items-center gap-2 px-8 py-3 font-semibold rounded-xl
                  shadow-lg transition-all duration-300 transform cursor-pointer
                  ${
                    isSaved
                      ? "bg-emerald-500 text-white"
                      : "bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 hover:-translate-y-0.5 active:translate-y-0"
                  }
                  disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none
                `}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Salvando...</span>
                  </>
                ) : isSaved ? (
                  <>
                    <FiCheck size={20} className="animate-[bounce_0.5s_ease-in-out]" />
                    <span>Salvo!</span>
                  </>
                ) : (
                  <>
                    <FiSave size={20} />
                    <span>{isEdit ? "Atualizar" : "Salvar"}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-purple-50 border border-purple-100 rounded-xl p-4 flex items-start gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <FiFlag className="text-purple-600" size={20} />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-purple-900 mb-1">Planos de Trabalho</h3>
            <p className="text-sm text-purple-800">
              Organize grupos de usuários e gerencie permissões de acesso aos certificados.
            </p>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-start gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FiInfo className="text-blue-600" size={20} />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-1">Próximos passos</h3>
            <p className="text-sm text-blue-800">
              Após criar o plano, você poderá adicionar grupos e configurar regras de acesso.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanosTrabalhoForm;
