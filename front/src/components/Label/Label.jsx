import React from "react";
import "./Label.css";

export default function Label({ children, htmlFor, className = "" }) {
  return (
    <label htmlFor={htmlFor} className={`ui-label ${className}`}>
      {children}
    </label>
  );
}
