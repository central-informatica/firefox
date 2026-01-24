//import React from "react";
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
    zIndex: 9999, 
    borderRadius: 8,
  }),

  option: (base, state) => ({
    ...base,
    color: "black",  
    backgroundColor: state.isSelected
      ? "#e0e7ff"    
      : state.isFocused
      ? "#f3f4f6"    
      : "white",
    ":active": {
      backgroundColor: "#dbeafe",
    },
  }),

  singleValue: (base) => ({
    ...base,
    color: "black", 
  }),
};

export default function SelectCustom({ styles = {}, ...props }) {
  const mergedStyles = {
    ...defaultStyles,
    ...styles, 
  };

  return <Select {...props} styles={mergedStyles} />;
}
