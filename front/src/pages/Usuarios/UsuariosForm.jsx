import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Input from "../../components/Input/Input";
import Button from "../../components/Button/Button";

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
    <div className="max-w-[700px] mx-auto my-10 mb-6 bg-white py-5 px-6 rounded-xl border border-gray-200 shadow-sm">
      <h1 className="mt-0 mb-4 text-2xl font-bold text-gray-800">
        {isEdit ? "Editar Usuário" : "Novo Usuário"}
      </h1>

      <form onSubmit={handleSubmit}>
        <Input
          name="nome"
          placeholder="Nome"
          value={form.nome}
          onChange={handleChange}
          required
        />

        <Input
          name="email"
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <div className="mb-4">
          <select
            name="nivel"
            value={form.nivel}
            onChange={handleChange}
            className="p-2.5 border border-gray-300 rounded-md text-[15px] text-black bg-[#fcfcfa] w-full box-border focus:border-primary focus:outline-none focus:bg-[#e9f7f8]"
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
