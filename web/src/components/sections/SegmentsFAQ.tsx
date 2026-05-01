import { Plus, Users, ShieldAlert, BarChart } from "lucide-react";

export function SegmentsFAQ() {
  const useCases = [
    { title: "For Analysts", icon: <BarChart /> },
    { title: "For Buyers", icon: <Users /> },
    { title: "Risk Mitigation", icon: <ShieldAlert /> }
  ];

  return (
    <section id="data" className="py-24 border-b-4 border-neo-black bg-neo-gray">
      <div className="container mx-auto px-4 md:px-8 grid lg:grid-cols-2 gap-16">
        <div>
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-8">
            Use Cases & Reliability
          </h2>
          <div className="grid gap-6">
            {useCases.map((useCase, idx) => (
              <div 
                key={idx} 
                className="bg-neo-white border-3 border-neo-black p-6 flex items-center justify-between group hover:bg-neo-yellow transition-colors neo-shadow cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 border-2 border-neo-black bg-neo-black text-neo-white group-hover:bg-neo-orange transition-colors">
                    {useCase.icon}
                  </div>
                  <h3 className="font-bold text-xl uppercase tracking-tight">{useCase.title}</h3>
                </div>
                <Plus className="w-6 h-6" />
              </div>
            ))}
          </div>

          <div className="mt-12 bg-neo-black text-neo-white p-8 neo-shadow-orange shadow-neo-orange font-mono">
            <div className="text-xs text-neo-gray mb-2 uppercase">Core System Metric</div>
            <div className="text-4xl font-bold tracking-tighter text-neo-yellow">
              94.8%
            </div>
            <div className="text-sm mt-2 opacity-80">
              R-Squared (R²) accuracy on holdout test set across 12 metropolitan zones. Maximum absolute error capped at ±4.2% within core zones.
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
                a: "A mixed tensor approach incorporating tabular census records, geometric polygon properties for zoning, and historical transaction graphs."
              },
              {
                q: "How does the platform handle missing variables?",
                a: "Missing inputs are imputed using K-Nearest Neighbors based on geometric proximity, ensuring outliers do not distort the vector space."
              },
              {
                q: "Is this model suitable for real-time market trading?",
                a: "This demonstration constitutes an academic proof-of-concept. Real-time arbitrage requires API-level integration with live listing services, which is supported by our architecture."
              },
              {
                q: "Can I self-host this prediction engine?",
                a: "Yes. The model is containerized with Docker and inferencing endpoints are built on FastAPI, enabling localized deployments."
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