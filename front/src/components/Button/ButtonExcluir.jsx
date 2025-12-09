import React from "react";

export default function Button({ children, ...props }) {
  return (
    <button
      className="bg-danger text-white px-4 py-2.5 rounded-md cursor-pointer text-base hover:bg-red-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none"
      {...props}
    >
      {children}
    </button>
  );
}
