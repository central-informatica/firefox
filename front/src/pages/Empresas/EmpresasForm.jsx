// pages/Empresas/EmpresaForm.jsx
import { getTimezoneOptions } from "../../services/timezoneService";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import Input from "../../components/Input/Input";
import InputMask from "../../components/Input/InputMask";
import Button from "../../components/Button/Button";
import Select from "../../components/Select/Select";
import Label from "../../components/Label/Label";
import "../../components/Forms/Forms.css";

import {
  getEmpresa,
  createEmpresa,
  updateEmpresa,
} from "../../services/empresasService";

const timezoneOptions = getTimezoneOptions();

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
    <div className="page-form">
      <h1 className="titulo">
        {isEdit ? "Editar Empresa" : "Nova Empresa"}
      </h1>

      <form onSubmit={handleSubmit}>
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
            onChange={(e) =>
              setForm({ ...form, cnpj: e.target.value })
            }
            required
          />
        </div>

        <div className="form-group" style={{ marginTop: "10px" }}>
          <Label>Fuso Horário</Label>
          <Select
            options={timezoneOptions}
            value={
              form.timezone
                ? { value: form.timezone, label: form.timezone }
                : null
            }
            onChange={(opt) => setForm({ ...form, timezone: opt.value })}
            placeholder="Selecione o fuso horário"
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

export default EmpresaForm;
