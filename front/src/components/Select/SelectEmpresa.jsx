import SelectCustom from "./Select";
import { useEmpresasUsuario } from "../../hooks/useEmpresasUsuario";

export default function SelectEmpresa({
  value,
  onChange,
  placeholder = "Selecione a empresa",
  ...props
}) {
  const { options = [], loading } = useEmpresasUsuario();
  const selected =
    options.find(
      (o) => String(o.value) === String(value)
    ) || null;

  return (
    <SelectCustom
      options={options}
      value={selected}
      isLoading={loading}
      onChange={(opt) => onChange?.(opt ? opt.value : null)}
      placeholder={placeholder}
      isClearable
      {...props}
    />
  );
}
