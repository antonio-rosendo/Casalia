import { Layers, Network, Zap } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import { useTranslation } from "react-i18next";

export function Methodology() {
  const { t } = useTranslation();

  const steps = [
    {
      icon: <Layers className="w-8 h-8" />,
      title: t("methodology.dataIngestion.title"),
      desc: t("methodology.dataIngestion.desc")
    },
    {
      icon: <Network className="w-8 h-8" />,
      title: t("methodology.featureExtraction.title"),
      desc: t("methodology.featureExtraction.desc")
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: t("methodology.dnn.title"),
      desc: t("methodology.dnn.desc")
    }
  ];

  return (
    <section id="methodology" className="py-24 border-b-4 border-neo-black bg-neo-white">
      <div className="container mx-auto px-4 md:px-8">
        <div className="mb-16">
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-4">
            {t("methodology.title")}
          </h2>
          <div className="w-full h-1 bg-neo-black mb-8" />
          <p className="font-mono text-lg max-w-3xl text-neo-darkgray">
            {t("methodology.description")}
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, idx) => (
            <Card key={idx} className="relative overflow-hidden group hover:bg-neo-black hover:text-neo-white transition-colors duration-300">
              {/* Decorative background number */}
              <div className="absolute -right-4 -top-8 text-9xl font-bold text-neo-gray opacity-20 pointer-events-none group-hover:text-neo-white/10 transition-colors">
                0{idx + 1}
              </div>
              
              <CardHeader className="border-neo-black group-hover:border-neo-white transition-colors relative z-10">
                <div className="mb-4 text-neo-orange group-hover:text-neo-yellow transition-colors">
                  {step.icon}
                </div>
                <CardTitle className="uppercase">{step.title}</CardTitle>
              </CardHeader>
              <CardContent className="relative z-10">
                <p className="font-mono text-sm leading-relaxed text-neo-darkgray group-hover:text-neo-gray transition-colors">
                  {step.desc}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Feature weights visualization */}
        <div className="mt-16 border-4 border-neo-black p-6 md:p-12 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiNlNWU1ZTUiLz48L3N2Zz4=')]">
          <div className="bg-neo-white border-2 border-neo-black p-6 md:p-8 neo-shadow-heavy shadow-neo-orange">
            <h3 className="text-2xl font-bold uppercase mb-6 flex items-center justify-between">
              <span>{t("methodology.featureImportance")}</span>
              <span className="font-mono text-xs bg-neo-black text-neo-white px-2 py-1">{t("methodology.shapValues")}</span>
            </h3>
            
            <div className="space-y-4 font-mono text-sm">
              {[
                { label: t("methodology.features.priceDynamics"), pct: 85, color: "bg-neo-black" },
                { label: t("methodology.features.macro"), pct: 72, color: "bg-neo-orange" },
                { label: t("methodology.features.currentPrice"), pct: 58, color: "bg-neo-yellow" },
                { label: t("methodology.features.demographics"), pct: 45, color: "bg-neo-darkgray" },
                { label: t("methodology.features.regional"), pct: 30, color: "bg-neo-gray" },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="w-48 truncate uppercase font-bold text-xs">{item.label}</div>
                  <div className="flex-1 h-6 bg-neo-white border-2 border-neo-black relative">
                    <div 
                      className={`absolute top-0 left-0 bottom-0 border-r-2 border-neo-black ${item.color}`} 
                      style={{ width: `${item.pct}%` }}
                    />
                  </div>
                  <div className="w-12 text-right font-bold">{item.pct}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}