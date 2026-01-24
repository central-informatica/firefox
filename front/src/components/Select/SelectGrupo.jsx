import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";
import CreatableSelect from "react-select/creatable";

import { listarGruposPorEmpresa } from "../../services/gruposService";
import { criarGrupo } from "../../services/gruposService";

export default function SelectGrupo({
  empresaId,
  planoTrabalhoId,
  value,
  onChange,
  isDisabled,
  placeholder = "Selecione ou crie um grupo",
}) {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  // 🔁 Carrega grupos sempre que a empresa ou o plano mudam
  useEffect(() => {
    if (!empresaId) {
      setOptions([]);
      return;
    }

    setLoading(true);

    // Se planoTrabalhoId estiver presente, passamos como filtro; caso contrário, listamos por empresa
    listarGruposPorEmpresa(empresaId, planoTrabalhoId)
      .then((grupos) => {
        setOptions(
          grupos.map((g) => ({
            value: g.grupo_id,
            label: g.nome,
          }))
        );
      })
      .catch((err) => {
        console.error("Erro ao carregar grupos:", err);
        setOptions([]);
      })
      .finally(() => setLoading(false));
  }, [empresaId, planoTrabalhoId]);

  // 🔎 Grupo selecionado
  const selected = useMemo(() => {
    return options.find((opt) => opt.value === value) || null;
  }, [options, value]);

  // ➕ Criar grupo inline
  const handleCreate = async (inputValue) => {
    if (!planoTrabalhoId) return;

    try {
      setLoading(true);

      const novoGrupo = await criarGrupo({
        nome: inputValue,
        plano_id: planoTrabalhoId,
        empresa_id: empresaId,
      });

      const option = {
        value: novoGrupo.grupo_id,
        label: novoGrupo.nome,
      };

      setOptions((prev) => [...prev, option]);
      onChange(option.value);
    } catch (err) {
      console.error("Erro ao criar grupo:", err.message);
      toast.error("Erro ao criar grupo ", err?.message || "");
    } finally {
      setLoading(false);
    }
  };

  return (
    <CreatableSelect
      isClearable
      isDisabled={isDisabled || !empresaId}
      isLoading={loading}
      options={options}
      value={selected}
      onChange={(opt) => onChange?.(opt ? opt.value : null)}
      onCreateOption={handleCreate}
      placeholder={
        !empresaId
          ? "Selecione uma empresa primeiro"
          : (!planoTrabalhoId ? placeholder : placeholder)
      }
      formatCreateLabel={(input) => `Criar grupo "${input}"`}
    />
  );
}
