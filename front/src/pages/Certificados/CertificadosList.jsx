import { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { getCertificados } from "../../services/certificadosService";
import "../../components/Tables/Tables.css"
import { Link } from "react-router-dom";
import Button from "../../components/Button/Button";

const CertificadosList = () => {
  const [certificados, setCertificados] = useState([]);
  const navigate = useNavigate();
  useEffect(() => {
    getCertificados().then(setCertificados);
  }, []);
  return (
    <div>
        <h1 className="titulo">Meus certificados</h1>
        <Link to="/certificados/nova" className="btn btn-danger">
        + Novo Certificado
        </Link>

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
            {certificados.map((e) => (
                <tr key={e.id}>
                <td>{e.criado_por}</td>
                <td>{e.nome_arquivo}</td>
                <td>{e.criado_em}</td>
                <td>
                    <div className="table-actions">
                    <Button
                        onClick={() => navigate(`/certificados/editar/${e.id}`)}
                    >Editar</Button>
                    </div>
                </td>
                </tr>
            ))}
            </tbody>
        </table>
        </div>

    </div>
    );

};

export default CertificadosList;