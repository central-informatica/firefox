import React from "react";
import "./Input.css";

export default function Input({ label, className, ...props }) {
  const finalClass = ["input", className].filter(Boolean).join(" ");

  return (
    <div className="input-group">
      {label && <label className="input-label">{label}</label>}
      <input className={finalClass} {...props} />
    </div>
  );
}
