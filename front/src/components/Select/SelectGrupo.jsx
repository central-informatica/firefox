import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";
import CreatableSelect from "react-select/creatable";

import { listarGruposPorEmpresa } from "../../services/gruposService";
import { criarGrupo } from "../../services/gruposService";

const darkThemeStyles = {
  control: (base, state) => ({
    ...base,
    backgroundColor: "#222222",
    borderRadius: 8,
    minHeight: 44,
    borderColor: state.isFocused ? "#F57C00" : "#2B2B2B",
    boxShadow: state.isFocused ? "0 0 0 2px rgba(245, 124, 0, 0.2)" : "none",
    ":hover": {
      borderColor: state.isFocused ? "#F57C00" : "#424242",
    },
  }),
  menu: (base) => ({
    ...base,
    backgroundColor: "#1A1A1A",
    borderRadius: 8,
    border: "1px solid #2B2B2B",
    zIndex: 9999,
  }),
  menuList: (base) => ({
    ...base,
    padding: 4,
  }),
  option: (base, state) => ({
    ...base,
    backgroundColor: state.isSelected
      ? "#F57C00"
      : state.isFocused
      ? "#2B2B2B"
      : "transparent",
    color: state.isSelected ? "white" : "#F5F5F5",
    borderRadius: 4,
    cursor: "pointer",
    ":active": {
      backgroundColor: "#F57C00",
    },
  }),
  singleValue: (base) => ({
    ...base,
    color: "#F5F5F5",
  }),
  input: (base) => ({
    ...base,
    color: "#F5F5F5",
  }),
  placeholder: (base) => ({
    ...base,
    color: "#757575",
  }),
  indicatorSeparator: (base) => ({
    ...base,
    backgroundColor: "#424242",
  }),
  dropdownIndicator: (base, state) => ({
    ...base,
    color: state.isFocused ? "#F57C00" : "#757575",
    ":hover": {
      color: "#F57C00",
    },
  }),
  clearIndicator: (base) => ({
    ...base,
    color: "#757575",
    ":hover": {
      color: "#C62828",
    },
  }),
  noOptionsMessage: (base) => ({
    ...base,
    color: "#757575",
  }),
};

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
          : placeholder
      }
      formatCreateLabel={(input) => `Criar grupo "${input}"`}
      styles={darkThemeStyles}
    />
  );
}
