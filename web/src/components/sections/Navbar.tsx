import { useEffect, useState } from "react";
import { CodeXml, Menu, X, Globe, Moon, Sun } from "lucide-react";
import logo from "../../assets/logo.png";
import { useTranslation } from "react-i18next";
import { useDarkMode } from "../../hooks/useDarkMode";
import { cn } from "../../utils/cn";
import { REPO_URL } from "../../config";

const LINKS = [
  { href: "#forecasts", key: "nav.forecasts" },
  { href: "#results", key: "nav.results" },
  { href: "#method", key: "nav.method" },
];

const iconButton = "p-2 border-2 border-neo-black bg-neo-white hover:bg-neo-yellow hover:text-ink font-mono font-bold uppercase text-xs flex items-center gap-1 transition-colors";

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { t, i18n } = useTranslation();
  const { isDark, toggleTheme } = useDarkMode();
  const isSpanish = i18n.language.startsWith("es");

  useEffect(() => {
    if (!isMenuOpen) return;
    const close = (e: KeyboardEvent) => e.key === "Escape" && setIsMenuOpen(false);
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [isMenuOpen]);

  return (
    <header className="sticky top-0 z-50 w-full bg-neo-white border-b-4 border-neo-black text-neo-black">
      <div className="container mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
        <a href="#" className="flex items-center gap-2 group no-underline text-neo-black">
          <div className="bg-neo-black p-1">
            <img src={logo} alt="" className={cn("w-5 h-5 object-contain", isDark ? "" : "invert")} />
          </div>
          <span className="font-bold text-xl tracking-tighter uppercase whitespace-nowrap">Casalia</span>
        </a>

        <nav className="hidden md:flex items-center gap-6 font-mono text-sm font-bold uppercase">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="hover:text-neo-accent hover:underline decoration-2 underline-offset-4">{t(l.key)}</a>
          ))}
          <a href={REPO_URL} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-neo-accent hover:underline decoration-2 underline-offset-4">
            <CodeXml className="w-4 h-4" /> {t("nav.code")}
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <button onClick={toggleTheme} className={iconButton} title={t("nav.toggleTheme")} aria-label={t("nav.toggleTheme")}>
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <button
            onClick={() => i18n.changeLanguage(isSpanish ? "en" : "es")}
            className={iconButton}
            aria-label={t("nav.switchLanguage")}
            lang={isSpanish ? "en" : "es"}
          >
            <Globe className="w-4 h-4" />
            {isSpanish ? "EN" : "ES"}
          </button>

          <button
            className={cn(iconButton, "md:hidden")}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label={t("nav.toggleMenu")}
            aria-expanded={isMenuOpen}
            aria-controls="mobile-menu"
          >
            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {isMenuOpen && (
        <div id="mobile-menu" className="md:hidden absolute top-16 left-0 w-full bg-neo-white border-b-4 border-neo-black flex flex-col p-4 font-mono font-bold uppercase">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="p-3 border-b-2 border-neo-black hover:bg-neo-yellow hover:text-ink" onClick={() => setIsMenuOpen(false)}>{t(l.key)}</a>
          ))}
          <a href={REPO_URL} target="_blank" rel="noreferrer" className="p-3 hover:bg-neo-yellow hover:text-ink">{t("nav.code")}</a>
        </div>
      )}
    </header>
  );
}
