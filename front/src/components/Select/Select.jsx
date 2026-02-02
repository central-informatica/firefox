import Select from "react-select";

const darkThemeStyles = {
  control: (base, state) => ({
    ...base,
    backgroundColor: "#222222",
    borderRadius: 8,
    minHeight: 44,
    borderColor: state.isFocused ? "#F57C00" : "#2B2B2B",
    boxShadow: state.isFocused ? "0 0 0 2px rgba(245, 124, 0, 0.2)" : "none",
    ":hover": {
      borderColor: state.isFocused ? "#F57C00" : "#424242",
    },
  }),

  menu: (base) => ({
    ...base,
    backgroundColor: "#1A1A1A",
    borderRadius: 8,
    border: "1px solid #2B2B2B",
    zIndex: 9999,
  }),

  menuList: (base) => ({
    ...base,
    padding: 4,
  }),

  option: (base, state) => ({
    ...base,
    backgroundColor: state.isSelected
      ? "#F57C00"
      : state.isFocused
      ? "#2B2B2B"
      : "transparent",
    color: state.isSelected ? "white" : "#F5F5F5",
    borderRadius: 4,
    cursor: "pointer",
    ":active": {
      backgroundColor: "#F57C00",
    },
  }),

  singleValue: (base) => ({
    ...base,
    color: "#F5F5F5",
  }),

  input: (base) => ({
    ...base,
    color: "#F5F5F5",
  }),

  placeholder: (base) => ({
    ...base,
    color: "#757575",
  }),

  indicatorSeparator: (base) => ({
    ...base,
    backgroundColor: "#424242",
  }),

  dropdownIndicator: (base, state) => ({
    ...base,
    color: state.isFocused ? "#F57C00" : "#757575",
    ":hover": {
      color: "#F57C00",
    },
  }),

  clearIndicator: (base) => ({
    ...base,
    color: "#757575",
    ":hover": {
      color: "#C62828",
    },
  }),

  multiValue: (base) => ({
    ...base,
    backgroundColor: "#2B2B2B",
    borderRadius: 4,
  }),

  multiValueLabel: (base) => ({
    ...base,
    color: "#F5F5F5",
  }),

  multiValueRemove: (base) => ({
    ...base,
    color: "#9E9E9E",
    ":hover": {
      backgroundColor: "#C62828",
      color: "white",
    },
  }),

  noOptionsMessage: (base) => ({
    ...base,
    color: "#757575",
  }),
};

export default function SelectCustom({ styles = {}, ...props }) {
  const mergedStyles = {
    ...darkThemeStyles,
    ...styles,
  };

  return <Select {...props} styles={mergedStyles} />;
}
