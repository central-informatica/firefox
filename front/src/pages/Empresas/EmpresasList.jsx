
import { useNavigate } from "react-router-dom";
import { listarEmpresasPaginado } from "../../services/empresasService";
import { Link } from "react-router-dom";
import Button from "../../components/Button/Button";
import DataTable from "../../components/Tables/DataTable";

const EmpresasList = () => {
  const navigate = useNavigate();

  const columns = [
    {
      header: "Nome",
      accessorKey: "nome",
    },
    {
      header: "CNPJ",
      accessorKey: "cnpj",
    },
    {
      header: "Fuso Horário",
      accessorKey: "timezone",
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <div className="table-actions">
          <Button
            onClick={() => navigate(`/empresas/editar/${row.original.id}`)}
          >
            Editar
          </Button>
        </div>
      ),
    },
  ];

  const fetchEmpresas = ({ page, limit, search, sort }) => {
    return listarEmpresasPaginado({ page, limit, search, sort });
  };

  return (
    <div>
      <h1 className="titulo">Minhas empresas</h1>

      <Link to="/empresas/nova" className="btn btn-danger">
        + Nova Empresa
      </Link>

      <DataTable
        columns={columns}
        fetchData={fetchEmpresas}
        limit={5}
      />
    </div>
  );
};

export default EmpresasList;
