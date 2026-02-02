import { useEffect, useState } from "react";
import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectGrupo from "../../components/Select/SelectGrupo";
import SelectPlanoTrabalho from "../../components/Select/SelectPlanoTrabalho";
import Label from "../../components/Label/Label";

import {
  FiArrowLeft,
  FiUsers,
  FiShield,
  FiChevronRight,
  FiPlus,
  FiX,
  FiCheckCircle,
  FiAlertCircle,
} from "react-icons/fi";

export default function GerenciarAssociacoes() {
  // ESTADOS MANTIDOS COMO NO ARQUIVO ORIGINAL
  const [empresaId, setEmpresaId] = useState(null);
  const [planoTrabalho, setPlanoTrabalho] = useState(null);
  const [grupo, setGrupo] = useState(null);

  // Estados de UI
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Estados de seleção
  const [planos, setPlanos] = useState([]);
  const [grupos, setGrupos] = useState([]);
  const [selectedPlano, setSelectedPlano] = useState("");
  const [selectedGrupo, setSelectedGrupo] = useState("");

  // Estados de dados
  const [todosUsuarios, setTodosUsuarios] = useState([]);
  const [todosCertificados, setTodosCertificados] = useState([]);
  const [usuariosNoGrupo, setUsuariosNoGrupo] = useState([]);
  const [certificadosNoGrupo, setCertificadosNoGrupo] = useState([]);

  const grupoSelecionado = grupos.find((g) => g.id === Number(selectedGrupo));

  // Função auxiliar para mostrar notificações
  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  /**
   * Quando troca a empresa:
   * - limpa plano
   * - limpa grupo
   */
  const handleEmpresaChange = (id) => {
    setEmpresaId(id);
    setPlanoTrabalho(null);
    setGrupo(null);
  };

  /**
   * Quando troca o plano:
   * - limpa grupo
   */
  const handlePlanoChange = (opt) => {
    setPlanoTrabalho(opt);
    setGrupo(null);
  };

  /**
   * Grupo é o último nível
   */
  const handleGrupoChange = (opt) => {
    setGrupo(opt);
  };

  /**
   * IDs finais (para submit / backend)
   */
  const planoTrabalhoId = planoTrabalho?.value || null;
  const grupoId = grupo?.value || null;

  return (
    <div className="space-y-6 w-full animate-[fadeInUp_0.6s_ease-out]">
      {/* Notification */}
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-6 py-4 rounded-xl shadow-lg animate-[slideInRight_0.3s_ease-out] ${
            notification.type === "success"
              ? "bg-xfire-orange text-white"
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
          onClick={() => navigate("/planos")}
          className="p-2 hover:bg-dark-tertiary rounded-lg text-neutral-400 hover:text-neutral-100 transition-all duration-200 cursor-pointer group"
          title="Voltar"
        >
          <FiArrowLeft
            size={20}
            className="group-hover:-translate-x-1 transition-transform duration-200"
          />
        </button>
        <div>
          <h1 className="text-3xl font-bold font-montserrat text-neutral-100 flex items-center gap-3">
            <FiUsers className="text-purple-400" />
            Gerenciar Associações
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Associe usuários e certificados aos grupos de trabalho
          </p>
        </div>
      </div>

      {/* Filtros de Seleção */}
      <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Selecionar Plano */}
          <div>
            <Label className="text-sm font-semibold text-neutral-400 mb-2">
              Plano de Trabalho
            </Label>
            <SelectEmpresa
              value={empresaId}
              onChange={handleEmpresaChange}
            />
          </div>

          {/* Selecionar Plano de trabalho */}
          <div>
            <Label className="text-sm font-semibold text-neutral-400 mb-2">
              Plano de Trabalho
            </Label>
            <SelectPlanoTrabalho
              empresaId={empresaId}
              value={planoTrabalho}
              onChange={handlePlanoChange}
              isDisabled={!empresaId}
              className="w-full disabled:opacity-50"
            />
          </div>
          {/* Selecionar Grupo */}
          <div>
            <Label className="text-sm font-semibold text-neutral-400 mb-2">
              Grupo
            </Label>
            <SelectGrupo
              planoTrabalhoId={planoTrabalhoId}
              value={grupo}
              onChange={handleGrupoChange}
              isDisabled={!planoTrabalhoId}
            />
          </div>
        </div>

        {/* Info do Grupo Selecionado */}
        {grupoSelecionado && (
          <div className="mt-4 p-4 bg-purple-900/20 border border-purple-800/50 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-900/30 rounded-lg">
                <FiUsers className="text-purple-400" size={20} />
              </div>
              <div>
                <p className="font-semibold text-purple-300">
                  {grupoSelecionado.nome}
                </p>
                <p className="text-sm text-purple-400">
                  {usuariosNoGrupo.length} usuário(s) • {certificadosNoGrupo.length}{" "}
                  certificado(s)
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Conteúdo Principal */}
      {selectedGrupo && !isLoading && (
        <div className="space-y-6">
          {/* Seção de Usuários */}
          <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-900/30 to-blue-800/30 px-6 py-4 border-b border-blue-800/50">
              <h2 className="text-lg font-bold text-blue-300 flex items-center gap-2">
                <FiUsers size={20} />
                Gerenciar Usuários
              </h2>
              <p className="text-sm text-blue-400 mt-1">
                Associe ou remova usuários deste grupo
              </p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Usuários Disponíveis */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-neutral-100">Disponíveis</h3>
                    <span className="text-xs bg-dark-tertiary text-neutral-400 px-2 py-1 rounded-full">
                      {usuariosDisponiveis.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {usuariosDisponiveis.length === 0 ? (
                      <p className="text-sm text-neutral-500 text-center py-8">
                        Todos os usuários já estão associados
                      </p>
                    ) : (
                      usuariosDisponiveis.map((usuario) => (
                        <div
                          key={usuario.id}
                          className="flex items-center justify-between p-3 bg-dark-tertiary hover:bg-neutral-800 rounded-lg transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center text-white font-bold flex-shrink-0">
                              {usuario.nome.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-neutral-100 text-sm">
                                {usuario.nome}
                              </p>
                              <p className="text-xs text-neutral-500">
                                {usuario.email}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleAddUsuario(usuario.id)}
                            className="p-2 bg-xfire-orange hover:bg-xfire-orange/80 text-white rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 cursor-pointer"
                            title="Adicionar ao grupo"
                          >
                            <FiPlus size={16} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Usuários Associados */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-neutral-100">Associados</h3>
                    <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
                      {usuariosAssociados.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {usuariosAssociados.length === 0 ? (
                      <p className="text-sm text-neutral-500 text-center py-8">
                        Nenhum usuário associado
                      </p>
                    ) : (
                      usuariosAssociados.map((usuario) => (
                        <div
                          key={usuario.id}
                          className="flex items-center justify-between p-3 bg-green-900/20 hover:bg-green-900/30 rounded-lg border border-green-800/50 transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-700 rounded-lg flex items-center justify-center text-white font-bold flex-shrink-0">
                              {usuario.nome.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-neutral-100 text-sm">
                                {usuario.nome}
                              </p>
                              <p className="text-xs text-neutral-500">
                                {usuario.email}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRemoveUsuario(usuario.id)}
                            className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 cursor-pointer"
                            title="Remover do grupo"
                          >
                            <FiX size={16} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Seção de Certificados */}
          <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-900/30 to-purple-800/30 px-6 py-4 border-b border-purple-800/50">
              <h2 className="text-lg font-bold text-purple-300 flex items-center gap-2">
                <FiShield size={20} />
                Gerenciar Certificados
              </h2>
              <p className="text-sm text-purple-400 mt-1">
                Associe ou remova certificados deste grupo
              </p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Certificados Disponíveis */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-neutral-100">Disponíveis</h3>
                    <span className="text-xs bg-dark-tertiary text-neutral-400 px-2 py-1 rounded-full">
                      {certificadosDisponiveis.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {certificadosDisponiveis.length === 0 ? (
                      <p className="text-sm text-neutral-500 text-center py-8">
                        Todos os certificados já estão associados
                      </p>
                    ) : (
                      certificadosDisponiveis.map((certificado) => (
                        <div
                          key={certificado.id}
                          className="flex items-center justify-between p-3 bg-dark-tertiary hover:bg-neutral-800 rounded-lg transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-700 rounded-lg flex items-center justify-center text-white flex-shrink-0">
                              <FiShield size={20} />
                            </div>
                            <div>
                              <p className="font-medium text-neutral-100 text-sm">
                                {certificado.nome_arquivo}
                              </p>
                              <p className="text-xs text-neutral-500">
                                {certificado.proprietario}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleAddCertificado(certificado.id)}
                            className="p-2 bg-xfire-orange hover:bg-xfire-orange/80 text-white rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 cursor-pointer"
                            title="Adicionar ao grupo"
                          >
                            <FiPlus size={16} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Certificados Associados */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-neutral-100">Associados</h3>
                    <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
                      {certificadosAssociados.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {certificadosAssociados.length === 0 ? (
                      <p className="text-sm text-neutral-500 text-center py-8">
                        Nenhum certificado associado
                      </p>
                    ) : (
                      certificadosAssociados.map((certificado) => (
                        <div
                          key={certificado.id}
                          className="flex items-center justify-between p-3 bg-green-900/20 hover:bg-green-900/30 rounded-lg border border-green-800/50 transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-700 rounded-lg flex items-center justify-center text-white flex-shrink-0">
                              <FiShield size={20} />
                            </div>
                            <div>
                              <p className="font-medium text-neutral-100 text-sm">
                                {certificado.nome_arquivo}
                              </p>
                              <p className="text-xs text-neutral-500">
                                {certificado.proprietario}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() =>
                              handleRemoveCertificado(certificado.id)
                            }
                            className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 cursor-pointer"
                            title="Remover do grupo"
                          >
                            <FiX size={16} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
        </div>
      )}

      {/* Empty State */}
      {!selectedGrupo && !isLoading && (
        <div className="bg-dark-secondary rounded-card shadow-sm border border-neutral-900 p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-dark-tertiary rounded-full flex items-center justify-center mx-auto mb-4">
              <FiUsers className="text-neutral-500" size={32} />
            </div>
            <h3 className="text-xl font-bold text-neutral-100 mb-2">
              Selecione um grupo
            </h3>
            <p className="text-neutral-400">
              Escolha um plano de trabalho e um grupo para gerenciar as associações de
              usuários e certificados.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
