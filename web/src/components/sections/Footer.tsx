import { ArrowUpRight } from "lucide-react";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

export function Footer() {
  return (
    <footer className="bg-neo-black text-neo-white py-12 border-t-4 border-neo-orange relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 border-l-4 border-b-4 border-neo-orange bg-neo-yellow text-neo-black font-mono text-xs uppercase font-bold z-10 hidden sm:block">
        Final Degree Project // 2026
      </div>

      <div className="container mx-auto px-4 md:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center border-b-2 border-neo-darkgray pb-12 mb-8">
          <div>
            <h2 className="text-4xl md:text-6xl font-bold uppercase tracking-tighter mb-4 text-neo-yellow">
              Ready <br />
              <span className="text-neo-white">To Deploy.</span>
            </h2>
            <p className="font-mono text-neo-gray max-w-sm">
              The AI-Powered Real Estate Platform built for scale, reliability, and precision.
            </p>
          </div>
          <div className="md:justify-self-end flex flex-col gap-4 w-full md:w-auto">
            <Button size="lg" className="w-full md:w-auto gap-2 group relative">
              Access Full API Docs
              <ArrowUpRight className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
            </Button>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-6 font-mono text-xs uppercase tracking-tight text-neo-gray">
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-neo-gray text-neo-gray">Casalia AI v1.0</Badge>
            <span>© 2026 Academic Demo</span>
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-neo-yellow transition-colors underline decoration-2 underline-offset-4">GitHub Repo</a>
            <a href="#" className="hover:text-neo-yellow transition-colors underline decoration-2 underline-offset-4">Documentation</a>
            <a href="#" className="hover:text-neo-yellow transition-colors underline decoration-2 underline-offset-4">MIT License</a>
          </div>
        </div>
      </div>
    </footer>
  );
}