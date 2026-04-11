import { alpha, createTheme } from "@mui/material/styles";

const ink = "#171312";
const paper = "#f4ead7";
const paperBright = "#fff7ea";
const orange = "#ff6b2c";
const blue = "#2358ff";
const yellow = "#f4c94f";
const moss = "#2d8f5c";
const brick = "#d6452f";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: orange,
      light: "#ff8d5f",
      dark: "#cc4f19",
      contrastText: ink,
    },
    secondary: {
      main: blue,
      light: "#6b8bff",
      dark: "#1436ad",
      contrastText: "#ffffff",
    },
    background: {
      default: paper,
      paper: paperBright,
    },
    text: {
      primary: ink,
      secondary: "#5f5347",
    },
    divider: alpha(ink, 0.16),
    error: {
      main: brick,
      light: "#f7ddd7",
    },
    warning: {
      main: "#b97700",
      light: "#ffefc6",
    },
    success: {
      main: moss,
      light: "#dbefe1",
    },
  },
  shape: {
    borderRadius: 24,
  },
  typography: {
    fontFamily: '"Space Grotesk", "Segoe UI", sans-serif',
    h1: {
      fontFamily: '"Bricolage Grotesque", "Space Grotesk", sans-serif',
      fontWeight: 800,
      letterSpacing: "-0.05em",
      lineHeight: 0.95,
    },
    h2: {
      fontFamily: '"Bricolage Grotesque", "Space Grotesk", sans-serif',
      fontWeight: 800,
      letterSpacing: "-0.045em",
      lineHeight: 0.98,
    },
    h3: {
      fontFamily: '"Bricolage Grotesque", "Space Grotesk", sans-serif',
      fontWeight: 700,
      letterSpacing: "-0.04em",
      lineHeight: 1,
    },
    h4: {
      fontFamily: '"Bricolage Grotesque", "Space Grotesk", sans-serif',
      fontWeight: 700,
      letterSpacing: "-0.03em",
      lineHeight: 1.05,
    },
    h5: {
      fontFamily: '"Bricolage Grotesque", "Space Grotesk", sans-serif',
      fontWeight: 700,
      letterSpacing: "-0.02em",
      lineHeight: 1.1,
    },
    h6: {
      fontFamily: '"Bricolage Grotesque", "Space Grotesk", sans-serif',
      fontWeight: 700,
      letterSpacing: "-0.02em",
      lineHeight: 1.1,
    },
    subtitle1: {
      fontWeight: 700,
      letterSpacing: "-0.01em",
    },
    body1: {
      lineHeight: 1.6,
      letterSpacing: "-0.01em",
    },
    body2: {
      lineHeight: 1.55,
      letterSpacing: "-0.01em",
    },
    overline: {
      fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
      fontWeight: 600,
      letterSpacing: "0.16em",
      textTransform: "uppercase",
    },
    button: {
      fontFamily: '"Space Grotesk", "Segoe UI", sans-serif',
      fontWeight: 700,
      letterSpacing: "0.04em",
      textTransform: "uppercase",
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          color: ink,
          backgroundColor: paper,
        },
        "::selection": {
          backgroundColor: alpha(yellow, 0.8),
          color: ink,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          border: `2px solid ${alpha(ink, 0.82)}`,
          backgroundImage: [
            `radial-gradient(circle at top right, ${alpha(yellow, 0.14)}, transparent 38%)`,
            `linear-gradient(180deg, ${alpha("#ffffff", 0.7)}, ${alpha(
              paperBright,
              0.96,
            )})`,
          ].join(","),
          boxShadow: `10px 10px 0 ${alpha(ink, 0.14)}`,
          transition:
            "transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: 52,
          borderRadius: 999,
          paddingInline: 24,
          borderWidth: 2,
          borderStyle: "solid",
          boxShadow: "none",
          transition:
            "transform 140ms ease, box-shadow 140ms ease, background-color 140ms ease, color 140ms ease",
          "&:hover": {
            transform: "translate(-2px, -2px)",
            boxShadow: `6px 6px 0 ${alpha(ink, 0.22)}`,
          },
        },
        containedPrimary: {
          borderColor: alpha(ink, 0.92),
          backgroundColor: orange,
          color: ink,
          "&:hover": {
            backgroundColor: "#ff7a43",
          },
        },
        containedSecondary: {
          borderColor: alpha(ink, 0.92),
          "&:hover": {
            backgroundColor: "#3e6dff",
          },
        },
        outlined: {
          borderColor: alpha(ink, 0.92),
          color: ink,
          backgroundColor: alpha("#ffffff", 0.44),
        },
        text: {
          borderColor: "transparent",
          paddingInline: 8,
          "&:hover": {
            backgroundColor: alpha(ink, 0.05),
            boxShadow: "none",
            transform: "none",
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          minHeight: 34,
          borderRadius: 999,
          border: `1.5px solid ${alpha(ink, 0.75)}`,
          backgroundColor: alpha("#ffffff", 0.56),
          color: ink,
          fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
          fontWeight: 500,
          letterSpacing: "0.02em",
        },
        deleteIcon: {
          color: alpha(ink, 0.72),
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 22,
          backgroundColor: alpha("#ffffff", 0.48),
          transition:
            "transform 140ms ease, box-shadow 140ms ease, background-color 140ms ease",
          "& .MuiOutlinedInput-notchedOutline": {
            borderWidth: 2,
            borderColor: alpha(ink, 0.75),
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: ink,
          },
          "&.Mui-focused": {
            boxShadow: `0 0 0 4px ${alpha(blue, 0.12)}`,
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: blue,
          },
        },
        input: {
          paddingTop: 15,
          paddingBottom: 15,
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          fontWeight: 700,
          letterSpacing: "0.01em",
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 24,
          border: `2px solid ${alpha(ink, 0.85)}`,
          color: ink,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          height: 12,
          borderRadius: 999,
          overflow: "hidden",
          backgroundColor: alpha(ink, 0.08),
        },
        bar: {
          borderRadius: 999,
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          color: orange,
        },
        rail: {
          opacity: 1,
          backgroundColor: alpha(ink, 0.12),
        },
        track: {
          border: "none",
        },
        thumb: {
          width: 18,
          height: 18,
          border: `2px solid ${ink}`,
          boxShadow: "none",
          backgroundColor: yellow,
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        switchBase: {
          "&.Mui-checked": {
            color: ink,
          },
          "&.Mui-checked + .MuiSwitch-track": {
            backgroundColor: yellow,
            opacity: 1,
          },
        },
        thumb: {
          backgroundColor: paperBright,
          border: `2px solid ${ink}`,
        },
        track: {
          opacity: 1,
          borderRadius: 999,
          backgroundColor: alpha(ink, 0.18),
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          margin: 4,
        },
      },
    },
  },
});
