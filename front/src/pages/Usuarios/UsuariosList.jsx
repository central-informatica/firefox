import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUsuarios, deleteUsuario } from "../../services/usuariosService";
import "../../components/Tables/Tables.css";

const UsuariosList = () => {
  const [usuarios, setUsuarios] = useState([]);

  const load = async () => {
    setUsuarios(await getUsuarios());
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id) => {
    if (!confirm("Deseja excluir este usuário?")) return;
    await deleteUsuario(id);
    load();
  };

  return (
    <>
      <h1>Usuários</h1>
      <Link to="/usuarios/novo" className="btn">Novo Usuário</Link>

      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Email</th>
            <th>Nível</th>
            <th>Ações</th>
          </tr>
        </thead>

        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.nome}</td>
              <td>{u.email}</td>
              <td>{u.nivel}</td>
              <td>
                <Link to={`/usuarios/editar/${u.id}`}>Editar</Link>
                {" | "}
                <button onClick={() => handleDelete(u.id)}>Excluir</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
};

export default UsuariosList;
