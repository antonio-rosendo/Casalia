import { ExternalLink } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Card } from "../ui/Card";
import { SectionHeader } from "../ui/SectionHeader";
import { BASELINES, DEV_MAE, HOLDOUT_MAE } from "../../data/results";
import type { ModelKey } from "../../data/results";
import { REPO_URL } from "../../config";
import { num } from "../../utils/format";
import { cn } from "../../utils/cn";

// Shared axis so both charts are comparable.
const SCALE = Math.ceil(Math.max(...Object.values(DEV_MAE), ...Object.values(HOLDOUT_MAE)));

// Same colours as the forecasts: momentum lime, trained models orange, other rules grey.
const barColour = (model: ModelKey) =>
  model === "momentum" ? "bg-neo-yellow" : BASELINES.includes(model) ? "bg-neo-gray" : "bg-neo-orange";

const REPORTS = [
  { key: "results", file: "results.md" },
  { key: "holdout", file: "holdout.md" },
  { key: "intervals", file: "intervals.md" },
  { key: "diagnostics", file: "diagnostics.md" },
] as const;

function MaeChart({ title, sub, values, note }: { title: string; sub: string; values: Record<ModelKey, number>; note: string }) {
  const { t, i18n } = useTranslation();
  const rows = (Object.entries(values) as [ModelKey, number][]).sort((a, b) => a[1] - b[1]);

  return (
    <Card className="flex flex-col">
      <div className="pb-4 mb-4 border-b-2 border-neo-black">
        <h3 className="text-xl font-bold uppercase tracking-tight">{title}</h3>
        <p className="font-mono text-xs text-neo-darkgray mt-1">{sub}</p>
      </div>
      <div className="space-y-3 flex-1">
        {rows.map(([model, mae]) => (
          <div key={model} className="grid grid-cols-[1fr_auto] sm:grid-cols-[11rem_1fr_3rem] items-center gap-x-3 gap-y-1">
            <span className="label">{t(`results.models.${model}`)}</span>
            <span className="h-6 border-2 border-neo-black bg-neo-white relative col-span-2 order-last sm:col-span-1 sm:order-none" aria-hidden="true">
              <span
                className={cn("absolute inset-y-0 left-0 border-r-2 border-neo-black", barColour(model))}
                style={{ width: `${(mae / SCALE) * 100}%` }}
              />
            </span>
            <span className="font-mono text-sm font-bold text-right">{num(mae, i18n.language)}</span>
          </div>
        ))}
      </div>
      <p className="text-sm text-neo-darkgray mt-6 border-l-4 border-neo-orange pl-3">{note}</p>
    </Card>
  );
}

export function Results() {
  const { t } = useTranslation();
  const years = ["2022", "2023", "2024", "2025"] as const;

  return (
    <section id="results" className="py-20 md:py-24 border-b-4 border-neo-black bg-neo-white scroll-mt-20">
      <div className="container mx-auto px-4 md:px-8">
        <SectionHeader title={t("results.title")}>{t("results.intro")}</SectionHeader>

        <div className="flex flex-wrap gap-5 mb-6 font-mono text-xs">
          <span className="flex items-center gap-2"><span className="w-5 h-3 bg-neo-yellow border-2 border-neo-black" />{t("results.legendMomentum")}</span>
          <span className="flex items-center gap-2"><span className="w-5 h-3 bg-neo-gray border-2 border-neo-black" />{t("results.legendBaselines")}</span>
          <span className="flex items-center gap-2"><span className="w-5 h-3 bg-neo-orange border-2 border-neo-black" />{t("results.legendModels")}</span>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          <MaeChart title={t("results.dev")} sub={t("results.devSub")} values={DEV_MAE} note={t("results.devNote")} />
          <MaeChart title={t("results.holdout")} sub={t("results.holdoutSub")} values={HOLDOUT_MAE} note={t("results.holdoutNote")} />
        </div>

        <p className="mt-6 text-sm text-neo-darkgray">{t("results.mlpNote")}</p>
        <p className="mt-2 text-sm text-neo-darkgray flex flex-wrap gap-x-3 gap-y-1">
          <span>{t("results.reports")}</span>
          {REPORTS.map((r) => (
            <a key={r.key} href={`${REPO_URL}/blob/master/ml/reports/${r.file}`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-bold underline decoration-2 underline-offset-4 hover:text-neo-accent">
              {t(`results.reportLinks.${r.key}`)} <ExternalLink className="w-3 h-3" />
            </a>
          ))}
        </p>

        <div className="mt-12 border-4 border-neo-black p-6 md:p-10 bg-ink text-paper">
          <h3 className="text-2xl md:text-3xl font-bold uppercase mb-3 text-lime">{t("results.diagTitle")}</h3>
          <p className="text-paper/80 mb-6 max-w-3xl leading-relaxed">{t("results.diagIntro")}</p>
          <ul className="space-y-4">
            {years.map((y) => (
              <li key={y} className="grid grid-cols-[4rem_1fr] gap-4 items-baseline">
                <span className="font-mono font-bold bg-neo-orange text-ink px-2 py-0.5 text-center">{y}</span>
                <span className="leading-relaxed">{t(`results.diag.${y}`)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
