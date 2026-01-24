import { useEffect, useState } from "react";
import { listarMinhasEmpresas } from "../services/empresasService";

export function useEmpresasUsuario() {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function carregar() {
      try {
        const res = await listarMinhasEmpresas();
        const empresas = res.data ?? [];

        setOptions(
          empresas.map((e) => ({
            value: e.empresa_id,
            label: e.fantasia || e.razao_social,
          }))
        );

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