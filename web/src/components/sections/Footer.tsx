import { Badge } from "../ui/Badge";
import { useTranslation } from "react-i18next";

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="bg-neo-black text-neo-white py-12 border-t-4 border-neo-orange relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 border-l-4 border-b-4 border-neo-orange bg-neo-yellow text-neo-black font-mono text-xs uppercase font-bold z-10 hidden sm:block">
        {t("footer.projectBadge")}
      </div>

      <div className="container mx-auto px-4 md:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center border-b-2 border-neo-darkgray pb-12 mb-8">
          <div>
            <h2 className="text-4xl md:text-6xl font-bold uppercase tracking-tighter mb-4 text-neo-yellow">
              {t("footer.titleReady")} <br />
              <span className="text-neo-white">{t("footer.titleDeploy")}</span>
            </h2>
            <p className="font-mono text-neo-gray max-w-sm">
              {t("footer.desc")}
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-6 font-mono text-xs uppercase tracking-tight text-neo-gray">
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-neo-black text-neo-black font-bold">Casalia AI v1.0</Badge>
            <span>{t("footer.academic")}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}