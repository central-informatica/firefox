import SelectCustom from "./Select";
import { useRamos } from "../../hooks/useRamos";

export default function SelectRamo({
  value,
  onChange,
  placeholder = "Selecione o ramo de atuação",
  ...props
}) {
  const { options = [], loading } = useRamos();
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
