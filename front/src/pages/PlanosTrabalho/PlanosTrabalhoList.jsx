import { useNavigate, Link } from "react-router-dom";
import DataTable from "../../components/Tables/DataTable";
import Button from "../../components/Button/Button";
import { listarPlanosTrabalhoPaginado } from "../../services/planosTrabalhoService";

const PlanosTrabalhoList = () => {
  const navigate = useNavigate();

  const columns = [
    {
      header: "Nome do plano",
      accessorKey: "nome",
    },
    {
      header: "Descrição",
      accessorKey: "descricao",
    },
    {
      header: "Ações",
      cell: ({ row }) => (
        <div className="table-actions">
          <Button
            onClick={() => navigate(`/planos/editar/${row.original.id}`)}
          >
            Editar
          </Button>
        </div>
      ),
    },
  ];

  const fetchPlanos = ({ page, limit, search, sort }) => {
    return listarPlanosTrabalhoPaginado({ page, limit, search, sort });
  };

  return (
    <div>
      <h1 className="titulo">Planos de trabalho</h1>

      <Link to="/planos/novo" className="btn btn-danger" style={{ marginBottom: 12 }}>
        + Novo plano de trabalho
      </Link>

      <DataTable
        columns={columns}
        fetchData={fetchPlanos}
        limit={5}
      />
    </div>
  );
};

export default PlanosTrabalhoList;
