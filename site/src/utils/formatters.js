export const formatNumber = (value) =>
  new Intl.NumberFormat("fr-FR").format(Number(value || 0));

export const formatDate = (value) => {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fr-FR", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  }).format(date);
};

export const shortName = (value, max = 28) => {
  if (!value) return "n/a";
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
};
