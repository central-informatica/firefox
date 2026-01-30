import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { ChevronLeft, ChevronRight, ArrowUpDown, Search } from "lucide-react";
import { useEffect, useState } from "react";

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
    <div className="mt-5 bg-dark-secondary p-4 rounded-card border border-neutral-900">
      {/* Busca */}
      <div className="relative mb-3">
        <Search size={18} className="absolute top-[12px] left-3 text-neutral-500" />
        <input
          type="text"
          placeholder="Buscar..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="w-[280px] py-2.5 px-3 pl-10 rounded-lg border border-neutral-800 text-sm bg-dark-tertiary text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:border-xfire-orange focus:ring-2 focus:ring-xfire-orange/20 transition-all duration-200"
        />
      </div>

      {/* Tabela */}
      <div className="overflow-x-auto">
        <table className="table-fixed w-full border-collapse mt-2">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => {
                  const key = header.column.columnDef.accessorKey;
                  const isCurrentSort = sort.includes(key);

                  return (
                    <th className="bg-dark-tertiary p-3 text-left font-semibold border-b border-neutral-800 text-neutral-300 first:rounded-tl-lg last:rounded-tr-lg" key={header.id}>
                      {key ? (
                        <button
                          className={`bg-transparent border-none font-semibold cursor-pointer flex items-center gap-1.5 hover:text-white transition-colors ${
                            isCurrentSort ? "text-xfire-orange" : "text-neutral-300"
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
                <td className="text-center py-8 text-neutral-500" colSpan={columns.length}>
                  <div className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-xfire-orange" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Carregando...</span>
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td className="text-center py-8 text-neutral-500" colSpan={columns.length}>
                  Nenhum registro encontrado
                </td>
              </tr>
            ) : (
              data.map((row, i) => (
                <tr key={i} className="hover:bg-dark-tertiary/50 transition-colors">
                  {columns.map((col, j) => {
                    const value = col.cell
                      ? col.cell({ row: { original: row } })
                      : row[col.accessorKey];

                    return (
                      <td className="p-3 border-b border-neutral-800 text-neutral-100" key={j}>
                        <span className="max-w-[180px] inline-block overflow-hidden whitespace-nowrap text-ellipsis align-middle" title={typeof value === 'string' ? value : ''}>
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
      </div>

      {/* Paginacao */}
      <div className="mt-4 flex items-center gap-3">
        <button
          className="bg-xfire-orange text-white border-none py-2 px-4 rounded-button cursor-pointer text-sm font-medium disabled:bg-neutral-700 disabled:cursor-not-allowed flex items-center gap-1 hover:bg-xfire-orange/90 transition-all duration-200"
          disabled={page === 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          <ChevronLeft size={16} /> Anterior
        </button>

        <span className="text-sm text-neutral-400">
          Pagina <strong className="text-neutral-100">{page}</strong> de{" "}
          <strong className="text-neutral-100">{Math.ceil(total / limit) || 1}</strong>
        </span>

        <button
          className="bg-xfire-orange text-white border-none py-2 px-4 rounded-button cursor-pointer text-sm font-medium disabled:bg-neutral-700 disabled:cursor-not-allowed flex items-center gap-1 hover:bg-xfire-orange/90 transition-all duration-200"
          disabled={page * limit >= total}
          onClick={() => setPage((p) => p + 1)}
        >
          Proximo <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
