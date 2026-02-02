import React from "react";
import { IMaskInput } from "react-imask";

export default function InputMaskField({ label, mask, value, onChange, className = "", ...props }) {
  const baseClass = "p-2.5 border border-gray-300 rounded-md text-[15px] text-black bg-[#fcfcfa] w-full box-border focus:border-primary focus:outline-none focus:bg-[#e9f7f8]";

  return (
    <div className="mb-[15px] flex flex-col w-full">
      {label && <label className="mb-2 text-sm font-medium text-gray-700">{label}</label>}

      <IMaskInput
        mask={mask}
        value={value}
        onAccept={(val) => onChange({ target: { value: val } })}
        className={`${baseClass} ${className}`}
        {...props}
      />
    </div>
  );
}
