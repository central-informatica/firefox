import React from "react";
import ReactSelect from "react-select";

export default function Select({
  label,
  options = [],
  value,
  onChange,
  placeholder = "Selecione...",
  className,
  ...props
}) {
  // Converte o value simples (ex: 1, "ADMIN") para o formato { value, label }
  const selectedOption =
    options.find((opt) => opt.value === value) || null;

  return (
    <div className="select-group">
      {label && <label className="select-label">{label}</label>}

      <ReactSelect
        className={className}
        options={options}
        value={selectedOption}
        onChange={(opt) => onChange(opt ? opt.value : null)}
        placeholder={placeholder}
        styles={{
          menu: (provided) => ({
            ...provided,
            zIndex: 9999,
          }),
        }}
        {...props}
      />
    </div>
  );
}
