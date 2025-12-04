import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { ChevronLeft, ChevronRight, ArrowUpDown, Search } from "lucide-react";
import { useEffect, useState } from "react";
import "./DataTable.css"; // CSS novo e exclusivo

export default function DataTable({ columns, fetchData, limit = 10 }) {
  const [data, setData] = useState([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [sort, setSort] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);

    try {
      const res = await fetchData({ page, limit, search, sort });
      setData(Array.isArray(res?.data) ? res.data : []);
      setTotal(Number(res?.total) || 0);
    } catch (err) {
      console.error("Erro no DataTable:", err);
      setData([]);
      setTotal(0);
    }

    setLoading(false);
  }

  useEffect(() => {
    load();
  }, [page, search, sort]);

  const table = useReactTable({
    data,
    columns,
    manualPagination: true,
    manualSorting: true,
    pageCount: Math.ceil(total / limit),
    getCoreRowModel: getCoreRowModel(),
  });

  function toggleSort(column) {
    const key = column.columnDef.accessorKey;
    if (!key) return;

    const isAsc = sort === `${key}.asc`;
    setSort(isAsc ? `${key}.desc` : `${key}.asc`);
    setPage(1);
  }

  return (
    <div className="dt-wrapper">
      {/* Busca */}
      <div className="dt-search-box">
        <Search size={18} className="dt-search-icon" />
        <input
          type="text"
          placeholder="Buscar..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="dt-search-input"
        />
      </div>

      {/* Tabela */}
      <table className="dt-table">
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => {
                const key = header.column.columnDef.accessorKey;
                const isCurrentSort = sort.includes(key);

                return (
                  <th key={header.id}>
                    {key ? (
                      <button
                        className={`dt-sort-btn ${
                          isCurrentSort ? "dt-sort-active" : ""
                        }`}
                        onClick={() => toggleSort(header.column)}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        <ArrowUpDown size={14} />
                      </button>
                    ) : (
                      flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )
                    )}
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>

        <tbody>
          {loading ? (
            <tr>
              <td className="dt-empty" colSpan={columns.length}>
                Carregando...
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td className="dt-empty" colSpan={columns.length}>
                Nenhum registro encontrado
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i}>
                {columns.map((col, j) => {
                  const value = col.cell
                    ? col.cell({ row: { original: row } })
                    : row[col.accessorKey];

                  return (
                    <td key={j}>
                      <span className="dt-cell-truncate" title={value}>
                        {value}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>

      {/* Paginação */}
      <div className="dt-pagination">
        <button
          className="dt-page-btn"
          disabled={page === 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          <ChevronLeft size={16} /> Anterior
        </button>

        <span className="dt-page-info">
          Página <strong>{page}</strong> de{" "}
          <strong>{Math.ceil(total / limit)}</strong>
        </span>

        <button
          className="dt-page-btn"
          disabled={page * limit >= total}
          onClick={() => setPage((p) => p + 1)}
        >
          Próximo <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
