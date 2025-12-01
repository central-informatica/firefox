import React from "react";
import { IMaskInput } from "react-imask";
import "./Input.css";

export default function InputMaskField({ label, mask, value, onChange, className = "", ...props }) {
  return (
    <div className="input-group">
      {label && <label className="input-label">{label}</label>}

      <IMaskInput
        mask={mask}
        value={value}
        onAccept={(val) => onChange({ target: { value: val } })}
        className={`input ${className}`}
        {...props}
      />
    </div>
  );
}
