import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
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

import Select from "../../components/Select/Select";
import Label from "../../components/Label/Label";

import { listarPlanosTrabalhoPaginado } from "../../services/planosTrabalhoService";
import { getGruposByPlano, getUsuariosByGrupo, getCertificadosByGrupo, addUsuarioToGrupo, removeUsuarioFromGrupo, addCertificadoToGrupo, removeCertificadoFromGrupo } from "../../services/gruposService";
import { getUsuarios } from "../../services/usuariosService";
import { getCertificadosSimples } from "../../services/certificadosService";

const GerenciarAssociacoes = () => {
  const navigate = useNavigate();

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

  // Estados de UI
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Carregar planos iniciais
  useEffect(() => {
    const carregarPlanos = async () => {
      const resultado = await listarPlanosTrabalhoPaginado({ page: 1, limit: 100 });
      setPlanos(resultado.data || []);
    };
    carregarPlanos();
  }, []);

  // Carregar grupos quando plano é selecionado
  useEffect(() => {
    if (selectedPlano) {
      const carregarGrupos = async () => {
        const gruposData = await getGruposByPlano(selectedPlano);
        setGrupos(gruposData || []);
        setSelectedGrupo("");
      };
      carregarGrupos();
    } else {
      setGrupos([]);
      setSelectedGrupo("");
    }
  }, [selectedPlano]);

  // Carregar usuários e certificados quando grupo é selecionado
  useEffect(() => {
    if (selectedGrupo) {
      const carregarDados = async () => {
        setIsLoading(true);
        try {
          // Carregar todos os usuários e certificados
          const [usuarios, certificados] = await Promise.all([
            getUsuarios(),
            getCertificadosSimples(),
          ]);

          setTodosUsuarios(usuarios);
          setTodosCertificados(certificados);

          // Carregar associações do grupo
          const [usuariosIds, certificadosIds] = await Promise.all([
            getUsuariosByGrupo(selectedGrupo),
            getCertificadosByGrupo(selectedGrupo),
          ]);

          setUsuariosNoGrupo(usuariosIds);
          setCertificadosNoGrupo(certificadosIds);
        } finally {
          setIsLoading(false);
        }
      };
      carregarDados();
    } else {
      setUsuariosNoGrupo([]);
      setCertificadosNoGrupo([]);
    }
  }, [selectedGrupo]);

  // Função auxiliar para mostrar notificações
  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Adicionar usuário ao grupo
  const handleAddUsuario = async (usuarioId) => {
    try {
      await addUsuarioToGrupo(selectedGrupo, usuarioId);
      setUsuariosNoGrupo([...usuariosNoGrupo, usuarioId]);
      showNotification("Usuário adicionado com sucesso!");
    } catch (error) {
      showNotification("Erro ao adicionar usuário", "error");
    }
  };

  // Remover usuário do grupo
  const handleRemoveUsuario = async (usuarioId) => {
    try {
      await removeUsuarioFromGrupo(selectedGrupo, usuarioId);
      setUsuariosNoGrupo(usuariosNoGrupo.filter((id) => id !== usuarioId));
      showNotification("Usuário removido com sucesso!");
    } catch (error) {
      showNotification("Erro ao remover usuário", "error");
    }
  };

  // Adicionar certificado ao grupo
  const handleAddCertificado = async (certificadoId) => {
    try {
      await addCertificadoToGrupo(selectedGrupo, certificadoId);
      setCertificadosNoGrupo([...certificadosNoGrupo, certificadoId]);
      showNotification("Certificado adicionado com sucesso!");
    } catch (error) {
      showNotification("Erro ao adicionar certificado", "error");
    }
  };

  // Remover certificado do grupo
  const handleRemoveCertificado = async (certificadoId) => {
    try {
      await removeCertificadoFromGrupo(selectedGrupo, certificadoId);
      setCertificadosNoGrupo(certificadosNoGrupo.filter((id) => id !== certificadoId));
      showNotification("Certificado removido com sucesso!");
    } catch (error) {
      showNotification("Erro ao remover certificado", "error");
    }
  };

  // Usuários disponíveis (não estão no grupo)
  const usuariosDisponiveis = todosUsuarios.filter(
    (u) => !usuariosNoGrupo.includes(u.id)
  );

  // Usuários associados
  const usuariosAssociados = todosUsuarios.filter((u) =>
    usuariosNoGrupo.includes(u.id)
  );

  // Certificados disponíveis
  const certificadosDisponiveis = todosCertificados.filter(
    (c) => !certificadosNoGrupo.includes(c.id)
  );

  // Certificados associados
  const certificadosAssociados = todosCertificados.filter((c) =>
    certificadosNoGrupo.includes(c.id)
  );

  const grupoSelecionado = grupos.find((g) => g.id === Number(selectedGrupo));

  return (
    <div className="space-y-6 w-full animate-[fadeInUp_0.6s_ease-out]">
      {/* Notification */}
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-6 py-4 rounded-xl shadow-lg animate-[slideInRight_0.3s_ease-out] ${
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
          onClick={() => navigate("/planos")}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-800 transition-all duration-200 cursor-pointer group"
          title="Voltar"
        >
          <FiArrowLeft
            size={20}
            className="group-hover:-translate-x-1 transition-transform duration-200"
          />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <FiUsers className="text-purple-600" />
            Gerenciar Associações
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Associe usuários e certificados aos grupos de trabalho
          </p>
        </div>
      </div>

      {/* Filtros de Seleção */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Selecionar Plano */}
          <div>
            <Label className="text-sm font-semibold text-gray-700 mb-2">
              Plano de Trabalho
            </Label>
            <Select
              value={selectedPlano}
              onChange={(e) => setSelectedPlano(e.target.value)}
              className="w-full"
            >
              <option value="">Selecione um plano...</option>
              {planos.map((plano) => (
                <option key={plano.id} value={plano.id}>
                  {plano.nome}
                </option>
              ))}
            </Select>
          </div>

          {/* Selecionar Grupo */}
          <div>
            <Label className="text-sm font-semibold text-gray-700 mb-2">
              Grupo
            </Label>
            <Select
              value={selectedGrupo}
              onChange={(e) => setSelectedGrupo(e.target.value)}
              disabled={!selectedPlano || grupos.length === 0}
              className="w-full disabled:opacity-50"
            >
              <option value="">
                {selectedPlano
                  ? grupos.length === 0
                    ? "Nenhum grupo disponível"
                    : "Selecione um grupo..."
                  : "Selecione um plano primeiro"}
              </option>
              {grupos.map((grupo) => (
                <option key={grupo.id} value={grupo.id}>
                  {grupo.nome}
                </option>
              ))}
            </Select>
          </div>
        </div>

        {/* Info do Grupo Selecionado */}
        {grupoSelecionado && (
          <div className="mt-4 p-4 bg-purple-50 border border-purple-100 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <FiUsers className="text-purple-600" size={20} />
              </div>
              <div>
                <p className="font-semibold text-purple-900">
                  {grupoSelecionado.nome}
                </p>
                <p className="text-sm text-purple-700">
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
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 px-6 py-4 border-b border-blue-200">
              <h2 className="text-lg font-bold text-blue-900 flex items-center gap-2">
                <FiUsers size={20} />
                Gerenciar Usuários
              </h2>
              <p className="text-sm text-blue-700 mt-1">
                Associe ou remova usuários deste grupo
              </p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Usuários Disponíveis */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-800">Disponíveis</h3>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      {usuariosDisponiveis.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {usuariosDisponiveis.length === 0 ? (
                      <p className="text-sm text-gray-500 text-center py-8">
                        Todos os usuários já estão associados
                      </p>
                    ) : (
                      usuariosDisponiveis.map((usuario) => (
                        <div
                          key={usuario.id}
                          className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold flex-shrink-0">
                              {usuario.nome.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-gray-800 text-sm">
                                {usuario.nome}
                              </p>
                              <p className="text-xs text-gray-500">
                                {usuario.email}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleAddUsuario(usuario.id)}
                            className="p-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 cursor-pointer"
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
                    <h3 className="font-semibold text-gray-800">Associados</h3>
                    <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">
                      {usuariosAssociados.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {usuariosAssociados.length === 0 ? (
                      <p className="text-sm text-gray-500 text-center py-8">
                        Nenhum usuário associado
                      </p>
                    ) : (
                      usuariosAssociados.map((usuario) => (
                        <div
                          key={usuario.id}
                          className="flex items-center justify-between p-3 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold flex-shrink-0">
                              {usuario.nome.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-gray-800 text-sm">
                                {usuario.nome}
                              </p>
                              <p className="text-xs text-gray-500">
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
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 px-6 py-4 border-b border-purple-200">
              <h2 className="text-lg font-bold text-purple-900 flex items-center gap-2">
                <FiShield size={20} />
                Gerenciar Certificados
              </h2>
              <p className="text-sm text-purple-700 mt-1">
                Associe ou remova certificados deste grupo
              </p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Certificados Disponíveis */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-800">Disponíveis</h3>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      {certificadosDisponiveis.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {certificadosDisponiveis.length === 0 ? (
                      <p className="text-sm text-gray-500 text-center py-8">
                        Todos os certificados já estão associados
                      </p>
                    ) : (
                      certificadosDisponiveis.map((certificado) => (
                        <div
                          key={certificado.id}
                          className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg flex items-center justify-center text-white flex-shrink-0">
                              <FiShield size={20} />
                            </div>
                            <div>
                              <p className="font-medium text-gray-800 text-sm">
                                {certificado.nome_arquivo}
                              </p>
                              <p className="text-xs text-gray-500">
                                {certificado.proprietario}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleAddCertificado(certificado.id)}
                            className="p-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 cursor-pointer"
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
                    <h3 className="font-semibold text-gray-800">Associados</h3>
                    <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">
                      {certificadosAssociados.length}
                    </span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {certificadosAssociados.length === 0 ? (
                      <p className="text-sm text-gray-500 text-center py-8">
                        Nenhum certificado associado
                      </p>
                    ) : (
                      certificadosAssociados.map((certificado) => (
                        <div
                          key={certificado.id}
                          className="flex items-center justify-between p-3 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition-all duration-200 group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-lg flex items-center justify-center text-white flex-shrink-0">
                              <FiShield size={20} />
                            </div>
                            <div>
                              <p className="font-medium text-gray-800 text-sm">
                                {certificado.nome_arquivo}
                              </p>
                              <p className="text-xs text-gray-500">
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      )}

      {/* Empty State */}
      {!selectedGrupo && !isLoading && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiUsers className="text-gray-400" size={32} />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              Selecione um grupo
            </h3>
            <p className="text-gray-600">
              Escolha um plano de trabalho e um grupo para gerenciar as associações de
              usuários e certificados.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default GerenciarAssociacoes;
