import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";
import "../../components/Forms/Forms.css";

import {
  createUsuario,
  getUsuarioById,
  updateUsuario,
} from "../../services/usuariosService";

const UsuarioForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const isEdit = Boolean(id);

  const [form, setForm] = useState({
    nome: "",
    email: "",
    nivel: "COMUM",
  });

  useEffect(() => {
    if (isEdit) {
      getUsuarioById(id).then((data) => {
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
      await updateUsuario(id, form);
    } else {
      await createUsuario(form);
    }

    navigate("/usuarios");
  };

  return (
    <div className="page-form">
      <h1 className="titulo">
        {isEdit ? "Editar Usuário" : "Novo Usuário"}
      </h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: "10px" }}>
          <Input
            name="nome"
            placeholder="Nome"
            value={form.nome}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group" style={{ marginBottom: "10px" }}>
          <Input
            name="email"
            placeholder="Email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group" style={{ marginBottom: "16px" }}>
          <select
            name="nivel"
            value={form.nivel}
            onChange={handleChange}
            className="select"
          >
            <option value="ADMINISTRADOR">ADMINISTRADOR</option>
            <option value="COMUM">COMUM</option>
          </select>
        </div>

        <Button type="submit">Salvar</Button>
      </form>
    </div>
  );
};

export default UsuarioForm;
