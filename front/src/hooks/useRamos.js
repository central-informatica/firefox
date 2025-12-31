import { useEffect, useState } from "react";
import { listarTodosRamos } from "../services/ramosService";

export function useRamos() {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function carregar() {
      try {
        const ramos = await listarTodosRamos();

        setOptions(
          ramos.map((r) => ({
            value: r.ramos_id,
            label: r.ramo,
          }))
        );

      } catch (e) {
        console.error("[useRamos] erro:", e);
        setOptions([]);
      } finally {
        setLoading(false);
      }
    }

    carregar();
  }, []);

  return { options, loading };
}
