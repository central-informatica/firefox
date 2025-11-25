import React from "react";
import "./Input.css";

export default function Input({ label, ...props }) {
  return (
    <div className="input-group">
      {label && <label className="input-label">{label}</label>}
      <input className="input" {...props} />
    </div>
  );
}

