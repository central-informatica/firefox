import React from "react";

export default function Input({ label, className, ...props }) {
  const baseClass = "p-2.5 border border-gray-300 rounded-md text-[15px] text-black bg-[#fcfcfa] w-full box-border focus:border-primary focus:outline-none focus:bg-[#e9f7f8]";
  const finalClass = [baseClass, className].filter(Boolean).join(" ");

  return (
    <div className="mb-[15px] flex flex-col w-full">
      {label && <label className="mb-2 text-sm font-medium text-gray-700">{label}</label>}
      <input className={finalClass} {...props} />
    </div>
  );
}