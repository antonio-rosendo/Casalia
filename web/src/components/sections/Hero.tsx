import { ArrowRight, CodeXml } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Badge } from "../ui/Badge";
import { LinkButton } from "../ui/LinkButton";
import { useForecasts } from "../../data/forecasts";
import { REPO_URL } from "../../config";
import { quarter } from "../../utils/format";

// Dot grid in the theme's grey, so it stays subtle in dark mode too.
const DOTS = "bg-[radial-gradient(var(--theme-gray)_1px,transparent_1px)] bg-[size:20px_20px]";

const STEPS = [
  { n: "01", title: "hero.graphic.data", sub: "hero.graphic.dataSub", dark: false },
  { n: "02", title: "hero.graphic.models", sub: "hero.graphic.modelsSub", dark: true },
  { n: "03", title: "hero.graphic.output", sub: "hero.graphic.outputSub", dark: false },
];

export function Hero() {
  const { t, i18n } = useTranslation();
  const { data } = useForecasts();
  const lng = i18n.language;

  return (
    <section className={`relative w-full pt-16 pb-20 md:pt-24 md:pb-28 border-b-4 border-neo-black overflow-hidden ${DOTS}`}>
      <div className="container mx-auto px-4 md:px-8 relative z-10 grid lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-7">
          <Badge className={`text-xs sm:text-sm px-3 py-1 ${data ? "" : "invisible"}`}>
            {data ? t("hero.badge", { origin: quarter(data.origin, lng), target: quarter(data.target, lng) }) : "…"}
          </Badge>
          <p className="font-mono text-sm md:text-base font-bold uppercase text-neo-darkgray">{t("hero.kicker")}</p>
          <h1 className="text-5xl md:text-7xl font-bold uppercase leading-[0.95] tracking-tighter">
            {t("hero.titleStart")} <span className="text-neo-orange">{t("hero.titleHighlight")}</span>
          </h1>
          <p className="text-lg md:text-xl font-bold max-w-xl leading-snug">{t("hero.answer")}</p>
          <p className="text-base max-w-xl leading-relaxed text-neo-darkgray border-l-4 border-neo-black pl-4">
            {t("hero.description")}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 pt-2">
            <LinkButton href="#forecasts" className="group">
              {t("hero.ctaForecasts")}
              <ArrowRight className="w-5 h-5 motion-safe:group-hover:translate-x-1 transition-transform" />
            </LinkButton>
            <LinkButton href={REPO_URL} external variant="secondary">
              <CodeXml className="w-5 h-5" />
              {t("hero.ctaCode")}
            </LinkButton>
          </div>
        </div>

        {/* Pipeline: official data -> model competition -> logged forecast */}
        <div className="justify-self-center lg:justify-self-end w-full max-w-md bg-neo-white border-4 border-neo-black shadow-neo-heavy p-6 md:p-8 flex flex-col items-center">
          {STEPS.map((s, i) => (
            <div key={s.n} className="w-full flex flex-col items-center">
              {i > 0 && (
                <div aria-hidden="true" className="flex flex-col items-center">
                  <div className="h-7 border-l-4 border-neo-black border-dashed my-1" />
                  <div className="w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[10px] border-t-neo-black mb-1" />
                </div>
              )}
              <div className={`w-full border-3 border-neo-black p-4 relative ${s.dark ? "bg-ink text-paper" : "bg-neo-white"}`}>
                <div className={`absolute -top-3 -left-3 font-mono text-xs px-2 py-1 border-2 border-neo-black font-bold ${s.dark ? "bg-neo-orange text-ink" : "bg-neo-black text-neo-white"}`}>
                  {s.n}
                </div>
                <div className={`text-center font-bold uppercase tracking-tight ${s.dark ? "text-lime" : ""}`}>{t(s.title)}</div>
                <div className={`text-center font-mono text-xs mt-1 ${s.dark ? "text-paper/80" : "text-neo-darkgray"}`}>{t(s.sub)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
