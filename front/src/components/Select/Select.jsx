import React from "react";
import Select from "react-select";

const defaultStyles = {
  control: (base) => ({
    ...base,
    borderRadius: 8,
    minHeight: 38,
    borderColor: "#c9c9c9",
    boxShadow: "none",
    ":hover": {
      borderColor: "#b3b3b3",
    },
  }),

  menu: (base) => ({
    ...base,
    zIndex: 9999, // evita ficar atrás do menu lateral
    borderRadius: 8,
  }),

  option: (base, state) => ({
    ...base,
    color: "black",  // cor da fonte
    backgroundColor: state.isSelected
      ? "#e0e7ff"     // fundo quando selecionado
      : state.isFocused
      ? "#f3f4f6"     // fundo no hover
      : "white",
    ":active": {
      backgroundColor: "#dbeafe",
    },
  }),

  singleValue: (base) => ({
    ...base,
    color: "black", // texto do item selecionado
  }),
};

export default function SelectCustom({ styles = {}, ...props }) {
  const mergedStyles = {
    ...defaultStyles,
    ...styles, // permite sobrescrever valores
  };

  return <Select {...props} styles={mergedStyles} />;
}
