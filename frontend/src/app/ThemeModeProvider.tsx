import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { createAppTheme, type ThemeMode } from "./theme";
import { ThemeModeContext } from "./ThemeModeContext";

const STORAGE_KEY = "ankislop-theme";

const themeColors: Record<ThemeMode, string> = {
  dark: "#0D0A08",
  light: "#FAF4EE",
};

function initialMode(): ThemeMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "dark" || stored === "light") {
      return stored;
    }
  } catch {
    return "dark";
  }
  return "dark";
}

function applyDocumentMode(mode: ThemeMode) {
  document.documentElement.style.colorScheme = mode;
  let meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  if (!meta) {
    meta = document.createElement("meta");
    meta.name = "theme-color";
    document.head.appendChild(meta);
  }
  meta.content = themeColors[mode];
}

export function ThemeModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(initialMode);
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  useEffect(() => {
    applyDocumentMode(mode);
  }, [mode]);

  const toggleMode = useCallback(() => {
    setMode((prev) => {
      const next: ThemeMode = prev === "dark" ? "light" : "dark";
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch {
        return next;
      }
      return next;
    });
  }, []);

  const value = useMemo(
    () => ({ mode, toggleMode }),
    [mode, toggleMode],
  );

  return (
    <ThemeModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
}
