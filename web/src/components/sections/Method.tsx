import { Database, History, Lock, Microscope, Scale, Target, TriangleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Card } from "../ui/Card";
import { SectionHeader } from "../ui/SectionHeader";

const STEPS = [
  { key: "data", icon: Database },
  { key: "leakage", icon: Lock },
  { key: "walkforward", icon: History },
  { key: "baselines", icon: Scale },
  { key: "uncertainty", icon: Target },
  { key: "explain", icon: Microscope },
] as const;

const LIMITS = ["appraisal", "revised", "turns", "small"] as const;

export function Method() {
  const { t } = useTranslation();

  return (
    <section id="method" className="py-20 md:py-24 border-b-4 border-neo-black bg-neo-white scroll-mt-20">
      <div className="container mx-auto px-4 md:px-8">
        <SectionHeader title={t("method.title")} />

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {STEPS.map(({ key, icon: Icon }, idx) => (
            <Card key={key}>
              <div className="flex items-center justify-between mb-3">
                <Icon className="w-7 h-7 text-neo-orange" aria-hidden="true" />
                <span className="font-mono text-sm font-bold text-neo-darkgray">0{idx + 1}</span>
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tight pb-3 mb-3 border-b-2 border-neo-black">
                {t(`method.steps.${key}.title`)}
              </h3>
              <p className="leading-relaxed text-neo-darkgray">{t(`method.steps.${key}.desc`)}</p>
            </Card>
          ))}
        </div>

        <div className="mt-12 border-4 border-neo-black p-6 md:p-8 bg-neo-tint">
          <h3 className="text-2xl font-bold uppercase mb-4 flex items-center gap-3">
            <TriangleAlert className="w-6 h-6 text-neo-orange" aria-hidden="true" /> {t("method.limitsTitle")}
          </h3>
          <ul className="grid md:grid-cols-2 gap-x-8 gap-y-3 list-disc pl-5 leading-relaxed">
            {LIMITS.map((l) => (
              <li key={l}>{t(`method.limits.${l}`)}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
