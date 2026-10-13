import { useRef, useState } from "react";
import { Euro, ExternalLink, MapPin, TriangleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Card } from "../ui/Card";
import { SectionHeader } from "../ui/SectionHeader";
import { GROUPS, regionName, useForecasts } from "../../data/forecasts";
import type { ForecastFile, RegionForecast } from "../../data/forecasts";
import { euros, longDate, pct, pp, quarter } from "../../utils/format";
import { REPO_URL } from "../../config";
import { cn } from "../../utils/cn";

const inputClass =
  "w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange";

export function Forecasts() {
  const { t, i18n } = useTranslation();
  const { data, error } = useForecasts();
  const lng = i18n.language;

  return (
    <section id="forecasts" className="py-20 md:py-24 border-b-4 border-neo-black bg-neo-tint scroll-mt-20">
      <div className="container mx-auto px-4 md:px-8">
        <SectionHeader title={t("forecasts.title")}>
          {data &&
            t("forecasts.subtitle", {
              origin: quarter(data.origin, lng),
              target: quarter(data.target, lng),
              generated: longDate(data.generated_on, lng),
            })}
        </SectionHeader>
        {error && <p className="font-mono p-3 bg-neo-orange text-ink border-2 border-neo-black inline-block">{t("forecasts.error")}</p>}
        {!data && !error && <p className="font-mono motion-safe:animate-pulse">{t("forecasts.loading")}</p>}
        {data && <ForecastExplorer data={data} />}
      </div>
    </section>
  );
}

