const locale = (lng: string) => (lng.startsWith("es") ? "es-ES" : "en-GB");

export const pct = (x: number, lng: string, digits = 1) =>
  new Intl.NumberFormat(locale(lng), {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    signDisplay: "exceptZero",
  }).format(x);

// A change expressed as a fraction, shown in percentage points ("p. p." in Spanish).
export const pp = (x: number, lng: string) =>
  `${new Intl.NumberFormat(locale(lng), {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
    signDisplay: "exceptZero",
  }).format(x * 100)}${lng.startsWith("es") ? " p. p." : " pp"}`;

export const num = (x: number, lng: string, digits = 2) =>
  new Intl.NumberFormat(locale(lng), {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(x);

export const euros = (x: number, lng: string) =>
  new Intl.NumberFormat(locale(lng), {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(x);

export const longDate = (iso: string, lng: string) =>
  new Intl.DateTimeFormat(locale(lng), { dateStyle: "long" }).format(new Date(`${iso}T00:00:00`));

// "2026-Q2" -> "2026-T2" in Spanish (trimestre).
export const quarter = (label: string, lng: string) => (lng.startsWith("es") ? label.replace("-Q", "-T") : label);
