import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUsuarios, deleteUsuario } from "../../services/usuariosService";
import "../../components/Tables/Tables.css";
import ButtonExcluir from "../../components/Button/ButtonExcluir";

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
      <h1 className="titulo">Usuários</h1>

      <Link to="/usuarios/novo" className="btn">
        Novo Usuário
      </Link>

      <div className="table-container" style={{ marginTop: "12px" }}>
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
                <Link className="btn" to={`/usuarios/editar/${u.id}`}>Editar</Link>
                {" | "}
                <ButtonExcluir onClick={() => handleDelete(u.id)}>Excluir</ButtonExcluir>

              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </>
  );
};

export default UsuariosList;
