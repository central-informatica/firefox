import React, { useEffect, useRef } from "react";
//import "./Select.css";
import "./Select2Style.css";

export default function Select({ label, options = [], value, onChange, className, ...props }) {
  const selectRef = useRef();

  useEffect(() => {
    const $ = window.$; // ← pega o jQuery global do CDN
    const $select = $(selectRef.current);

    console.log("jQuery:", typeof $);
    console.log("Select2 existe?", typeof $.fn.select2);

    if (!$.fn.select2) {
      console.error("❌ Select2 NÃO carregou.");
      return;
    }

    $select.select2({
      width: "100%",
      placeholder: props.placeholder || "Selecione...",
      language: {
        noResults: () => "Nenhum resultado encontrado",
    }
    });

    $select.on("change", (e) => onChange?.(e));

    if (value) {
      $select.val(value).trigger("change");
    }

    return () => $select.select2("destroy");
  }, []);

  return (
    <div className="select-group">
      {label && <label className="select-label">{label}</label>}
      <select ref={selectRef} className={className} {...props}>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
