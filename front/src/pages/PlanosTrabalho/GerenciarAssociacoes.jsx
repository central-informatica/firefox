import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import SelectEmpresa from "../../components/Select/SelectEmpresa";
import SelectPlanoTrabalho from "../../components/Select/SelectPlanoTrabalho";
import CertificadoCard from "../../components/Cards/CertificadoCard";
import SelectGrupo from "../../components/Select/SelectGrupo";
import Label from "../../components/Label/Label";
import { formatDate } from "../../utils/date";
import {
  FiArrowLeft,
  FiUsers,
  FiCheckCircle,
  FiAlertCircle,
} from "react-icons/fi";

// ✅ Ajuste o caminho/nome do service conforme seu projeto
import {
  listarCertificadosDaEmpresa,
  listarCertificadosDoGrupo,
  adicionarCertificadoAoGrupo,
  removerCertificadoDoGrupo,
} from "../../services/certificadosService";

import {listarCertificadosPaginado} from "../../services/certificadosService";

export default function GerenciarAssociacoes() {
  const navigate = useNavigate();

  // Estados principais (UI)
  const [empresaId, setEmpresaId] = useState(null);

  // ✅ Como seus selects retornam ID, guarde como ID
  const [planoId, setPlanoId] = useState(null);
  const [grupoId, setGrupoId] = useState(null);

  // UI
  const [notification, setNotification] = useState(null);

  // Certificados
  const [certificadosDisponiveis, setCertificadosDisponiveis] = useState([]);
  const [certificadosDoGrupo, setCertificadosDoGrupo] = useState([]);

  // Loading simples (opcional)
  const [loadingCertificados, setLoadingCertificados] = useState(false);

  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Handlers
  const handleEmpresaChange = (id) => {
    setEmpresaId(id);
    setPlanoId(null);
    setGrupoId(null);
    /*setCertificadosDisponiveis([]);
    setCertificadosDoGrupo([]);*/
  };

  // ✅ recebe ID do select
  const handlePlanoChange = (id) => {
    
    setPlanoId(id);
    setGrupoId(null);
    setCertificadosDisponiveis([]);
    setCertificadosDoGrupo([]);
  };

  // ✅ recebe ID do select
  const handleGrupoChange = (id) => {
    setGrupoId(id);
    setCertificadosDoGrupo([]);
    setCertificadosDisponiveis([]);
  };

  const carregarCertificadosDisponiveis = async () => {
    
    if (!empresaId) return;
      try {
        const response = await listarCertificadosPaginado({
          empresa_id: empresaId,
          page: 1,
          limit: 1000,
          search: "",
          sort: "",
        });

        const todosPermitidos = Array.isArray(response?.data)? response.data: [];
        // ✅ IDs dos certificados já vinculados AO GRUPO
        const certificadosNoGrupoIds = new Set(
          certificadosDoGrupo.map((c) => c.certificado_id)
        );

        // ✅ Disponíveis = permitidos - já vinculados
        const disponiveis = todosPermitidos.filter(
          (c) => !certificadosNoGrupoIds.has(c.certificado_id)
        );

        setCertificadosDisponiveis(disponiveis);
      } catch (err) {
        console.error("Erro ao carregar certificados disponíveis", err);
    }
  };


  const carregarCertificadosDoGrupo = async () => {
    if (!empresaId || !grupoId) return;

    setLoadingCertificados(true);
    try {
      // ✅ BUSCA SOMENTE certificados vinculados ao grupo
      const vinculados = await listarCertificadosDoGrupo(grupoId);
      // ✅ ATUALIZA APENAS certificadosDoGrupo
      setCertificadosDoGrupo(Array.isArray(vinculados) ? vinculados : []);
    } catch (err) {
      console.error("Erro ao carregar certificados:", err);
      showNotification("Erro ao carregar certificados", "error");
    } finally {
      setLoadingCertificados(false);
    }
  };

  useEffect(() => {
    if (!empresaId) return;
    carregarCertificadosDisponiveis();
  }, [empresaId, certificadosDoGrupo]);

  // ✅ Esse effect é quem chama a carga (agora com ids corretos)
  useEffect(() => {
    if (!empresaId || !grupoId) return;
    carregarCertificadosDoGrupo();
  }, [empresaId, grupoId]);

  // Ações (vincular / desvincular)
  const handleVincular = async (certificadoId) => {
    try {
      await adicionarCertificadoAoGrupo(grupoId, certificadoId, empresaId);
      showNotification("Certificado vinculado com sucesso!");
      carregarCertificadosDoGrupo();
    } catch (err) {
      console.error(err);
      showNotification("Erro ao vincular certificado", "error");
    }
  };

  const handleDesvincular = async (certificadoId) => {
    try {
      await removerCertificadoDoGrupo(grupoId, certificadoId, empresaId);
      showNotification("Certificado removido do grupo!");
      carregarCertificadosDoGrupo();
    } catch (err) {
      console.error(err);
      showNotification("Erro ao remover certificado", "error");
    }
  };

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
              value={planoId}
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
              planoTrabalhoId={planoId}
              value={grupoId}
              onChange={handleGrupoChange}
              isDisabled={!planoId}
            />
          </div>
        </div>
      </div>

      {/* Empty State */}
      {!grupoId && (
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
              um grupo para gerenciar os certificados vinculados.
            </p>
          </div>
        </div>
      )}

      {/* ✅ Listas de certificados (só aparece com grupo selecionado) */}
      {grupoId && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-800">
              Certificados do Grupo
            </h2>
            {loadingCertificados && (
              <span className="text-sm text-gray-500">Carregando...</span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Disponíveis */}
            <div className="border border-gray-100 rounded-xl p-4">
              <h3 className="font-semibold text-gray-800 mb-3">
                Disponíveis na empresa {certificadosDisponiveis.length}
              </h3>

              {certificadosDisponiveis.length === 0 ? (
                <p className="text-sm text-gray-500">
                  Nenhum certificado disponível.
                </p>
              ) : (
                <ul className="space-y-2">
                  {certificadosDisponiveis.map((c) => (
                    <li
                      key={c.certificado_id}
                      className="p-3 rounded-lg border border-gray-100"
                    >
                      <CertificadoCard
                        certificado={{
                          certificado_id: c.certificado_id,
                          nome_arquivo: c.nome_arquivo,
                          proprietario: c.proprietario,
                          emitido_por: c.emitido_por,
                          data_inicio: c.data_inicio,
                          valido_ate: c.valido_ate,
                          cnpj: c.cnpj,
                        }}
                      >
                        <button
                          type="button"
                          onClick={() => handleVincular(c.certificado_id)}
                          className="px-3 py-2 rounded-lg bg-purple-600 text-white text-sm hover:bg-purple-700 transition"
                        >
                          Adicionar
                        </button>
                      </CertificadoCard>
                    </li>
                  ))}
                </ul>

              )}
            </div>

            {/* Vinculados */}
            <div className="border border-gray-100 rounded-xl p-4">
              <h3 className="font-semibold text-gray-800 mb-3">
                Já vinculados ao grupo
              </h3>

              {certificadosDoGrupo.length === 0 ? (
                <p className="text-sm text-gray-500">
                  Nenhum certificado vinculado.
                </p>
              ) : (
                <ul className="space-y-2">
                  {certificadosDoGrupo.map((c) => (
                    <li
                      key={c.certificado_id}
                      className="p-3 rounded-lg border border-gray-100"
                    >
                      <CertificadoCard
                        certificado={{
                          certificado_id: c.certificado_id,
                          nome_arquivo: c.nome_arquivo,
                          proprietario: c.proprietario,
                          emitido_por: c.emitido_por,
                          data_inicio: c.data_inicio,
                          valido_ate: c.valido_ate,
                          cnpj: c.cnpj,
                        }}
                      >
                        <button
                          type="button"
                          onClick={() => handleDesvincular(c.certificado_id)}
                          className="px-3 py-2 rounded-lg bg-gray-200 text-gray-800 text-sm hover:bg-gray-300 transition"
                        >
                          Remover
                        </button>
                      </CertificadoCard>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
