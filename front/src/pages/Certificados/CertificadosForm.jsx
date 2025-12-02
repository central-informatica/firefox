
// pages/Empresas/EmpresaForm.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import Input from "../../components/Input/Input";
import InputMask from "../../components/Input/InputMask";
import Button from "../../components/Button/Button";
import Select from "../../components/Select/Select";
import Label from "../../components/Label/Label";

import {
  getCertificado,
  createCertificado,
} from "../../services/certificadosService"; // updateCertificado,

const CertificadosForm = () => {
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
      getCertificado(id).then((certificado) => {
        if (certificado) setForm(certificado);
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

    navigate("/certificados");
  };

  return (
    <div>
      <h1>{isEdit ? "Editar Certificado" : "Novo Certificado"}</h1>

      <form onSubmit={handleSubmit} style={{ maxWidth: "800px" }}>
        <div className="form-group">
          <Label>Nome</Label>
          <Input
            name="nome"
            className="form-control"
            value={form.nome}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group" style={{ marginTop: "10px" }}>
          <Label>CNPJ</Label>
          <InputMask
            name="cnpj"
            mask="00.000.000/0000-00"
            className="form-control"
            value={form.cnpj}
            onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
            required
          />
        </div>

        <div className="form-group" style={{ marginTop: "10px" }}>
          <Label>Fuso Horário</Label>
          <Select
            value={form.timezone}
            onChange={(e) => setForm({ ...form, timezone: e.target.value })}
            options={[
              { value: "America/Sao_Paulo", label: "America/Sao_Paulo" },
              { value: "America/Recife", label: "America/Recife" },
              { value: "America/Manaus", label: "America/Manaus" },
              { value: "America/Cuiaba", label: "America/Cuiaba" },
            ]}
          />
        </div>

        <Button
          type="submit"
          className="btn"
          style={{ marginTop: "20px" }}
        >
          Salvar
        </Button> 
      </form>
    </div>
  );
};

export default CertificadosForm;
