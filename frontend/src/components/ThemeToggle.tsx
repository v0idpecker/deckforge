import { Box, IconButton } from "@mui/material";
import { useThemeMode } from "../app/ThemeModeContext";

function SunIcon() {
  return (
    <Box
      component="svg"
      viewBox="0 0 24 24"
      sx={{ width: 20, height: 20 }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </Box>
  );
}

function MoonIcon() {
  return (
    <Box
      component="svg"
      viewBox="0 0 24 24"
      sx={{ width: 18, height: 18 }}
      fill="currentColor"
      aria-hidden
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </Box>
  );
}

export function ThemeToggle() {
  const { mode, toggleMode } = useThemeMode();
  return (
    <IconButton
      onClick={toggleMode}
      aria-label={mode === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      sx={{
        color: "text.secondary",
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2,
        transition: "color 0.2s ease, border-color 0.2s ease",
        "&:hover": {
          color: "primary.main",
          borderColor: "primary.main",
          backgroundColor: "transparent",
        },
      }}
    >
      {mode === "dark" ? <SunIcon /> : <MoonIcon />}
    </IconButton>
  );
}
