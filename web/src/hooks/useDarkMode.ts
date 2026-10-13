import { useEffect, useState } from "react";

// Storage can be blocked (private mode, strict privacy settings): never let it break the page.
function savedTheme(): string | null {
  try {
    return localStorage.getItem("theme");
  } catch {
    return null;
  }
}

export function useDarkMode() {
  const [isDark, setIsDark] = useState(() => {
    const saved = savedTheme();
    return saved ? saved === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  // Only an explicit choice is remembered; otherwise the page follows the system theme.
  const toggleTheme = () => {
    const next = !isDark;
    setIsDark(next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      // keep the choice for this visit only
    }
  };

  return { isDark, toggleTheme };
}
