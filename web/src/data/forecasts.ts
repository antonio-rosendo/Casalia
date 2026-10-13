import { useEffect, useState } from "react";

// Shape of public/forecasts.json, written by ml/publish_forecasts.py.
// Changes are fractions: 0.05 = +5% over 12 months.
export interface RegionForecast {
  region: string;
  name: string;
  small_market: boolean;
  price_m2_at_origin: number;
  champion: { chg_12m: number; low: number; high: number };
  challenger: { chg_12m: number; explanation?: Record<string, number> };
}

export interface ForecastFile {
  generated_on: string;
  origin: string;
  target: string;
  champion: string;
  challenger: string;
  challenger_average_forecast?: number;
  regions: RegionForecast[];
}

export const GROUPS = ["momentum", "inflation", "rates", "labour", "credit"] as const;

// Short names; the JSON carries the official MIVAU ones ("Madrid (Comunidad de)").
export const REGION_NAMES: Record<string, string> = {
  andalucia: "Andalucía",
  aragon: "Aragón",
  asturias: "Asturias",
  baleares: "Illes Balears",
  canarias: "Canarias",
  cantabria: "Cantabria",
  castilla_la_mancha: "Castilla-La Mancha",
  castilla_y_leon: "Castilla y León",
  cataluna: "Cataluña",
  ceuta: "Ceuta",
  comunitat_valenciana: "Comunitat Valenciana",
  extremadura: "Extremadura",
  galicia: "Galicia",
  madrid: "Madrid",
  melilla: "Melilla",
  murcia: "Murcia",
  navarra: "Navarra",
  pais_vasco: "País Vasco",
  rioja: "La Rioja",
};

export const regionName = (r: RegionForecast) => REGION_NAMES[r.region] ?? r.name;

// Fetched once and shared by every component that needs it.
let request: Promise<ForecastFile> | null = null;

function loadForecasts(): Promise<ForecastFile> {
  request ??= fetch(`${import.meta.env.BASE_URL}forecasts.json`).then((res) => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }).then((data: ForecastFile) => {
    if (!Array.isArray(data.regions) || data.regions.length === 0) throw new Error("No regions in forecasts.json");
    return data;
  });
  return request;
}

export function useForecasts() {
  const [state, setState] = useState<{ data?: ForecastFile; error?: boolean }>({});
  useEffect(() => {
    let active = true;
    loadForecasts()
      .then((data) => active && setState({ data }))
      .catch(() => {
        request = null;
        if (active) setState({ error: true });
      });
    return () => {
      active = false;
    };
  }, []);
  return state;
}
