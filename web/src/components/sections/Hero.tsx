import { ArrowRight, Database } from "lucide-react";
import { Badge } from "../ui/Badge";
import { useTranslation } from "react-i18next";

export function Hero() {
  const { t } = useTranslation();

  return (
    <section className="relative w-full pt-20 pb-24 md:pt-32 md:pb-40 border-b-4 border-neo-black overflow-hidden bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiNlNWU1ZTUiLz48L3N2Zz4=')]">
      <div className="container mx-auto px-4 md:px-8 relative z-10 grid lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-8">
          <Badge variant="warning" className="text-base px-3 py-1">
            {t("hero.version")}
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold uppercase leading-[0.9] tracking-tighter">
            {t("hero.architect")} <br />
            <span className="text-neo-orange">{t("hero.future")}</span> {t("hero.value")}
          </h1>
          <p className="font-mono text-base md:text-lg max-w-lg leading-relaxed text-neo-darkgray border-l-4 border-neo-black pl-4">
            {t("hero.description")}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <a href="#estimator" className="inline-flex items-center justify-center whitespace-nowrap font-mono font-bold uppercase transition-all duration-300 active:translate-y-0.5 active:shadow-none bg-neo-black text-neo-white hover:bg-neo-orange border-2 border-neo-black neo-shadow h-12 px-8 text-base w-full sm:w-auto gap-2 group">
              {t("hero.testModel")}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </a>
            <a href="/datos_unidos_meses.csv" download className="inline-flex items-center justify-center whitespace-nowrap font-mono font-bold uppercase transition-all duration-300 active:translate-y-0.5 active:shadow-none bg-neo-white text-neo-black hover:bg-neo-yellow border-2 border-neo-black neo-shadow h-12 px-8 text-base w-full sm:w-auto gap-2">
              <Database className="w-5 h-5" />
              {t("hero.viewDataset")}
            </a>
          </div>
        </div>

        <div className="relative justify-self-center lg:justify-self-end w-full max-w-md">
          {/* Data Pipeline Visualization */}
          <div className="bg-neo-black p-4 relative neo-shadow-heavy shadow-neo-orange">
            <div className="absolute inset-0 opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiNlNWU1ZTUiLz48L3N2Zz4=')]" />
            
            <div className="w-full bg-neo-white border-2 border-neo-black flex flex-col relative z-10">
              <div className="h-10 border-b-2 border-neo-black flex items-center px-4 gap-2 bg-neo-gray">
                <div className="w-3 h-3 rounded-full bg-neo-black" />
                <div className="w-3 h-3 rounded-full bg-neo-orange" />
                <div className="w-3 h-3 rounded-full bg-neo-yellow" />
              </div>
              
              <div className="p-6 md:p-8 flex flex-col items-center">
                {/* Node 1: Data Feed */}
                <div className="w-full border-3 border-neo-black bg-neo-white p-4 relative group hover:bg-neo-yellow transition-colors duration-300 z-10">
                  <div className="absolute -top-3 -left-3 bg-neo-black text-neo-white font-mono text-xs px-2 py-1 border-2 border-neo-black font-bold">
                    01
                  </div>
                  <div className="text-center font-bold uppercase tracking-tight">{t("hero.graphic.ineData")}</div>
                  <div className="text-center font-mono text-xs text-neo-darkgray mt-1">{t("hero.graphic.macro")}</div>
                </div>

                {/* Arrow Down */}
                <div className="h-8 border-l-4 border-neo-black border-dashed my-1 relative z-0" />
                <div className="w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[10px] border-t-neo-black mb-1 z-10" />

                {/* Node 2: Model Layer */}
                <div className="w-full border-3 border-neo-black bg-neo-black text-neo-white p-4 relative shadow-neo-orange neo-shadow-orange z-10">
                  <div className="absolute -top-3 -left-3 bg-neo-orange text-neo-black font-mono text-xs px-2 py-1 border-2 border-neo-black font-bold">
                    02
                  </div>
                  <div className="text-center font-bold uppercase tracking-tight text-neo-yellow">{t("hero.graphic.pytorch")}</div>
                  <div className="text-center font-mono text-xs text-neo-gray mt-1">{t("hero.graphic.tensor")}</div>
                </div>

                {/* Arrow Down */}
                <div className="h-8 border-l-4 border-neo-black border-dashed my-1 relative z-0" />
                <div className="w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[10px] border-t-neo-black mb-1 z-10" />

                {/* Node 3: Output */}
                <div className="w-full border-3 border-neo-black bg-neo-white p-4 relative group hover:bg-neo-orange transition-colors duration-300 z-10">
                  <div className="absolute -top-3 -left-3 bg-neo-black text-neo-white font-mono text-xs px-2 py-1 border-2 border-neo-black font-bold">
                    03
                  </div>
                  <div className="text-center font-bold uppercase tracking-tight text-xl">{t("hero.graphic.prediction")}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}