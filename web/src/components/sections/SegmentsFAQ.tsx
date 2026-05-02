import { useState } from "react";
import { Plus, Minus, Users, ShieldAlert, BarChart } from "lucide-react";
import { useTranslation } from "react-i18next";

export function SegmentsFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const { t } = useTranslation();

  const useCases = [
    { 
      title: t("faq.cases.analysts.title"), 
      icon: <BarChart />,
      desc: t("faq.cases.analysts.desc")
    },
    { 
      title: t("faq.cases.buyers.title"), 
      icon: <Users />,
      desc: t("faq.cases.buyers.desc")
    },
    { 
      title: t("faq.cases.risk.title"), 
      icon: <ShieldAlert />,
      desc: t("faq.cases.risk.desc")
    }
  ];

  return (
    <section id="data" className="py-24 border-b-4 border-neo-black bg-neo-gray">
      <div className="container mx-auto px-4 md:px-8 grid lg:grid-cols-2 gap-16">
        <div>
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-8">
            {t("faq.title")}
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
            <div className="text-xs text-neo-gray mb-2 uppercase">{t("faq.metric.title")}</div>
            <div className="text-3xl md:text-4xl font-bold tracking-tighter text-neo-yellow">
              {t("faq.metric.value")}
            </div>
            <div className="text-sm mt-2 opacity-80">
              {t("faq.metric.desc")}
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-tighter mb-8">
            {t("faq.techTitle")}
          </h2>
          <div className="space-y-4">
            {[
              {
                q: t("faq.questions.q1.q"),
                a: t("faq.questions.q1.a")
              },
              {
                q: t("faq.questions.q2.q"),
                a: t("faq.questions.q2.a")
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