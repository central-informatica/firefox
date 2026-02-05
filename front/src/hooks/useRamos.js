import { useEffect, useState } from "react";
import { listarTodosRamos } from "../services/ramosService";

export function useRamos() {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function carregar() {
      try {
        const response = await listarTodosRamos();
        console.log("[useRamos] response:", response);

        // Adapta o response do Auth service para o formato do select
        // Tenta diferentes estruturas possíveis
        let categorias = [];
        if (Array.isArray(response)) {
          categorias = response;
        } else if (response?.data && Array.isArray(response.data)) {
          categorias = response.data;
        } else if (response?.categories && Array.isArray(response.categories)) {
          categorias = response.categories;
        }

        console.log("[useRamos] categorias:", categorias);
        if (categorias.length > 0) {
          console.log("[useRamos] primeiro item:", categorias[0]);
          console.log("[useRamos] campos disponíveis:", Object.keys(categorias[0]));
        }

        setOptions(
          categorias.map((c) => {
            // Determina o value (id da categoria)
            const value = c.id || c.category_id || c.codigo || c.code;
            // Determina o label (nome da categoria)
            // Auth service retorna 'category' como nome do campo
            const label = c.category || c.name || c.category_name || c.nome || c.description || c.descricao;

            console.log("[useRamos] mapeando:", { original: c, value, label });

            return { value, label };
          })
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
