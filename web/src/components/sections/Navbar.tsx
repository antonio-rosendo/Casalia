import { useState } from "react";
import { Menu, X, Globe } from "lucide-react";
import logo from "../../assets/logo.png";
import { useTranslation } from "react-i18next";

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { t, i18n } = useTranslation();

  const toggleLanguage = () => {
    const nextLang = i18n.language === 'es' ? 'en' : 'es';
    i18n.changeLanguage(nextLang);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-neo-white border-b-4 border-neo-black">
      <div className="container mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
        <a href="#" className="flex items-center gap-2 group cursor-pointer no-underline text-neo-black">
          <div className="bg-neo-black p-1">
            <img src={logo} alt="Casalia Logo" className="w-5 h-5 object-contain invert group-hover:sepia transition-all" />
          </div>
          <span className="font-bold text-xl tracking-tighter uppercase whitespace-nowrap">
            Casalia AI
          </span>
        </a>
        
        <nav className="hidden md:flex items-center gap-6 font-mono text-sm font-bold uppercase">
          <a href="#estimator" className="hover:text-neo-orange hover:underline decoration-2 underline-offset-4 transition-all">{t("nav.prediction")}</a>
          <a href="#methodology" className="hover:text-neo-orange hover:underline decoration-2 underline-offset-4 transition-all">{t("nav.methodology")}</a>
          <a href="#data" className="hover:text-neo-orange hover:underline decoration-2 underline-offset-4 transition-all">{t("nav.dataMetrics")}</a>
        </nav>

        <div className="flex items-center gap-2">
          <button 
            onClick={toggleLanguage}
            className="p-2 border-2 border-neo-black bg-neo-white hover:bg-neo-yellow font-mono font-bold uppercase text-xs flex items-center gap-1"
          >
            <Globe className="w-4 h-4" />
            {i18n.language === 'es' ? 'EN' : 'ES'}
          </button>
          
          <button 
            className="md:hidden p-2 border-2 border-neo-black bg-neo-white hover:bg-neo-yellow"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="md:hidden absolute top-16 left-0 w-full bg-neo-white border-b-4 border-neo-black flex flex-col p-4 font-mono font-bold uppercase">
          <a href="#estimator" className="p-3 border-b-2 border-neo-black hover:bg-neo-yellow" onClick={() => setIsMenuOpen(false)}>{t("nav.prediction")}</a>
          <a href="#methodology" className="p-3 border-b-2 border-neo-black hover:bg-neo-yellow" onClick={() => setIsMenuOpen(false)}>{t("nav.methodology")}</a>
          <a href="#data" className="p-3 hover:bg-neo-yellow" onClick={() => setIsMenuOpen(false)}>{t("nav.dataMetrics")}</a>
        </div>
      )}
    </header>
  );
}