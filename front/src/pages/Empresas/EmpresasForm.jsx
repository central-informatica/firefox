import { getTimezoneOptions } from "../../services/timezoneService";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  FiBriefcase, FiFileText, FiClock, FiSave, FiArrowLeft, FiCheck, FiTag
} from "react-icons/fi";

import Input from "../../components/Input/Input";
import InputMask from "../../components/Input/InputMask";
import Select from "../../components/Select/Select";
import SelectRamo from "../../components/Select/SelectRamo";
import Label from "../../components/Label/Label";

import {
  getEmpresa,
  createEmpresa,
  updateEmpresa,
} from "../../services/empresasService";

const timezones = Intl.supportedValuesOf("timeZone");
const timezoneOptions = timezones.map((tz) => ({
  value: tz,
  label: tz,
}));

const EmpresaForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const isEdit = !!id;
  const [isLoading, setIsLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const [form, setForm] = useState({
    razao_social: "",
    cnpj: "",
    timezone: "America/Sao_Paulo",
    ramos_id: 1,
  });

  useEffect(() => {
    if (isEdit) {
      getEmpresa(id).then((empresa) => {
        if (empresa) setForm(empresa);
      });
    }
  }, [id, isEdit]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isEdit) {
        await updateEmpresa(id, form);
      } else {
        console.log(form);
        await createEmpresa(form);
      }

      setIsSaved(true);
      setTimeout(() => {
        navigate("/empresas");
      }, 800);
    } catch (error) {
      console.error(error);
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
            onClick={() => navigate("/empresas")}
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-800 transition-all duration-200 cursor-pointer group"
            title="Voltar"
          >
            <FiArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform duration-200" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
              {isEdit ? (
                <>
                  <FiBriefcase className="text-blue-600" />
                  Editar Empresa
                </>
              ) : (
                <>
                  <FiBriefcase className="text-emerald-600" />
                  Nova Empresa
                </>
              )}
            </h1>
            <p className="text-gray-600 text-sm mt-1">
              {isEdit ? "Atualize os dados da empresa" : "Preencha os dados para cadastrar uma nova empresa"}
            </p>
          </div>
        </div>
      </div>

      {/* Form Card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nome da Empresa */}
            <div className="group">
              <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FiFileText className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                Nome da Empresa
              </Label>
              <div className="relative">
                <Input
                  name="razao_social"
                  placeholder="Digite o nome da empresa"
                  value={form.razao_social}
                  onChange={handleChange}
                  required
                  className="w-full transition-all duration-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>
            </div>

            {/* CNPJ */}
            <div className="group">
              <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FiBriefcase className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                CNPJ
              </Label>
              <div className="relative">
                <InputMask
                  name="cnpj"
                  mask="00.000.000/0000-00"
                  placeholder="00.000.000/0000-00"
                  value={form.cnpj}
                  onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
                  required
                  className="w-full transition-all duration-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 font-mono"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Digite apenas números, a máscara será aplicada automaticamente</p>
            </div>

            {/* Ramo de Atuação */}
            <div className="group">
              <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FiTag className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                Ramo de Atuação
              </Label>
              <div className="relative">
                <SelectRamo
                  value={form.ramos_id}
                  onChange={(val) => setForm({ ...form, ramos_id: val })}
                  placeholder="Selecione o ramo de atuação"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Selecione o ramo de atuação da empresa</p>
            </div>

            {/* Fuso Horário */}
            <div className="group">
              <Label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <FiClock className="text-gray-400 group-hover:text-emerald-500 transition-colors duration-200" size={16} />
                Fuso Horário
              </Label>
              <div className="relative">
                <Select
                  options={timezoneOptions}
                  value={
                    form.timezone
                      ? { value: form.timezone, label: form.timezone }
                      : null
                  }
                  onChange={(opt) => setForm({ ...form, timezone: opt.value })}
                  placeholder="Selecione o fuso horário"
                  className="transition-all duration-200"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Selecione o fuso horário onde a empresa está localizada</p>
            </div>

            {/* Divider */}
            <div className="border-t border-gray-100"></div>

            {/* Actions */}
            <div className="flex items-center justify-between gap-4 pt-2">
              <button
                type="button"
                onClick={() => navigate("/empresas")}
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

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-start gap-3">
        <div className="p-2 bg-blue-100 rounded-lg">
          <FiBriefcase className="text-blue-600" size={20} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-blue-900 mb-1">Informações importantes</h3>
          <p className="text-sm text-blue-800">
            Após cadastrar a empresa, você poderá adicionar membros, certificados e configurar permissões específicas.
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmpresaForm;
