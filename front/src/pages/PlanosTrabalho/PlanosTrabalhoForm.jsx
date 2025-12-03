import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";
import TextArea from "../../components/TextArea/TextArea"
import Label from "../../components/Label/Label"

import "../../components/Forms/Forms.css";

import {
  getPlanoTrabalho,
  createPlanoTrabalho,
  updatePlanoTrabalho,
} from "../../services/planosTrabalhoService";

const PlanosTrabalhoForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [form, setForm] = useState({
    nome: "",
    descricao: "",
  });

  useEffect(() => {
    if (isEdit) {
      getPlanoTrabalho(id).then((data) => {
        if (data) setForm(data);
      });
    }
  }, [id, isEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((old) => ({ ...old, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isEdit) {
      await updatePlanoTrabalho(id, form);
    } else {
      await createPlanoTrabalho(form);
    }

    navigate("/planos");
  };

  return (
    <div className="page-form">
      <h1 className="titulo">
        {isEdit ? "Editar plano de trabalho" : "Novo plano de trabalho"}
      </h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: 10 }}>
          <Label>Nome do plano</Label>
          <Input
            name="nome"
            value={form.nome}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group" style={{ marginBottom: 16 }}>
          <Label>Descrição</Label>
          <TextArea
            name="descricao"
            value={form.descricao}
            onChange={handleChange}
            className="form-control"
            rows={4}
          />
        </div>

        <Button type="submit" className="btn">
          Salvar
        </Button>
      </form>
    </div>
  );
};

export default PlanosTrabalhoForm;