function ForecastExplorer({ data }: { data: ForecastFile }) {
  const { t, i18n } = useTranslation();
  const lng = i18n.language;
  const [selected, setSelected] = useState("madrid");
  const [price, setPrice] = useState("");
  const detailRef = useRef<HTMLDivElement>(null);

  const region = data.regions.find((r) => r.region === selected) ?? data.regions[0];
  const options = [...data.regions].sort((a, b) => regionName(a).localeCompare(regionName(b), "es"));
  // Accept "250000", "250.000" or "250,000": keep the digits only.
  const value = Number(price.replace(/\D/g, ""));
  const hasPrice = value > 0;
  const champ = region.champion;

  const selectFromChart = (slug: string) => {
    setSelected(slug);
    const smooth = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    detailRef.current?.scrollIntoView({ behavior: smooth ? "smooth" : "auto", block: "start" });
  };

  return (
    <>
      <div ref={detailRef} className="scroll-mt-24 space-y-8">
        <Card className="grid md:grid-cols-2 gap-5">
          <label className="block space-y-2">
            <span className="label flex items-center gap-2">
              <MapPin className="w-4 h-4" /> {t("forecasts.region")}
            </span>
            <select value={region.region} onChange={(e) => setSelected(e.target.value)} className={inputClass}>
              {options.map((r) => (
                <option key={r.region} value={r.region}>{regionName(r)}</option>
              ))}
            </select>
          </label>
          <label className="block space-y-2">
            <span className="label flex items-center gap-2">
              <Euro className="w-4 h-4" /> {t("forecasts.price", { origin: quarter(data.origin, lng) })}
            </span>
            <input
              type="text"
              inputMode="numeric"
              autoComplete="off"
              value={price}
              placeholder={t("forecasts.pricePlaceholder")}
              onChange={(e) => setPrice(e.target.value)}
              className={inputClass}
            />
          </label>
        </Card>

        <div className="grid lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-7 bg-ink text-paper border-4 border-neo-black shadow-neo-heavy p-6 md:p-8 space-y-5">
            <h3 className="label text-paper/80">{t("forecasts.champion")}</h3>
            <div>
              <p className="text-6xl md:text-8xl font-bold tracking-tighter text-lime">{pct(champ.chg_12m, lng)}</p>
              <p className="font-mono text-base mt-2">
                {t("forecasts.interval", { low: pct(champ.low, lng), high: pct(champ.high, lng) })}
              </p>
            </div>
            {hasPrice && (
              <div className="border-t-2 border-paper/20 pt-4">
                <p className="label text-paper/80">{t("forecasts.projected", { target: quarter(data.target, lng) })}</p>
                <p className="text-3xl font-bold tracking-tight">{euros(value * (1 + champ.chg_12m), lng)}</p>
                <p className="font-mono text-sm">
                  {t("forecasts.projectedRange", {
                    low: euros(value * (1 + champ.low), lng),
                    high: euros(value * (1 + champ.high), lng),
                  })}
                </p>
                <p className="text-sm text-paper/80 mt-2">{t("forecasts.homeNote")}</p>
              </div>
            )}
            <div className="border-t-2 border-paper/20 pt-4 text-sm text-paper/80 space-y-1">
              <p>{t("forecasts.championNote")}</p>
              <p>{t("forecasts.intervalNote")}</p>
            </div>
            {region.small_market && (
              <p className="flex gap-2 items-start p-3 bg-neo-orange text-ink border-2 border-paper font-mono text-xs font-bold">
                <TriangleAlert className="w-4 h-4 shrink-0" /> {t("forecasts.smallMarket")}
              </p>
            )}
          </div>

          <Card className="lg:col-span-5 flex flex-col gap-4">
            <div className="pb-4 border-b-2 border-neo-black space-y-1">
              <h3 className="label text-neo-darkgray">{t("forecasts.challenger")}</h3>
              <p className="text-5xl font-bold tracking-tighter">{pct(region.challenger.chg_12m, lng)}</p>
              <p className="text-sm text-neo-darkgray">{t("forecasts.challengerNote")}</p>
            </div>
            {region.challenger.explanation && data.challenger_average_forecast !== undefined && (
              <ShapChart region={region} average={data.challenger_average_forecast} />
            )}
            <p className="text-sm text-neo-darkgray border-l-4 border-neo-orange pl-3">
              {t("forecasts.shapNote")} {t("forecasts.rounded")}
            </p>
          </Card>
        </div>

        <GapNote data={data} />
      </div>

      <AllRegions data={data} selected={region.region} onSelect={selectFromChart} />

      <p className="mt-6 text-sm text-neo-darkgray">
        {t("forecasts.log", { target: quarter(data.target, lng) })}{" "}
        <a href={`${REPO_URL}/tree/master/ml/forecasts`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-bold underline decoration-2 underline-offset-4 hover:text-neo-accent">
          {t("forecasts.logLink")} <ExternalLink className="w-3 h-3" />
        </a>
      </p>
    </>
  );
}

// Why the two forecasts differ, computed from the data so it stays true every quarter.
function GapNote({ data }: { data: ForecastFile }) {
  const { t } = useTranslation();
  const total = data.regions.length;
  const below = data.regions.filter((r) => r.challenger.chg_12m < r.champion.chg_12m).length;
  const outside = data.regions.filter(
    (r) => r.challenger.chg_12m < r.champion.low || r.challenger.chg_12m > r.champion.high,
  ).length;
  const key = below * 2 >= total ? "forecasts.gapBelow" : "forecasts.gapAbove";

  return (
    <div className="border-4 border-neo-black bg-neo-white p-5 md:p-6">
      <h3 className="label mb-2">{t("forecasts.gapTitle")}</h3>
      <p className="leading-relaxed">
        {t(key, { below, above: total - below, outside, total })}
        {key === "forecasts.gapBelow" && ` ${t("forecasts.gapHistory")}`}
      </p>
    </div>
  );
}

// Waterfall-style SHAP view: average forecast + group contributions = this forecast.
function ShapChart({ region, average }: { region: RegionForecast; average: number }) {
  const { t, i18n } = useTranslation();
  const lng = i18n.language;
  const contributions = GROUPS.map((g) => ({ group: g, value: region.challenger.explanation?.[g] ?? 0 }));
  const largest = Math.max(...contributions.map((c) => Math.abs(c.value)), 1e-9);

  return (
    <div className="font-mono text-sm">
      <div className="flex justify-between py-2 border-b-2 border-neo-black">
        <span className="label">{t("forecasts.shapAverage")}</span>
        <span className="font-bold">{pct(average, lng)}</span>
      </div>
      {contributions.map(({ group, value }) => {
        const width = (Math.abs(value) / largest) * 50;
        return (
          <div key={group} className="grid grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1 py-2">
            <span className="label">{t(`forecasts.groups.${group}`)}</span>
            <span className="text-right font-bold">{pp(value, lng)}</span>
            <div className="relative h-4 border-2 border-neo-black bg-neo-white col-span-2" aria-hidden="true">
              <div className="absolute inset-y-0 left-1/2 w-0.5 bg-neo-darkgray" />
              <div
                className={cn("absolute inset-y-0", value >= 0 ? "bg-neo-orange" : "bg-neo-darkgray")}
                style={{ left: `${value >= 0 ? 50 : 50 - width}%`, width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
      <div className="flex justify-between py-2 border-t-2 border-neo-black">
        <span className="label">= {t("forecasts.shapResult")}</span>
        <span className="font-bold">{pct(region.challenger.chg_12m, lng)}</span>
      </div>
    </div>
  );
}

function AllRegions({ data, selected, onSelect }: { data: ForecastFile; selected: string; onSelect: (r: string) => void }) {
  const { t, i18n } = useTranslation();
  const lng = i18n.language;
  const rows = [...data.regions].sort(
    (a, b) => Number(a.small_market) - Number(b.small_market) || b.champion.chg_12m - a.champion.chg_12m,
  );

  // Axis in steps of 5 percentage points, always including 0.
  const step = 0.05;
  const values = rows.flatMap((r) => [r.champion.low, r.champion.high, r.challenger.chg_12m, 0]);
  const lo = Math.floor(Math.min(...values) / step) * step;
  const hi = Math.ceil(Math.max(...values) / step) * step;
  const x = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const ticks = Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => lo + i * step);
  // Phones: name and values on one line, the bar full width below.
  const grid = "grid grid-cols-[1fr_auto_auto] sm:grid-cols-[11rem_1fr_4rem_4rem] items-center gap-x-3 gap-y-1";
  const bar = "col-span-3 order-last sm:col-span-1 sm:order-none";

  return (
    <Card className="mt-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 mb-4 border-b-2 border-neo-black">
        <h3 className="text-xl font-bold uppercase tracking-tight">{t("forecasts.allTitle")}</h3>
        <div className="flex flex-wrap gap-4 font-mono text-xs">
          <span className="flex items-center gap-2"><span className="w-6 h-3 bg-neo-yellow border-2 border-neo-black" />{t("forecasts.legendInterval")}</span>
          <span className="flex items-center gap-2"><span className="w-1 h-4 bg-neo-black" />{t("forecasts.legendChampion")}</span>
          <span className="flex items-center gap-2"><span className="w-3 h-3 rotate-45 bg-neo-orange border border-neo-black" />{t("forecasts.legendChallenger")}</span>
        </div>
      </div>
      <div className="space-y-1">
        <div className={cn(grid, "px-1 label text-neo-darkgray")} aria-hidden="true">
          <span className="hidden sm:block" />
          <span className="hidden sm:block" />
          <span className="text-right sm:col-start-3">{t("forecasts.colMain")}</span>
          <span className="text-right text-neo-accent">{t("forecasts.colMl")}</span>
        </div>
        {rows.map((r) => {
          const c = r.champion;
          const ml = r.challenger.chg_12m;
          return (
            <button
              key={r.region}
              type="button"
              onClick={() => onSelect(r.region)}
              aria-pressed={r.region === selected}
              aria-label={t("forecasts.rowLabel", {
                name: regionName(r),
                main: pct(c.chg_12m, lng),
                low: pct(c.low, lng),
                high: pct(c.high, lng),
                ml: pct(ml, lng),
              })}
              className={cn(grid, "w-full text-left px-1 py-1 hover:bg-neo-tint", r.region === selected && "ring-2 ring-inset ring-neo-orange bg-neo-tint")}
            >
              <span className="label truncate">
                {regionName(r)}
                {r.small_market && <span className="text-neo-accent"> *</span>}
              </span>
              <span className={cn("relative h-7", bar)} aria-hidden="true">
                <span className="absolute inset-y-0 w-px bg-neo-darkgray" style={{ left: `${x(0)}%` }} />
                <span
                  className="absolute top-1.5 bottom-1.5 bg-neo-yellow border-2 border-neo-black"
                  style={{ left: `${x(c.low)}%`, width: `${x(c.high) - x(c.low)}%` }}
                />
                <span className="absolute inset-y-0 w-1 -translate-x-1/2 bg-neo-black" style={{ left: `${x(c.chg_12m)}%` }} />
                <span
                  className="absolute top-1/2 w-3 h-3 -translate-x-1/2 -translate-y-1/2 rotate-45 bg-neo-orange border border-neo-black"
                  style={{ left: `${x(ml)}%` }}
                />
              </span>
              <span className="font-mono text-xs font-bold text-right">{pct(c.chg_12m, lng)}</span>
              <span className="font-mono text-xs text-right text-neo-accent">{pct(ml, lng)}</span>
            </button>
          );
        })}
        <div className={cn(grid, "px-1 pt-2")} aria-hidden="true">
          <span className="font-mono text-xs text-neo-accent col-span-3 order-last sm:col-span-1 sm:order-none">
            {rows.some((r) => r.small_market) && `* ${t("forecasts.smallMarketMark")}`}
          </span>
          <span className={cn("relative h-5 border-t-2 border-neo-black", bar)}>
            {ticks.map((v) => (
              <span key={v} className="absolute top-1 -translate-x-1/2 font-mono text-xs" style={{ left: `${x(v)}%` }}>
                {pct(v, lng, 0)}
              </span>
            ))}
          </span>
        </div>
      </div>
    </Card>
  );
}
