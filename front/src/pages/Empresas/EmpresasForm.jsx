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
            className="p-2 hover:bg-dark-secondary rounded-lg text-neutral-400 hover:text-neutral-100 transition-all duration-200 cursor-pointer group"
            title="Voltar"
          >
            <FiArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform duration-200" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-neutral-100 flex items-center gap-3 font-montserrat">
              {isEdit ? (
                <>
                  <FiBriefcase className="text-status-monitorado" />
                  Editar Empresa
                </>
              ) : (
                <>
                  <FiBriefcase className="text-xfire-orange" />
                  Nova Empresa
                </>
              )}
            </h1>
            <p className="text-neutral-400 text-sm mt-1">
              {isEdit ? "Atualize os dados da empresa" : "Preencha os dados para cadastrar uma nova empresa"}
            </p>
          </div>
        </div>
      </div>

      {/* Form Card */}
      <div className="bg-dark-secondary rounded-card border border-neutral-900 overflow-hidden">
        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nome da Empresa */}
            <div className="group">
              <Label className="text-sm font-semibold text-neutral-300 mb-2 flex items-center gap-2">
                <FiFileText className="text-neutral-500 group-hover:text-xfire-orange transition-colors duration-200" size={16} />
                Nome da Empresa
              </Label>
              <div className="relative">
                <Input
                  name="razao_social"
                  placeholder="Digite o nome da empresa"
                  value={form.razao_social}
                  onChange={handleChange}
                  required
                  className="w-full"
                />
              </div>
            </div>

            {/* CNPJ */}
            <div className="group">
              <Label className="text-sm font-semibold text-neutral-300 mb-2 flex items-center gap-2">
                <FiBriefcase className="text-neutral-500 group-hover:text-xfire-orange transition-colors duration-200" size={16} />
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
                  className="w-full font-mono"
                />
              </div>
              <p className="text-xs text-neutral-500 mt-1">Digite apenas numeros, a mascara sera aplicada automaticamente</p>
            </div>

            {/* Ramo de Atuacao */}
            <div className="group">
              <Label className="text-sm font-semibold text-neutral-300 mb-2 flex items-center gap-2">
                <FiTag className="text-neutral-500 group-hover:text-xfire-orange transition-colors duration-200" size={16} />
                Ramo de Atuacao
              </Label>
              <div className="relative">
                <SelectRamo
                  value={form.ramos_id}
                  onChange={(val) => setForm({ ...form, ramos_id: val })}
                  placeholder="Selecione o ramo de atuacao"
                />
              </div>
              <p className="text-xs text-neutral-500 mt-1">Selecione o ramo de atuacao da empresa</p>
            </div>

            {/* Fuso Horario */}
            <div className="group">
              <Label className="text-sm font-semibold text-neutral-300 mb-2 flex items-center gap-2">
                <FiClock className="text-neutral-500 group-hover:text-xfire-orange transition-colors duration-200" size={16} />
                Fuso Horario
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
                  placeholder="Selecione o fuso horario"
                />
              </div>
              <p className="text-xs text-neutral-500 mt-1">Selecione o fuso horario onde a empresa esta localizada</p>
            </div>

            {/* Divider */}
            <div className="border-t border-neutral-800"></div>

            {/* Actions */}
            <div className="flex items-center justify-between gap-4 pt-2">
              <button
                type="button"
                onClick={() => navigate("/empresas")}
                className="px-6 py-3 bg-dark-tertiary hover:bg-neutral-800 text-neutral-300 font-semibold rounded-xl transition-all duration-200 cursor-pointer border border-neutral-800"
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
                      ? "bg-status-permitido text-white"
                      : "bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white shadow-xfire-orange/30 hover:shadow-xl hover:shadow-xfire-orange/40 hover:-translate-y-0.5 active:translate-y-0"
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
      <div className="bg-status-monitorado/10 border border-status-monitorado/30 rounded-xl p-4 flex items-start gap-3">
        <div className="p-2 bg-status-monitorado/20 rounded-lg">
          <FiBriefcase className="text-status-monitorado" size={20} />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-status-monitorado mb-1">Informacoes importantes</h3>
          <p className="text-sm text-status-monitorado/80">
            Apos cadastrar a empresa, voce podera adicionar membros, certificados e configurar permissoes especificas.
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmpresaForm;
