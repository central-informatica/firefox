import { useEffect, useState } from "react";
import { listarMinhasEmpresas } from "../services/empresasService";

export function useEmpresasUsuario() {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function carregar() {
      try {
        const res = await listarMinhasEmpresas();
        console.log("[useEmpresasUsuario] resposta:", res);
        const empresas = res.data ?? [];
        console.log("[useEmpresasUsuario] empresas:", empresas);

        const opts = empresas.map((e) => ({
          value: e.empresa_id,
          label: e.fantasia || e.razao_social || e.name,
          ativo: e.ativo !== false, // default true
        }));
        console.log("[useEmpresasUsuario] options:", opts);
        setOptions(opts);

      } catch (e) {
        console.error("[useEmpresasUsuario] erro:", e);
        setOptions([]);
      } finally {
        setLoading(false);
      }
    }

    carregar();
  }, []);

  return { options, loading };
}