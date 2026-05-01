import { ArrowRight, Database } from "lucide-react";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

export function Hero() {
  return (
    <section className="relative w-full pt-20 pb-24 md:pt-32 md:pb-40 border-b-4 border-neo-black overflow-hidden bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiNlNWU1ZTUiLz48L3N2Zz4=')]">
      <div className="container mx-auto px-4 md:px-8 relative z-10 grid lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-8">
          <Badge variant="warning" className="text-base px-3 py-1">
            v1.2.0 Model Live
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold uppercase leading-[0.9] tracking-tighter">
            Architect <br />
            <span className="text-neo-orange">Future</span> Value.
          </h1>
          <p className="font-mono text-base md:text-lg max-w-lg leading-relaxed text-neo-darkgray border-l-4 border-neo-black pl-4">
            An academically rigorous, AI-driven housing prediction model. We estimate and contextualize property values across real estate markets using verifiable metrics and transparent algorithms.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <Button size="lg" className="w-full sm:w-auto gap-2 group">
              Test Model
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button variant="secondary" size="lg" className="w-full sm:w-auto gap-2">
              <Database className="w-5 h-5" />
              View Dataset
            </Button>
          </div>
        </div>

        <div className="relative justify-self-center lg:justify-self-end w-full max-w-md">
          {/* Abstract geometric composition imitating a raw technical dashboard */}
          <div className="aspect-square bg-neo-black p-4 relative neo-shadow-heavy shadow-neo-orange">
            <div className="absolute top-0 right-0 p-2 bg-neo-yellow border-l-4 border-b-4 border-neo-black font-mono font-bold text-xs uppercase z-20">
              Inference Mode
            </div>
            
            <div className="w-full h-full bg-neo-white border-2 border-neo-black flex flex-col relative z-10 relative overflow-hidden">
              <div className="h-10 border-b-2 border-neo-black flex items-center px-4 gap-2 bg-neo-gray">
                <div className="w-3 h-3 rounded-full bg-neo-black" />
                <div className="w-3 h-3 rounded-full bg-neo-orange" />
                <div className="w-3 h-3 rounded-full bg-neo-yellow" />
              </div>
              
              <div className="flex-1 p-6 flex flex-col gap-4">
                <div className="space-y-1">
                  <div className="text-xs font-mono text-neo-darkgray uppercase">Target Value</div>
                  <div className="text-4xl font-bold tracking-tighter">$425,500</div>
                </div>
                
                <div className="w-full h-32 mt-auto border-2 border-neo-black bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiNlNWU1ZTUiLz48L3N2Zz4=')] relative flex items-end">
                   {/* Fake chart bars */}
                   <div className="w-1/6 h-1/4 bg-neo-black border-t-2 border-r-2 border-neo-black"></div>
                   <div className="w-1/6 h-2/4 bg-neo-black border-t-2 border-r-2 border-neo-black"></div>
                   <div className="w-1/6 h-1/3 bg-neo-black border-t-2 border-r-2 border-neo-black"></div>
                   <div className="w-1/6 h-3/4 bg-neo-orange border-t-2 border-r-2 border-neo-black relative">
                     <span className="absolute -top-6 left-1/2 -translate-x-1/2 font-mono text-[10px] font-bold">+12%</span>
                   </div>
                   <div className="w-1/6 h-1/2 bg-neo-black border-t-2 border-r-2 border-neo-black"></div>
                   <div className="w-1/6 h-full bg-neo-yellow border-t-2 border-l-2 border-neo-black relative">
                     <span className="absolute -top-6 left-1/2 -translate-x-1/2 font-mono text-[10px] font-bold">PROJ</span>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}