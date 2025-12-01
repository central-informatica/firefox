import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

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
      getUsuarioById(id).then((data) => setForm(data));
    }
  }, [id]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
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
    <div>
      <h1>{isEdit ? "Editar Usuário" : "Novo Usuário"}</h1>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 10, width: 300 }}>
        <input
          name="nome"
          placeholder="Nome"
          value={form.nome}
          onChange={handleChange}
        />

        <input
          name="email"
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={handleChange}
        />

        <select name="nivel" value={form.nivel} onChange={handleChange}>
          <option value="ADMINISTRADOR">ADMINISTRADOR</option>
          <option value="COMUM">COMUM</option>
        </select>

        <button type="submit">Salvar</button>
      </form>
    </div>
  );
};

export default UsuarioForm;
