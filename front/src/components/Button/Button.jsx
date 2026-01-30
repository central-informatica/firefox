import React from "react";

export default function Button({ children, variant = "primary", className = "", ...props }) {
  const baseStyles = "px-4 py-2.5 rounded-button cursor-pointer text-base font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none flex items-center justify-center gap-2";

  const variants = {
    primary: "bg-xfire-orange text-white hover:bg-xfire-orange/90 shadow-lg shadow-xfire-orange/20 hover:shadow-xl hover:shadow-xfire-orange/30",
    secondary: "bg-transparent text-neutral-200 border border-neutral-700 hover:bg-neutral-800 hover:border-neutral-600",
    danger: "bg-xfire-red text-white hover:bg-xfire-red/90",
  };

  const variantStyles = variants[variant] || variants.primary;

  return (
    <button
      className={`${baseStyles} ${variantStyles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
