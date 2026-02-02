let cache = null;
export function getTimezoneOptions() {
  if (!cache) {
    cache = typeof Intl.supportedValuesOf === "function"
      ? Intl.supportedValuesOf("timeZone")
      : ["UTC", "America/Sao_Paulo", "America/Manaus"];
  }
  return cache;
}
