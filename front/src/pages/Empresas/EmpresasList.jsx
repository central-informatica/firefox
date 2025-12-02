// pages/Empresas/EmpresasList.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEmpresas } from "../../services/empresasService";
import "../../components/Tables/Tables.css";
import { Link } from "react-router-dom";
import Button from "../../components/Button/Button";

const EmpresasList = () => {
  const [empresas, setEmpresas] = useState([]);
  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 5;

  const navigate = useNavigate();

  useEffect(() => {
    getEmpresas().then(setEmpresas);
  }, []);

  // Paginação
  const totalPaginas = Math.ceil(empresas.length / itensPorPagina);

  const empresasPaginadas = empresas.slice(
    (paginaAtual - 1) * itensPorPagina,
    paginaAtual * itensPorPagina
  );

  const proximaPagina = () => {
    if (paginaAtual < totalPaginas) setPaginaAtual(paginaAtual + 1);
  };

  const paginaAnterior = () => {
    if (paginaAtual > 1) setPaginaAtual(paginaAtual - 1);
  };

  return (
    <div>
      <h1 className="titulo">Minhas empresas</h1>

      <Link to="/empresas/nova" className="btn btn-danger">
        + Nova Empresa
      </Link>

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>CNPJ</th>
              <th>Fuso Horário</th>
              <th style={{ width: "120px" }}></th>
            </tr>
          </thead>
          <tbody>
            {empresasPaginadas.map((e) => (
              <tr key={e.id}>
                <td>{e.nome}</td>
                <td>{e.cnpj}</td>
                <td>{e.timezone}</td>
                <td>
                  <div className="table-actions">
                    <Button onClick={() => navigate(`/empresas/editar/${e.id}`)}>
                      Editar
                    </Button>
                  </div>
                </td>
              </tr>
            ))}

            {empresasPaginadas.length === 0 && (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>
                  Nenhuma empresa encontrada.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Controles de paginação */}
      {totalPaginas > 1 && (
        <div style={{ marginTop: "15px", display: "flex", gap: "10px" }}>
          <button
            className="btn btn-secondary"
            disabled={paginaAtual === 1}
            onClick={paginaAnterior}
          >
            ◀ Anterior
          </button>

          <span>
            Página {paginaAtual} de {totalPaginas}
          </span>

          <button
            className="btn btn-secondary"
            disabled={paginaAtual === totalPaginas}
            onClick={proximaPagina}
          >
            Próxima ▶
          </button>
        </div>
      )}
    </div>
  );
};

export default EmpresasList;
