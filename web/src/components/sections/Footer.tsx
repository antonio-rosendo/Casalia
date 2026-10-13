import { CodeXml, ExternalLink } from "lucide-react";
import { useTranslation } from "react-i18next";
import { EMAIL, GITHUB_URL, LINKEDIN_URL, REPO_URL } from "../../config";

const linkClass = "inline-flex items-center gap-1 font-bold underline decoration-2 underline-offset-4 hover:text-lime";

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="bg-ink text-paper py-12 border-t-4 border-neo-orange">
      <div className="container mx-auto px-4 md:px-8">
        <div className="grid md:grid-cols-[2fr_1fr] gap-10 border-b-2 border-paper/20 pb-10 mb-8">
          <p className="leading-relaxed text-paper/80 max-w-2xl">{t("footer.story")}</p>
          <div className="md:justify-self-end">
            <a href={REPO_URL} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 font-mono font-bold uppercase border-2 border-paper px-4 h-11 hover:bg-lime hover:text-ink transition-colors">
              <CodeXml className="w-4 h-4" /> {t("footer.code")}
            </a>
          </div>
        </div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono text-sm">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            <span className="text-lime font-bold uppercase">{t("footer.by")}</span>
            <a href={LINKEDIN_URL} target="_blank" rel="noreferrer" className={linkClass}>LinkedIn <ExternalLink className="w-3 h-3" /></a>
            <a href={GITHUB_URL} target="_blank" rel="noreferrer" className={linkClass}>GitHub <ExternalLink className="w-3 h-3" /></a>
            <a href={`mailto:${EMAIL}`} className={linkClass}>{EMAIL}</a>
          </div>
          <span className="text-xs uppercase text-paper/80">{t("footer.data")} {t("footer.disclaimer")}</span>
        </div>
      </div>
    </footer>
  );
}
