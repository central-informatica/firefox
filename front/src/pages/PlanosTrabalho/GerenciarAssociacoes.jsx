import { useState } from "react";
import { useNavigate } from "react-router-dom";

import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectPlanoTrabalho from "../../components/Select/SelectPlanoTrabalho";
import SelectGrupo from "../../components/Select/SelectGrupo";
import Label from "../../components/Label/Label";

import {
  FiArrowLeft,
  FiUsers,
  FiCheckCircle,
  FiAlertCircle,
} from "react-icons/fi";

export default function GerenciarAssociacoes() {
  const navigate = useNavigate();

  // Estados principais
  const [empresaId, setEmpresaId] = useState(null);
  const [planoTrabalho, setPlanoTrabalho] = useState(null);
  const [grupo, setGrupo] = useState(null);

  // UI
  const [notification, setNotification] = useState(null);

  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Handlers
  const handleEmpresaChange = (id) => {
    setEmpresaId(id);
    setPlanoTrabalho(null);
    setGrupo(null);
  };

  const handlePlanoChange = (opt) => {
    setPlanoTrabalho(opt);
    setGrupo(null);
  };

  const handleGrupoChange = (opt) => {
    setGrupo(opt);
  };

  // IDs derivados
  const planoTrabalhoId =
    planoTrabalho && typeof planoTrabalho === "object"
      ? planoTrabalho.value
      : null;

  return (
    <div className="space-y-6 w-full animate-[fadeInUp_0.6s_ease-out]">
      {/* Notification */}
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-6 py-4 rounded-xl shadow-lg ${
            notification.type === "success"
              ? "bg-emerald-500 text-white"
              : "bg-red-500 text-white"
          }`}
        >
          {notification.type === "success" ? (
            <FiCheckCircle size={20} />
          ) : (
            <FiAlertCircle size={20} />
          )}
          <span className="font-medium">{notification.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-800 transition"
        >
          <FiArrowLeft size={20} />
        </button>

        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <FiUsers className="text-purple-600" />
            Gerenciar Associações
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Organize grupos dentro dos planos de trabalho da empresa
          </p>
        </div>
      </div>

      {/* Seletores */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Empresa */}
          <div>
            <Label className="text-sm font-semibold text-gray-700 mb-2">
              Empresa
            </Label>
            <SelectEmpresa value={empresaId} onChange={handleEmpresaChange} />
          </div>

          {/* Plano */}
          <div>
            <Label className="text-sm font-semibold text-gray-700 mb-2">
              Plano de Trabalho
            </Label>
            <SelectPlanoTrabalho
              empresaId={empresaId}
              value={planoTrabalhoId}
              onChange={handlePlanoChange}
              isDisabled={!empresaId}
            />
          </div>

          {/* Grupo */}
          <div>
            <Label className="text-sm font-semibold text-gray-700 mb-2">
              Grupo do Plano
            </Label>
            <SelectGrupo
              empresaId={empresaId}
              planoTrabalhoId={planoTrabalhoId}
              value={grupo}
              onChange={handleGrupoChange}
              isDisabled={!planoTrabalhoId}
            />
          </div>
        </div>
      </div>

      {/* Empty State */}
      {!grupo && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiUsers className="text-gray-400" size={32} />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              Nenhum grupo selecionado
            </h3>
            <p className="text-gray-600">
              Selecione uma empresa e um plano de trabalho. Em seguida, escolha
              um grupo existente ou crie um novo grupo diretamente dentro do
              plano selecionado.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
