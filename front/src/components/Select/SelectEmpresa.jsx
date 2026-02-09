import SelectCustom from "./Select";
import { useEmpresasUsuario } from "../../hooks/useEmpresasUsuario";

export default function SelectEmpresa({
  value,
  onChange,
  onChangeWithData,
  placeholder = "Selecione a empresa",
  ...props
}) {
  const { options = [], loading } = useEmpresasUsuario();
  const selected =
    options.find(
      (o) => String(o.value) === String(value)
    ) || null;

  const handleChange = (opt) => {
    // If onChangeWithData is provided, pass the full option (id + ativo)
    if (onChangeWithData) {
      onChangeWithData(opt ? { id: opt.value, ativo: opt.ativo } : null);
    }
    // Always call onChange with just the value for backward compatibility
    onChange?.(opt ? opt.value : null);
  };

  return (
    <SelectCustom
      options={options}
      value={selected}
      isLoading={loading}
      onChange={handleChange}
      placeholder={placeholder}
      isClearable
      {...props}
    />
  );
}
