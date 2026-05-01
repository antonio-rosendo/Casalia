import { useState } from "react";
import { Calculator, MapPin, Ruler, Calendar, CheckSquare } from "lucide-react";
import { Button } from "../ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { cn } from "../../utils/cn";

export function Estimator() {
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState<number | null>(null);

  const handlePredict = () => {
    setIsPredicting(true);
    setResult(null);
    setTimeout(() => {
      setIsPredicting(false);
      setResult(385000 + Math.random() * 50000);
    }, 1500);
  };

  return (
    <section id="estimator" className="py-24 border-b-4 border-neo-black bg-neo-yellow/10">
      <div className="container mx-auto px-4 md:px-8">
        <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="max-w-2xl">
            <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-4">
              Model Inference
            </h2>
            <p className="font-mono text-neo-darkgray bg-neo-white p-3 border-2 border-neo-black inline-block">
              // Inputs are sanitized and fed to the XGBoost ensemble model.
            </p>
          </div>
          <Badge variant="warning" className="text-lg px-4 py-2 self-start md:self-auto neo-shadow">
            LIVE DEMO
          </Badge>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          {/* Predictor Form */}
          <div className="lg:col-span-7">
            <Card className="bg-neo-white">
              <CardHeader>
                <CardTitle className="uppercase flex items-center gap-2">
                  <Calculator className="w-5 h-5" />
                  Define Parameters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); handlePredict(); }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <MapPin className="w-4 h-4" /> Zoning District
                      </label>
                      <select className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover">
                        <option>Urban Core (D1)</option>
                        <option>Suburban Res (R2)</option>
                        <option>Commercial Mix (C3)</option>
                        <option>Industrial Edge (I1)</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <Ruler className="w-4 h-4" /> Area (Sq. Meters)
                      </label>
                      <input 
                        type="number" 
                        defaultValue={120}
                        className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <Calendar className="w-4 h-4" /> Year Built
                      </label>
                      <input 
                        type="number" 
                        defaultValue={2015}
                        className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="font-mono text-sm font-bold uppercase block flex items-center gap-2">
                        <CheckSquare className="w-4 h-4" /> Transit Proximity
                      </label>
                      <select className="w-full h-12 border-2 border-neo-black bg-neo-white px-3 font-sans focus:outline-none focus:ring-2 focus:ring-neo-orange neo-shadow-hover">
                        <option>High (&lt;500m)</option>
                        <option>Medium (500m - 2km)</option>
                        <option>Low (&gt;2km)</option>
                      </select>
                    </div>
                  </div>

                  <Button type="submit" className="w-full mt-4" disabled={isPredicting}>
                    {isPredicting ? "Computing Tensor Data..." : "Execute Prediction"}
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
                  <h3 className="font-bold text-xl uppercase">Awaiting Input</h3>
                  <p className="font-mono text-sm max-w-[250px] mx-auto text-neo-darkgray opacity-70">
                    Provide the spatial parameters to calculate the estimated local valuation.
                  </p>
                </div>
              )}

              {isPredicting && (
                <div className="space-y-6">
                  <div className="w-16 h-16 border-4 border-dashed border-neo-black border-t-neo-orange rounded-full flex items-center justify-center mx-auto animate-spin" />
                  <div className="font-mono text-sm animate-pulse space-y-1">
                    <p>Load weights: OK</p>
                    <p>Normalize parameters: OK</p>
                    <p>Running inference...</p>
                  </div>
                </div>
              )}

              {result && !isPredicting && (
                <div className="space-y-6 w-full animate-in fade-in zoom-in duration-300">
                  <Badge variant="warning" className="border-neo-white">SUCCESS_OP</Badge>
                  <div className="space-y-2">
                    <p className="font-mono text-neo-gray text-sm uppercase">Predicted Market Value</p>
                    <p className="text-5xl md:text-6xl font-bold tracking-tighter text-neo-yellow">
                      ${result.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 w-full mt-8 border-t-2 border-neo-white/20 pt-6">
                    <div className="text-left font-mono text-xs">
                      <span className="block text-neo-gray/70 uppercase">Confidence</span>
                      <span className="block text-lg text-neo-white font-bold">92.4%</span>
                    </div>
                    <div className="text-right font-mono text-xs">
                      <span className="block text-neo-gray/70 uppercase">Model Volatility</span>
                      <span className="block text-lg text-neo-white font-bold">±$12k</span>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </section>
  );
}