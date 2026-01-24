export function formatDate(dateString) {
  if (!dateString) return "";

  const date = new Date(dateString);
  const locale = navigator.language || "pt-BR";

  if (isNaN(date)) return "";

  return date.toLocaleDateString(locale);
}

export default formatDate;
