import React from "react";

export default function Input({ label, className, ...props }) {
  const baseClass = "p-3 border border-gray-300 rounded-lg text-[15px] text-black bg-[#fcfcfa] w-full box-border focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:bg-white transition-all duration-200";
  const finalClass = [baseClass, className].filter(Boolean).join(" ");

  return (
    <div className="flex flex-col w-full">
      {label && <label className="mb-2 text-sm font-medium text-gray-700">{label}</label>}
      <input className={finalClass} {...props} />
    </div>
  );
}