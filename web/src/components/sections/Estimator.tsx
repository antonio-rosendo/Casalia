import { useState } from "react";
import { Calculator, MapPin, Ruler } from "lucide-react";
import { Button } from "../ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { cn } from "../../utils/cn";
import { useTranslation } from "react-i18next";

export function Estimator() {
  const { t } = useTranslation();
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState<number | null>(null);
  const [pctChange, setPctChange] = useState<number | null>(null);
  const [confidence, setConfidence] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [comunidad, setComunidad] = useState("madrid");
  const [metros, setMetros] = useState(80);
  const [precioTotal, setPrecioTotal] = useState(250000);

  const handlePredict = async () => {
    setIsPredicting(true);
    setResult(null);
    setPctChange(null);
    setConfidence(null);
    setErrorMsg(null);

    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          comunidad_autonoma: comunidad,
          metros_cuadrados: metros,
          precio_total: precioTotal
        })
      });
      
      if (!response.ok) {
        throw new Error("Local backend error");
      }
      
      const data = await response.json();
      setResult(data.precio_futuro_vivienda);
      setPctChange(data.pct_change_12m);
      setConfidence(data.confidence_category);
    } catch(err: unknown) {
      console.error(err);
      setErrorMsg(t("estimator.error"));
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <section id="estimator" className="py-24 border-b-4 border-neo-black bg-neo-yellow/10">
      <div className="container mx-auto px-4 md:px-8">
        <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="max-w-2xl">
            <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-4">
              {t("estimator.title")}
            </h2>
            <p className="font-mono text-neo-darkgray bg-neo-white p-3 border-2 border-neo-black inline-block">
              {t("estimator.subtitle")}
            </p>
          </div>
          <Badge variant="warning" className="text-lg px-4 py-2 self-start md:self-auto neo-shadow">
            {t("estimator.liveDemo")}
          </Badge>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          {/* Predictor Form */}
          <div className="lg:col-span-7">
            <Card className="bg-neo-white">
              <CardHeader>
                <CardTitle className="uppercase flex items-center gap-2">
                  <Calculator className="w-5 h-5" />
                  {t("estimator.defineParams")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); handlePredict(); }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <MapPin className="w-4 h-4" /> {t("estimator.comunidad")}
                      </label>
                      <select 
                        value={comunidad}
                        onChange={(e) => setComunidad(e.target.value)}
                        className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover"
                      >
                        <option value="andalucia">Andalucía</option>
                        <option value="aragon">Aragón</option>
                        <option value="asturias">Asturias</option>
                        <option value="baleares">Baleares</option>
                        <option value="canarias">Canarias</option>
                        <option value="cantabria">Cantabria</option>
                        <option value="castilla_y_leon">Castilla y León</option>
                        <option value="castilla_la_mancha">Castilla-La Mancha</option>
                        <option value="cataluna">Cataluña</option>
                        <option value="comunitat_valenciana">Comunidad Valenciana</option>
                        <option value="extremadura">Extremadura</option>
                        <option value="galicia">Galicia</option>
                        <option value="madrid">Madrid</option>
                        <option value="murcia">Murcia</option>
                        <option value="navarra">Navarra</option>
                        <option value="pais_vasco">País Vasco</option>
                        <option value="rioja">La Rioja</option>
                        <option value="ceuta">Ceuta</option>
                        <option value="melilla">Melilla</option>
                        <option value="nacional">Nacional (Media)</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <Ruler className="w-4 h-4" /> {t("estimator.metros")}
                      </label>
                      <input 
                        type="number" 
                        value={metros}
                        onChange={(e) => setMetros(Number(e.target.value))}
                        className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <Calculator className="w-4 h-4" /> {t("estimator.precio")}
                      </label>
                      <input 
                        type="number" 
                        value={precioTotal}
                        onChange={(e) => setPrecioTotal(Number(e.target.value))}
                        className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover"
                      />
                    </div>
                  </div>

                  <Button type="submit" className="w-full mt-4" disabled={isPredicting}>
                    {isPredicting ? t("estimator.compute") : t("estimator.execute")}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Results Display */}
          <div className="lg:col-span-5 h-full">
            <div className={cn(
                "h-full border-4 border-neo-black flex flex-col items-center justify-center p-8 text-center transition-colors duration-300",
                result ? "bg-neo-black text-neo-white" : "bg-neo-gray text-neo-black"
              )}>
              
              {!result && !isPredicting && (
                <div className="space-y-4">
                  <div className="w-16 h-16 border-4 border-neo-black rounded-full flex items-center justify-center mx-auto bg-neo-white">
                    <span className="font-mono font-bold text-xl">?</span>
                  </div>
                  <h3 className="font-bold text-xl uppercase">{t("estimator.awaiting")}</h3>
                  <p className="font-mono text-sm max-w-[250px] mx-auto text-neo-darkgray opacity-70">
                    {t("estimator.provide")}
                  </p>
                </div>
              )}

              {isPredicting && (
                <div className="space-y-6">
                  <div className="w-16 h-16 border-4 border-dashed border-neo-black border-t-neo-orange rounded-full flex items-center justify-center mx-auto animate-spin" />
                  <div className="font-mono text-sm animate-pulse space-y-1">
                    <p>{t("estimator.loading.weights")}</p>
                    <p>{t("estimator.loading.normalize")}</p>
                    <p>{t("estimator.loading.inference")}</p>
                  </div>
                </div>
              )}

              {result && !isPredicting && (
                <div className="space-y-6 w-full animate-in fade-in zoom-in duration-300">
                  <Badge variant="warning" className="border-neo-white">{t("estimator.success")}</Badge>
                  <div className="space-y-2">
                    <p className="font-mono text-neo-gray text-sm uppercase">{t("estimator.predictedValue")}</p>
                    <p className="text-5xl md:text-6xl font-bold tracking-tighter text-neo-yellow">
                      €{result.toLocaleString('es-ES', { maximumFractionDigits: 0 })}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 w-full mt-8 border-t-2 border-neo-white/20 pt-6">
                    <div className="text-left font-mono text-xs">
                      <span className="block text-neo-gray/70 uppercase">{t("estimator.increase")}</span>
                      <span className="block text-lg text-neo-white font-bold">
                        {pctChange !== null ? (pctChange > 0 ? "+" : "") + (pctChange * 100).toFixed(2) + "%" : "N/A"}
                      </span>
                    </div>
                    <div className="text-right font-mono text-xs">
                      <span className="block text-neo-gray/70 uppercase">{t("estimator.confidence")}</span>
                      <span className="block text-lg text-neo-white font-bold">
                        {confidence ? t(`estimator.${confidence}`) : t("estimator.excellent")}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {errorMsg && (
                <div className="mt-4 p-3 bg-neo-orange font-mono text-neo-black border-2 border-neo-black neo-shadow">
                  {errorMsg}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}