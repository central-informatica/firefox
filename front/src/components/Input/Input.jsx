import React from "react";

export default function Input({ label, className, ...props }) {
  const baseClass = "p-3 border border-neutral-800 rounded-lg text-[15px] text-neutral-100 bg-dark-tertiary w-full box-border focus:border-xfire-orange focus:outline-none focus:ring-2 focus:ring-xfire-orange/20 placeholder:text-neutral-500 transition-all duration-200";
  const finalClass = [baseClass, className].filter(Boolean).join(" ");

  return (
    <div className="flex flex-col w-full">
      {label && <label className="mb-2 text-sm font-medium text-neutral-300">{label}</label>}
      <input className={finalClass} {...props} />
    </div>
  );
}
