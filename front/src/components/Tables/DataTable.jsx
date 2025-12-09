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
    <div className="mt-5 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
      {/* Busca */}
      <div className="relative mb-3">
        <Search size={18} className="absolute top-[9px] left-2.5 text-gray-500" />
        <input
          type="text"
          placeholder="Buscar..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="w-[280px] py-2 px-3 pl-8 rounded-md border border-gray-300 text-sm bg-white text-black focus:outline-none focus:border-[#3a7afe]"
        />
      </div>

      {/* Tabela */}
      <table className="table-fixed w-full border-collapse mt-2">
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => {
                const key = header.column.columnDef.accessorKey;
                const isCurrentSort = sort.includes(key);

                return (
                  <th className="bg-gray-100 p-2.5 text-left font-bold border-b-2 border-gray-300 text-gray-700" key={header.id}>
                    {key ? (
                      <button
                        className={`bg-transparent border-none font-bold cursor-pointer flex items-center gap-1.5 hover:text-black ${
                          isCurrentSort ? "text-[#1e64ff]" : "text-gray-700"
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
              <td className="text-center py-5 text-gray-500" colSpan={columns.length}>
                Carregando...
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td className="text-center py-5 text-gray-500" colSpan={columns.length}>
                Nenhum registro encontrado
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} className="hover:bg-[#f6faff]">
                {columns.map((col, j) => {
                  const value = col.cell
                    ? col.cell({ row: { original: row } })
                    : row[col.accessorKey];

                  return (
                    <td className="p-2.5 border-b border-gray-200 text-[#24044b]" key={j}>
                      <span className="max-w-[180px] inline-block overflow-hidden whitespace-nowrap text-ellipsis align-middle" title={value}>
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
      <div className="mt-3.5 flex items-center gap-3">
        <button
          className="bg-[#1e64ff] text-white border-none py-2 px-3.5 rounded-md cursor-pointer text-sm disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-1"
          disabled={page === 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          <ChevronLeft size={16} /> Anterior
        </button>

        <span className="text-sm text-gray-700">
          Página <strong>{page}</strong> de{" "}
          <strong>{Math.ceil(total / limit)}</strong>
        </span>

        <button
          className="bg-[#1e64ff] text-white border-none py-2 px-3.5 rounded-md cursor-pointer text-sm disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-1"
          disabled={page * limit >= total}
          onClick={() => setPage((p) => p + 1)}
        >
          Próximo <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
