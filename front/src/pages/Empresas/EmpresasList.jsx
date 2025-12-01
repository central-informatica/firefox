// pages/Empresas/EmpresasList.jsx
import { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { getEmpresas } from "../../services/empresasService";
import "./Empresas.css"
import { Link } from "react-router-dom";
import Button from "../../components/Button/Button";

const EmpresasList = () => {
  const [empresas, setEmpresas] = useState([]);
  const navigate = useNavigate();
  useEffect(() => {
    getEmpresas().then(setEmpresas);
  }, []);
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
            {empresas.map((e) => (
                <tr key={e.id}>
                <td>{e.nome}</td>
                <td>{e.cnpj}</td>
                <td>{e.timezone}</td>
                <td>
                    <div className="table-actions">
                    <Button
                        onClick={() => navigate(`/empresas/editar/${e.id}`)}
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

export default EmpresasList;