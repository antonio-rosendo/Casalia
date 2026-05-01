import { Activity, Menu } from "lucide-react";
import { Button } from "../ui/Button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full bg-neo-white border-b-4 border-neo-black">
      <div className="container mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2 group cursor-pointer">
          <div className="bg-neo-black text-neo-white p-1">
            <Activity className="w-5 h-5 group-hover:text-neo-yellow transition-colors" />
          </div>
          <span className="font-bold text-xl tracking-tighter uppercase whitespace-nowrap">
            Casalia AI
          </span>
        </div>
        
        <nav className="hidden md:flex items-center gap-6 font-mono text-sm font-bold uppercase">
          <a href="#estimator" className="hover:text-neo-orange hover:underline decoration-2 underline-offset-4 transition-all">Prediction</a>
          <a href="#methodology" className="hover:text-neo-orange hover:underline decoration-2 underline-offset-4 transition-all">Methodology</a>
          <a href="#data" className="hover:text-neo-orange hover:underline decoration-2 underline-offset-4 transition-all">Data & Metrics</a>
        </nav>

        <div className="hidden md:flex items-center gap-4">
          <Button variant="outline" size="sm">Whitepaper</Button>
          <Button size="sm">Get Access</Button>
        </div>

        <button className="md:hidden p-2 border-2 border-neo-black bg-neo-white hover:bg-neo-yellow">
          <Menu className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}