// timezoneService.js

// Usa API nativa do navegador (melhor opção)
/*export function getTimezones() {
  if (typeof Intl.supportedValuesOf === "function") {
    return Intl.supportedValuesOf("timeZone");
  }

  // fallback caso o navegador seja MUITO antigo
  return [
    "UTC",
    "America/Sao_Paulo",
    "America/Manaus",
    "America/Recife",
  ];
}*/

let cache = null;
export function getTimezoneOptions() {
  if (!cache) {
    cache = typeof Intl.supportedValuesOf === "function"
      ? Intl.supportedValuesOf("timeZone")
      : ["UTC", "America/Sao_Paulo", "America/Manaus"];
  }
  return cache;
}
