import React from "react";

export default function ButtonExcluir({ children, className = "", ...props }) {
  return (
    <button
      className={`bg-xfire-red text-white px-4 py-2.5 rounded-button cursor-pointer text-base font-medium hover:bg-xfire-red/90 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
