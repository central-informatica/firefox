import React from "react";

export default function Label({ children, htmlFor, className = "" }) {
  return (
    <label htmlFor={htmlFor} className={`block mb-1.5 text-sm font-semibold text-gray-800 tracking-wide ${className}`}>
      {children}
    </label>
  );
}
