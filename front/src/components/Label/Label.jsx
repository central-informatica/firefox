import React from "react";

export default function Label({ children, htmlFor, className = "" }) {
  return (
    <label htmlFor={htmlFor} className={`block mb-1.5 text-sm font-semibold text-neutral-200 tracking-wide ${className}`}>
      {children}
    </label>
  );
}
