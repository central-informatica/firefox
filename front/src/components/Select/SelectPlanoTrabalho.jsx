import SelectCustom from "./Select";
import { useEffect, useState } from "react";
import { listarPlanosTrabalho } from "../../services/planosTrabalhoService";

export default function SelectPlanoTrabalho({
  empresaId,
  value,
  onChange,
  placeholder = "Selecione o plano de trabalho",
  ...props
}) {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!empresaId) {
      setOptions([]);
      onChange?.(null);
      return;
    }

    const carregarPlanos = async () => {
      setLoading(true);
      try {
        const response = await listarPlanosTrabalho({
          page: 1,
          limit: 100,
          empresa_id: empresaId,
        });

        const planos = response?.data || [];

        setOptions(
          planos.map((p) => ({
            value: p.plano_id,
            label: p.nome,
          }))
        );
      } finally {
        setLoading(false);
      }
    };

    carregarPlanos();
  }, [empresaId]);

  const selected =
    options.find((o) => String(o.value) === String(value)) || null;

  return (
    <SelectCustom
      options={options}
      value={selected}
      isLoading={loading}
      onChange={(opt) => onChange?.(opt ? opt.value : null)}
      placeholder={
        empresaId ? placeholder : "Selecione uma empresa primeiro"
      }
      isClearable
      isDisabled={!empresaId}
      {...props}
    />

  );
}
