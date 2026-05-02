import { useState } from "react";
import { Plus, Minus, Users, ShieldAlert, BarChart } from "lucide-react";

export function SegmentsFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const useCases = [
    { 
      title: "For Analysts", 
      icon: <BarChart />,
      desc: "Analyze structural shifts in local real estate markets using verifiable INE data on inflation and mortgages to build comprehensive quarterly reports."
    },
    { 
      title: "For Buyers", 
      icon: <Users />,
      desc: "Gain an academic projection on future house pricing across autonomous communities to inform better long-term residential investments."
    },
    { 
      title: "Risk Mitigation", 
      icon: <ShieldAlert />,
      desc: "Understand how macroeconomic forces (like changing mortgage rates and age demographics) will likely stress local housing demand over the next 12 months."
    }
  ];

  return (
    <section id="data" className="py-24 border-b-4 border-neo-black bg-neo-gray">
      <div className="container mx-auto px-4 md:px-8 grid lg:grid-cols-2 gap-16">
        <div>
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-8">
            Use Cases & Reliability
          </h2>
          <div className="grid gap-4">
            {useCases.map((useCase, idx) => {
              const isOpen = openIndex === idx;
              return (
                <div 
                  key={idx} 
                  className="bg-neo-white border-3 border-neo-black flex flex-col group neo-shadow cursor-pointer transition-colors"
                  onClick={() => setOpenIndex(isOpen ? null : idx)}
                >
                  <div className={`p-6 flex items-center justify-between ${isOpen ? 'bg-neo-yellow' : 'hover:bg-neo-yellow'}`}>
                    <div className="flex items-center gap-4">
                      <div className="p-2 border-2 border-neo-black bg-neo-black text-neo-white group-hover:bg-neo-orange transition-colors">
                        {useCase.icon}
                      </div>
                      <h3 className="font-bold text-xl uppercase tracking-tight">{useCase.title}</h3>
                    </div>
                    {isOpen ? <Minus className="w-6 h-6" /> : <Plus className="w-6 h-6" />}
                  </div>
                  {isOpen && (
                    <div className="p-6 pt-0 border-t-2 border-neo-black font-mono text-sm bg-neo-white">
                      <div className="mt-4">{useCase.desc}</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="mt-12 bg-neo-black text-neo-white p-8 neo-shadow-orange shadow-neo-orange font-mono">
            <div className="text-xs text-neo-gray mb-2 uppercase">Core System Metric</div>
            <div className="text-3xl md:text-4xl font-bold tracking-tighter text-neo-yellow">
              Continuous Learning
            </div>
            <div className="text-sm mt-2 opacity-80">
              The model incorporates the latest macroeconomic updates from the INE, ensuring inference relies on current market reality rather than stale historical baselines.
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-8">
            Technical FAQ
          </h2>
          <div className="space-y-4">
            {[
              {
                q: "What data structures support the prediction?",
                a: "A tensor approach incorporating tabular economic indicators (IPC, mortgages), demographic data, and historical pricing dynamics."
              },
              {
                q: "How does the platform handle missing variables?",
                a: "Missing INE data points or API fallbacks are gracefully handled using established regional baselines to ensure continuous inference."
              }
            ].map((faq, i) => (
              <div key={i} className="border-3 border-neo-black bg-neo-white p-6 relative">
                <div className="absolute -top-3 -left-3 bg-neo-orange text-neo-black font-bold font-mono text-xs px-2 py-1 border-2 border-neo-black">
                  Q.0{i+1}
                </div>
                <h4 className="font-bold text-lg uppercase mb-2 ml-4">{faq.q}</h4>
                <p className="font-mono text-sm text-neo-darkgray ml-4 pl-4 border-l-2 border-neo-black">
                  {faq.a}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}