// pages/Empresas/EmpresaForm.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import {
  getEmpresa,
  createEmpresa,
  updateEmpresa,
} from "../../services/empresasService";

const EmpresaForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const isEdit = !!id;

  const [form, setForm] = useState({
    nome: "",
    cnpj: "",
    timezone: "America/Sao_Paulo",
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

    if (isEdit) {
      await updateEmpresa(id, form);
    } else {
      await createEmpresa(form);
    }

    navigate("/empresas");
  };

  return (
    <div>
      <h1>{isEdit ? "Editar Empresa" : "Nova Empresa"}</h1>

      <form onSubmit={handleSubmit} style={{ maxWidth: "400px" }}>
        <div className="form-group">
          <label>Nome</label>
          <input
            name="nome"
            className="form-control"
            value={form.nome}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group" style={{ marginTop: "10px" }}>
          <label>CNPJ</label>
          <input
            name="cnpj"
            className="form-control"
            value={form.cnpj}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group" style={{ marginTop: "10px" }}>
          <label>Fuso Horário</label>
          <select
            name="timezone"
            className="form-control"
            value={form.timezone}
            onChange={handleChange}
          >
            <option value="America/Sao_Paulo">America/Sao_Paulo</option>
            <option value="America/Recife">America/Recife</option>
            <option value="America/Manaus">America/Manaus</option>
            <option value="America/Cuiaba">America/Cuiaba</option>
          </select>
        </div>

        <button
          type="submit"
          className="btn btn-success"
          style={{ marginTop: "20px" }}
        >
          Salvar
        </button>
      </form>
    </div>
  );
};

export default EmpresaForm;
