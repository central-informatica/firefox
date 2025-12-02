import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCertificados } from "../../services/certificadosService";
import { getEmpresasDoUsuario } from "../../services/empresasService";
import { useAuth } from "../../auth/useAuth";
import Select from "react-select";

import "../../components/Tables/Tables.css";
import ButtonExcluir from "../../components/Button/ButtonExcluir";

const CertificadosList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [certificados, setCertificados] = useState([]);

  const [empresasDoUsuario, setEmpresasDoUsuario] = useState([]);
  const [empresaFiltro, setEmpresaFiltro] = useState(null);

  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 5;

  // Carrega certificados
  useEffect(() => {
    getCertificados().then(setCertificados);
  }, []);

  // Carrega empresas do usuário
  useEffect(() => {
    if (!user) return;

    getEmpresasDoUsuario(user.id)
      .then((empresas) => {
        setEmpresasDoUsuario(
          empresas.map((e) => ({
            value: e.empresa_id,
            label: e.razao_social,
          }))
        );
      })
      .catch((err) => {
        console.error("Erro ao carregar empresas:", err);
      });
  }, [user]);

// Seleciona automaticamente a primeira empresa ao carregar
useEffect(() => {
  if (empresasDoUsuario.length > 0 && !empresaFiltro) {
    const primeiraEmpresa = empresasDoUsuario[0];
    setEmpresaFiltro(primeiraEmpresa);
    setPaginaAtual(1);
  }
}, [empresasDoUsuario]);

  // Filtragem dos certificados
  const certificadosFiltrados = empresaFiltro
    ? certificados.filter(
        (c) => Number(c.empresa_id) === Number(empresaFiltro.value)
      )
    : certificados;

  // Paginação
  const totalPaginas = Math.ceil(certificadosFiltrados.length / itensPorPagina);

  const certificadosPaginados = certificadosFiltrados.slice(
    (paginaAtual - 1) * itensPorPagina,
    paginaAtual * itensPorPagina
  );

  return (
    <div>
      <h1 className="titulo">Meus certificados</h1>

      {/* Select de empresas */}
      <div style={{ width: "280px", marginBottom: "15px" }}>
        <Select
          placeholder="Filtrar por empresa"
          isClearable
          value={empresaFiltro}
          onChange={(value) => {
            setEmpresaFiltro(value);
            setPaginaAtual(1);
          }}
          options={empresasDoUsuario}
        />
      </div>

      <button
        className="btn btn-danger"
        onClick={() => navigate("/certificados/novo")}
      >
        + Novo Certificado
      </button>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Criado por</th>
              <th>Nome do arquivo</th>
              <th>Criado em</th>
              <th style={{ width: "120px" }}>Ações</th>
            </tr>
          </thead>

          <tbody>
            {certificadosPaginados.map((e) => (
              <tr key={e.id}>
                <td>{e.criado_por_nome}</td>
                <td>{e.nome_arquivo}</td>
                <td>{e.criado_em}</td>
                <td>
                  <div className="table-actions">
                    <ButtonExcluir
                      onClick={() => navigate(`/certificados/excluir/${e.id}`)}
                    >
                      Excluir
                    </ButtonExcluir>
                  </div>
                </td>
              </tr>
            ))}

            {certificadosPaginados.length === 0 && (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>
                  Nenhum certificado encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Paginação */}
      {totalPaginas > 1 && (
        <div style={{ marginTop: "15px", display: "flex", gap: "10px" }}>
          <button
            className="btn btn-secondary"
            disabled={paginaAtual === 1}
            onClick={() => setPaginaAtual(paginaAtual - 1)}
          >
            ◀ Anterior
          </button>

          <span>
            Página {paginaAtual} de {totalPaginas}
          </span>

          <button
            className="btn btn-secondary"
            disabled={paginaAtual === totalPaginas}
            onClick={() => setPaginaAtual(paginaAtual + 1)}
          >
            Próxima ▶
          </button>
        </div>
      )}
    </div>
  );
};

export default CertificadosList;
