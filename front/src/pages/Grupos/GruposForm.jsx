import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  FiUsers,
  FiSave,
  FiArrowLeft,
  FiInfo,
} from "react-icons/fi";
import { toast } from "react-toastify";

import Input from "../../components/Input/Input";
import TextArea from "../../components/TextArea/TextArea";
import Label from "../../components/Label/Label";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectPlanoTrabalho from "../../components/Select/SelectPlanoTrabalho";

import {
  getGrupoById,
  criarGrupo,
  atualizarGrupo,
} from "../../services/gruposService";

const GruposForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [form, setForm] = useState({
    nome: "",
    descricao: "",
  });

  const [empresaSelecionada, setEmpresaSelecionada] = useState(null);
  const [planoSelecionado, setPlanoSelecionado] = useState(null);

  useEffect(() => {
    if (!isEdit) return;

    getGrupoById(id).then((data) => {
      setForm({
        nome: data.nome ?? "",
        descricao: data.descricao ?? "",
      });
    });
  }, [id, isEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handlePlanoChange =(plano_id) => {
    setPlanoSelecionado(plano_id);
  }

  const handleEmpresaChange = (empresa) => {
    setEmpresaSelecionada(empresa);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {};
    if (form.nome?.trim()) payload.nome = form.nome.trim();
    if (empresaSelecionada) {
      payload.empresa_id = empresaSelecionada;
    }else{
      toast.warning("Selecione uma empresa");
      return
    }
    if (planoSelecionado) {
      payload.plano_id = planoSelecionado;
    }else{
      toast.warning("Selecione um plano de trabalho");
      return
    }
    if (Object.keys(payload).length === 0) return;

    const response = isEdit
      ? await atualizarGrupo(id, payload)
      : await criarGrupo(payload);

    if (response) {
      navigate("/grupos");
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={() => navigate("/grupos")}
          className="p-2 hover:bg-dark-tertiary rounded-lg text-neutral-400 hover:text-neutral-100"
        >
          <FiArrowLeft size={20} />
        </button>
        <h1 className="text-3xl font-bold font-montserrat text-neutral-100 flex items-center gap-3">
          <FiUsers className="text-blue-400" />
          {isEdit ? "Editar Grupo" : "Novo Grupo"}
        </h1>
      </div>

      {/* Form */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <div className="flex flex-col md:flex-row gap-4">
            {/* Empresa */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-neutral-400 mb-2">
                Empresa
              </label>

              <SelectEmpresa
                value={empresaSelecionada}
                onChange={handleEmpresaChange}
              />
            </div>

            {/* Plano de Trabalho */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-neutral-400 mb-2">
                Plano de trabalho
              </label>

              <SelectPlanoTrabalho
                empresaId={empresaSelecionada}
                value={planoSelecionado}
                onChange={handlePlanoChange}
              />
            </div>
          </div>
            <Label>Nome do Grupo</Label>
            <Input
              name="nome"
              value={form.nome}
              onChange={handleChange}
              placeholder="Digite o nome do grupo"
              required
            />
          </div>

          <div>
            <Label>Descrição</Label>
            <TextArea
              name="descricao"
              value={form.descricao}
              onChange={handleChange}
              placeholder="Descreva o objetivo do grupo"
              rows={5}
            />
          </div>

          {form.descricao && (
            <div className="flex items-center gap-2 text-xs text-neutral-500">
              <FiInfo size={14} />
              <span>{form.descricao.length} caracteres</span>
            </div>
          )}

          <div className="flex justify-between pt-4">
            <button
              type="button"
              onClick={() => navigate("/grupos")}
              className="px-6 py-3 bg-dark-tertiary hover:bg-neutral-800 text-neutral-100 rounded-xl"
            >
              Cancelar
            </button>

            <button
              type="submit"
              className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-xfire-orange to-xfire-red hover:from-xfire-orange/90 hover:to-xfire-red/90 text-white font-semibold rounded-xl"
            >
              <FiSave size={20} />
              {isEdit ? "Atualizar" : "Salvar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GruposForm;
